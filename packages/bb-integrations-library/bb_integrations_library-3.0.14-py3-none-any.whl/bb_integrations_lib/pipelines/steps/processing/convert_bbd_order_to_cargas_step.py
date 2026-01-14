from datetime import datetime
from typing import AsyncGenerator

import pandas as pd
from loguru import logger

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.mappers.rita_mapper import RitaMapperCore, RitaMapper, RitaAPIMappingProvider
from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.protocols.pipelines import GeneratorStep
from bb_integrations_lib.provider.api.cargas.model import CreateWholesaleTicketRequestBundle, \
    CreateWholesaleTicketRequest, CreateWholesaleLineRequest


class ConvertBBDOrderToCargasWholesaleStep(GeneratorStep):
    def __init__(self, rita_client: GravitateRitaAPI, sd_client: GravitateSDAPI, mapping_source_system: str = "Cargas", *args, **kwargs):
        """
        Convert a BBD order's drops to Cargas wholesale ticket request objects. Input should be an item returned by the
        v1/bols_and_drops endpoint, and should only include orders with at least 1 drop at a wholesale store. Passing an
        order with no wholesale drops will result in a ticket request being generated with no line items.

        Mappings are best-effort; if a field that is not strictly required is not mapped, it will be left out.

        :param rita_client: The GravitateRitaAPI instance to use to get mappings with.
        :param sd_client: The GravitateSDAPI instance to use for API calls.
        :param mapping_source_system: The source system to use for mapping. Defaults to "Cargas".
        """
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.sd_client = sd_client
        self.mapping_source_system = mapping_source_system

        self.store_lkp = {}
        self.driver_sched_lkp = {}
        # Only optional because it will be late initialized by either _load_lookups or _set_test_lookups.
        self.rita_mapper: RitaMapper | None = None

    def describe(self) -> str:
        return f"Convert drops on a BBD order to Cargas create wholesale ticket / ticket line requests"

    async def _load_lookups(self, driver_schedules: set[str]):
        stores = await self.sd_client.get_all_stores()
        stores.raise_for_status()
        self.store_lkp = {store["_id"]: store for store in stores.json()}

        drivers = await self.sd_client.get_driver_tracking(driver_schedule_ids=list(driver_schedules))
        drivers.raise_for_status()
        self.driver_sched_lkp = {driver["driver_schedule_id"]: driver for driver in drivers.json()}

        self.rita_mapper = RitaMapper(
            provider=RitaAPIMappingProvider(self.rita_client),
            source_system=self.mapping_source_system
        )
        await self.rita_mapper.load_mappings_async()

    def _set_test_lookups(self, store_lkp: dict, driver_sched_lkp: dict, rita_mapper: RitaMapperCore):
        self.store_lkp = store_lkp
        self.driver_sched_lkp = driver_sched_lkp
        self.rita_mapper = rita_mapper

    async def generator(self, orders: list[dict]) -> AsyncGenerator[CreateWholesaleTicketRequestBundle, None]:
        driver_schedules = set([
            abol["driver_schedule"] for order in orders for abol in order["allocated_bols"]
        ])
        await self._load_lookups(driver_schedules=driver_schedules)

        assert self.rita_mapper is not None, "RITA mapper must be initialized before generator is called"

        for order in orders:
            for result in self.convert_order(order):
                yield result

    def convert_order(self, order: dict) -> list[CreateWholesaleTicketRequestBundle]:
        """
        Converts an S&D order dictionary into one or more Cargas ticket request bundle objects, including line items.
        Line items produced by this function will have a blank DocumentID, which should be filled in with the
        DocumentID that CreateWholesaleTicket returns.
        """
        order_number = order["order_number"]
        allocated_bols = order["allocated_bols"]
        if not allocated_bols:
            raise Exception("Could not convert order: no allocated BOLs")

        bols_df = pd.DataFrame.from_records(allocated_bols)
        # Precompute destination counterparty - could be 2 different stores of same counterparty on a split load
        bols_df["store_counterparty_name"] = bols_df.apply(
            lambda x: self.store_lkp[x["store_id"]]["counterparty_name"],
            axis="columns"
        )
        bols_df["driver_name"] = bols_df.apply(
            lambda x: self.driver_sched_lkp.get(x["driver_schedule"], {}).get("driver_name", ""),
            axis="columns"
        )
        bols_df["tractor"] = bols_df.apply(
            lambda x: self.driver_sched_lkp.get(x["driver_schedule"], {}).get("driver_log", {}).get("tractor", ""),
            axis="columns"
        )

        results = []
        bol_gb = bols_df.groupby(by=["bol_number", "store_counterparty_name", "driver_name", "tractor"])
        for (bol_number, store_cp_name, driver_name, tractor), group in bol_gb:
            mcid_str = None
            try:
                mcid_str = self.rita_mapper.get_source_parent_id(store_cp_name, MappingType.counterparty)
                mapped_customer_id = int(mcid_str)
            except KeyError as e:
                mapped_customer_id = None
                logger.warning(f"Failed to map store counterparty {store_cp_name}: {e}, skipping drops")
                continue
            except ValueError as e:
                logger.warning(f"Failed to convert mapped customer ID '{mcid_str}' to int, skipping drops")
                continue

            try:
                mapped_driver_id = self.rita_mapper.get_source_parent_id(driver_name, MappingType.driver)
            except KeyError:
                logger.warning(f"Failed to map driver ID '{driver_name}', it will be blank on the ticket")
                mapped_driver_id = None
            try:
                mapped_tractor_id = self.rita_mapper.get_source_parent_id(tractor, MappingType.tractor)
            except KeyError:
                logger.warning(f"Failed to map tractor ID '{tractor}', it will be blank on the ticket")
                mapped_tractor_id = None

            try:
                ticket_request = CreateWholesaleTicketRequest(
                    CustomerID=mapped_customer_id,
                    DeliveryDate=datetime.fromisoformat(max(group["delivered_date"])),
                    CustomerPONumber=bol_number,
                    DriverID=mapped_driver_id,
                    WholesaleTruckID=mapped_tractor_id,
                    Message="",
                    InvoiceNotes="",
                    CostCenterID=None,
                    SubTypeID=None,
                    SalespersonID=None,
                    AdditionalNotes="",
                    UserName="Gravitate"
                )

                line_requests = []
                for index, bol_item in group.iterrows():
                    try:
                        store_number = bol_item["store_number"]
                        tank_number = str(bol_item["store_tank"])
                        mtid_str = None
                        try:
                            mtid_str = self.rita_mapper.get_source_child_id(
                                gravitate_parent_id=store_number, gravitate_child_id=tank_number,
                                mapping_type=MappingType.tank
                            )
                            mapped_tank_id = int(mtid_str)
                        except KeyError as e:
                            logger.warning(f"Failed to map tank '{tank_number}', skipping BOL item: {e}")
                            continue
                        except ValueError as e:
                            logger.warning(
                                f"Failed to convert mapped tank '{tank_number}'->'{mtid_str}' to int, skipping BOL item: {e}")
                            continue

                        miid_str = None
                        bol_product = bol_item["bol_product"]
                        try:
                            miid_str = self.rita_mapper.get_source_parent_id(
                                gravitate_id=bol_product, mapping_type=MappingType.product
                            )
                            mapped_item_id = int(miid_str)
                        except KeyError as e:
                            logger.warning(f"Failed to map product '{bol_product}', skipping BOL item: {e}")
                            continue
                        except ValueError as e:
                            logger.warning(
                                f"Failed to convert mapped product '{bol_product}'->'{miid_str}', skipping BOL item: {e}")
                            continue

                        # We could theoretically be handed an order with no wholesale store drops, in which case we'll
                        # upload a wholesale ticket with no line items. However, upstream should prefilter out any
                        # orders with no wholesale store drops.
                        if self.store_lkp[bol_item["store_id"]].get("extra_data", {}).get("type") != "Wholesale":
                            logger.info(
                                f"Skipping drop at non-wholesale store '{group['store_number']}' "
                                f"(order {order_number}, BOL {bol_number})"
                            )
                            continue

                        line_requests.append(
                            CreateWholesaleLineRequest(
                                DocumentID=-1,
                                ItemID=mapped_item_id,
                                TankID=mapped_tank_id,
                                Quantity=bol_item["bol_net_volume_allocated"],
                                QuantityGross=bol_item["bol_gross_volume_allocated"],
                                UnitPrice=bol_item.get("price", {}).get("price"),
                                FreightRateID=None,  # TODO: Retrieve? May not be necessary
                                VendorLocationID=None,
                                FreightAmount=None,  # TODO: Retrieve? May not be necessary
                                SurchargeAmount=None,
                                UnitCostOverride=None,
                                CustomerPricingID=None,
                                UserName="Gravitate"
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Could not convert bol item #{index} on order {order_number}: {e}")
                        continue

                if not line_requests:
                    logger.warning(
                        f"No line requests for order {order_number}; will upload a ticket request but it will be empty")
                results.append(CreateWholesaleTicketRequestBundle(
                    ticket_request=ticket_request,
                    line_requests=line_requests
                ))

            except Exception as e:
                logger.warning(f"Could not convert order {order_number}, BOL {bol_number}: {e}")
                continue

        return results

    def get_store_cp_name(self, store_id: str) -> str:
        return self.store_lkp[store_id]["counterparty_name"]
