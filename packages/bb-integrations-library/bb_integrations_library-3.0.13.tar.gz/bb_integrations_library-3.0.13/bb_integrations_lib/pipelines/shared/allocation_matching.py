from typing import Optional

from pydantic import BaseModel

from bb_integrations_lib.models.sd.bols_and_drops import (
    AllocatedBOL,
    BOL,
    BOLDetail,
    Drop as ExecutedDrop,
)
from bb_integrations_lib.models.sd.get_order import (
    Drop as PlannedDrop,
    DropDetail as PlannedDropDetail,
    Load as PlannedLoad,
    LoadDetail as PlannedLoadDetail,
)


class MatchedAllocation(BaseModel):
    """Result of matching an allocated BOL to planned and executed data."""

    # Executed
    allocated_bol: AllocatedBOL
    executed_bol: Optional[BOL] = None
    executed_bol_detail: Optional[BOLDetail] = None
    executed_drop: Optional[ExecutedDrop] = None

    # Planned
    planned_load: Optional[PlannedLoad] = None
    planned_load_detail: Optional[PlannedLoadDetail] = None
    planned_drop: Optional[PlannedDrop] = None
    planned_drop_detail: Optional[PlannedDropDetail] = None

    # Variance
    planned_quantity: Optional[int] = None
    actual_quantity: int
    variance: Optional[int] = None
    variance_pct: Optional[float] = None

    # Match status
    matched_to_planned_drop: bool = False
    matched_to_planned_load: bool = False
    matched_to_executed_bol: bool = False
    matched_to_executed_drop: bool = False


def calculate_volume_variance(
    actual_qty: int,
    planned_qty: Optional[int],
) -> tuple[Optional[int], Optional[float]]:
    """
    Calculate variance between actual and planned quantities.

    Returns:
        tuple of (variance, variance_pct) - both None if planned_qty is None or zero
    """
    if planned_qty is None or planned_qty <= 0:
        return None, None
    variance = actual_qty - planned_qty
    variance_pct = (variance / planned_qty) * 100
    return variance, variance_pct


def match_allocated_to_planned_drop(
    allocated_bol: AllocatedBOL,
    planned_drops: list[PlannedDrop],
) -> tuple[Optional[PlannedDrop], Optional[PlannedDropDetail]]:
    """
    Match an allocated BOL to a planned drop detail.

    Match keys:
    - allocated_bol.location_id == planned_drop.location_id
    - allocated_bol.store_product_id == planned_drop.detail.product_id
    - allocated_bol.store_tank == planned_drop.detail.tank_id
    """
    for drop in planned_drops:
        if drop.location_id != allocated_bol.location_id:
            continue
        for detail in drop.details:
            if (
                detail.product_id == allocated_bol.store_product_id
                and detail.tank_id == allocated_bol.store_tank
            ):
                return drop, detail
    return None, None


def match_drop_to_load(
    drop_detail: Optional[PlannedDropDetail],
    planned_loads: list[PlannedLoad],
) -> tuple[Optional[PlannedLoad], Optional[PlannedLoadDetail]]:
    """
    Match a planned drop detail to a planned load detail using compartment_index.

    The bridge: drop_detail.sources[].compartment_index -> load_detail.compartment_index
    """
    if drop_detail is None:
        return None, None

    compartment_indexes = {s.compartment_index for s in drop_detail.sources}

    for load in planned_loads:
        for load_detail in load.details:
            if load_detail.compartment_index in compartment_indexes:
                return load, load_detail
    return None, None


def match_allocated_to_executed_bol(
    allocated_bol: AllocatedBOL,
    executed_bols: list[BOL],
) -> tuple[Optional[BOL], Optional[BOLDetail]]:
    """
    Match an allocated BOL to an executed BOL detail.

    Match keys:
    - allocated_bol.bol_terminal_id == executed_bol.location_id
    - allocated_bol.bol_product_id == executed_bol.detail.product_id
    """
    for bol in executed_bols:
        if bol.location_id != allocated_bol.bol_terminal_id:
            continue
        for detail in bol.details:
            if detail.product_id == allocated_bol.bol_product_id:
                return bol, detail
    return None, None


def match_allocated_to_executed_drop(
    allocated_bol: AllocatedBOL,
    executed_drops: list[ExecutedDrop],
) -> Optional[ExecutedDrop]:
    """
    Match an allocated BOL to an executed drop.

    Match keys:
    - allocated_bol.location_id == executed_drop.location_id
    - allocated_bol.store_product_id == executed_drop.product_id
    - allocated_bol.store_tank == executed_drop.tank_id
    """
    for drop in executed_drops:
        if (
            drop.location_id == allocated_bol.location_id
            and drop.product_id == allocated_bol.store_product_id
            and drop.tank_id == allocated_bol.store_tank
        ):
            return drop
    return None


def match_allocations(
    allocated_bols: list[dict],
    executed_bols: list[dict],
    executed_drops: list[dict],
    planned_loads: list[dict],
    planned_drops: list[dict],
) -> list[MatchedAllocation]:
    """
    Match allocated BOLs to planned and executed data.

    Args:
        allocated_bols: List of allocated_bols from bols_and_drops response
        executed_bols: List of bols from bols_and_drops response
        executed_drops: List of drops from bols_and_drops response
        planned_loads: List of loads from get_orders response
        planned_drops: List of drops from get_orders response

    Returns:
        List of MatchedAllocation results with variance calculations
    """
    # Parse inputs into Pydantic models
    parsed_allocated = [AllocatedBOL.model_validate(ab) for ab in allocated_bols]
    parsed_executed_bols = [BOL.model_validate(b) for b in executed_bols]
    parsed_executed_drops = [ExecutedDrop.model_validate(d) for d in executed_drops]
    parsed_planned_loads = [PlannedLoad.model_validate(l) for l in planned_loads]
    parsed_planned_drops = [PlannedDrop.model_validate(d) for d in planned_drops]

    results: list[MatchedAllocation] = []

    for allocated_bol in parsed_allocated:
        # Step 1: Match to planned drop
        planned_drop, planned_drop_detail = match_allocated_to_planned_drop(
            allocated_bol, parsed_planned_drops
        )

        # Step 2: Match planned drop to planned load via compartment
        planned_load, planned_load_detail = match_drop_to_load(
            planned_drop_detail, parsed_planned_loads
        )

        # Step 3: Match to executed BOL
        executed_bol, executed_bol_detail = match_allocated_to_executed_bol(
            allocated_bol, parsed_executed_bols
        )

        # Step 4: Match to executed drop
        executed_drop = match_allocated_to_executed_drop(
            allocated_bol, parsed_executed_drops
        )

        # Step 5: Calculate variance
        actual_qty = allocated_bol.bol_gross_volume_allocated
        planned_qty = planned_drop_detail.quantity if planned_drop_detail else None
        variance, variance_pct = calculate_volume_variance(actual_qty, planned_qty)

        results.append(
            MatchedAllocation(
                allocated_bol=allocated_bol,
                executed_bol=executed_bol,
                executed_bol_detail=executed_bol_detail,
                executed_drop=executed_drop,
                planned_load=planned_load,
                planned_load_detail=planned_load_detail,
                planned_drop=planned_drop,
                planned_drop_detail=planned_drop_detail,
                planned_quantity=planned_qty,
                actual_quantity=actual_qty,
                variance=variance,
                variance_pct=variance_pct,
                matched_to_planned_drop=planned_drop is not None,
                matched_to_planned_load=planned_load is not None,
                matched_to_executed_bol=executed_bol is not None,
                matched_to_executed_drop=executed_drop is not None,
            )
        )

    return results
