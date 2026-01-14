from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import RawData


class SaveRawDataToDiskStep(Step):
    """Save a RawData object to disk in the current working directory."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self) -> str:
        return "Save a RawData object to the current working directory"

    async def execute(self, i: RawData) -> None:
        with open(i.file_name, "wb") as f:
            f.write(i.data)
