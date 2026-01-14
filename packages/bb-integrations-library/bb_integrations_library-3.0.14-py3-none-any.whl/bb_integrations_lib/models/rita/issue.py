from datetime import datetime
from enum import Enum
from typing import Optional, List, Annotated

from annotated_types import MaxLen
from pydantic import BaseModel, Field


class IssueCategory(Enum):
    UNKNOWN = "unknown"
    MISC = "misc"
    ORDER = "order"
    PAYROLL = "payroll"
    TANK_READING = "tank"
    PRICE = "price"
    REFERENCE_DATA = "reference_data"
    CROSSROADS = "crossroads"
    CROSSROADS_MAPPINGS = "crossroads_mappings"


class IssueBase(BaseModel):
    key: str = Field(description="Unique key for this issue")
    config_id: str = Field(description="Config object this issue is reported under.")
    # group or config id?
    name: str = Field(description="Human readable name")
    category: IssueCategory = Field(description="Broad category of the issue")
    problem_short: Optional[str] = Field(default=None,
                                         description="Short description of the problem (e.g. an exception class name)")
    problem_long: Optional[str] = Field(default=None, description="Long description of the problem (e.g. traceback)")
    occurrences: Annotated[
        List[datetime], Field(default=[], description="List of most recent datetimes that this issue was reported",
                              max_length=50)]

    class Config:
        arbitrary_types_allowed = True

    @property
    def most_recent_occurrence(self) -> Optional[datetime]:
        return max(self.occurrences, default=None)

    def get_occurrence_limit(self) -> int:
        """Get the annotated max_length of the occurrences list."""
        for meta in self.model_fields["occurrences"].metadata:
            if isinstance(meta, MaxLen):
                return meta.max_length
        raise AttributeError("IssueBase.occurrences does not have an annotated max_length")

    def trim_occurrences(self):
        """
        Trims the occurrences array to fit within the annotated Field.max_length.
        The array gets sorted as a side effect.
        """
        self.occurrences = sorted(self.occurrences)[-self.get_occurrence_limit():]


class UpdateIssue(BaseModel):
    key: str = Field(description="Unique key for this issue")
    config_id: Optional[str] = Field(default=None, description="Config object this issue is reported under.")
    name: Optional[str] = Field(default=None, description="Human readable name")
    category: Optional[IssueCategory] = Field(default=None, description="Broad category of the issue")
    problem_short: Optional[str] = Field(default=None,
                                         description="Short description of the problem (e.g. an exception class name)")
    problem_long: Optional[str] = Field(default=None, description="Long description of the problem (e.g. traceback)")
