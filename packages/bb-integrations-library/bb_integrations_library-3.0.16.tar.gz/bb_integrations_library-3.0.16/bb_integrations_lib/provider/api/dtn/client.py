import asyncio
from contextlib import contextmanager
from typing import Dict, List
import httpx
import pandas as pd

class DTNClient(httpx.AsyncClient):
    def __init__(
            self, username: str,
            web_service_key: str,
            api_key: str,
            base_url: str,
            timeout: float = 180.0,
    ):
        super().__init__(base_url=base_url)
        self.username = username
        self.web_service_key = web_service_key
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=180)
        self.timeout = httpx.Timeout(timeout, connect=60.0)

    def __repr__(self):
        return """DTN API Client designed for DTN Allocation Tracker"""

    @property
    def custom_headers(self) -> Dict[str, str]:
        return {
            'username': self.username,
            'Accept': 'application/vnd.dtn.energy.v1+JSON',
            'webservicekey': self.web_service_key,
            'apikey': self.api_key,
        }

    async def get_allocations(self) -> List[Dict]:
        url = '/allocations'
        res = await self.get(url=url, headers=self.custom_headers, timeout=self.timeout)
        return res.json()

    async def get_data_in_group(self, url: str) -> List[Dict]:
        if url.startswith(self.base_url):
            url = url.removeprefix(self.base_url)
        if not url.startswith('/'):
            url = f'/{url}'
        res = await self.get(
            url=url,
            headers=self.custom_headers,
            timeout=self.timeout
        )
        return res.json()

    async def get_terminal(self, href) -> Dict:
        res = await self.get(url=href, headers=self.custom_headers, timeout=self.timeout)
        return res.json()



@contextmanager
def init_dtn_api(username=None, web_service_key=None, api_key=None) -> DTNClient:
    dtn_client = DTNClient(
        username=username,
        web_service_key=web_service_key,
        api_key=api_key,
        base_url='https://api.dtn.com/fuelsuite/allocationtracker/'
    )
    yield dtn_client


def parse_allocation_data(allocation_data):
    ret = []
    for allocation in allocation_data['data']:
        supplier = allocation.get('supplier', {})
        location_data = allocation.get('location', {})
        customer_data = allocation.get('customer', {})
        consignee_group_data = customer_data.get('consigneeGroup', {})
        product_group_data = allocation.get('productAllocationList', [])
        terminal_data = location_data.get('terminal', {}) or {}
        location_group_data = location_data.get('terminalGroup', {}) or {}
        sold_to_data = consignee_group_data.get('soldTo', {}) or {}
        supplier_name = supplier.get('name')
        supplier_code = supplier.get('sellerNum')
        terminal_name = location_group_data.get('name') or terminal_data.get('name') or None
        terminal_code = location_group_data.get('id') or terminal_data.get('id') or None
        terminal_hfref = location_group_data.get('terminalListLink', {}).get('href')
        consignee_name = consignee_group_data.get('name')
        consignee_id = consignee_group_data.get('id')
        sold_to_id = sold_to_data.get('id')
        sold_to_name = sold_to_data.get('name')
        for group in product_group_data:
            product_group_name = group.get('name')
            uom = group.get('unitOfMeasure')
            allocation_remaining_monthly = group.get('allocationRemainingAmountMonthly')
            lifted_amount_monthly = group.get('liftedAmountMonthly')
            refresh_amount_monthly = group.get('refreshAmountMonthly')
            refresh_date_monthly = group.get('refreshDateMonthly')
            scaled_start_amount_monthly = group.get('scaledStartAmountMonthly')
            start_amount_monthly = group.get('startAmountMonthly')
            row = {
                'supplier_name': supplier_name,
                'supplier_code': supplier_code,
                'terminal_name': terminal_name,
                'terminal_code': terminal_code,
                'terminal_hfref': terminal_hfref,
                'consignee_name': consignee_name,
                'consignee_id': consignee_id,
                'sold_to_name': sold_to_name,
                'sold_to_id': sold_to_id,
                'product_group_name': product_group_name,
                'uom': uom,
                'allocation_remaining_monthly': allocation_remaining_monthly,
                'lifted_amount_monthly': lifted_amount_monthly,
                'refresh_amount_monthly': refresh_amount_monthly,
                'refresh_date_monthly': refresh_date_monthly,
                'scaled_start_amount_monthly': scaled_start_amount_monthly,
                'start_amount_monthly': start_amount_monthly,
            }
            ret.append(row)
    return pd.DataFrame(ret)


if __name__ == "__main__":
    async def get_allocation_data():
        with init_dtn_api(username="", web_service_key="", api_key="") as dtn_client:
            allocations = await dtn_client.get_allocations()
            print(allocations)


    asyncio.run(get_allocation_data())
