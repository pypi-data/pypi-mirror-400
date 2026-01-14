from io import StringIO
from typing import Self

import pandas as pd

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.secrets.credential_models import KachoolieCredential

class KachoolieApiClient(BaseAPI):
    """API client for Kachoolie tank inventory data."""

    column_names = [
        "Site Id",
        "Site Name",
        "City",
        "Kachoolie Number",
        "Timestamp",
        "Product Type",
        "Tank Name",
        "Tank Number",
        "Tank Volume in gross gallons",
        "Height in Ins."
    ]

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    @classmethod
    def from_credential(cls, credential: KachoolieCredential) -> Self:
        return cls(**credential.model_dump(exclude={"type_tag"}))

    async def get_inventory(self, headings: bool = False) -> list[dict]:
        """
        Fetch inventory data from Kachoolie API.

        Args:
            headings: If True, includes column headings in response (useful for debugging)

        Returns:
            List of dictionaries with tank inventory records
        """
        params = {"headings": "on" if headings else "off"}
        response = await self.get(self.base_url, params=params)
        response.raise_for_status()

        return self._parse_html_response(response.text, header=headings)

    def _parse_html_response(self, text: str, header: bool = False) -> list[dict]:
        """Parse HTML table response into list of dictionaries.

        Args:
            text: HTML string containing table data
            header: If True, use headers from the HTML table;
                    if False, use predefined column names from self.headers

        Returns:
            List of dictionaries with tank inventory records
        """
        tables = pd.read_html(StringIO(text), header=0 if header else None)

        if not tables:
            return []

        df = tables[0]

        if not header:
            df.columns = self.column_names

        return df.to_dict(orient="records")



if __name__ == "__main__":
    import asyncio

    async def main():
        client = KachoolieApiClient(
            base_url="https://kachoolie.com/dooleys.php"
        )
        inventory = await client.get_inventory()
        print(f"Retrieved {inventory} records")


    asyncio.run(main())
