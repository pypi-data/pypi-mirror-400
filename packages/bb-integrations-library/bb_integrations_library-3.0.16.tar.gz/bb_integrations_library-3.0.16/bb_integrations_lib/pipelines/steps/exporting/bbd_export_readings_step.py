import asyncio
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, Optional, Tuple, Iterable
from zoneinfo import ZoneInfo

import pandas as pd
from bson.raw_bson import RawBSONDocument
from loguru import logger
from pandas import DataFrame
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import ReadingQuery, ExportReadingsWindowMode


class BBDExportReadingsStep(Step):
    def __init__(self, rita_client: GravitateRitaAPI, sd_client: GravitateSDAPI, ims_database: AsyncDatabase,
                 reading_query: ReadingQuery, timezone: str = "UTC",
                 window_mode: ExportReadingsWindowMode = ExportReadingsWindowMode.HOURS_BACK, hours_back: float = 6,
                 batch_hours: float = 2, big_dataset: int = 750, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.sd_client = sd_client
        self.ims_database = ims_database

        self.reading_query = reading_query
        self.timezone = timezone
        self.window_mode = window_mode
        self.hours_back = hours_back
        self.batch_hours = batch_hours
        self.big_dataset = big_dataset

    def describe(self) -> str:
        return "Export tank readings from BBD with a customizable query"

    async def execute(self, _: Any) -> Tuple[Dict, Dict, Iterable]:
        # Compute start/end windows based on the provided configuration
        if self.window_mode == ExportReadingsWindowMode.HOURS_BACK or self.window_mode == ExportReadingsWindowMode.LATEST_ONLY:
            now = datetime.now(UTC)
            window_start = now - timedelta(hours=self.hours_back)
            window_end = now
        elif self.window_mode == ExportReadingsWindowMode.PREVIOUS_DAY:
            window_end = datetime.now(ZoneInfo(self.timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
            window_start = window_end - timedelta(days=1)
        else:
            raise Exception(f"Unknown window mode {self.window_mode}")

        if self.window_mode == ExportReadingsWindowMode.HOURS_BACK:
            logger.info(
                f"Exporting tank readings from BBD for the last {self.hours_back} hours "
                f"(from {window_start} to {window_end})"
            )
        elif self.window_mode == ExportReadingsWindowMode.LATEST_ONLY:
            logger.info(
                f"Exporting ONLY the most recent tank reading from BBD for the last {self.hours_back} hours "
                f"(from {window_start} to {window_end}"
            )
        elif self.window_mode == ExportReadingsWindowMode.PREVIOUS_DAY:
            logger.info(f"Exporting tank readings from BBD for the previous day (from {window_start} to {window_end})")

        store_lkp, tank_lkp, filtered_stores = await self.get_sites_and_tank_ids_to_export()

        if len(filtered_stores) > self.big_dataset and self.reading_query.by_wildcard is None:
            raise ValueError(
                f"Large dataset ({len(filtered_stores)} stores) detected. "
                f"Must use wildcard query strategy (by_wildcard) for datasets > 500 stores."
            )

        use_or_filter = len(filtered_stores) <= self.big_dataset

        return await self.get_inventory(
            window_start=window_start,
            window_end=window_end,
            latest_only=self.window_mode == ExportReadingsWindowMode.LATEST_ONLY,
            store_lkp=store_lkp,
            tank_lkp=tank_lkp,
            filtered_stores=filtered_stores,
            use_or_filter=use_or_filter,
        )

    @staticmethod
    def collection_as_raw_bson(collection: AsyncCollection):
        return collection.with_options(
            codec_options=collection.codec_options.with_options(document_class=RawBSONDocument))

    async def get_sites_and_tank_ids_to_export(self, query: Optional[ReadingQuery] = None) -> Tuple[
        Dict, Dict, DataFrame]:
        query_to_use = query if query else self.reading_query
        stores = (await self.sd_client.get_all_stores(include_tanks=True)).json()
        filtered_stores = self.apply_reading_query_filter(stores=stores, query=query_to_use)
        filtered_store_numbers = filtered_stores["store_number"].to_list()
        store_lkp, tank_lkp = BBDExportReadingsStep.lkps(
            [store for store in stores if store["store_number"] in filtered_store_numbers])
        return store_lkp, tank_lkp, filtered_stores

    def apply_reading_query_filter(self, stores: list[Dict], query: Optional[ReadingQuery] = None) -> DataFrame:
        query_to_use = query if query else self.reading_query
        df = pd.DataFrame(stores)
        tanks_df = df.explode("tanks")
        tanks_df = tanks_df[~tanks_df["tanks"].isna()].reset_index()
        tanks_df["tank_id"] = tanks_df["tanks"].apply(lambda x: x["tank_id"])
        tanks_df["composite_key"] = tanks_df["store_number"] + ":" + tanks_df["tank_id"].astype(str)
        if query_to_use.by_wildcard is not None and query_to_use.by_wildcard == "*":
            return tanks_df[["store_number", "tank_id", "composite_key"]]
        mask = query_to_use.as_mask(tanks_df)
        filtered = tanks_df[mask]
        return filtered[["store_number", "tank_id", "composite_key"]]

    @staticmethod
    def ims_query_pairs(filtered_stores: DataFrame) -> list:
        pairs = []
        for _, row in filtered_stores.iterrows():
            pairs.append({
                "store_number": row["store_number"],
                "tank_id": str(row["tank_id"])
            })
        return pairs

    async def get_inventory(self,
                            window_start: datetime,
                            window_end: datetime,
                            latest_only: bool,
                            store_lkp: dict,
                            tank_lkp: dict,
                            filtered_stores: DataFrame | None = None,
                            use_or_filter: bool = True,  # Add this parameter
                            ) -> Tuple[Dict, Dict, Iterable]:
        """
        Get inventory / tank readings, filtering to the stores and tanks specified by reading_query.
        :param window_start: Include readings newer than or equal to this datetime.
        :param window_end: Include readings older than this datetime.
        :param latest_only: Whether only the latest reading within the window should be provided.
        :param store_lkp: Optional pre-fetched store lookup dict.
        :param tank_lkp: Optional pre-fetched tank lookup dict.
        :param filtered_stores: Optional pre-fetched filtered stores DataFrame.
        :param use_or_filter: Whether to include $or clause in aggregation for store/tank filtering.
        :return: A tuple containing a store lookup dict, tank lookup dict, and iterable of tank reading documents.
        """
        ims_pairs = BBDExportReadingsStep.ims_query_pairs(filtered_stores)
        collection = self.ims_database['tank_inventory_log']

        match_conditions: list[dict] = [
            {
                "read_time": {
                    "$gte": window_start,
                    "$lte": window_end
                }
            }
        ]

        if use_or_filter:
            match_conditions.append({
                                        "$or": ims_pairs
                                        })

        _query: list[dict] = [
            {
                "$match": {
                    "$and": match_conditions
                }
            },
            {
                "$sort": {
                    "read_time": 1
                }
            },
            {
                "$project": {
                    "tank_agent_name": 1,
                    "store_number": 1,
                    "run_time": 1,
                    "tank_id": 1,
                    "read_time": 1,
                    "product": 1,
                    "monitor_type": 1,
                    "volume": 1,
                }
            }
        ]
        # If we're getting only the most recent tank reading, aggregate by store and tank, then grab the latest
        # reading document from the lookback period.
        if latest_only:
            _query.append({
                "$group": {
                    "_id": {
                        "store_number": "$store_number",
                        "tank_id": "$tank_id"
                    },
                    "documents": {
                        "$last": "$$ROOT"
                    }
                }
            })

        cursor = await collection.aggregate(_query)
        results = await cursor.to_list()
        # Have to extract the latest document from the aggregate if we're grabbing the latest, as the query result
        # set is shaped differently.
        if latest_only:
            return store_lkp, tank_lkp, (r["documents"] for r in results)
        return store_lkp, tank_lkp, results

    @staticmethod
    def lkps(stores: Iterable) -> Tuple[Dict, Dict]:
        store_lkp = {}
        tank_lkp = {}
        for store in stores:
            store_number = store['store_number']
            tanks = store['tanks']
            for tank in tanks:
                tank_id = tank['tank_id']
                store_lkp[f"{store_number}"] = store
                tank_lkp[f"{store_number}:{tank_id}"] = tank
        return store_lkp, tank_lkp


if __name__ == "__main__":
    from pymongo import AsyncMongoClient

    async def main():
        export = BBDExportReadingsStep(
            rita_client=GravitateRitaAPI(
                base_url="",
                client_id="",
                client_secret=""
            ),
            sd_client=GravitateSDAPI(
                base_url="",
                client_id="",
                client_secret=""
            ),
            ims_database=AsyncMongoClient("mongodb conn str")["db_name"],
            reading_query=ReadingQuery(
                by_store_numbers=["100101"]
            )
        )
        return await export.execute("Majors")

    readings = asyncio.run(main())
