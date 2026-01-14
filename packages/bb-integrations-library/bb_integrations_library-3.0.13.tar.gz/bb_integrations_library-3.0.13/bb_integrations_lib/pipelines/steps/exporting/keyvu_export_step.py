from datetime import datetime, timedelta, UTC

from bson import ObjectId
from loguru import logger
from pymongo import MongoClient, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.synchronous.database import Database

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.rita.config import GenericConfig
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.api.keyvu.model import Delivery, StationDelivery, \
    DeliveryStatus, KeyVuDeliveryPlan, default_serialization_options, StationDeliveryDetails, StationDeliveryBOL, \
    GeoLocation
from bb_integrations_lib.shared.model import RawData

# See also v1 order trip status for better DeliveryStatus mapping
delivery_status_map = {
    "accepted": DeliveryStatus.planned,
    "assigned": DeliveryStatus.planned,
    "in progress": DeliveryStatus.unloading,
    "complete": DeliveryStatus.delivered,
    "canceled": DeliveryStatus.canceled
}


class KeyVuExportStep(Step):
    def __init__(self, rita_client: GravitateRitaAPI, sd_client: GravitateSDAPI, mongo_database: AsyncDatabase,
                 time_back: timedelta, only_mapped_sites: bool = True, by_counterparties: list[str] | None = None,
                 order_nums: list[int] | None = None, *args, **kwargs):
        """
        Build a KeyVu delivery plan from recently modified orders in the S&D environment.

        Automatically uses RITA mappings with a KeyVu source system.

        :param rita_client: RITA client to retrieve mappings with.
        :param sd_client: S&D client to retrieve orders from.
        :param mongo_database: An initialized MongoDB database to retrieve order details from.
        :param time_back: Gets orders with modification timestamp within the last timedelta duration.
        :param only_mapped_sites: Whether to only include sites with extant Gravitate->KeyVu site ID mappings. If False
          and no mapping is available for a site, the Gravitate location name will be used as the KeyVu site ID.
        :param by_counterparties: Counterparties to include in the delivery plan. If empty, all counterparties are
          included. Intended to be set by the RITA config, but a fallback can be set here.
        """
        super().__init__(*args, **kwargs)
        self.time_back: timedelta = time_back
        self.order_nums = order_nums

        self.sd_client = sd_client
        self.rita_client = rita_client
        self.mongo_database = mongo_database

        self.keyvu_site_mappings = None  # To be filled in by execute() (can't load it here since Rita client is async)

        self.tcn_field_name = "source_system_id"
        # This defaults to true to prevent leaking all sites to SWTO if we don't have mappings
        self.only_mapped_sites = only_mapped_sites
        self.by_counterparties = by_counterparties

    def describe(self) -> str:
        return "Export recent order updates to KeyVu"

    async def execute(self, i: None = None) -> KeyVuDeliveryPlan:
        logger.warning("Delivery dates and times are not fully implemented for all order scenarios.")

        # Load additional configuration from Rita
        try:
            rita_config: GenericConfig = (await self.rita_client.get_config_by_name("/KeyVu", "KeyVu"))["KeyVu"]
            self.tcn_field_name = rita_config.config.get("extra_data_tcn_field", self.tcn_field_name)
            self.only_mapped_sites = rita_config.config.get("only_mapped_sites", self.only_mapped_sites)
            self.by_counterparties = rita_config.config.get("by_counterparties", self.by_counterparties)
        except Exception as e:
            logger.warning(
                f"Failed to load KeyVu config from RITA, using defaults"
            )
            logger.warning(f"Exception: {e}")

        logger.info(
            f"Configuration: extra_data_tcn_field: '{self.tcn_field_name}', "
            f"only_mapped_sites: {self.only_mapped_sites}, "
            f"by_counterparties: {self.by_counterparties}"
        )

        # Preload mappings
        maps = await self.rita_client.get_mappings_by_source_system("KeyVu")
        self.keyvu_site_mappings = {x.gravitate_id: x.source_id for x in maps}
        if self.only_mapped_sites and not self.keyvu_site_mappings:
            raise Exception("No KeyVu site mappings found, but only_mapped_sites is True")

        end_date = datetime.now(UTC).replace(microsecond=0)
        start_date = end_date - self.time_back
        logger.info(f"Downloading orders newer than {start_date}")
        if self.order_nums is not None:
            orders_raw = []
            for i, order_num in enumerate(self.order_nums):
                logger.info(f"Downloading order {order_num} ({i + 1}/{len(self.order_nums)})")
                order_resp = await self.sd_client.get_orders(order_number=order_num)
                order_resp.raise_for_status()
                orders_raw.extend(order_resp.json())
        else:
            order_resp = await self.sd_client.get_orders(last_change_date=start_date)
            orders_raw = order_resp.json()

        # Filter out orders supposedly changed in the future
        orders = list(filter(
            lambda o: datetime.fromisoformat(o.get("last_change_date")) < datetime.now() + timedelta(days=1),
            orders_raw
        ))

        # Using non-v1 API here
        logger.info("Getting BOL details")
        bol_resp = await self.sd_client.token_post(url="order/bols_and_drops", json={
            "order_ids": [order["order_id"] for order in orders]
        })
        bol_resp.raise_for_status()
        bols_raw = bol_resp.json()
        self.bol_lkp = {int(bol["order_number"]): bol for bol in bols_raw}

        logger.info("Getting order details from database")
        order_numbers = [order["order_number"] for order in orders]
        order_docs = await self.mongo_database["order_v2"].find({
            "number": {
                "$in": order_numbers
            }
        }).to_list()
        self.order_lkp = {o["number"]: o for o in order_docs}

        logger.info("Getting location details from API")
        loc_resp = await self.sd_client.all_locations()
        loc_resp.raise_for_status()
        locations_raw = loc_resp.json()
        self.loc_lkp = {loc["id"]: loc for loc in locations_raw}

        logger.info("Getting counterparty details from API")
        cp_resp = await self.sd_client.all_counterparties()
        cp_resp.raise_for_status()
        cp_raw = cp_resp.json()
        self.cp_lkp = {cp["id"]: cp for cp in cp_raw}

        logger.info("Getting stores from API")
        store_resp = await self.sd_client.all_stores(include_tanks=False)
        store_resp.raise_for_status()
        store_raw = store_resp.json()
        self.store_lkp = {store["store_number"]: store for store in store_raw}

        logger.info("Getting driver schedule details from database")
        ds_ids = list(filter(lambda x: x is not None,
                             [order.get("driver_schedule_id", None) for number, order in self.order_lkp.items()]))
        ds_ids = [ObjectId(id) for id in ds_ids]
        ds_docs = await self.mongo_database["driver_schedule"].find({
            "_id": {
                "$in": ds_ids
            }
        }).to_list()
        self.driver_sched_lkp = {str(ds["_id"]): ds for ds in ds_docs}

        logger.info("Building delivery plan models")
        export_date = datetime.now(UTC).replace(microsecond=0)
        deliveries = []
        for o in orders:
            try:
                deliveries.append(self.order_to_keyvu_delivery(o))
            except Exception as e:
                logger.error(f"Failed to build a delivery item for {o['order_number']}: {e}")
        dp = KeyVuDeliveryPlan(
            start_date=start_date,
            end_date=end_date,
            export_date=export_date,
            deliveries=deliveries
        )
        return dp

    def determine_delivery_status(self, order: dict, order_doc: dict, drop_index: int) -> DeliveryStatus:
        match order["order_state"]:
            case "accepted" | "assigned" | "open":
                return DeliveryStatus.planned
            case "canceled" | "deleted":
                return DeliveryStatus.canceled
            case "in progress":
                drop_doc: dict = order_doc["drops"][drop_index]
                route_status = drop_doc.get('route_status')
                # TODO: Implement better state tracking here - can we tell whether this particular delivery is being
                #   loaded or not? Currently we'll just say it's planned.
                if route_status == "driving to drop":
                    return DeliveryStatus.on_route_loaded
                elif route_status == "arrived at drop":
                    return DeliveryStatus.unloading
                return DeliveryStatus.planned
            case "complete":
                return DeliveryStatus.delivered
            case _:
                raise Exception(f"Could not determine delivery status from order state '{order['order_state']}'")

    def get_delivery_date(self, order: dict, drop: dict, delivery_status: DeliveryStatus) -> datetime:
        # TODO: Get the correct delivery date for all order scenarios.
        delivery_date = None
        if delivery_status == DeliveryStatus.planned or delivery_status == DeliveryStatus.unloading:
            # Sometimes this is a str, sometimes it's a datetime
            delivery_date = drop["eta"]
        elif delivery_status == DeliveryStatus.canceled:
            # Is this acceptable?
            delivery_date = order.get("dispatch_window_end") or order.get("last_changed_date")
        elif delivery_status == DeliveryStatus.delivered:
            logger.debug("Delivered")
            bols = self.bol_lkp.get(order["order_number"], {}).get("bols")
            if not bols:
                logger.warning("No BOL on order")
            else:
                delivery_date = max([datetime.fromisoformat(b["date"]) for b in bols])
        if delivery_date is None:
            logger.warning("Unable to determine a delivery date - using current datetime")
            return datetime.now(UTC)

        if type(delivery_date) is str:
            delivery_date = datetime.fromisoformat(delivery_date)
        return delivery_date.astimezone(UTC).replace(microsecond=0)

    def drop_to_keyvu_station_delivery(self, order: dict, drop: dict, drop_index: int) -> StationDelivery | None:
        # Confirm if the counterparty is included
        if self.by_counterparties:
            location = self.loc_lkp[drop["location_id"]]
            store_cp_name = self.store_lkp[location["name"]][
                "counterparty_name"]  # location name seems to = store_number
            if store_cp_name not in self.by_counterparties:
                logger.debug(
                    f"Skipping order {order['order_number']} drop #{drop_index}, "
                    f"{store_cp_name} not in counterparties list"
                )
                return None
        delivery_status = self.determine_delivery_status(order, self.order_lkp[order["order_number"]], drop_index)

        # Map the site IDs, if available
        if self.keyvu_site_mappings:
            site_id = self.keyvu_site_mappings.get(drop["location_name"])
            # If the lookup fails...
            if not site_id:
                # ...and we are skipping unmapped sites, skip this one
                if self.only_mapped_sites:
                    logger.warning(
                        f"Skipping {order['order_number']} drop #{drop_index}, could not find site_id in mappings")
                    return None
                # otherwise we can use the location name as a fallback
                else:
                    site_id = drop["location_name"]
        # But if not, use location name directly
        else:
            site_id = drop["location_name"]

        def bol_correlates(bol: dict, tanks: list[int]) -> bool:
            return bol["location_id"] == drop["location_id"] and bol["store_tank"] in tanks

        allocated_bols = self.order_lkp[order["order_number"]].get("allocated_bols", [])
        # allocated_bols will have multiple entries - one per product - if a load is split.
        # Since KeyVu doesn't have any product details, just supplier and terminal, this results in apparent duplicates
        # when it gets converted to their format.
        # Convert all BOLs, but only keep them if we haven't already generated an identical BOL entry.
        converted_bols = []
        for bol in allocated_bols:
            converted = self.allocated_bol_to_keyvu_bol(bol)
            drop_tanks = [x['tank_id'] for x in drop["details"]]
            if converted not in converted_bols and bol_correlates(bol, drop_tanks):
                converted_bols.append(converted)
        return StationDelivery(
            delivery_status=delivery_status,
            site_id=site_id,
            details=[StationDeliveryDetails.from_v1_order_dict(x) for x in drop["details"]],
            delivery_date=self.get_delivery_date(order, drop, delivery_status),
            bill_of_ladings=converted_bols
        )

    def allocated_bol_to_keyvu_bol(self, allocated_bol: dict) -> StationDeliveryBOL:
        return StationDeliveryBOL(
            supplier=allocated_bol["bol_supplier"],
            terminal_name=allocated_bol["bol_terminal"],
            bill_of_lading_number=allocated_bol["bol_number"],
            terminal_control_number=self.loc_lkp.get(
                allocated_bol["bol_terminal_id"], {}).get("extra_data", {}).get(self.tcn_field_name, ""),
            consignee=""  # KeyVu says if we don't have a consignee ID ("usually some 5 digit number") to leave it empty
        )

    def all_drops_to_keyvu_station_deliveries(self, order: dict) -> list[StationDelivery]:
        station_deliveries = [
            self.drop_to_keyvu_station_delivery(order, drop, index)
            for index, drop in enumerate(order["drops"])
        ]
        # Filter out failed conversions (typically failed site lookups)
        return [d for d in station_deliveries if d is not None]

    def order_to_keyvu_delivery(self, order: dict) -> Delivery:
        updated_at: datetime = datetime.fromisoformat(max(filter(
            lambda x: x is not None,
            [order["last_change_date"], order.get("hauled_by_updated")])
        ))
        order_detail = self.order_lkp.get(order["order_number"], {})
        unit = ""
        if dsid := order_detail.get("driver_schedule_id"):
            driver_log = self.driver_sched_lkp.get(dsid, {}).get("driver_log", {})
            tractor = driver_log.get("tractor")
            trailer = driver_log.get("trailer")
            unit += tractor if tractor else ""
            if unit and trailer:
                unit += f"-{trailer}"
            elif trailer:
                unit = trailer

        station_deliveries = self.all_drops_to_keyvu_station_deliveries(order)
        if not station_deliveries:
            raise Exception(f"No station deliveries built for order {order['order_number']}, skipping order")
        return Delivery(
            id=str(order["order_number"]),
            carrier_name=order["supply_option"].get("carrier"),
            # Grab the SCAC from the carrier counterparty, falling back to None (which becomes blank) if not found.
            scac=self.cp_lkp.get(order_detail.get("carrier_id"), {}).get("scac"),
            # GeoLocation must be included but we don't necessarily have any data to fill in (this would be driver
            # breadcrumbs).
            # This prevents geolocation from getting ignored entirely during serialization, because the schema expects
            # it to be there, but doesn't add any sub-elements, which are optional.
            geo_location=GeoLocation(longitude=None, latitude=None, heading=None, last_updated=None),
            unit=unit,
            last_updated=updated_at.astimezone(UTC).replace(microsecond=0),
            station_deliveries=station_deliveries
        )


if __name__ == "__main__":
    import asyncio


    async def main():
        s = KeyVuExportStep(
            rita_client=GravitateRitaAPI(
                base_url="",
                username="",
                password="",
            ),
            sd_client=GravitateSDAPI(
                base_url="",
                username="",
                password="",
            ),
            mongo_database=AsyncMongoClient("mongo conn str")["mongo db name"],
            time_back=timedelta(minutes=60),
            order_nums=[]
        )
        plan = await s.execute()
        dp_string = plan.to_xml(**default_serialization_options)
        plan_file = RawData(
            data=dp_string,
            file_name=f"plan_file{datetime.now().isoformat()}.xml"
        )
        with open(plan_file.file_name, "wb") as f:
            f.write(plan_file.data)


    asyncio.run(main())
