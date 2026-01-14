from enum import Enum
from typing import Protocol, Iterable, Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from bb_integrations_lib.shared.model import RawData, File


class FileStorageClient(Protocol):
    """Protocol for classes that can upload and download files from some source, when credentials are provided."""

    def list_files(self, directory: str, credential_file_name: str = None) -> list[str]:
        """Integration method to list files in a remote directory"""
        pass

    def get_raw_data(self, min_date: datetime, credential_file_name: str = None, check_date: bool = True) -> \
            Iterable[RawData]:
        """Integration method to download a file from a remote directory"""
        pass

    def rename_file(self, old_name: str, new_name: str, credential_file_name: str = None) -> None:
        """Integration method to rename a remote file"""
        pass

    def delete_file(self, path: str, credential_file_name: str = None) -> None:
        """Integration method to delete a remote file"""
        pass

    def upload_file(self, file: File, path: str, credential_file_name: str = None) -> None:
        """Integration method to upload a file to a remote directory"""
        pass


class Integration(Protocol):
    """
    An integration retrieves data from a source and returns an iterable of RawData objects.
    """

    def get_raw_data(self, min_date: datetime = datetime.min) -> Iterable[RawData]:
        """Method for fetching the raw data from the integration"""

    def archive_data(self, raw_data: RawData):
        """Method that archives the data after it has been processed"""


class Translator(Protocol):
    def translate_row(self, row: dict) -> dict:
        """Translate the data in the provided row. Returns a new dictionary that has been translated."""


class Parser(Protocol):
    def parse_raw_data(self, raw_data: RawData) -> Iterable:
        """Method to process the raw data from the get_raw_data Integration method."""


class TankMonitorType(str, Enum):
    bbd = "bbd"
    aws = "aws"


class TankReading(BaseModel):
    date: str  # ISO Datetime
    payload: dict = {}
    store: str
    tank: str
    timezone: str | None
    volume: float
    monitor_type: TankMonitorType


class SalesAdjustedDeliveryReading(BaseModel):
    source: str
    number: str
    store_id: str
    tank_id: str
    product_id: str
    volume: float
    date: datetime

class TankSales(BaseModel):
    store_number: str
    tank_id: str
    date: str  # ISO Datetime
    sales: float

class PELookup(BaseModel):
    """Lookup model for common source identifiers"""
    SourceSystemId: Optional[int] = None
    SourceId: Optional[int] = None
    SourceId2: Optional[int] = None
    SourceId3: Optional[int] = None
    SourceIdString: Optional[str] = None


class PriceInstrumentDTO(BaseModel):
    """Price Instrument Data Transfer Object"""
    Name: str
    Abbreviation: str
    UnitOfMeasureLookup: Optional[PELookup] = None
    CurrencyLookup: Optional[PELookup] = None
    BookLookup: Optional[PELookup] = None
    ProductLookup: Optional[PELookup] = None
    LocationLookup: Optional[PELookup] = None
    ToCurrencyLookup: Optional[PELookup] = None
    CounterPartyLookup: Optional[PELookup] = None
    IsActive: bool = True
    ExternalReferenceNumber: Optional[str] = None
    SourceId: Optional[int] = None
    SourceIdString: Optional[str] = None


class PriceTypeDTO(BaseModel):
    """Price Type Data Transfer Object"""
    PriceTypeMeaning: str
    ExtractPrices: bool = True


class BulkSyncIntegrationDTO(BaseModel):
    """Integration Data Transfer Object"""
    Name: Optional[str] = None
    Abbreviation: Optional[str] = None
    PricePublisherTypeMeaning: Optional[str] = None
    IsActive: bool = True
    MatchByType: Literal["SourceId", "SourceIdString"] = None
    PriceInstrumentDTOs: List[PriceInstrumentDTO] = Field(default_factory=list)
    PriceTypeDTOs: List[PriceTypeDTO] = Field(default_factory=list)
    SourceId: Optional[int] = None
    SourceIdString: Optional[str] = None



class PeBulkSyncIntegrationOptions(BaseModel):
    """Options configuration"""
    IsPartialDataSet: bool = True


class PeBulkSyncIntegration(BaseModel):
    """Root model for price integration data"""
    Options: PeBulkSyncIntegrationOptions = PeBulkSyncIntegrationOptions()
    IntegrationDtos: List[BulkSyncIntegrationDTO] = Field(default_factory=list)
    SourceSystemId: int = None

class PriceMergeValue(BaseModel):
    Value: float
    PriceTypeMeaning: Literal["High", "Low", "Posting", "Average"] = "Posting"

class PriceMergeIntegrationDTO(BaseModel):
    PriceInstrumentLookup: Optional[PELookup] = None
    EstimateActual: Literal["A", "S"] = "A"
    EffectiveFromDateTime: str = None
    EffectiveToDateTime: Optional[str] = None
    TradePeriodFromDateTime: Optional[str] = None
    TradePeriodToDateTime: Optional[str] = None
    UnitOfMeasureLookup: Optional[PELookup] = None
    IsActive: Optional[bool] = True
    PriceValues: List[PriceMergeValue]

class PePriceMergeIntegration(BaseModel):
    IntegrationDtos: List
    SourceSystemId: Optional[int] = None

class DriverCredential(BaseModel):
    driver_id: dict
    expiration_date: str | None  # ISO Datetime
    certification_date: str | None  # ISO Datetime
    credential_id: str | None


class PriceRow(BaseModel):
    effective_from: str  # ISO Datetime
    effective_to: str  # ISO Datetime
    price: float
    price_type: str
    contract: Optional[str] = ""  # This is to make sure we don't break contracts
    timezone: Optional[str] = "UTC"
    terminal_id: Optional[str] = None
    terminal_source_id: Optional[str] = None
    terminal_source_system_id: Optional[str] = None
    terminal: Optional[str] = None
    product_id: Optional[str] = None
    product_source_id: Optional[str] = None
    product_source_system_id: Optional[str] = None
    product: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_source_id: Optional[str] = None
    supplier_source_system_id: Optional[str] = None
    counterparty_source_id: Optional[str] = None
    counterparty_source_system_id: Optional[str] = None
    supplier: Optional[str] = None
    enabled: Optional[bool] = None
    disabled_until: Optional[str] = None
    expire: Optional[str] = None
    min_quantity: Optional[str] = None
    max_quantity: Optional[str] = None
    curve_id: Optional[str] = None
    row: Optional[str] = None


class TankSales(BaseModel):
    store_number: str
    tank_id: str
    date: str  # ISO Datetime
    sales: float


class UniqueTank(BaseModel):
    store: str
    tank_id: str
    monitor_type: TankMonitorType


