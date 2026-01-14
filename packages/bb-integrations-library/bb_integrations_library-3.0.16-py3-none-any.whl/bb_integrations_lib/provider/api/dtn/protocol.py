from typing import Optional, Dict, Protocol, List


class DTNClient(Protocol):
    async def get_allocations(self) -> List[Dict]:
        """Get all allocation data"""

    async def get_data_in_group(self, url: str) -> List[Dict]:
        """Get data in group href"""
