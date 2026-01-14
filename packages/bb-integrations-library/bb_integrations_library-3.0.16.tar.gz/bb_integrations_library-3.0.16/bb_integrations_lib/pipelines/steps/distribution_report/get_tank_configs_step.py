import json
from typing import Dict, List

from pymongo.asynchronous.database import AsyncDatabase

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import init_db, CustomJSONEncoder
from loguru import logger
from pandas import DataFrame


class GetTankConfigsStep(Step):
    def __init__(self, mongo_database: AsyncDatabase, include_model_mode: str = "latest_only", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = mongo_database
        self.include_model_mode = include_model_mode

    def describe(self) -> str:
        return f"Get tank configs"

    async def execute(self, i: None) -> str | DataFrame:
        return await self.get_tank_configs()

    async def get_tank_configs(self) -> List[Dict] | DataFrame:
        dos_columns = ['store_number', 'product', 'daily_lifting_estimate', 'measured_inventory']
        collection = self.database["tank_config"]
        tank_configs = collection.find(
            {},
            {col: 1 for col in dos_columns}
        )
        tank_configs = await tank_configs.to_list()
        self.pipeline_context.included_files[f'{self.__class__.__name__} result'] = json.dumps(tank_configs, cls=CustomJSONEncoder)
        if not hasattr(self, "custom_parser"):
            tc = tank_configs
        else:
            logger.info(f"Using custom parser for {self.__class__.__name__}")
            parser = self.custom_parser()
            tc =  await parser.parse(tank_configs)
        self.pipeline_context.extra_data["tank_configs"] = tc
        return tc