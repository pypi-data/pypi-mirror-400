from datetime import datetime, UTC, timedelta
from typing import Dict
from dateutil.parser import parse

import loguru

from bb_integrations_lib.provider.api.pc_miler.client import PCMilerClient
from bb_integrations_lib.provider.api.pc_miler.model import TokenData


class _RoutingAPI:
    def __init__(self, client: PCMilerClient):
        self.client = client

    def _custom_headers(self):
        return {
            'Authorization': f'{self.client.api_key}',
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

    async def get_route_reports(self, url: str, params: Dict):
        custom_headers = self._custom_headers()
        return await self.client.get(url, params=params, headers=custom_headers)

    @property
    def service_name(self):
        return """ROUTING_API"""



class RoutingAPI(_RoutingAPI):
    def __init__(self, client: PCMilerClient):
        super().__init__(client)


class _SingleSearchAPI:
    def __init__(self, client: PCMilerClient):
        pass


class SingleSearchAPI(_SingleSearchAPI):
    def __init__(self, client: PCMilerClient):
        super().__init__(client)


class _PlacesAPI:
    def __init__(self, client: PCMilerClient):
        self.client = client
        self.tokendata: TokenData | None = None

    async def _custom_headers(self):
        if not (self.tokendata and self.tokendata.token and datetime.now(UTC) < parse(self.tokendata.expires)):
            self.tokendata = await self.client.get_token("https://api.trimblemaps.com/places/v1/authenticate")
        return {
            'Authorization': f'Bearer {self.tokendata.token}',
        }

    @property
    def service_name(self):
        return """PLACES_API"""

class PlacesAPI(_PlacesAPI):
    def __init__(self, client: PCMilerClient):
        super().__init__(client)

    async def get_place_by_id(self, id: str):
        custom_headers = await self._custom_headers()
        result = await self.client.get(
            url=f"https://api.trimblemaps.com/places/v1/place/{id}/details",
            headers=custom_headers
        )
        return result

    async def get_updated_places(self, last_modified_timestamp: str) -> list[dict] | None:
        custom_headers = await self._custom_headers()
        # last_modified_record=None
        all_results = []
        retries = 3
        while True:
            result = await self.client.get(
                url=f"https://api.trimblemaps.com/places/v1/place/updatedPlaces",
                params={
                    "lastModifiedDate": last_modified_timestamp,
                    # "lastModifiedRecord": last_modified_record,
                    "pageSize": 100
                },
                headers=custom_headers
            )
            if result.status_code != 200:
                retries -= 1
                if retries == 0:
                    return None
                continue
            data = result.json()
            items = data.get("items", [])
            all_results.extend(items)
            if len(items) < 100:
                break
            # last_modified_record = data.get("lastModifiedRecord", None)
            new_last_modified_timestamp = data.get("lastModifiedTimestamp", datetime(1970, 1, 1).isoformat())
            if new_last_modified_timestamp == last_modified_timestamp:
                # WARNING: This is a workaround for a bug in the Trimble API.
                # In short, the API only returns 100 datapoints at a time, and if a timestamp has more than 100 datapoints
                # associated it's not possible to get any datapoints after the 100th; the API ONLY lets me pick by timestamp
                # and not by a generic page number or anything. Bulk operations seem to trigger this worse than most.
                # As a workaround I will check if the timestamp we're going to "next" is the same as the current one, and add
                # 1 millisecond if it is.
                #
                # This can skip over an unknown number of events! So far I've only seen problems due to mass deletions,
                # but if there's a mass-edit functionality it could be an issue there too.
                new_last_modified_timestamp = datetime.fromisoformat(new_last_modified_timestamp) + timedelta(milliseconds=1)
                new_last_modified_timestamp = new_last_modified_timestamp.isoformat()
            last_modified_timestamp = new_last_modified_timestamp
            loguru.logger.debug(f"Fetching page from date {last_modified_timestamp}")
        return all_results

    async def create_place(self, place_req: dict, dry_run: bool = False):
        custom_headers = await self._custom_headers()
        if dry_run:
            loguru.logger.debug(f"Dry run: Would create place {place_req}")
            return

        result = await self.client.post(
            url=f"https://api.trimblemaps.com/places/v1/place",
            json=place_req,
            headers=custom_headers
        )
        loguru.logger.debug(result.status_code)
        return result

