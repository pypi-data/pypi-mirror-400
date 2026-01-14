import json
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, Tuple, Iterable

import polars as pl
import pytz
from loguru import logger

from bb_integrations_lib.models.pipeline_structs import StopPipeline
from dateutil.parser import parse

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.exceptions import StepInitializationError
from bb_integrations_lib.shared.model import RawData, FileFormat


class ReadingParser:
    """
    Parser for tank reading data that supports multiple output formats.

    This class provides parsing capabilities for tank reading data into different
    client-specific formats, including standard PDI-compatible output and various
    Circle K formats for different integration systems.

    The parser takes preprocessed DataFrame input (with standardized column names)
    and transforms it according to the specified format requirements.

    Supported formats:
        - standard: PDI-compatible format with configurable disconnection tracking
        - circlek: Circle K format with TelaPoint integration fields
        - circlek2: Simplified Circle K format for Gravitate system integration
    """

    def __init__(self, file_format: FileFormat):
        """
        Initialize the parser with a specific output format.

        Args:
            file_format (FileFormat): The desired output format for parsed data
        """
        self.format = file_format

    def parse(self, df: pl.DataFrame, disconnected_column: bool = False,
              disconnected_only: bool = False, water_level_column: bool = False) -> pl.DataFrame:
        """
        Parse tank reading data according to the configured format.

        Args:
            df (DataFrame): Input DataFrame with standardized column names:
                - Store Number: Store identifier
                - Name: Store name
                - Tank Id: Tank identifier
                - Tank Product: Product type in tank
                - Carrier: Carrier information
                - Volume: Current volume measurement
                - Ullage: Unfilled space in tank
                - Read Time: Timestamp of reading
                - Store Source Number: Store number assigned by client  (extra_data.site_source_number)
                - Disconnected: Boolean disconnection status (optional)
            disconnected_column (bool): Whether to include Disconnected column
                in output (standard format only)
            disconnected_only (bool): Whether to filter to only disconnected
                tanks (standard format only)
            water_level_column (bool): Whether to include Water Level column

        Returns:
            DataFrame: Parsed data in the specified format

        Raises:
            ValueError: If the configured format is not supported
        """
        if self.format == FileFormat.standard:
            return self._parse_standard(df, disconnected_column, disconnected_only, water_level_column)
        elif self.format == FileFormat.circlek:
            return self._parse_circlek(df)
        elif self.format == FileFormat.circlek2:
            return self._parse_circlek2(df)
        elif self.format == FileFormat.reduced:
            return self._parse_reduced(df)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _parse_standard(self, df: pl.DataFrame, disconnected_column: bool,
                        disconnected_only: bool, water_level_column: bool) -> pl.DataFrame:
        """
        Parse data into standard PDI-compatible format.

        Produces columns: Store Number, Name, Tank Id, Tank Product, Carrier,
        Volume, Ullage, Read Time, and optionally Disconnected.
        """
        column_order = [
            'Store Number', 'Name', 'Tank Id', 'Tank Product',
            'Carrier', 'Volume', 'Ullage', 'Read Time'
        ]

        if water_level_column:
            column_order.append('Water')

        if disconnected_column:
            column_order.append('Disconnected')

        if disconnected_only:
            df = df.filter(pl.col("Disconnected") == True)

        return df.select(column_order)

    def _parse_circlek(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Parse data into Circle K format with TelaPoint integration fields.

        Transforms input data into Circle K's expected structure with TelaPoint
        account/site numbers and formatted timestamps.
        """

        def parse_date(dt: str) -> str:
            dt = parse(dt)
            return dt.strftime("%m/%d/%Y %H:%M")

        rows = []
        records = df.to_dicts()

        for record in records:
            rows.append({
                "ClientName": None,
                "FacilityName": None,
                "FacilityInternalID": None,
                "FacilityState": None,
                "VolumePercentage": None,
                "TankStatus": None,
                "TankNbr": None,
                "TankInternalID": None,
                "AtgTankNumber": record['Tank Id'],
                "ATGTankLabel": None,
                "Product": None,
                "TankCapacity": None,
                "Ullage": None,
                "SafeUllage": None,
                "Volume": record['Volume'],
                "Height": None,
                "Water": None,
                "Temperature": None,
                "InventoryDate": parse_date(record['Read Time']),
                "SystemUnits": None,
                "CollectionDateTimeUtc": None,
                "TelaPointAccountNumber": 100814,
                "TelaPointSiteNumber": record['Store Number'],
            })

        return pl.DataFrame(rows)

    def _parse_circlek2(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Parse data into simplified Circle K format.
        """

        def parse_date(dt: str) -> str:
            dt = parse(dt)
            return dt.strftime("%m/%d/%Y %H:%M")

        rows = []
        records = df.to_dicts()

        for record in records:
            rows.append({
                "storeNumber": record.get('Store Source Number'),
                "timestamp": parse_date(record['Read Time']),
                "tankLabel": record.get('Tank Product'),  # Product name assigned to tank
                "volume": record['Volume'],
                "tankNumber": record['Tank Id'],
                "ullage": record.get('Ullage', 0),
                "productLevel": 0,  # Can be set to 0 as specified
                "waterLevel": 0,  # Can be set to 0 as specified
                "temperature": 0  # Can be set to 0 as specified
            })

    def _parse_reduced(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Parse data into reduced format with minimal columns.
        """
        df = df.with_columns([
            (pl.col('Read Time')
            .str.replace(" UTC", "")
            .str.to_datetime(format="%Y-%m-%d %H:%M:%S %z")
            .dt.convert_time_zone("UTC")
            .dt.strftime("%Y-%m-%dT%H:%M:%S.%3f")
            .str.replace(r"\.(\d{3})\d*$", ".$1")
            + pl.lit("Z"))
            .alias('read_time')
        ])

        return df.select([
            pl.col('Store Number').alias('store_number'),
            pl.col('Tank Id').alias('tank_id'),
            pl.col('read_time'),
            pl.col('Volume').alias('volume')
        ])

    @classmethod
    def create_parser(cls, file_format: FileFormat) -> 'ReadingParser':
        """
        Factory method to create a parser for the specified format.

        Args:
            file_format (FileFormat): The desired output format

        Returns:
            ReadingParser: Configured parser instance
        """
        return cls(file_format)


class ParseTankReadingsStep(Step):
    def __init__(self, file_format: FileFormat, timezone: str, include_water_level: bool = False,
                 disconnected_column: bool = False, disconnected_only: bool = False,
                 disconnected_hours_threshold: float | None = None,
                 *args, **kwargs):
        """
        Parse tank readings from BBDExportReadingsStep and create a PDI-compatible file, either in the standard output
        format (with some configuration options) or in a client-specific format.

        See the ``FileFormat`` enum for currently supported formats.

        :param file_format: The ``FileFormat`` to use for the output file. "standard" provides a PDI compatible file,
          but additional formats may be implemented at client request.
        :param timezone: Timezone to localize read times to. Must be a Pytz-known timezone name.
        :param include_water_level: Whether to include water level in the output file. Defaults to False.
        :param disconnected_column: Whether to include a "Disconnected" column in the output file. Independent of
          disconnected_only. Requires ``disconnected_hours_threshold`` to be set.
        :param disconnected_only: Whether to post-filter result rows to only disconnected site/tanks. Independent of
          disconnected_column. Requires ``disconnected_hours_threshold`` to be set.
        :param disconnected_hours_threshold: How long it may be since the last reading before a tank is considered
          disconnected. Setting this value without ``disconnected_column`` or ``disconnected_only`` will have no effect.
        """
        super().__init__(*args, **kwargs)
        self.file_format: FileFormat = file_format
        self.timezone = timezone
        self.step_created_time = datetime.now(UTC)
        self.include_water_level = include_water_level
        self.disconnected_column = disconnected_column
        self.disconnected_only = disconnected_only
        self.disconnected_hours_threshold = disconnected_hours_threshold
        self.disconnected_threshold = timedelta(
            hours=self.disconnected_hours_threshold) if self.disconnected_hours_threshold else None

        # Initialize the reading parser for the configured format
        self.reading_parser = ReadingParser(self.file_format)

        if (self.disconnected_column or self.disconnected_only) and not self.disconnected_hours_threshold:
            raise StepInitializationError(
                "If disconnected_column or disconnected_only is True, disconnected_hours_threshold must be set")

    def describe(self) -> str:
        return f"Format tank readings step"

    async def execute(self, data: Tuple[Dict, Dict, Iterable]) -> pl.DataFrame:
        store_lkp, tank_lkp, readings = data
        df = pl.LazyFrame(readings, schema={
            "tank_agent_name": str,
            "store_number": str,
            "run_time": datetime,
            "tank_id": str,
            "read_time": datetime,
            "product": str,
            "monitor_type": str,
            "volume": float,
        })
        return (await self.parse_data(data=df, tank_lkp=tank_lkp, store_lkp=store_lkp)).collect()

    @staticmethod
    def safe_expand_extra_data(df: pl.DataFrame, extra_data_col='extra_data') -> pl.DataFrame:
        if extra_data_col not in df.columns:
            logger.warning(f"Warning: {extra_data_col} column not found")
            return df
        if df[extra_data_col].is_null().all():
            logger.warning(f"Warning: All {extra_data_col} values are null")
            return df.drop(extra_data_col)
        try:
            col_dtype = df[extra_data_col].dtype
            if str(col_dtype).startswith("Struct"):
                df = df.unnest(extra_data_col)
            else:
                df = df.with_columns([
                    pl.col(extra_data_col).map_elements(
                        lambda x: x if isinstance(x, dict) else (json.loads(x) if isinstance(x, str) else {}),
                        return_dtype=pl.Struct
                    ).alias(f"{extra_data_col}_parsed")
                ])
                df = df.unnest(f"{extra_data_col}_parsed")
                df = df.drop(extra_data_col)
            return df
        except Exception as e:
            logger.error(f"Error expanding {extra_data_col}: {e}")
            return df

    def maybe_add_water_level(self, df: pl.DataFrame, columns_to_keep: list) -> pl.DataFrame:
        if self.include_water_level:
            columns_to_keep.append('water')
            df = df.with_columns([
                pl.col('water').fill_nan(None).alias('water')
            ])
        return df

    def map_stores_to_gravitate_name(self, df: pl.DataFrame, store_lkp: Dict) -> pl.DataFrame:
        store_name_map = {k: v.get('name') if v else None for k, v in store_lkp.items()}
        store_source_number_map = {k: v.get('extra_data', {}).get('site_source_number') if v else None
                                   for k, v in store_lkp.items()}

        df = df.with_columns([
            pl.col('store_number').replace(store_name_map, default=None).alias('name'),
            pl.col('store_number').replace(store_source_number_map, default=None).alias('store_source_number')
        ])
        return df

    def select_keep_columns(self, df: pl.DataFrame, columns_to_keep: list) -> pl.DataFrame:
        return df.select(columns_to_keep)

    def localize_timestamps(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns([
            pl.col('read_time')
            .dt.replace_time_zone("UTC")
            .dt.convert_time_zone(self.timezone)
            .alias('read_time')
        ])
        return df

    def maybe_calculate_disconnected_tanks(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Optionally calculate disconnected status for tanks.

        Groups by (store_number, tank_id) and determines if tank is disconnected
        based on reading timestamps and configured threshold.

        Args:
            df: Input DataFrame with read_time column

        Returns:
            DataFrame with optional 'disconnected' column added
        """
        if self.disconnected_column or self.disconnected_only:
            disconnections = df.group_by(['store_number', 'tank_id']).agg([
                pl.col('read_time').map_elements(
                    lambda times: self.is_disconnected(times, self.disconnected_threshold),
                    return_dtype=pl.Boolean
                ).first().alias('disconnected')
            ])
            df = df.join(disconnections, on=['store_number', 'tank_id'], how='left')
        return df

    def format_timestamps(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Format read_time datetime to string using vectorized strftime.

        Converts to "YYYY-MM-DD HH:MM:SS TZ±HHMM" format.

        Args:
            df: Input DataFrame with datetime read_time column

        Returns:
            DataFrame with string-formatted read_time
        """
        df = df.with_columns([
            pl.col('read_time').dt.strftime("%Y-%m-%d %H:%M:%S %Z%z").alias('read_time')
        ])
        return df

    def create_tank_lookup_key(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns([
            (pl.col('store_number').cast(pl.Utf8) + ':' + pl.col('tank_id').cast(pl.Utf8)).alias('key')
        ])
        return df

    def map_tank_metadata(self, df: pl.DataFrame, tank_lkp: Dict) -> pl.DataFrame:
        """
        Map tank metadata (product, carrier, storage_max) using composite key.
        """
        tank_product_map = {k: v.get('product') if v else None for k, v in tank_lkp.items()}
        tank_carrier_map = {k: v.get('carrier') if v else None for k, v in tank_lkp.items()}
        tank_storage_max_map = {k: v.get('storage_max') if v else None for k, v in tank_lkp.items()}
        df = df.with_columns([
            pl.col('key').replace(tank_product_map, default=None).alias('tank_product'),
            pl.col('key').replace(tank_carrier_map, default=None).alias('carrier'),
            pl.col('key').replace(tank_storage_max_map, default=None).alias('storage_max')
        ])
        return df

    def calculate_ullage(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Formula: ullage = storage_max - volume
        """
        df = df.with_columns([
            (pl.col('storage_max').fill_null(0) - pl.col('volume').fill_null(0)).alias('ullage')
        ])
        return df

    def map_tanks_to_gravitate_id(self, df: pl.DataFrame, tank_lkp: Dict) -> pl.DataFrame:
        df = self.create_tank_lookup_key(df)
        df = self.map_tank_metadata(df, tank_lkp)
        df = self.calculate_ullage(df)
        return df

    def format_column_names(self, df: pl.DataFrame) -> pl.DataFrame:
        column_mapping = {col: ParseTankReadingsStep.format_column_name(col) for col in df.columns}
        return df.rename(column_mapping)

    def add_reference_data(self, df: pl.DataFrame, tank_lkp: Dict, store_lkp: Dict) -> pl.DataFrame:
        columns_to_keep = ['store_number', 'tank_id', 'read_time', 'volume', 'name', 'store_source_number']
        df = self.maybe_add_water_level(df, columns_to_keep)
        df = self.map_stores_to_gravitate_name(df, store_lkp)
        df = self.select_keep_columns(df, columns_to_keep)
        df = self.localize_timestamps(df)
        df = self.maybe_calculate_disconnected_tanks(df)
        df = self.format_timestamps(df)
        df = self.map_tanks_to_gravitate_id(df, tank_lkp)
        df = self.format_column_names(df)

        return df

    def file_parser(self, df: pl.DataFrame, tank_lkp: Dict, store_lkp: Dict) -> pl.DataFrame:
        """
        Parse tank reading data into the configured output format.

        This method first enriches the data with reference information, then uses
        the ReadingParser to transform it into the appropriate format.

        Args:
            df (DataFrame): Raw tank readings DataFrame
            tank_lkp (Dict): Tank lookup dictionary
            store_lkp (Dict): Store lookup dictionary

        Returns:
            DataFrame: Parsed DataFrame in the configured output format
        """
        df = self.add_reference_data(df, tank_lkp, store_lkp)
        return self.reading_parser.parse(
            df,
            disconnected_column=self.disconnected_column,
            disconnected_only=self.disconnected_only,
            water_level_column=self.include_water_level
        )

    def localize(self, dt: datetime, timezone: str = None) -> datetime:

        if timezone is None:
            timezone = self.timezone
        utc = pytz.timezone('UTC')
        dt = utc.localize(dt)
        dt = dt.astimezone(pytz.timezone(timezone))
        return dt

    def format_dt_col(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z%z")

    def is_disconnected(self, reading_times: Iterable[datetime], threshold: timedelta) -> bool:
        """
        Determine if a tank is disconnected based on reading timestamps.

        A tank is considered disconnected if it has no readings within the threshold
        period from the current time, or if it has no readings at all.

        Args:
            reading_times (Iterable[datetime]): Collection of reading timestamps
            threshold (timedelta): Time threshold for disconnection detection

        Returns:
            bool: True if tank is disconnected, False otherwise
        """
        # Skip future times, with a 15 minute grace period (maybe the clocks are just slightly desynced)
        filtered = [t for t in reading_times if t <= self.step_created_time + timedelta(minutes=15)]
        # No readings, or a reading older than now - threshold? Disconnected
        return len(filtered) == 0 or max(filtered) < datetime.now(UTC) - threshold

    @staticmethod
    def format_column_name(col_name: str) -> str:
        return ' '.join(word.capitalize() for word in col_name.split('_'))

    async def parse_data(self, data: pl.DataFrame, store_lkp: Dict, tank_lkp: Dict) -> pl.DataFrame:
        """
        Parse tank reading data and return as RawData for pipeline output.

        Args:
            data (DataFrame): Raw tank readings DataFrame
            store_lkp (Dict): Store lookup dictionary
            tank_lkp (Dict): Tank lookup dictionary

        Returns:
            DataFrame: Parsed data output in the requested format. An additional step is required to export this data
            to a RawData object.
        """
        df = self.file_parser(df=data, tank_lkp=tank_lkp, store_lkp=store_lkp)
        # self.pipeline_context.included_files["parse pricing engine prices to PDI file step"] = json.dumps(
        #     df.to_dicts())
        return df
