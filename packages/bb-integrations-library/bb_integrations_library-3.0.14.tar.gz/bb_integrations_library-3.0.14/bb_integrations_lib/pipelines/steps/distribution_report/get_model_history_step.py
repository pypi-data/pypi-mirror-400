import json
from datetime import datetime, timedelta, UTC

from pymongo.asynchronous.database import AsyncDatabase

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import CustomJSONEncoder


class GetModelHistoryStep(Step):
    def __init__(self, mongo_database: AsyncDatabase, hours_back: float | None = None, include_model_mode: str = "latest_only", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo_database = mongo_database
        self.hours_back = hours_back
        self.include_model_mode = include_model_mode

    def describe(self) -> str:
        return f"Get model history"

    async def execute(self, i: None) -> str | list:
        if self.include_model_mode == "latest_only":
            return await self.get_latest_model_id()
        else:
            if self.hours_back is not None:
                return await self.get_last_n_models(int(self.hours_back))
            else:
                raise NotImplementedError("Please specify n_hours_back in the configuration")

    async def get_latest_model_id(self) -> str:
        collection = self.mongo_database["model_history"]
        latest_model = await collection.find_one(
            {'status': 'Success'},
            sort=[('time_ran', -1)]
        )
        latest_model_id = str(latest_model['_id'])
        self.pipeline_context.included_files[f'{self.__class__.__name__} result'] = json.dumps(latest_model, cls=CustomJSONEncoder)
        self.pipeline_context.extra_data["latest_model_id"] = latest_model_id
        return latest_model


    async def get_last_n_models(self, n: int) -> list:
        n_hours_ago = datetime.now(UTC) - timedelta(hours=n)
        collection = self.mongo_database["model_history"]
        models = collection.find(
            {'status': 'Success', 'time_ran': {'$gte': n_hours_ago}},
            sort=[('time_ran', -1)]
        )
        models = await models.to_list()
        self.pipeline_context.included_files[f'{self.__class__.__name__} result'] = json.dumps(models, cls=CustomJSONEncoder)
        return models
