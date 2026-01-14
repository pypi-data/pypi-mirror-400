from bb_integrations_lib.protocols.pipelines import Step, Input
from loguru import logger


class EchoStep(Step[Input, Input]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self):
        return "Echo step input at debug priority"

    async def execute(self, i: Input) -> Input:
        logger.debug(i)
        return i
