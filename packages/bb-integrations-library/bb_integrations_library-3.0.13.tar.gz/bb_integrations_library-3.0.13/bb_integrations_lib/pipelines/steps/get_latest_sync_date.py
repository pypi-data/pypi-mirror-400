from datetime import datetime, UTC
from typing import Dict

import pytz
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.config import MaxSync
from bb_integrations_lib.protocols.pipelines import Step
from dateutil.parser import parse


class GetLatestSyncDate(Step):
    def __init__(self, step_configuration: Dict[str, str]):
        super().__init__(step_configuration)
        self.tenant_name = step_configuration['tenant_name']
        self.mode = step_configuration.get('mode', 'production')
        self.rita_client: GravitateRitaAPI = self.config_manager.environment_from_name(self.tenant_name,
                                                                                  self.mode).rita.api_client
        self.config_id = step_configuration.get("config_id")
        self.test_override = step_configuration.get("test_override", None)

    def describe(self) -> str:
        return "Get Latest Sync Date"

    async def execute(self, i: str) -> datetime:
        return await self.get_last_sync_date()

    async def get_last_sync_date(self) -> datetime:
        if self.test_override:
            return parse(self.test_override).replace(tzinfo=pytz.UTC)
        if not self.config_id or self.config_id is None:
            return datetime.now(UTC)
        max_sync: MaxSync  = await self.rita_client.get_config_max_sync(config_id=self.config_id)
        dt = max_sync.max_sync_date.replace(tzinfo=pytz.UTC)
        return dt
