import os
from datetime import datetime, date
from enum import Enum, StrEnum
from io import BytesIO
from typing import Any, Optional, List, Literal, Union
from typing import Self
import re
import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, constr, field_validator, PrivateAttr, \
    model_validator, field_serializer, Field

from bb_integrations_lib.models.rita.audit import ProcessReportBase
from bb_integrations_lib.models.rita.config import FileConfig

from bb_integrations_lib.shared.shared_enums import TimezoneEnum, PriceType, timezone_to_canonical_name

class MappingMode(str, Enum):
    full = "full",  # Every row must be mapped. If a row doesn't have a mapping, it will not be uploaded.
    partial = "partial",  # Use a mapping if available, but otherwise use the raw value from the file.
    skip = "skip"  # No row is expected to have a map. Mappings will not be used.



class ConfigMode(Enum):
    """Configuration loading modes for SFTP file processing.

    Determines how file configurations are loaded from RITA:
    - FromBucket: Load all fileconfigs from a specific bucket
    - ByName: Load a single fileconfig by bucket and name
    - AllFiltered: Load all configs and filter by names
    """
    FromBucket = "FromBucket"
    """Load all of the fileconfigs in a given RITA bucket specified by the `bucket_name` parameter."""
    ByName = "ByName"
    """Load the single file config specified by the `bucket_name` and `config_name` parameters."""
    AllFiltered = "AllFiltered"
    """Load all configs and filter down by their names. This setting ignores buckets and pulls the names from the
    `config_names` step parameters."""


class ConfigMatchMode(Enum):
    """File matching modes for SFTP file processing.

    Determines how files are matched against configuration patterns:
    - Exact: File name must exactly match the pattern
    - Partial: File name must contain the pattern as a substring
    - ByExtension: File extension must match the configured extension
    """
    Exact = "Exact"
    """File name must exactly match"""
    Partial = "Partial"
    """File Name must partially match"""
    ByExtension = "ByExtension"
    """File extension must match provided extension"""


class RawData(BaseModel):
    file_name: str
    data: Any
    empty_ok: bool = False

    @property
    def is_empty(self) -> bool:
        if self.data is None:
            return True
        if isinstance(self.data, (str, bytes)):
            return len(self.data) == 0
        if isinstance(self.data, pd.DataFrame):
            return self.data.empty
        if hasattr(self.data, '__len__'):
            return len(self.data) == 0
        return False


class FileConfigRawData(RawData):
    data_buffer_bkp: Any = None
    file_config: FileConfig


class FileType(str, Enum):
    excel = "excel"
    csv = "csv"


class FileReference:
    """A reference to a file object on the filesystem for use in the bb_integrations_lib.storage API"""

    # TODO: See if this can be rolled into RawData
    def __init__(self, file_path: str, file_type: FileType, sheet_name: str = None):
        self.file_path = file_path
        self.file_type = file_type
        self.sheet_name = sheet_name

    def get_filename(self):
        return os.path.basename(self.file_path)

    @property
    def is_empty(self) -> bool:
        if not os.path.exists(self.file_path):
            return True
        return os.path.getsize(self.file_path) == 0


class CredentialType(str, Enum):
    """
    Enumeration of credential file types for different integrations.

    Attributes:
        ftp (str): Credential file for FTP connections.
        aws (str): Credential file for AWS connections.
        google (str): Credential file for Google integrations.
    """
    ftp = 'ftp.credentials'
    aws = 'aws.credentials'
    google = 'google.credentials'
    imap = 'imap.credentials'


class File(BaseModel):
    """
    Model representing a file with data and metadata.

    Attributes:
        file_name (str | None): Name of the file, without extension.
        file_data (str | dict): The file content as a string or dictionary.
        content_type (str): MIME type of the file. Defaults to empty string.
        is_public (bool): Whether the file should be publicly accessible. Defaults to False.
        file_extension (str): File extension. Defaults to 'csv'.
        check_if_exists (bool): Whether to check for file existence before uploading. Defaults to True.
    """
    file_name: str | None = None
    file_data: Any
    content_type: str = ''
    is_public: bool = False
    file_extension: str = 'csv'
    check_if_exists: bool = True

    class Config:
        arbitrary_types_allowed = True
        ser_json_bytes = "base64"
        val_json_bytes = "base64"

    @classmethod
    def to_bytes(cls, data: Any) -> BytesIO:
        """
        Convert data to a `BytesIO` object for binary file upload.

        Args:
            data (Any): The data to be converted. Supports `DataFrame`, `str`, or `bytes`.

        Returns:
            io.BytesIO: A `BytesIO` object containing the file data in binary format.

        Raises:
            ValueError: If data is of an unsupported type.
        """
        if isinstance(data, BytesIO):
            return data
        elif isinstance(data, DataFrame):
            csv_data = data.to_csv(index=False).encode('utf-8')
            return BytesIO(csv_data)
        elif isinstance(data, str):
            return BytesIO(data.encode('utf-8'))
        elif isinstance(data, bytes):
            return BytesIO(data)
        else:
            raise ValueError("Unsupported data type for conversion to bytes.")


class FileUpload(BaseModel):
    """
    Model representing the result of a file upload operation.

    Attributes:
        message (str): Status or response message from the upload.
        bucket (Optional[str]): The storage bucket where the file was uploaded.
        blob_path (Optional[str]): Path within the bucket or storage where the file is stored.
        file_name (str): Name of the uploaded file.
        file_path (str): Full path of the file on the server.
        file_size (Optional[int]): Size of the file in bytes, if available.
        content_type (str): MIME type of the uploaded file.
        public_url (Optional[str]): URL for public access to the file, if applicable.
    """
    message: str
    bucket: Optional[str] = None
    blob_path: Optional[str] = None
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    content_type: str
    public_url: Optional[str] = None


class OrderType(str, Enum):
    regular = "regular"
    backhaul = "backhaul"


class OrderStateGetBolsDrops(str, Enum):
    canceled = "canceled"
    deleted = "deleted"
    open = "open"
    recommended = "recommended"
    accepted = "accepted"
    assigned = "assigned"
    in_progress = "in_progress"
    complete = "complete"


class GetOrderBolsAndDropsRequest(BaseModel):
    order_date_start: Optional[datetime] = None
    order_date_end: Optional[datetime] = None
    movement_updated_start: Optional[datetime] = None
    movement_updated_end: Optional[datetime] = None
    order_ids: Optional[List[str]] = None
    order_numbers: Optional[List[int]] = None
    order_states: Optional[List[OrderStateGetBolsDrops]] = None
    order_type: Optional[OrderType] = None
    include_invalid: Optional[bool] = False
    include_bol_allocation: Optional[bool] = True

class DateWindow(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

class GetFreightInvoicesRequest(BaseModel):
    book_type: Literal["Revenue", "Cost"] | None = None
    order_numbers: list[int] | None = None
    order_ids: list[str] | None = None
    invoice_numbers: list[str] | None = None
    status: Literal["open", "sent", "blocked", "hold"] | None = None
    counterparty_name: str | None = None
    counterparty_id: str | None = None
    as_of: datetime | None = None
    between: DateWindow | None = None
    exported: bool | None = None


class CreateProcess(ProcessReportBase):
    trigger: str


class SourceModel(BaseModel):
    id: str | None = None
    source_id: str | None = None
    source_system_id: str | None = None

    def source_request(self):
        if self.source_id and self.source_system_id:
            return {
                "source_id": self.source_id,
                "source_system_id": self.source_system_id,
            }


class DisabledReason(str, Enum):
    terminal_maintenance = "Terminal Maintenance"
    terminal_outage = "Terminal Outage"
    supplier_out = "Supplier Out"
    met_allocation_limit = "Met Allocation Limit"
    contract_utilization = "Contract Utilization"

    @classmethod
    def string_of_values(cls):
        return ",".join([v.value for v in cls.__members__.values()])

    @classmethod
    def list_of_values(cls):
        return [v.value for v in cls.__members__.values()]


class PriceRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    modify: Literal["Ignore", "Update"] = "Ignore"
    terminal: str | None = None
    product: str
    supplier: str
    counterparty: str | None = None
    site: str | None = None
    price: float
    price_type: PriceType
    contract: str | None = ""
    timezone: TimezoneEnum | None = None
    effective_from: datetime
    effective_to: datetime
    disabled: bool | None = False
    disabled_reason: DisabledReason | None = None
    disabled_until: datetime | None = None
    _row_number: int | None = PrivateAttr(None)

    @field_validator("price", mode="before")
    def to_float(cls, v):
        return float(v) if v is not None else None

    def __init__(self, **data):
        super().__init__(**data)
        self._row_number = int(data["_row_number"]) if "_row_number" in data else None

    @property
    def primary_keys(self) -> dict:
        """Primary Key fields used for detecting duplicate entries"""
        return {
            "terminal": self.terminal,
            "product": self.product,
            "supplier": self.supplier,
            "site": self.site,
            "counterparty": self.counterparty,
            "contract": self.contract,
        }

    def __hash__(self):
        return hash(tuple(self.primary_keys.values()))

    def __eq__(self, other):
        if isinstance(other, PriceRow):
            return self.__hash__() == other.__hash__()
        return super().__eq__(other)


class SupplyPriceUpdateResponse(BaseModel):
    contract: str | None = None

    timezone: TimezoneEnum | None = None
    effective_from: datetime
    effective_to: datetime
    price: float
    price_type: PriceType

    terminal_id: constr(min_length=24, max_length=24) | None = None
    terminal_source_id: str | None = None
    terminal_source_system_id: str | None = None
    terminal: str | None = None

    product_id: constr(min_length=24, max_length=24) | None = None
    product_source_id: str | None = None
    product_source_system_id: str | None = None
    product: str | None = None

    supplier_id: constr(min_length=24, max_length=24) | None = None
    supplier_source_id: str | None = None
    supplier_source_system_id: str | None = None
    supplier: str | None = None

    counterparty_id: constr(min_length=24, max_length=24) | None = None
    counterparty_source_id: str | None = None
    counterparty_source_system_id: str | None = None
    counterparty: str | None = None

    enabled: bool = True
    disabled_until: datetime | None = None
    min_quantity: int | None = None
    max_quantity: int | None = None
    curve_id: str | None = None
    error: str | None = None
    row: int | None = None

    source_id: str | None = None
    source_system_id: str | None = None

    @field_validator("timezone")
    def validate_timezone(cls, v):
        return timezone_to_canonical_name(v)

    @property
    def identifier(self):
        return (
            self.effective_from,
            self.effective_to,
            self.product_id,
            self.supplier_id,
            self.terminal_id,
            self.counterparty_id,
            self.contract,
            self.price_type,
        )


class SupplyPriceUpdateManyRequest(SourceModel):
    model_config = ConfigDict(from_attributes=True)

    contract: str | None = None

    timezone: TimezoneEnum | None = None
    effective_from: datetime
    effective_to: datetime
    price: float
    price_type: PriceType

    terminal_id: constr(min_length=24, max_length=24) | None = None
    terminal_source_id: str | None = None
    terminal_source_system_id: str | None = None
    terminal: str | None = None

    product_id: constr(min_length=24, max_length=24) | None = None
    product_source_id: str | None = None
    product_source_system_id: str | None = None
    product: str | None = None

    supplier_id: constr(min_length=24, max_length=24) | None = None
    supplier_source_id: str | None = None
    supplier_source_system_id: str | None = None
    supplier: str | None = None

    counterparty_id: constr(min_length=24, max_length=24) | None = None
    counterparty_source_id: str | None = None
    counterparty_source_system_id: str | None = None
    counterparty: str | None = None

    store_id: constr(min_length=24, max_length=24) | None = None
    store_source_id: str | None = None
    store_source_system_id: str | None = None
    store_number: str | None = None

    enabled: bool = True
    disabled_until: datetime | None = None
    expire: datetime | None = None
    min_quantity: int | None = None
    max_quantity: int | None = None
    curve_id: str | None = None
    error: str | None = None
    row: int | None = None
    price_publisher: str | None = None

    @field_validator("min_quantity", "max_quantity", mode="before")
    def quantity_val(cls, v):
        return v if v else None

    @field_validator("curve_id", mode="before")
    def convert_to_string(cls, v):
        if v is None:
            return v
        return str(v)

    @field_validator("supplier_source_id", "product_source_id",
                     "store_source_id", "counterparty_source_id",
                     "terminal_source_id",
                     mode="before")
    def validate_source_ids(cls, v):
        if isinstance(v, int):
            return str(v)
        return v


    @field_validator("timezone")
    def validate_timezone(cls, v):
        return timezone_to_canonical_name(v)

    @classmethod
    def from_price_row(cls, row: PriceRow):
        ret = cls.model_validate(row)
        ret.store_number = row.site
        return ret

    @property
    def extra_data(self):
        return {"source_id": self.source_id, "source_system_id": self.source_system_id}


class PriceUpdateResponse(BaseModel):
    created: int = 0
    end_dated: int = 0
    bad_data: list[SupplyPriceUpdateResponse]
    duplicates: list[SupplyPriceUpdateResponse]
    exact_match: list[SupplyPriceUpdateResponse]


class SDDirectivePriceType(str, Enum):
    rack = "rack"
    contract = "contract"
    index = "index"
    inventory = "inventory"
    spot = "spot"


class SDDirectiveVolumeDist(BaseModel):
    market: str
    percent: float


class SDDirectiveContractVolume(BaseModel):
    applicable_date: date
    volume: float


class SDDirectiveKey(BaseModel):
    """A key definition for a directive."""
    contract: str | None = None
    price_type: SDDirectivePriceType
    product_source_id: str | None = None
    product_source_system: str | None = None
    product: str | None = None
    supplier_source_id: str | None = None
    supplier_source_system: str | None = None
    supplier: str | None = None
    terminal_source_id: str | None = None
    terminal_source_system: str | None = None
    terminal: str | None = None

    @model_validator(mode="after")
    def check_ids(self) -> Self:
        if not self.product and (not self.product_source_id or not self.product_source_system):
            raise ValueError("Supply only one of product or (product_source_id, product_source_system)")
        if self.product and self.product_source_id and self.product_source_system:
            raise ValueError("Supply only one of product or (product_source_id, product_source_system)")
        if not self.supplier and (not self.supplier_source_id or not self.supplier_source_system):
            raise ValueError("Supply only one of supplier or (supplier_source_id, supplier_source_system)")
        if self.supplier and self.supplier_source_id and self.supplier_source_system:
            raise ValueError("Supply only one of supplier or (supplier_source_id, supplier_source_system)")
        if not self.terminal and (not self.terminal_source_id or not self.terminal_source_system):
            raise ValueError("Supply only one of terminal or (terminal_source_id, terminal_source_system)")
        if self.terminal and self.terminal_source_id and self.terminal_source_system:
            raise ValueError("Supply only one of terminal or (terminal_source_id, terminal_source_system)")
        return self


class SDDirective(BaseModel):
    """Required info to create a directive in S&D"""
    source_id: str | None = None
    name: str
    keys: List[SDDirectiveKey]
    as_of: datetime
    min: float | None = None
    max: float | None = None
    volume_distributions: List[SDDirectiveVolumeDist] = []
    contract_volumes: List[SDDirectiveContractVolume] = []
    daily_percent: float | None = None
    weekly_percent: float | None = None
    monthly_percent: float | None = None
    week_start_day: str | None = None


class SDDirectiveUpdate(BaseModel):
    curve_id: str
    daily_percent: float | None
    weekly_percent: float | None
    monthly_percent: float | None
    contract_volumes: List[SDDirectiveContractVolume] = []

class SDSupplierInvoiceDetailType(StrEnum):
    tax = "tax"
    supply = "supply"


class SDSupplierInvoiceDetail(BaseModel):
    bol_number: str | None = None
    bol_date: datetime | None = Field(
        default=None, description="BOL date (UTC). Use bol_date_local if the tz is assumed to be terminal-local.")
    bol_date_local: datetime | None = Field(
        default=None, description="BOL date (local). Use bol_date if the tz is concretely known.")
    type: SDSupplierInvoiceDetailType
    product: dict[str, str] | None = None
    tax_type: str | None = None
    tax_description: str | None = None
    tax_authority: str | None = None
    tax_non_deferred: bool | None = None
    rate: float | None = None
    amount: float | None = None
    total: float
    uom: str | None = None
    gross_volume: float | None = None
    net_volume: float | None = None

class SDSupplierReconciliationInvoiceStatus(str, Enum):
    approved = "approved"
    unapproved = "unapproved"
    unmatched = "unmatched"
    void = "void"
    hold = "void"

class SDDeliveryReconciliationMatchStatus(str, Enum):
    approved = "approved"
    matched = "matched"
    unmatched = "unmatched" # only measures not orders ( WR Volumes)
    voided = "voided"

class ERPStatus(str, Enum):
    sent = "sent"
    pending = "pending"
    errors = "errors"
    staged = "staged"

class SDGetUnexportedOrdersRequest(BaseModel):
    as_of: str | datetime | None = None

    @field_validator('as_of', mode="before")
    def convert_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

class SDGetUnexportedOrdersResponse(BaseModel):
    order_id: str
    order_number: str | int
    completed_date: datetime | None = None
    export_status: ERPStatus
    error_message: str | None = None


class SDSetOrderExportStatusRequest(BaseModel):
    order_id: str
    status: ERPStatus
    error: str | None = None

class SDGetAllSupplierReconciliationInvoiceRequest(BaseModel):
    status: SDSupplierReconciliationInvoiceStatus | None = None
    due_date_start: datetime | None = None
    due_date_end: datetime | None = None
    last_change_date: datetime | None = None
    suppliers: list[str] | None = None
    invoice_numbers: list[str] | None = None
    include_exported: bool | None = None

class SDDeliveryReconciliationMatchOverviewRequest(BaseModel):
    status: SDDeliveryReconciliationMatchStatus | None = None
    store_id: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


class SDSupplierInvoiceCreateRequest(BaseModel):
    invoice_number: str
    source_name: str
    supplier: str
    terminal: str | None = None
    due_date_utc: datetime | None = Field(
        default=None,
        description="Invoice due date (UTC). Use due_date_local if the tz is assumed to be terminal-local."
    )
    due_date_local: datetime | None = Field(
        default=None, description="Invoice due date (local). Use due_date_utc if the tz is concretely known.")
    invoice_date: datetime | None = Field(
        default=None,
        description="Date of invoice (UTC). Use invoice_date_local if the tz is assumed to be terminal-local."
    )
    invoice_date_local: datetime | None = Field(
        default=None, description="Date of invoice (local). Use invoice_date if the tz is concretely known.")
    details: list[SDSupplierInvoiceDetail]
    extra_data: Optional[dict] = Field(default_factory=dict)
    ship_to_city: str | None = None
    ship_to_state: str | None = None
    ship_from_city: str | None = None
    ship_from_state: str | None = None

    @field_serializer("supplier")
    def serialize_supplier(self, supplier: str):
        return {
            "source_name": supplier
        }

    @field_serializer("terminal")
    def serialize_terminal(self, terminal: str | None):
        if not terminal:
            return None
        return {
            "source_name": terminal
        }


class CurvePointPrice(BaseModel):
    CurvePointPriceId: Optional[int] = None
    FormulaMarkerId: Optional[int] = None
    FormulaResult: Optional[Union[float, str]] = None
    FormulaResultId: Optional[int] = None
    PriceTypeMeaning: Optional[str] = None
    SourceId: Optional[Union[int, str]] = None
    Value: Optional[float] = None


class PEPriceData(BaseModel):
    CostSourceTypeMeaning: Optional[str] = None
    CounterParty: Optional[str] = None
    CounterPartyId: Optional[int] = None
    CounterPartySourceId: Optional[Union[int, str]] = None
    CounterPartySourceIdString: Optional[str] = None
    CredentialUsername: Optional[str] = None
    Currency: Optional[str] = None
    CurrencyId: Optional[int] = None
    CurrencySourceId: Optional[Union[int, str]] = None
    CurvePointId: Optional[int] = None
    CurvePointPrices: Optional[List[CurvePointPrice]] = None
    CurvePointTypeMeaning: Optional[str] = None
    EffectiveFromDateTime: Optional[Union[datetime, str]] = None
    EffectiveToDateTime: Optional[Union[datetime, str]] = None
    EstimateActual: Optional[str] = None
    ExchangeSymbol: Optional[str] = None
    IsActive: Optional[bool] = None
    Location: Optional[str] = None
    LocationId: Optional[int] = None
    LocationSourceId: Optional[Union[int, str]] = None
    LocationSourceIdString: Optional[str] = None
    NetOrGrossMeaning: Optional[str] = None
    PriceInstrument: Optional[str] = None
    PriceInstrumentId: Optional[int] = None
    PriceInstrumentSourceId: Optional[Union[int, str]] = None
    PricePublisher: Optional[str] = None
    PricePublisherId: Optional[int] = None
    Product: Optional[str] = None
    ProductId: Optional[int] = None
    ProductSourceId: Optional[Union[int, str]] = None
    ProductSourceIdString: Optional[str] = None
    QuoteConfigurationId: Optional[int] = None
    SourceContractDetailId: Optional[int] = None
    SourceContractId: Optional[int] = None
    SourceContractValuationPriceInstrumentId: Optional[int] = None
    SourceId: Optional[Union[int, str]] = None
    SourceInternalContractNumber: Optional[str] = None
    TradePeriodFromDateTime: Optional[Union[datetime, str]] = None
    TradePeriodToDateTime: Optional[Union[datetime, str]] = None
    UnitOfMeasure: Optional[str] = None
    UnitOfMeasureId: Optional[int] = None
    UpdatedDateTime: Optional[Union[datetime, str]] = None
    ExtendByDays: Optional[int] = None
    Rank: Optional[int] = None
    PriceType: Optional[str] = None
    IsLatest: Optional[bool] = False


class SQLClientParams(BaseModel):
    server: str
    database: str
    username: str
    password: str
    echo: Optional[bool] = False


class RITAClientParams(BaseModel):
    base_url: str
    client_id: str
    client_secret: str
    rita_tenant: str
    system_name: Optional[str] = "RITA"

class ReadingQuery(BaseModel):
    by_store_numbers: Optional[list[str]] = None
    by_tank_ids: Optional[list[int]] = None
    by_market: Optional[list[str]] = None
    by_counterparty: Optional[list[str]] = None
    by_wildcard: Optional[str] = None

    def as_mask(self, original: pd.DataFrame) -> pd.Series:
        final_filt = pd.Series(data=True, index=original.index)
        if self.by_store_numbers:
            composite_stores = [s for s in self.by_store_numbers if ":" in s]
            simple_stores = [s for s in self.by_store_numbers if ":" not in s]
            store_mask = pd.Series(data=False, index=original.index)
            if composite_stores:
                store_mask |= original["composite_key"].str.contains(
                    "|".join(re.escape(s) for s in composite_stores), regex=True)
            if simple_stores:
                store_mask |= original["store_number"].isin(simple_stores)
            final_filt &= store_mask
        if self.by_tank_ids:
            final_filt &= original["tank_id"].isin(self.by_tank_ids)
        if self.by_market:
            final_filt &= original["market"].isin(self.by_market)
        if self.by_counterparty:
            final_filt &= original["counterparty_name"].isin(self.by_counterparty)
        return final_filt


class FileFormat(str, Enum):
    """
    File format options for tank reading output files.

    This enum defines the available output formats for parsed tank readings data.
    Each format produces a different structure and field set tailored to specific
    client requirements or integration systems.

    Attributes:
        standard (str): PDI-compatible format with the following field structure:
            - Store Number: Store identifier from the source system
            - Name: Store name from lookup data
            - Tank Id: Tank identifier within the store
            - Tank Product: Product type stored in the tank
            - Carrier: Carrier information from tank lookup
            - Volume: Current volume measurement in the tank
            - Ullage: Unfilled space (storage_max - volume)
            - Read Time: Timestamp in "YYYY-MM-DD HH:MM:SS TZ±HHMM" format
            - Disconnected (optional): Boolean indicating if tank hasn't reported
              within the configured threshold
            Supports filtering to disconnected tanks only via configuration.

        circlek (str): Circle K specific format with TelaPoint integration structure:
            - ClientName: Client identifier (set to None)
            - FacilityName: Facility name (set to None)
            - FacilityInternalID: Internal facility ID (set to None)
            - FacilityState: State location (set to None)
            - VolumePercentage: Volume as percentage (set to None)
            - TankStatus: Current tank status (set to None)
            - TankNbr: Tank number (set to None)
            - TankInternalID: Internal tank ID (set to None)
            - AtgTankNumber: ATG tank number (mapped from Tank Id)
            - ATGTankLabel: ATG tank label (set to None)
            - Product: Product information (set to None)
            - TankCapacity: Maximum tank capacity (set to None)
            - Ullage: Unfilled space (set to None)
            - SafeUllage: Safe ullage level (set to None)
            - Volume: Current volume measurement
            - Height: Tank height measurement (set to None)
            - Water: Water level measurement (set to None)
            - Temperature: Temperature measurement (set to None)
            - InventoryDate: Formatted timestamp as "MM/DD/YYYY HH:MM"
            - SystemUnits: Unit system (set to None)
            - CollectionDateTimeUtc: UTC collection time (set to None)
            - TelaPointAccountNumber: Fixed value of 100814
            - TelaPointSiteNumber: Store number from source data

        circlek2 (str): Simplified Circle K format for Gravitate system integration:
            - storeNumber: Store number as it appears in Gravitate
            - timestamp: Timestamp when the volume was read
            - tankLabel: Product name assigned to the tank
            - volume: Volume of tank at the time of reading
            - tankNumber: Tank ID as it appears in Gravitate
            - ullage: Unfilled space within the tank
            - productLevel: Product level measurement (can be set to 0)
            - waterLevel: Water level measurement (can be set to 0)
            - temperature: Temperature measurement (can be set to 0)

    Example:
        >>> format_type = FileFormat.standard
        >>> step_config = {"format": FileFormat.circlek2, ...}
    """

    standard = "standard"
    circlek = "circlek"
    circlek2 = "circlek2"
    reduced = "reduced"

class ExportReadingsWindowMode(StrEnum):
    HOURS_BACK = "hours_back"
    LATEST_ONLY = "latest_only"
    PREVIOUS_DAY = "previous_day"

class ExportReadingsConfig(BaseModel):
    """Configuration for exporting tank readings to external systems.
    
    This model defines how tank readings should be queried, formatted, and delivered
    to external recipients via FTP or email. It supports various file formats and
    filtering options for different client requirements.
    
    Attributes:
        reading_query (ReadingQuery): Query filters for selecting which readings to export
        window_mode (ExportReadingsWindowMode): One of 3 modes that chooses what sort of date filtering to perform on
          tank readings: ``hours_back`` will filter to readings within the last X hours as of job run time.
          ``latest_only`` will get readings within ``hours_back`` and keep only the latest one for each tank (tanks with
          only older readings will not appear in the result set). ``previous_day`` will filter to readings within the
          previous day as of job run time, from midnight to midnight.
        reading_reported_timezone (str): Timezone for reading timestamps
        hours_back (int): How many hours back to look for readings
        file_base_name (str): Base filename for the exported file
        file_name_date_format (str): Date format string for filename timestamps
        ftp_directory (str): Target directory on FTP server (if using FTP delivery)
        file_format (FileFormat): Output format (standard, circlek, circlek2)
        email_addresses (list[str]): Email recipients (if using email delivery)
        include_water_level (bool): Whether to include water level measurements
        disconnected_column (bool): Whether to include disconnected tank status
        disconnected_only (bool): Whether to export only disconnected tanks
        disconnected_hours_threshold (float): Hours threshold for considering tanks disconnected
        ftp_credentials (str): FTP credentials identifier for delivery
    """
    config_names: list[str]
    reading_query: ReadingQuery
    window_mode: ExportReadingsWindowMode
    reading_reported_timezone: str
    hours_back: int = 1
    file_base_name: str
    sd_credentials: str
    ims_credentials: str
    file_name_date_format: Optional[str] = "%Y%m%d%H%M%S"
    ftp_directory: Optional[str] = None
    file_format: FileFormat = FileFormat.standard
    email_addresses: Optional[list[str]] = None
    include_water_level: bool = False
    disconnected_column: bool = False
    disconnected_only: bool = False
    disconnected_hours_threshold: Optional[float] = None
    ftp_credentials: Optional[str] = None
    use_polars: bool = False

class ExportReadingsMultiConfig(BaseModel):
    configs: list[ExportReadingsConfig]

class DistributionReportConfig(BaseModel):
    """Configuration for generating and distributing contract rack utilization reports.
    
    This model defines how distribution reports should be generated from Gravitate data,
    formatted, and delivered to external recipients via FTP or email. It handles the
    processing of contract rack utilization data with both detailed and summary views.
    
    Attributes:
        file_base_name (str): Base filename for the generated report files
        google_project_id (str): Google Cloud Project ID containing the BigQuery datasets
        gbq_table_details (str): BigQuery table path for detailed contract rack utilization data.
            Contains product-level details for each contract and rack combination
        gbq_table_summary (str): BigQuery table path for summarized contract rack utilization data.
            Contains aggregated metrics without product-level breakdown
        file_name_date_format (str): Date format string for timestamp suffixes in filenames
        ftp_directory (str): Target directory on FTP server (if using FTP delivery)
        email_addresses (list[str]): Email recipients (if using email delivery)
    """
    file_base_name: str
    google_project_id: str
    n_hours_back: int | None = None
    include_model_mode: str | None = "latest_only"
    order_state : str | None = "accepted"
    days_back: int | None = None
    days_forward: int | None = None
    gbq_table_details: Optional[str] = "bb_reporting.contract_rack_util_product_detail"
    gbq_table_summary: Optional[str] = "bb_reporting.contract_rack_util"
    file_name_date_format: Optional[str] = "%Y%m%d%H%M%S"
    ftp_directory: Optional[str] = None
    email_addresses: Optional[list[str]] = None

    @property
    def start_date(self) -> datetime:
        if self.days_back is not None:
            return datetime.now() - datetime.timedelta(days=self.days_back)
        else:
            return datetime.now()

    @property
    def end_date(self) -> datetime:
        if self.days_forward is not None:
            return datetime.now() + datetime.timedelta(days=self.days_forward)
        else:
            return datetime.now()

class ATGConfig(BaseModel):
    """Configuration for a specific vendor's tank reading import.
    
    This model defines how to import tank readings from a specific vendor through
    SFTP or email delivery. It includes file matching settings, processing options,
    and post-processing actions like archiving or deletion.
    
    Attributes:
        config_names (List[str]): List of file configuration names to process
        archive_gcs_bucket_path (str): GCS bucket path for archiving processed files
        gcs_credentials (str): GCS credentials identifier for bucket access
        ftp_credentials (str): FTP credentials identifier for file retrieval
        to_email_address (str): Email address of inbox for email attachment-based delivery.
        from_email_address (str): Email address of sender, if desired, for email attachment-based delivery.
        delivered_to_email_address (str): Used for certain forwarding setups where the from/to might not be our own
          mailbox.
        config_mode (ConfigMode): How to load file configurations (AllFiltered, FromBucket, ByName)
        file_match_type (ConfigMatchMode): How to match files (Exact, Partial, ByExtension)
        mapping_type (MappingMode): Mapping mode to use during parsing
        archive_files (bool): Whether to archive files after processing
        delete_files (bool): Whether to delete files after processing (mutually exclusive with archive_files)
        minutes_back (int): How many minutes back to look for files
        timezone (str): Timezone for date filtering operations
        
    Note: archive_files and delete_files are mutually exclusive.
    """
    config_names: List[str]
    archive_gcs_bucket_path: Optional[str] = None
    sd_credentials: str = None
    gcs_credentials: Optional[str] = None
    ftp_credentials: Optional[str] = None
    email_credentials: Optional[str] = None
    to_email_address: Optional[str] = None
    from_email_address: Optional[str] = None
    delivered_to_email_address: Optional[str] = None
    attachment_extension: Optional[str] = None
    email_subject: Optional[str] = None
    config_mode: ConfigMode = ConfigMode.AllFiltered
    file_match_type: ConfigMatchMode = ConfigMatchMode.Partial
    mapping_type: MappingMode = MappingMode.full
    archive_files: bool = False
    delete_files: bool = False
    minutes_back: Optional[int] = None
    timezone: Optional[str] = None


    @field_validator('delete_files')
    @classmethod
    def validate_mutually_exclusive(cls, v, info):
        if v and info.data.get('archive_files', False):
            raise ValueError("Cannot have both archive_files and delete_files set to True")
        return v

    @property
    def mode(self):
        return "ftp" if self.ftp_credentials else "email"


class ImportTankReadings(BaseModel):
    """Container for multiple vendor configurations for tank reading imports.
    
    This model serves as a wrapper for multiple VendorConfig objects, enabling
    batch processing of tank readings from different vendors in a single pipeline
    execution. Each vendor can have different file sources, processing rules,
    and post-processing actions.
    
    Attributes:
        configs (List[VendorConfig]): List of vendor-specific import configurations
            Each config defines how to import and process tank readings from that vendor
        sd_env_mode (str): Whether to target the "production" or "test" S&D environment.
    """
    configs: List[ATGConfig]


class AgGridBaseModel(BaseModel):
    """Base class for AgGrid models."""

    @classmethod
    def default_column_defs(cls, hidden_columns: list[str] = None, only_include_columns: list[str] = None):
        columns = []
        if hidden_columns is None:
            hidden_columns = []
        for field_name, field_info in cls.model_fields.items():
            display_name = field_name.replace('_', ' ').title()
            is_hidden = False
            if only_include_columns is not None:
                is_hidden = field_name not in only_include_columns
            else:
                is_hidden = field_name in hidden_columns
            column_def = {
                'field': field_name,
                'headerName': display_name,
                'isHidden': is_hidden,
            }
            if (hasattr(field_info.annotation, '__mro__') and
                    BaseModel in field_info.annotation.__mro__ and
                    hasattr(field_info.annotation, 'default_column_defs')):
                column_def.update({
                    'type': 'object',
                    'children': field_info.annotation.default_column_defs(),
                })
            else:
                python_type = str(field_info.annotation).lower()
                if 'int' in python_type or 'float' in python_type:
                    cell_type = 'number'
                elif 'bool' in python_type:
                    cell_type = 'boolean'
                elif 'date' in python_type:
                    cell_type = 'date'
                elif 'list' in python_type or 'dict' in python_type:
                    cell_type = 'object'
                else:
                    cell_type = 'text'
                column_def['type'] = cell_type
            columns.append(column_def)
        return columns