from zipfile import BadZipFile

import json
import math
import pandas as pd

from bb_integrations_lib.mappers.rita_mapper import AsyncMappingProvider, RitaAPIMappingProvider
from bb_integrations_lib.util.utils import CustomJSONEncoder
from loguru import logger
from pydantic import BaseModel
from typing import AsyncGenerator, Union
from typing import Tuple, List, Dict, Any, TypeVar

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.config import FileConfig, ConfigAction
from bb_integrations_lib.protocols.pipelines import Step, ParserBase, Parser
from bb_integrations_lib.shared.exceptions import FileParsingError
from bb_integrations_lib.shared.model import FileConfigRawData, MappingMode, RawData

AnyParser = TypeVar("AnyParser", bound=ParserBase | Parser)


class FileConfigParserJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        return super().default(o)


class FileConfigParserV2(Step):
    def __init__(self, rita_client: GravitateRitaAPI, mapping_type: MappingMode = MappingMode.full,
                 parser: type[AnyParser] | None = None, parser_kwargs: dict | None = None, *args, **kwargs):
        """
        Parse an input file using a FileConfig, and optionally, a custom parser.

        :param rita_client: GravitateRitaAPI instance
        :param mapping_type: How the parser should use mappings while processing rows. Defaults to "full"
        :param parser: Custom parser to pass translated rows through. Can be used to process many different types of
          files, such as tank readings or price tables.
        :param parser_kwargs: Additional keyword arguments to pass to the custom parser's init method.
        """
        super().__init__(*args, **kwargs)
        if parser:
            self.custom_parser: type[ParserBase] = parser
            self.custom_parser_kwargs = parser_kwargs or {}

        self.rita_client = rita_client
        self.mapping_type = mapping_type

    def describe(self) -> str:
        """Return a description of this step for logging."""
        return "Parse and translate file data using FileConfig"

    async def execute(self, rd: FileConfigRawData) -> Union[List[Dict], RawData]:
        """
        Execute file parsing and translation.
        Args:
            rd: FileConfigRawData containing file data and configuration

        Returns:
            List of translated records, or RawData if the custom parser returns RawData
        """
        file_name = rd.file_name or "<unknown filename>"
        self.pipeline_context.included_files[f"{file_name}"] = rd.data.read()
        translated_records, errors = self.get_translated_records(rd)
        mapping_provider = RitaAPIMappingProvider(rita_client=self.rita_client)
        if errors:
            logger.warning(f"Found {len(errors)} translation errors during parsing")
            self.pipeline_context.included_files["File Config Parser Step Translation Errors"] = json.dumps(errors)
        if not hasattr(self, "custom_parser"):
            self.pipeline_context.included_files["Parsed Results"] = json.dumps(translated_records)
            return translated_records
        else:
            logger.info(f"Using custom parser: {self.custom_parser.__name__}")
            parser = self.custom_parser(
                source_system=rd.file_config.source_system,
                file_name=rd.file_name,
                mapping_provider=mapping_provider,
                **self.custom_parser_kwargs
            )
            result = parser.parse(translated_records, self.mapping_type)
            if isinstance(result, AsyncGenerator):
                parser_results = [item async for item in result]
            else:
                parser_results = await result

            if isinstance(parser_results, RawData):
                logger.info(f"Parser returned RawData: {parser_results.file_name}")
                return parser_results

            self.pipeline_context.included_files[f"{self.custom_parser.__name__} Results"] = json.dumps(
                parser_results, cls=CustomJSONEncoder
            )
            return parser_results

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize dataframe:
        - Strip whitespace from column names
        - Strip whitespace from all string values
        - Remove duplicate rows

        Args:
            df: Input DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        df = df.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.drop_duplicates()
        return df

    def get_records(self, rd: FileConfigRawData) -> List[Dict]:
        """
        Parse file data into records based on file extension configuration.

        Supports multiple file formats:
        - csv: Standard CSV with headers
        - csv1: CSV with first row skipped
        - csv_headless: CSV without headers (generates col 1, col 2, etc.)
        - xls/xlsx: Excel files (tries openpyxl first, falls back to xlrd)
        - html: HTML tables

        Args:
            rd: FileConfigRawData containing file data and configuration

        Returns:
            List of dictionaries, each representing a row from the file

        Raises:
            FileParsingError: If file parsing fails for any reason
        """
        try:
            if hasattr(rd.data, 'seek'):
                rd.data.seek(0)

            match rd.file_config.file_extension:
                case "csv1":
                    temp_df = pd.read_csv(
                        rd.data,
                        index_col=False,
                        dtype=str,
                        skiprows=1,
                        keep_default_na=False
                    )

                case "csv":
                    temp_df = pd.read_csv(
                        rd.data,
                        index_col=False,
                        dtype=str,
                        keep_default_na=False
                    )

                case "csv_headless":
                    temp_df = pd.read_csv(
                        rd.data,
                        index_col=False,
                        dtype=str,
                        header=None,
                        keep_default_na=False
                    )
                    temp_df.columns = [f"col {i + 1}" for i in range(temp_df.shape[1])]

                case "xls" | "xlsx":
                    try:
                        temp_df = pd.read_excel(
                            rd.data,
                            engine="openpyxl",
                            dtype=str,
                            keep_default_na=False
                        )
                    except (OSError, BadZipFile):
                        temp_df = pd.read_excel(
                            rd.data,
                            engine="xlrd",
                            dtype=str,
                            keep_default_na=False
                        )

                case "html":
                    data = pd.read_html(rd.data, header=0, keep_default_na=False)
                    temp_df = pd.concat(data)
                    temp_df = temp_df.astype(str)

                case "override_header":
                    temp_df = pd.read_csv(
                        rd.data,
                        index_col=False,
                        dtype=str,
                        skiprows=1,
                        keep_default_na=False
                    )
                    temp_df.columns = [f"col {i + 1}" for i in range(temp_df.shape[1])]

                case _:
                    raise ValueError(
                        f"File extension '{rd.file_config.file_extension}' is not supported"
                    )

            temp_df = self._clean_dataframe(temp_df)
            records = temp_df.to_dict(orient="records")
            return records

        except Exception as e:
            msg = f"Failed to parse file with extension '{rd.file_config.file_extension}': {e}"
            logger.error(msg)
            raise FileParsingError(msg) from e

    def get_translated_records(self, rd: FileConfigRawData) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse and translate file records using the file configuration.
        
        Extracts records from the file and applies column transformations
        defined in the file configuration. Collects translation errors
        without stopping processing.
        
        Args:
            rd: FileConfigRawData containing file data and configuration

        Returns:
            Tuple of (successfully_translated_records, translation_errors)
            - successfully_translated_records: List of translated record dictionaries
            - translation_errors: List of error dictionaries with 'row' and 'error' keys
        """
        translated_records = []
        translation_errors = []
        records = self.get_records(rd)
        for row in records:
            try:
                translated = FileConfigParserV2.translate_row(rd.file_config, row)
            except Exception as e:
                logger.warning(f"Translation failed for record {row}: {e}")
                translation_errors.append({
                    "row": row,
                    "error": str(e)
                })
                continue
            translated_records.append(translated)
        return translated_records, translation_errors

    @staticmethod
    def translate_row(file_config: FileConfig, row: dict) -> Dict:
        """
        Transform a single row based on file configuration column mappings.

        Applies various transformation actions to row data:
        - concat: Concatenate multiple columns/literals
        - parse_date: Parse date strings using pandas
        - concat_date: Concatenate multiple columns/literals with spaces, then parse as date
        - add: Add literal values
        - remove_leading_zeros/remove_trailing_zeros: Strip zeros
        - wesroc_volume_formula: Calculate Wesroc volume using the formula: (val1 * val2) / 100
        - default: Direct column mapping

        Sets failed column transformations to None and logs warnings.

        Args:
            file_config: FileConfig containing column transformation rules
            row: Dictionary representing a single data row

        Returns:
            Transformed row dictionary with mapped column names
        """
        output_row = {}
        for column in file_config.cols:
            try:
                if len(column.file_columns) == 0:
                    output_row[column.column_name] = None
                elif column.action == ConfigAction.concat:
                    concatenated = ""
                    for entry in column.file_columns:
                        stripped_entry = entry.strip()
                        if stripped_entry in row:
                            value = row[stripped_entry]
                            if value is None or (isinstance(value, float) and math.isnan(value) or pd.isna(value)):
                                concatenated += ""
                            else:
                                concatenated += str(value)
                        else:
                            # entry is not in col, concat it literally, don't strip it to avoid issues with intentional spaces
                            concatenated += str(entry)
                    output_row[column.column_name] = concatenated
                elif column.action == ConfigAction.parse_date:
                    if column.file_columns[0] not in row:
                        raise KeyError(f"Column '{column.file_columns[0]}' not found in row")
                    try:
                        output_row[column.column_name] = FileConfigParserV2._parse_datetime_to_string(
                            row[column.file_columns[0]],
                            column.format
                        )
                    except Exception as e:
                        raise ValueError(f"Failed to parse date from '{row[column.file_columns[0]]}': {e}")
                elif column.action == ConfigAction.concat_date:
                    concatenated_parts = []
                    for entry in column.file_columns:
                        stripped_entry = entry.strip()
                        if stripped_entry in row:
                            value = row[stripped_entry]
                            if value is None or (isinstance(value, float) and math.isnan(value) or pd.isna(value)):
                                continue
                            else:
                                concatenated_parts.append(str(value))
                        else:
                            concatenated_parts.append(str(entry))

                    concatenated = " ".join(concatenated_parts)
                    try:
                        output_row[column.column_name] = FileConfigParserV2._parse_datetime_to_string(
                            concatenated,
                            column.format
                        )
                    except Exception as e:
                        raise ValueError(f"Failed to parse date from concatenated string '{concatenated}': {e}")
                elif column.action == ConfigAction.add:
                    output_row[column.column_name] = column.file_columns[0]
                elif column.action == ConfigAction.remove_leading_zeros:
                    if column.file_columns[0] not in row:
                        raise KeyError(f"Column '{column.file_columns[0]}' not found in row")
                    output_row[column.column_name] = FileConfigParserV2.strip_leading_zeroes(
                        str(row[column.file_columns[0]]))
                elif column.action == ConfigAction.remove_trailing_zeros:
                    if column.file_columns[0] not in row:
                        raise KeyError(f"Column '{column.file_columns[0]}' not found in row")
                    output_row[column.column_name] = FileConfigParserV2.strip_trailing_zeroes(
                        str(row[column.file_columns[0]]))
                elif column.action == ConfigAction.wesroc_volume_formula:
                    if len(column.file_columns) != 2:
                        raise ValueError(
                            f"Wesroc volume formula action requires exactly 2 columns, got {len(column.file_columns)}")
                    if column.file_columns[0] not in row:
                        raise KeyError(f"Column '{column.file_columns[0]}' not found in row")
                    if column.file_columns[1] not in row:
                        raise KeyError(f"Column '{column.file_columns[1]}' not found in row")
                    output_row[column.column_name] = FileConfigParserV2.calculate_wesroc_volume(
                        row[column.file_columns[0]],
                        row[column.file_columns[1]],
                        column.file_columns[0],
                        column.file_columns[1]
                    )
                else:
                    if column.file_columns[0] not in row:
                        raise KeyError(f"Column '{column.file_columns[0]}' not found in row")
                    output_row[column.column_name] = str(row[column.file_columns[0]])
            except Exception as e:
                logger.warning(f"Failed to translate column '{column.column_name}': {e}")
                output_row[column.column_name] = None
        return output_row

    @staticmethod
    def _parse_datetime_to_string(value: str, date_format: str | None) -> str:
        """
        Parse a datetime value and convert it to a string.

        Args:
            value: The value to parse as a datetime
            date_format: Optional format string for parsing (None means auto-detect)

        Returns:
            String representation of the parsed datetime
        """
        return str(
            pd.to_datetime(
                value,
                format=date_format  # None means auto-detect
            )
        )

    @staticmethod
    def strip_leading_zeroes(row: str) -> str:
        """
        Remove leading zeros from a string.
        
        Args:
            row: Input string to process
            
        Returns:
            String with leading zeros removed
        """
        return row.lstrip('0')

    @staticmethod
    def strip_trailing_zeroes(row: str) -> str:
        """
        Remove trailing zeros from a string.

        Args:
            row: Input string to process

        Returns:
            String with trailing zeros removed
        """
        return row.rstrip('0')

    @staticmethod
    def calculate_wesroc_volume(val1: Any, val2: Any, col1_name: str, col2_name: str) -> float:
        """
        Calculate Wesroc volume using the formula: (val1 * val2) / 100

        Args:
            val1: First value (typically quantity or percentage)
            val2: Second value (typically quantity or percentage)
            col1_name: Name of first column (for error messages)
            col2_name: Name of second column (for error messages)

        Returns:
            Calculated volume as float

        Raises:
            ValueError: If values are None/NaN or cannot be converted to float
        """
        if val1 is None or (isinstance(val1, float) and math.isnan(val1)) or pd.isna(val1):
            raise ValueError(f"Column '{col1_name}' contains null/NaN value")

        if val2 is None or (isinstance(val2, float) and math.isnan(val2)) or pd.isna(val2):
            raise ValueError(f"Column '{col2_name}' contains null/NaN value")

        try:
            return (float(val1) * float(val2)) / 100
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to calculate Wesroc volume from '{val1}' and '{val2}': {e}")
