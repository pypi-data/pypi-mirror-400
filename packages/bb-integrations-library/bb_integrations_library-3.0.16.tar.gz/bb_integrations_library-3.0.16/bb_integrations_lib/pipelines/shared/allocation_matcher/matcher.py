from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.pipelines.shared.allocation_matcher.matching_utils import (
    MatchedAllocation,
    match_allocations,
)
from bb_integrations_lib.pipelines.shared.allocation_matcher.model import OrderData
from bb_integrations_lib.shared.model import GetOrderBolsAndDropsRequest
from bb_integrations_lib.util.utils import lookup
from loguru import logger
import asyncio


class AllocationMatcher:
    """A matcher for matching executed details to planned details.

    Matches allocated BOLs to their planned details. Carriers generally need
    this information to pay their drivers and bill their customers.

    Can be used to match any list of order numbers. The core matching logic
    is in :func:`match_allocations`, which can be imported and used directly.

    Example:
        Using the class method (recommended)::

            from bb_integrations_lib.pipelines.shared.allocation_matcher.matcher import AllocationMatcher

            results = await AllocationMatcher.match_order_numbers(
                order_numbers=[1103, 1196],
                sd_client=sd_client,
            )

        Using the instance method::

            matcher = AllocationMatcher(order_numbers=[1103, 1196])
            results = await matcher.run_allocation_matching(sd_client)

        Using ``match_allocations`` directly (for custom data sources)::

            from bb_integrations_lib.pipelines.shared.allocation_matcher.matching_utils import match_allocations

            results = match_allocations(
                order_number="1103",
                allocated_bols=bols_and_drops["allocated_bols"],
                executed_bols=bols_and_drops["bols"],
                executed_drops=bols_and_drops["drops"],
                planned_loads=planned_order["loads"],
                planned_drops=planned_order["drops"],
            )
    """
    _semaphore: asyncio.Semaphore | None = None

    def __init__(
            self,
            order_numbers: list[int],
            max_concurrent: int = 10,
    ):
        self.order_numbers = order_numbers
        self.max_concurrent = max_concurrent

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """Lazy-initialized semaphore for rate limiting API calls."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    async def get_planned_details(
            self,
            client: GravitateSDAPI,
            order_number: str,
    ) -> tuple[str, dict | None, str | None]:
        """Get planned order details for a single order number."""
        async with self.semaphore:
            try:
                resp = await client.get_orders(order_number=order_number)
                data = resp.json()
                return order_number, data[0] if data else None, None
            except Exception as e:
                logger.warning(f"Failed to get planned order {order_number}: {e}")
                return order_number, None, str(e)

    async def get_order_data(
            self,
            client: GravitateSDAPI,
    ) -> list[OrderData]:
        """
        Get all planned + executed order data for a list of order numbers.
        """
        results = []

        bols_and_drops_req = GetOrderBolsAndDropsRequest(order_numbers=self.order_numbers)
        bols_response = await client.get_bols_and_drops(bols_and_drops_req)
        all_bols = bols_response.json()
        bols_by_order = lookup(all_bols, lambda x: x['order_number'])
        order_strs = [str(n) for n in self.order_numbers]
        planned_results = await asyncio.gather(
            *[self.get_planned_details(client, n) for n in order_strs]
        )

        for order_num, planned, error in planned_results:
            results.append(OrderData(
                order_number=order_num,
                bols_and_drops=bols_by_order.get(order_num),
                planned_order=planned,
                error=error,
            ))
        return results

    async def run_allocation_matching(
            self,
            sd_client: GravitateSDAPI,
    ) -> list[MatchedAllocation]:
        """
        Get order data and match allocations for all order numbers.
        """
        order_data_list = await self.get_order_data(sd_client)
        all_results: list[MatchedAllocation] = []
        for data in order_data_list:
            if data.error or not data.bols_and_drops or not data.planned_order:
                continue

            results = match_allocations(
                order_number=data.order_number,
                allocated_bols=data.bols_and_drops["allocated_bols"],
                executed_bols=data.bols_and_drops["bols"],
                executed_drops=data.bols_and_drops["drops"],
                planned_loads=data.planned_order["loads"],
                planned_drops=data.planned_order["drops"],
            )
            all_results.extend(results)

        return all_results

    @classmethod
    async def match_order_numbers(
            cls,
            order_numbers: list[int],
            sd_client: GravitateSDAPI,
            max_concurrent: int = 10,
    ):
        return await cls(order_numbers, max_concurrent).run_allocation_matching(sd_client)
