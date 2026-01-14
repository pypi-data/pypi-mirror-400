import asyncio

import httpx
from loguru import logger
from pydantic import ValidationError
from bb_integrations_lib.provider.api.pc_miler.model import TokenData

route_reports_eagle_standard_params = {
    "ReportRoutes": [
        {
            "ReportingOptions": {
                "UseTollData": True,
                "TollDiscount": "All",
                "IncludeFerryDistance": True,
                "EstimatedTimeOptions": {
                    "ETAETD": 1,
                    "DateOption": 2,
                    "DateAndTime": {
                        "DayOfWeek": 4,
                        "TimeOfDay": "10:00 AM",
                        "TimeZone": 0
                    }
                },
                "UseTraffic": True
            },
            "ReportTypes": [
                {
                    "__type": "StateReportType:http://pcmiler.alk.com/APIs/v1.0",
                    "SortByRoute": False
                },
                {
                    "__type": "GeoTunnelReportType:http://pcmiler.alk.com/APIs/v1.0",
                    "CiteInterval": 5.0
                }
            ],
            "Stops": [
                {
                    "Coords": {
                        "Lat": "38.36440700",
                        "Lon": "-82.60173800"
                    }
                },
                {
                    "Coords": {
                        "Lat": "38.08867300",
                        "Lon": "-81.83779700"
                    }
                }
            ],
            "Options": {
                "VehicleType": 0,
                "RoutingType": 0,
                "HighwayOnly": False,
                "DistanceUnits": 0,
                "TollRoads": 3,
                "BordersOpen": True,
                "OverrideRestrict": False,
                "HazMatType": 4,
                "RouteOptimization": 0,
                "hubRouting": False,
                "SideOfStreetAdherence": 0,
                "ferryDiscourage": True,
                "AFSetIDs": [-1],
                "UseSites": True
            }
        }
    ]
}


class PCMilerClient(httpx.AsyncClient):
    def __init__(
            self,
            base_url: str,
            username: str,
            password: str,
            api_key: str,
            timeout: float = 180.0,
    ):
        super().__init__(base_url=base_url)
        self.username = username
        self.password = password
        self.api_key = api_key
        self.apis = PCMilerAPIWrapper(client=self)
        self.timeout = httpx.Timeout(timeout, connect=60.0)

    def __repr__(self):
        return """PC Miler Client designed for PC Miler Web Service"""

    async def get_token(self, url: str) -> TokenData:
        try:
            json_data = {'apiKey': self.api_key}
            response = await self.post(url, json=json_data)
            response.raise_for_status()
            response_data = response.json()
            return TokenData.model_validate(response_data)

        except httpx.ReadTimeout as e:
            logger.error(f"Request timed out while getting token: {e}")
            raise

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP error {status_code} while getting token: {e.response.text}")
            raise

        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while getting token: {e}")
            raise

        except ValidationError as e:
            logger.error(f"Invalid token data received: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error while getting token: {e}")
            raise


class PCMilerAPIWrapper:
    def __init__(self, client: PCMilerClient):
        from bb_integrations_lib.provider.api.pc_miler.web_services_apis import RoutingAPI
        from bb_integrations_lib.provider.api.pc_miler.web_services_apis import SingleSearchAPI
        from bb_integrations_lib.provider.api.pc_miler.web_services_apis import PlacesAPI

        self.routing = RoutingAPI(client=client)
        self.single_search = SingleSearchAPI(client=client)
        self.places = PlacesAPI(client=client)


