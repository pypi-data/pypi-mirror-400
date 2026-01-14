from typing import Any

from bb_integrations_lib.protocols.pipelines import Step, Input, Output


class NullStep(Step[Any, None]):
    """A step that performs no action. May be useful as the first step in a job pipeline."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self) -> str:
        return "Null Step"

    async def execute(self, i: Any) -> None:
        return None
