from typing import Optional
from pydantic import BaseModel

from bb_integrations_lib.models.sd.get_order import (
    Drop as PlannedDrop,
    DropDetail as PlannedDropDetail,
    Load as PlannedLoad,
    LoadDetail as PlannedLoadDetail,
)

from bb_integrations_lib.models.sd.bols_and_drops import (
    AllocatedBOL,
    BOL,
    BOLDetail,
    Drop as ExecutedDrop,
)

class OrderData(BaseModel):
    """Container for retrieved order data """
    order_number: str
    bols_and_drops: dict | None = None
    planned_order: dict | None = None
    error: str | None = None

class MatchedAllocation(BaseModel):
    """Result of matching an allocated BOL to planned and executed data."""
    order_number: str
    allocated_bol: AllocatedBOL | None = None
    executed_bol: Optional[BOL] = None
    executed_bol_detail: Optional[BOLDetail] = None
    executed_drop: Optional[ExecutedDrop] = None
    planned_load: Optional[PlannedLoad] = None
    planned_load_detail: Optional[PlannedLoadDetail] = None
    planned_drop: Optional[PlannedDrop] = None
    planned_drop_detail: Optional[PlannedDropDetail] = None
    planned_quantity: Optional[int] = None
    actual_quantity: int
    variance: Optional[int] = None
    variance_pct: Optional[float] = None
    matched_to_planned_drop: bool = False
    matched_to_planned_load: bool = False
    matched_to_executed_bol: bool = False
    matched_to_executed_drop: bool = False