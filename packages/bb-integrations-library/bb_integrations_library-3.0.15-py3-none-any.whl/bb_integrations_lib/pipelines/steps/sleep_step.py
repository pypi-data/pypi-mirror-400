import asyncio

from loguru import logger

from bb_integrations_lib.protocols.pipelines import Step


class SleepStep(Step):
    def __init__(self, duration: float, *args, **kwargs):
        """
        Equivalent to ``asyncio.sleep(duration)``.

        :param duration: The number of seconds to sleep.
        """
        super().__init__(*args, **kwargs)

        self.duration = duration

    def describe(self) -> str:
        return f"Wait a specified number of seconds"

    async def execute(self, data: None) -> None:
        logger.debug(f"Sleeping for {self.duration} seconds...")
        await asyncio.sleep(self.duration)
