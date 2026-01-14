from datetime import datetime, UTC
from typing import Dict

import pytz
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.config import MaxSync
from bb_integrations_lib.protocols.pipelines import Step
from dateutil.parser import parse


class GetLatestSyncDate(Step):
    def __init__(
            self,
            rita_client: GravitateRitaAPI,
            config_id: str | None = None,
            test_override: str | None = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.config_id = config_id
        self.test_override = test_override

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
