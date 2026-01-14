import asyncio
from datetime import datetime, UTC, timedelta
from typing import Any, Optional, Literal
from zoneinfo import ZoneInfo

from bson import ObjectId
from httpx import HTTPStatusError
from loguru import logger
from pydantic import BaseModel, ValidationError
from pymongo import MongoClient
from pymongo.asynchronous.database import AsyncDatabase

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.api.platform_science.client import PlatformScienceClient
from bb_integrations_lib.provider.api.platform_science.model import JobDefinition, ShipmentDetails, ValueWithUnit, \
    JobLocation, JobStep, JobTask, LoadDefinition, LoadEntity
from bb_integrations_lib.util.utils import lookup


class PlatSciLink(BaseModel):
    """Platform Science linkage details to be stored in S&D order_v2 extra_data."""
    job_id: str
    completed: bool
    last_order_state: str


class PlatformScienceOrderSyncStep(Step):
    """
    Export the current status of a Gravitate order to Platform Science workflow, either creating, updating, or
    completing as necessary.
    """

    def __init__(
            self,
            sd_client: GravitateSDAPI,
            psc: PlatformScienceClient,
            mongo_database: AsyncDatabase,
            order_nums: list[int] | None = None,
            ps_link_key: str = "platform_science",
            timezone: ZoneInfo = UTC,
            *args, **kwargs
    ):
        super().__init__(*args, *kwargs)
        self.sd_client = sd_client
        self.psc = psc
        self.db = mongo_database

        self.order_nums = order_nums

        self.loc_lkp: Optional[dict] = None
        self.dt_lkp: Optional[dict] = None
        self.ps_link_key = ps_link_key
        self.timezone = timezone

    def describe(self) -> str:
        return "Update Platform Science workflow from Gravitate order status"

    async def execute(self, i: Any) -> None:
        if self.loc_lkp is None:
            logger.info("Fetching locations from S&D")
            locations = await self.sd_client.all_locations()
            self.loc_lkp = lookup(locations.json(), lambda x: x["id"])

        if self.order_nums:
            logger.warning(f"Using provided order numbers for testing: {self.order_nums}")
            changed_orders = []
            for i, order_num in enumerate(self.order_nums):
                logger.info(f"Downloading order {order_num} ({i+1}/{len(self.order_nums)})")
                order_resp = await self.sd_client.get_orders(order_number=order_num)
                order_resp.raise_for_status()
                changed_orders.extend(order_resp.json())
        else:
            change_window = 60
            logger.info(f"Fetching orders changed in the last {change_window} minutes from S&D")
            changed_orders_resp = await self.sd_client.get_orders(
                last_change_date=datetime.now(tz=UTC) - timedelta(minutes=change_window)
            )
            changed_orders = changed_orders_resp.json()

        if not changed_orders:
            logger.info(f"No changed orders, stopping")
            return

        if self.dt_lkp is None:
            self.dt_lkp = {}
            driver_tracking = await self.sd_client.get_driver_tracking(
                order_numbers=[x["order_number"] for x in changed_orders])
            for dt_item in driver_tracking.json():
                for ao in dt_item["assigned_orders"]:
                    self.dt_lkp[ao["number"]] = dt_item

        logger.info("Ordering orders by status: completions, updates, creations")
        completions, updates, creations = self._categorize_orders(changed_orders)
        logger.info(f"Processing {len(completions)} completions, {len(updates)} updates, {len(creations)} creations")
        ordered_orders = completions + updates + creations

        for order in ordered_orders:
            try:
                with logger.contextualize(order_number=order["order_number"]):
                    logger.info(f"Syncing order {order['order_number']}")
                    if order["order_number"] in self.dt_lkp.keys():
                        await self.sync_to_platform_science(order)
                    else:
                        logger.warning("No driver tracking record found for this order, skipping")
            except HTTPStatusError as he:
                if he.response.status_code == 404:
                    logger.warning("Got a 404 from PS syncing the order, resetting PS link.")
                    self._clear_ps_link(order["order_id"])
                    # Also have to clear out the extra_data field in the cached order object
                    order.get("extra_data", {}).pop(self.ps_link_key, None)
                    logger.info("Recreating PS order")
                    try:
                        await self.sync_to_platform_science(order)
                    except HTTPStatusError as retry_he:
                        logger.exception(f"Failed to recreate PS order after 404: {retry_he}: {retry_he.response.text}")
                    except Exception as retry_e:
                        logger.exception(f"Failed to recreate PS order after 404: {retry_e}")
                else:
                    logger.exception(f"Failed to sync order {order['order_number']}: {he}: {he.response.text}")
            except Exception as e:
                logger.exception(f"Failed to sync order {order['order_number']}: {e}")

    async def sync_to_platform_science(self, order: dict) -> None:
        # First, figure out if we have an existing PS workflow for this order
        # If we do, update the workflow. If not, create a new one. If we do have a workflow and this order is now
        # completed, attempt to complete the workflow.
        grav_order_state = order["order_state"]
        extra_data = order.get("extra_data", {})
        ps_link_raw = extra_data.get(self.ps_link_key)
        try:
            ps_link = PlatSciLink.model_validate(ps_link_raw)
        except ValidationError:
            if ps_link_raw is not None:
                logger.warning(f"Malformed Platform Science link data from extra_data: {ps_link_raw}")
            ps_link = None

        driver = self._get_driver(order)
        logger.info(f"For driver {driver}")

        # Do we have good link data?
        if ps_link:
            # Is it updatable?
            if not ps_link.completed:
                if grav_order_state != "complete":
                    logger.info(f"Updating an existing PS workflow ({ps_link.job_id})")
                    await self.update_existing_ps_workflow(driver, ps_link.job_id, order)
                    if grav_order_state == "in progress" and ps_link.last_order_state != "in progress":
                        logger.info("Order transitioned to in progress, creating load")
                        try:
                            await self.create_load(order, driver)
                        except HTTPStatusError as he:
                            logger.warning(f"{he.response.status_code}: {he.response.text}")
                else:
                    logger.info(f"Completing an uncompleted PS workflow ({ps_link.job_id})")
                    await self.complete_existing_ps_workflow(driver, ps_link.job_id, order)
            else:
                logger.info("PS workflow already completed, cannot send further updates")
        else:
            if driver:
                logger.info("No PS workflow found, creating new")
                await self.create_new_ps_workflow(order, driver)
                if grav_order_state == "in progress":
                    logger.info("New order is in progress, creating load")
                    await self.create_load(order, driver)
            else:
                logger.error("No driver on order - must have a driver to create in Platform Science")

    @staticmethod
    def order_is_pre_assign(order: dict) -> bool:
        return order["order_state"] == "accepted"

    async def create_load(self, order: dict, driver: str) -> None:
        entities = [
            LoadEntity(
                type="bill_of_lading",
                value=str(order["order_number"])
            ),
        ]
        if trailer := order.get("trailer"):
            entities.append(LoadEntity(
                type="trailer",
                value=str(trailer)
            ))

        start_date = datetime.now(self.timezone).date()
        # Get the latest drop ETA for this order, or set end_date = start_date if there are no drops / ETAs
        end_date = datetime.min
        for drop in order["drops"]:
            eta = drop.get("eta")
            if eta:
                eta = datetime.fromisoformat(eta)
                end_date = max(end_date, eta)
        if end_date == datetime.min:
            end_date = start_date
        else:
            end_date = end_date.astimezone(self.timezone).date()

        resp = await self.psc.create_load(
            driver,
            LoadDefinition(
                start_date=start_date,
                end_date=end_date,
                # TODO: Depends on this func getting called only when the order is completed
                user_external_id=driver,
                load=None,
                entities=entities
            )
        )
        if resp.is_error:
            logger.error(resp.json())
            resp.raise_for_status()

    async def create_new_ps_workflow(self, order: dict, driver: str) -> None:
        resp = await self.psc.create_workflow_job(
            driver,
            job_definition=self._convert_grav_order_to_job_definition(
                order, self.loc_lkp, self.dt_lkp, pre_assign=self.order_is_pre_assign(order)
            )
        )
        if resp.is_error:
            logger.error(resp.json())
            resp.raise_for_status()
        body = resp.json()
        logger.info(f"Created order, PS response {body}")
        logger.info("Setting S&D extra_data")
        job_id = str(body["data"]["job_id"])

        order_completed = order["order_state"] == "complete"
        if order_completed:
            logger.info("Order already completed, completing PS workflow")
            await self.complete_existing_ps_workflow(driver, job_id, order)
        else:
            await self._save_ps_link(
                order["order_id"],
                PlatSciLink(job_id=job_id, completed=order_completed, last_order_state=order["order_state"])
            )

    async def update_existing_ps_workflow(self, driver_id: str, job_id: str, order: dict) -> None:
        resp = await self.psc.update_workflow_job(
            driver_id,
            job_id,
            self._convert_grav_order_to_job_definition(order, self.loc_lkp, self.dt_lkp,
                                                       pre_assign=self.order_is_pre_assign(order))
        )
        resp.raise_for_status()
        await self._save_ps_link(
            order["order_id"],
            PlatSciLink(job_id=job_id, completed=False, last_order_state=order["order_state"])
        )

    async def complete_existing_ps_workflow(self, driver: str, ps_job_id: str, order: dict) -> None:
        # last_change_date is okay here since the likely last update on the order was when it was completed, if this job
        # runs soon after.
        await self.update_existing_ps_workflow(driver, ps_job_id, order)
        await self.psc.complete_workflow_job(ps_job_id, datetime.fromisoformat(order["last_change_date"]))
        await self._save_ps_link(
            order["order_id"],
            PlatSciLink(job_id=ps_job_id, completed=True, last_order_state=order["order_state"])
        )

    async def _save_ps_link(self, order_id: str, psl: PlatSciLink):
        ur = await self.db["order_v2"].update_one(
            filter={
                "_id": ObjectId(order_id)
            },
            update={
                "$set": {
                    f"extra_data.{self.ps_link_key}": psl.model_dump(mode="json")
                }
            }
        )
        logger.debug(f"Saved PS link: {psl}")

    async def _clear_ps_link(self, order_id: str):
        ur = await self.db["order_v2"].update_one(
            filter={
                "_id": ObjectId(order_id)
            },
            update={
                "$unset": {
                    f"extra_data.{self.ps_link_key}": ""
                }
            }
        )
        logger.debug(f"Cleared PS link for order_id '{order_id}'")

    @staticmethod
    def _get_driver(order: dict) -> str | None:
        drivers = order.get("drivers", [])
        if not drivers:
            logger.warning("No drivers found for order")
            return None
        if len(drivers) > 1:
            # Sync job uses this, so it should match the external_id field in Platform Science
            primary_driver = drivers[0]["username"]
            logger.warning(f"More than one driver found for order, using first driver ({primary_driver})")
        else:
            primary_driver = drivers[0]["username"]
        return primary_driver

    def _bulk_get_ps_links(self, order_ids: list[str]) -> dict[str, Optional[PlatSciLink]]:
        """Get PS links for a list of order ids"""
        results = self.db["order_v2"].find(
            filter={
                "_id": {
                    "$in": [ObjectId(oid) for oid in order_ids]
                }
            },
            projection={
                "_id": 1,
                f"extra_data.{self.ps_link_key}": 1
            }
        )

        ps_links = PlatformScienceOrderSyncStep._validate_ps_links_by_order_id(results, self.ps_link_key)
        return ps_links

    @staticmethod
    def _validate_ps_links_by_order_id(results: Cursor, ps_link_key: str) -> dict[str, Optional[PlatSciLink]]:
        ps_links = {}
        for doc in results:
            order_id = str(doc["_id"])
            ps_link_raw = doc.get("extra_data", {}).get(ps_link_key)
            try:
                ps_link = PlatSciLink.model_validate(ps_link_raw) if ps_link_raw else None
            except ValidationError:
                logger.warning(f"Bad Platform Science link data for order {order_id}: {ps_link_raw}")
                ps_link = None
            ps_links[order_id] = ps_link
        return ps_links

    def _categorize_orders(self, changed_orders: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
        """
        Categorize orders into completions, updates, and creations based on PS link status.
        """
        order_ids = [order["order_id"] for order in changed_orders]
        ps_links = self._bulk_get_ps_links(order_ids)

        completions = []
        updates = []
        creations = []

        for order in changed_orders:
            order_id = order["order_id"]
            ps_link = ps_links.get(order_id)

            if order["order_number"] not in self.dt_lkp.keys():
                logger.warning(
                    f"No driver tracking record found for order {order['order_number']}, skipping order...")
                continue

            if ps_link and not ps_link.completed:
                if order["order_state"] == "complete":
                    completions.append(order)
                else:
                    updates.append(order)
            else:
                creations.append(order)

        return completions, updates, creations

    @staticmethod
    def _convert_grav_order_to_job_definition(order: dict, loc_lkp: dict, dt_lkp: dict,
                                              pre_assign: bool) -> JobDefinition:
        loads = order["loads"]
        drops = order["drops"]
        return JobDefinition(
            status="pre_assign" if pre_assign else "active",
            external_id=str(order["order_number"]),
            locations=[PlatformScienceOrderSyncStep._convert_to_job_location(load, loc_lkp)
                       for load in loads] +
                      [PlatformScienceOrderSyncStep._convert_to_job_location(drop, loc_lkp)
                       for drop in drops],
            steps=PlatformScienceOrderSyncStep._loads_and_drops_to_steps(order["loads"], order["drops"],
                                                                         order["order_number"], dt_lkp),
            shipment_details=ShipmentDetails(
                total_distance=ValueWithUnit(
                    value=order["total_miles"],
                    uom="miles"
                )
            )
        )

    @staticmethod
    def _convert_to_job_location(load_or_drop: dict, loc_lkp: dict) -> JobLocation:
        """
        Loads and drops have a very similar (identical?) structure, so we can reuse this method for either case.
        Most of the data comes from the S&D location lookup anyway.
        """
        sd_loc = loc_lkp[load_or_drop["location_id"]]
        return JobLocation(
            external_id=load_or_drop["location_id"],  # TODO: Do we want to expose the location ID here?
            name=load_or_drop["location_name"],
            address=sd_loc["address"],
            latitude=f"{sd_loc['lat']:.4f}",
            longitude=f"{sd_loc['lon']:.4f}",
            city=sd_loc["city"],
            state=sd_loc["state"],
            country_code="US",  # TODO: Don't hardcode this
        )

    @staticmethod
    def _loads_and_drops_to_steps(loads: list[dict], drops: list[dict], order_number: int, dt_lkp: dict) -> list[
        JobStep]:
        dt_this = dt_lkp[order_number]
        inc = 1
        steps = []
        for load in loads:
            steps.append(
                PlatformScienceOrderSyncStep._convert_load_or_drop_to_job_step(load, inc, order_number, "Load",
                                                                               dt_this))
            inc += 1
        for drop in drops:
            steps.append(
                PlatformScienceOrderSyncStep._convert_load_or_drop_to_job_step(drop, inc, order_number, "Drop",
                                                                               dt_this))
            inc += 1
        return steps

    @staticmethod
    def _convert_task(eid: str, product_name: str, task_order: int, load_or_drop: Literal["Load", "Drop"],
                      completed: bool, completed_at: datetime) -> JobTask:
        return JobTask(
            remarks=[],
            fields={},
            id=str(task_order),
            name=f"{load_or_drop} Product ({product_name})",
            # What types are available and how do we use them? "arrived" is the only one I have verified so far
            type="arrived",
            completed=completed,
            completed_at=completed_at,
            external_id=eid,
            order=task_order,
            status="New",
        )

    @staticmethod
    def _convert_load_or_drop_to_job_step(data: dict, step_order: int, order_number: int,
                                          load_or_drop: Literal["Load", "Drop"], dt_this: dict) -> JobStep:
        product_names = {x["product_name"] for x in data["details"]}
        # Every detail that we care about can be represented by the first item in its group
        detail_len = len(product_names)
        detail_slug = f"{detail_len} product" + ("s" if detail_len > 1 else "")

        completed = data["status"] == "complete"
        completed_at = None
        # Locate the update in the DT data, and filter to route events for this order specifically
        for route in filter(lambda x: x["order_number"] == order_number, dt_this["route"]):
            action_map = {
                "Load": "loading",
                "Drop": "dropping"
            }
            action_matches = action_map[load_or_drop] == route["action"]
            destination = route["destination_id"]
            if action_matches and destination == data["location_id"]:
                completed = route["complete"]
                if completed:
                    completed_at = route["end_time"]
                else:
                    completed_at = None
                break

        return JobStep(
            tasks=[
                PlatformScienceOrderSyncStep._convert_task(f"{order_number}-{step_order}-{task_order}", d, task_order,
                                                           load_or_drop, completed, completed_at)
                for task_order, d in enumerate(product_names)
            ],
            order=step_order,
            completed=completed,
            completed_at=completed_at,
            type="New",
            name=f"{load_or_drop} {detail_slug}",
            external_id=f"{order_number}-{step_order}",
            location_external_id=data["location_id"]
        )


if __name__ == "__main__":
    async def main():
        step = PlatformScienceOrderSyncStep(
            sd_client=GravitateSDAPI(
                base_url="",
                client_id="",
                client_secret=""
            ),
            psc=PlatformScienceClient(
                base_url="",
                client_id="",
                client_secret=""
            ),
            order_nums=[],
            mongo_database=MongoClient("mongodb conn str")["db_name"]
        )
        res = await step.execute(None)


    asyncio.run(main())
