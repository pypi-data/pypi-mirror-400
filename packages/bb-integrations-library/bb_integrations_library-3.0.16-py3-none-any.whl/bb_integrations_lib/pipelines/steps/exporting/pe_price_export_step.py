import json
from datetime import datetime, timedelta, UTC
from functools import lru_cache
from itertools import groupby
from typing import Dict, Any, List, Tuple, Optional

import pytz
from dateutil.parser import parse
from more_itertools.more import chunked

from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.mappers.prices.model import PricePublisher, PricingIntegrationConfig
from bb_integrations_lib.models.pipeline_structs import StopPipeline
from bb_integrations_lib.models.rita.config import GenericConfig
from bb_integrations_lib.protocols.pipelines import Step, ParserBase
from bb_integrations_lib.shared.model import PEPriceData


class ImpossibleToParseDate(Exception):
    pass


class PEPriceExportStep(Step):
    def __init__(self,
                 rita_client: GravitateRitaAPI,
                 pe_client: GravitatePEAPI,
                 price_publishers: list[PricePublisher],
                 parser: type[ParserBase] | None = None,
                 parser_kwargs: dict | None = None,
                 config_id: str | None = None,
                 hours_back: int = 24,
                 addl_endpoint_args: dict | None = None,
                 last_sync_date: datetime | None = datetime.now(UTC),
                 *args, **kwargs):
        """This step requires:
            - tenant_name: [REQUIRED] client name. (i.e Jacksons, TTE, Coleman)
            - price_publishers:[REQUIRED] a list of price publisher names to be included in the price request
            - config_id: [OPTIONAL] a RITA config to pull last sync date
            - hours_back: [OPTIONAL] hours back from last sync date, defaults to 12
            - mode: [OPTIONAL] can be 'production' or 'development', defaults to production
        """
        super().__init__(*args, **kwargs)
        self.pe_client = pe_client
        self.price_publishers = price_publishers
        self.config_id = config_id
        self.hours_back = hours_back
        self.rita_client = rita_client
        self.additional_endpoint_arguments = addl_endpoint_args or {}
        self.last_sync_date = last_sync_date
        if parser:
            self.custom_parser = parser
            self.custom_parser_kwargs = parser_kwargs or {}

    def price_publisher_lkp(self) -> Dict[str, PricePublisher]:
        lkp = {}
        pp = self.price_publishers
        for p in pp:
            lkp[p.name] = p
        return lkp

    def get_publisher_extend_by(self, key: str) -> int | None:
        lkp = self.price_publisher_lkp()
        return lkp[key].extend_by_days

    def get_publisher_price_type(self, key: str) -> str:
        lkp = self.price_publisher_lkp()
        return lkp[key].price_type

    def price_type_rows(self, rows: List[PEPriceData]) -> List[PEPriceData]:
        for row in rows:
            price_type = self.get_publisher_price_type(row.PricePublisher)
            row.PriceType = price_type
        return rows

    def describe(self) -> str:
        return f"Export Pricing Engine Prices"

    async def execute(self, _: Any = None) -> List[PEPriceData] | List[Dict]:
        updated_prices = await self.get_updated_prices_for_publishers(last_sync_date=self.last_sync_date,
                                                                      price_publishers=self.price_publishers)
        if not updated_prices:
            raise StopPipeline
        updated_price_instrument_ids, min_updated_date = PEPriceExportStep.instrument_ids_and_min_date(updated_prices)
        historic_prices_per_instrument_id = await self.get_updated_prices_for_instruments(
            min_effective_date=min_updated_date,
            price_publishers=self.price_publishers,
            instrument_ids=updated_price_instrument_ids)
        prices = self.update_historical_prices(historic_prices_per_instrument_id)
        if not hasattr(self, "custom_parser"):
            return prices
        else:
            parser = self.custom_parser(**self.custom_parser_kwargs)
            parser_results = await parser.parse(prices)
            return parser_results

    def update_historical_prices(self, rows: List[PEPriceData]) -> List[PEPriceData]:
        _sorted_id = sorted(rows, key=lambda r: (r.PriceInstrumentId, r.EffectiveFromDateTime), reverse=True)
        for instrument_id, group in groupby(_sorted_id, key=lambda r: r.PriceInstrumentId):
            group_list = PEPriceExportStep.rank_rows(list(group))
            group_list_price_typed = self.price_type_rows(group_list)
            max_row = max(group_list_price_typed, key=lambda r: r.EffectiveFromDateTime)
            max_row.ExtendByDays = self.get_publisher_extend_by(max_row.PricePublisher)  # makes it more configurable
            max_row.IsLatest = True
        return _sorted_id


    async def get_prices(
            self,
            query: Dict,
            count: int = 1000,
            include_source_data: bool = True
    ) -> List[PEPriceData]:
        records = []
        payload = {
            "Query": {**query,
                      "COUNT": count
                      },
            "includeSourceData": include_source_data
        }
        resp = await self.pe_client.get_prices(payload)
        while len(resp['Data']) > 0:
            records.extend(resp['Data'])
            max_sync = resp["MaxSyncResult"]
            if max_sync is None:
                break
            payload["Query"]["MaxSync"] = max_sync
            resp = await self.pe_client.get_prices(payload)
        self.pipeline_context.included_files["Pricing Engine Export Prices Step"] = json.dumps(records)
        return [PEPriceData.model_validate(price) for price in records]

    async def get_updated_prices_for_publishers(self,
                                                last_sync_date: datetime,
                                                price_publishers: List[PricePublisher] = None) -> List[PEPriceData]:
        last_sync_date = (last_sync_date - timedelta(hours=self.hours_back)).replace(tzinfo=pytz.UTC)
        payload = {
            "IsActiveFilterType": "ActiveOnly",
            "PricePublisherNames": [p.name for p in (price_publishers or [])],
            "MaxSync": {
                "MaxSyncDateTime": last_sync_date.isoformat(),
                "MaxSyncPkId": 0
            },
            **self.additional_endpoint_arguments,
        }
        rows = await self.get_prices(query=payload, include_source_data=True)
        return rows

    async def get_updated_prices_for_instruments(self,
                                                 min_effective_date: datetime,
                                                 instrument_ids: List[int],
                                                 price_publishers: List[PricePublisher] = None) -> List[PEPriceData]:
        res_rows = []
        for idx, group in enumerate(chunked(instrument_ids, 50)):
            payload = {
                "IsActiveFilterType": "ActiveOnly",
                "PricePublisherNames": [p.name for p in (price_publishers or [])],
                "MinEffectiveDate": min_effective_date.isoformat(),
                "PriceInstrumentIds": group
            }
            rows = await self.get_prices(query=payload, include_source_data=True)
            res_rows.extend(rows)
        return res_rows

    @staticmethod
    def instrument_ids_and_min_date(rows: List[PEPriceData]) -> Tuple[list, datetime]:
        unique_price_instrument_ids = list(set([r.PriceInstrumentId for r in rows]))
        min_date = min([PEPriceExportStep.try_to_parse_date(r.EffectiveFromDateTime) for r in rows])
        return unique_price_instrument_ids, min_date

    @staticmethod
    def rank_rows(rows: List[PEPriceData]) -> List[PEPriceData]:
        for idx, row in enumerate(rows):
            row.Rank = idx + 1
        return rows

    @staticmethod
    def try_to_parse_date(dt_string: str) -> datetime:
        if isinstance(dt_string, str):
            try:
                parsed_datetime = parse(dt_string)
                return parsed_datetime
            except (ValueError, TypeError):
                raise ImpossibleToParseDate(f"Could not parse date: {dt_string}")
        elif isinstance(dt_string, datetime):
            return dt_string
        else:
            raise ImpossibleToParseDate(f"Could not parse date: {dt_string} -> Format not supported")

    @staticmethod
    def check_if_date_bigger_equal_previous_weekday(date: str) -> bool:
        parsed = parse(date).replace(tzinfo=pytz.UTC)
        _weekday = PEPriceExportStep.previous_weekday()
        return parsed >= _weekday

    @staticmethod
    @lru_cache(maxsize=1)
    def previous_weekday(anchor: Optional[datetime] = None) -> datetime:
        if anchor is None:
            anchor = datetime.now(UTC)
        anchor = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
        current_weekday = anchor.weekday()
        if current_weekday == 0:  # Monday
            days_back = 3  # Go back to Friday
        elif current_weekday == 6:  # Sunday
            days_back = 2  # Go back to Friday
        else:  # Tuesday through Saturday
            days_back = 1  # Go back one day
        return anchor - timedelta(days=days_back)


async def load_config(rita_client: GravitateRitaAPI, environment: str) -> Tuple[PricingIntegrationConfig, str]:
    config_name = f"{environment} Pricing Engine Contract Integration"
    configs = await rita_client.get_config_by_name(bucket_path="/Prices", config_name=config_name)
    job_config: GenericConfig = configs[config_name]
    pipeline_config: PricingIntegrationConfig = PricingIntegrationConfig.model_validate(job_config.config)
    return pipeline_config, job_config.config_id


if __name__ == "__main__":
    async def main():
        rita_client = GravitateRitaAPI(
            base_url="",
            client_id="",
            client_secret=""
        )
        config, config_id = await load_config(environment="Loves", rita_client=rita_client)
        s = PEPriceExportStep(
            rita_client=rita_client,
            pe_client=GravitatePEAPI(
                base_url="",
                username="",
                password=""
            ),
            price_publishers=config.price_publishers,
            config_id=config_id,
            hours_back=24,
        )
        await s.execute()
