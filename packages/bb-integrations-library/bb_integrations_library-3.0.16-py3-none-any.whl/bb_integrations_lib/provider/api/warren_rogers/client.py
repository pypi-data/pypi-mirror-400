import asyncio
from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional

import httpx
from loguru import logger

from bb_integrations_lib.protocols.flat_file import TankReading, TankMonitorType


class WarrenRogersClient(httpx.AsyncClient):
    def __init__(
            self,
            client_id: str,
            client_secret: str,
            api_key: str,
            company_id: str,
            token_endpoint: str,
            base_url: str,
            timeout: float = 180.0
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.company_id = company_id
        self.token_endpoint = token_endpoint
        self.page_size = 100
        self.oauth_token = None
        # Expect to refresh token 30s before actual expiry, in case of time desync between us and server
        self.pre_expiry_refresh = timedelta(seconds=30)

    def __repr__(self):
        return "Warren Rogers API Client"

    @property
    async def access_token(self):
        await self.ensure_token()
        return self.oauth_token["access_token"]

    async def _refresh_token(self):
        now = datetime.now()
        res = await self.post(self.token_endpoint,
                              auth=(self.client_id, self.client_secret),
                              headers={"Content-Type": "application/x-www-form-urlencoded"},
                              params="grant_type=client_credentials")
        res.raise_for_status()
        self.oauth_token = res.json()
        self.oauth_token["expires_at"] = now + timedelta(seconds=self.oauth_token["expires_in"])

    def is_token_expired(self):
        return datetime.now() > self.oauth_token["expires_at"] + self.pre_expiry_refresh

    async def ensure_token(self):
        # First run or expired token? Then refresh
        if not self.oauth_token or self.is_token_expired():
            await self._refresh_token()

    def _build_url(self, endpoint: str, api_ver: str = "v1") -> str:
        return f"api/{api_ver}/companies/{self.company_id}/{endpoint}"

    async def _get(self, url: str, params=None):
        headers = {
            "Accept": "application/json",
            "x-api-key": self.api_key,
            "wra-auth": await self.access_token
        }
        return await self.get(url, headers=headers, params=params)

    async def _paginated_get(self, url: str):
        pages = []
        page_no = 1

        first_page = (await self._get(url)).json()
        total_results = first_page["totalResults"]
        pages.append(first_page)
        entries_retrieved = first_page["size"]

        while entries_retrieved < total_results:
            page_no += 1
            page = (await self._get(url, params={"page": page_no})).json()
            pages.append(page)
            entries_retrieved += page["size"]

        return pages

    async def _continuation_get(self, url: str, starting_token: Optional[str] = None) -> tuple[str, list[dict]]:
        """
        Get data from a paginated stream that uses continuation tokens, like the /deliveries endpoint.
        If a starting continuation token is provided, it will be passed to the API; otherwise, the default API behavior
        will be used. In /deliveries case, this is retrieving the last hour of data, for example.

        :param url: The URL of the endpoint.
        :param starting_token: An optional continuation token to resume the stream from.
        :return: A tuple; item 1 is the continuation token from the API, and item 2 is the list of pages of the API
            response.
        """
        pages = []
        page_n = 1
        starting = True
        con_token = starting_token
        while starting or con_token:
            logger.debug(f"Getting page {page_n}, continuation token {con_token}")
            resp = await self._get(url=url, params={"continuationToken": con_token} if con_token else {})
            resp.raise_for_status()
            data = resp.json()
            con_token = data.get("continuationToken")
            pages.append(resp.json())
            if not data.get("truncated"):
                break
            starting = False
            page_n += 1
        return con_token, pages

    async def get_inventory_levels(self) -> list[dict]:
        """
        Get "inventory levels" (tank readings) for all tanks. Does not parse any values, but deserializes the json to a
        dict.
        """
        raw = await self._paginated_get(self._build_url("inventory-levels"))
        # The data this endpoint provides is a list of pages. Each page has some metadata plus an "inventoryLevels"
        # field, which has the actual locations and their ATGs and readings. Flatten to one big list of inventoryLevels.
        return [x for xs in raw for x in xs["inventoryLevels"]]

    async def get_inventory_levels_at_loc(self, location: str) -> list[dict]:
        """Like get_inventory_levels, but for a specific location."""
        raw = await self._get(self._build_url(f"locations/{location}/inventory-levels"))
        return raw.json()

    def _parse_tankreadings(self, location: dict) -> list[TankReading]:
        """Parse inventory levels from the WR API and convert them to TankReadings."""
        trs: list[TankReading] = []
        # For each ATG at location
        for atg_level in location["atgLevels"]:
            # For each of the actual inventory readings on this ATG
            ils = atg_level["tankInventoryLevels"]
            for il in ils:
                # Specific inventory level reading - i.e., tank
                # Note that this does not take the units reported by the WR API into account - this appears to be
                # gallons, so far.
                trs.append(
                    TankReading(
                        date=il["readingDateTime"],
                        payload={},
                        store=location["locationUniqueId"],
                        tank=il["tankUniqueId"],
                        timezone=None,  # Not needed, ISO date str has timezone
                        volume=il["atgGrossVolume"],
                        monitor_type=TankMonitorType.bbd
                    )
                )
        return trs

    async def get_unmapped_tank_readings(self) -> list[TankReading]:
        """
        Get all tank readings available to the client, like get_inventory_levels, but parse the tank readings with
        _parse_tankreadings, returning them as a flat list. Note that the store and tank identifiers are returned
        straight from the API, unmapped.
        """
        raw = await self._paginated_get(self._build_url("inventory-levels"))
        # The data this endpoint provides is a list of pages. Each page has some metadata plus an "inventoryLevels"
        # field, which has the actual locations and their ATGs and readings. Flatten to one big list of inventoryLevels.
        inventory_levels = [x for xs in raw for x in xs["inventoryLevels"]]
        trs = []
        # For each store
        for location in inventory_levels:
            trs.extend(self._parse_tankreadings(location))
        return trs

    async def get_unmapped_tank_readings_loc(self, location: str):
        """Like get_unmapped_tank_readings, but for a specific location."""
        raw = await self._get(self._build_url(f"locations/{location}/inventory-levels"))
        return self._parse_tankreadings(raw.json())

    async def get_deliveries(self, starting_token: Optional[str] = None) -> tuple[str, list[dict]]:
        """
        Get a list of locations and their deliveries. If starting_token is provided, resume the data stream from that
        continuation token. May return duplicates / repeated data.

        :param starting_token: An optional continuation token to resume the stream from. If not provided, gets the last
            hour of deliveries.
        :return: A tuple; item 1 is the final continuation token from the API (for resuming the stream in the future),
            and item 2 is the list of locations and their deliveries.
        """
        next_ct, raw = await self._continuation_get(
            self._build_url("deliveries", api_ver="v3"),
            starting_token=starting_token)
        # Flatten the locationDeliveries lists from each page into one list of dicts of locations and their deliveries.
        return next_ct, [x for xs in raw for x in xs["locationDeliveries"]]


if __name__ == "__main__":
    async def main():
        client = WarrenRogersClient(
            client_id="",
            client_secret="",
            api_key="",
            company_id="LOVES_TRAVEL_STOPS_AND_COUNTRY_STORES",
            token_endpoint="https://auth.api.wr-cloud.com/oauth2/token",
            base_url="https://api.wr-cloud.com")

        inventory_levels = await client.get_inventory_levels()
        pprint(inventory_levels)

    asyncio.run(main())
