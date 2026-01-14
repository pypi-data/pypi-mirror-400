from typing import Dict, Any, Awaitable

from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
from bb_integrations_lib.mappers.prices.model import Action
from bb_integrations_lib.protocols.pipelines import Step


class PEIntegrationJobActionStep(Step):
    def __init__(self, pe_client: GravitatePEAPI, action: Action, integration_name: str, source_system_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pe_client = pe_client
        self.action = action
        self.integration_name = integration_name
        self.source_system_id = source_system_id

    def describe(self) -> str:
        return "Start, end or error pricing engine integration job"

    async def execute(self, _: Any):
        return await self.match_action()

    async def match_action(self) -> Awaitable:
        match self.action:
            case Action.start:
                return self.pe_client.integration_start
            case Action.stop:
                return self.pe_client.integration_stop
            case Action.error:
                return self.pe_client.integration_error
            case _:
                raise ValueError(f"Unexpected action {self.action}")