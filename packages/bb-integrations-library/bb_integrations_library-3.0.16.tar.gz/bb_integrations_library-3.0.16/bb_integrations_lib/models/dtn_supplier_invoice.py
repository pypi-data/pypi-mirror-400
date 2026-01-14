import csv
from abc import abstractmethod, ABC
from datetime import datetime, date
from enum import StrEnum
from typing import Union, Optional, TextIO, Literal, Any, Generator

from pydantic import BaseModel, Field, conlist


class RecordType(StrEnum):
    """Possible types of rows in DTN supplier invoice CSVs."""
    HEADER = "BEGIN"
    ITEM = "ITM"
    RINS = "ITMRIN"
    TAX = "ITMTAX"
    SUMMARY_TAX = "SUMTAX"
    DEFERRED_TAX = "DEFTAX"
    FOOTER = "END"


class ParsableRow(ABC):
    """Abstract class for parsable DTN CSV rows, additionally providing some common helper functions."""

    @staticmethod
    def _try_parse_date(date: str, format: str) -> date | None:
        if date is None:
            return None
        try:
            return datetime.strptime(date, format).date()
        except ValueError:
            return None

    @staticmethod
    def _try_parse_datetime(date: str, format: str) -> datetime | None:
        try:
            return datetime.strptime(date, format)
        except ValueError:
            return None

    @staticmethod
    def _optional_float(val: str) -> float | None:
        return None if not val else float(val)

    @staticmethod
    def _pad_row(row: list, to: int) -> list:
        row_copy = list(row)
        if len(row_copy) < to:
            row_copy.extend([None] * (to - len(row_copy)))
        return row_copy

    @staticmethod
    def _parse_bool(val: str) -> bool:
        match val:
            case "Y":
                return True
            case "N":
                return False
            case _:
                raise ValueError(f"Failed to parse boolean field: {val} is not Y or N")

    @classmethod
    @abstractmethod
    def parse(cls, row: list[str]):
        pass


class Header(ParsableRow, BaseModel):
    """
    Header row. Contains summary data for the invoice.
    Only 1 allowed, per the file format specification (though we don't enforce this).
    """
    record_type: RecordType = RecordType.HEADER
    dtn_transaction_number: str
    dtn_version_number: str
    transmission_datetime: datetime
    invoice_number: str
    invoice_date: date
    document_type: str
    seller_name: str
    sold_to_name: str
    sold_to_cust_no: Optional[str] = None
    purchase_order_no: Optional[str] = None
    terms_description: str
    document_grand_total: float
    invoice_due_date: Optional[date] = None
    total_invoice_amount: float
    discount_due_date: Optional[date] = None
    discount: float
    discount_amount: float
    sender_id: str

    @classmethod
    def parse(cls, row: list[str]) -> "Header":
        row = cls._pad_row(row, 20)
        common_date_fmt = "%Y%m%d"
        trans_datetime_str = row[3] + "T" + row[4]
        trans_datetime = datetime.strptime(trans_datetime_str, "%Y%m%dT%H%M")

        return cls(
            dtn_transaction_number=row[1],
            dtn_version_number=row[2],
            transmission_datetime=trans_datetime,
            invoice_number=row[5],
            invoice_date=cls._try_parse_date(row[6], common_date_fmt),
            document_type=row[7],
            seller_name=row[8],
            sold_to_name=row[9],
            sold_to_cust_no=row[10],
            purchase_order_no=row[11],
            terms_description=row[12],
            document_grand_total=float(row[13]),
            invoice_due_date=cls._try_parse_date(row[14], common_date_fmt),
            total_invoice_amount=cls._optional_float(row[15]),
            discount_due_date=cls._try_parse_date(row[16], common_date_fmt),
            discount=cls._optional_float(row[17]),
            discount_amount=cls._optional_float(row[18]),
            sender_id=row[19],
        )


class BilledQuantityIndicator(StrEnum):
    NET = "N"
    GROSS = "G"
    UNKNOWN = "U"


class Item(ParsableRow, BaseModel):
    """Inventory item data row."""
    record_type: RecordType = RecordType.ITEM
    invoice_number: str
    bol_number: Optional[str] = None
    description: str
    dtn_product_code: Optional[str] = None
    supplier_product_code: Optional[str] = None
    quantity_billed: float
    billed_quantity_indicator: BilledQuantityIndicator
    gross_quantity: Optional[float] = None
    net_quantity: Optional[float] = None
    unit_of_measure: str
    rate: Optional[float] = None
    line_total: float
    ship_datetime: Optional[datetime] = None
    ship_from_name: str
    ship_from_address: Optional[str] = None
    ship_from_address_2: Optional[str] = None
    ship_from_city: Optional[str] = None
    ship_from_state: Optional[str] = None
    ship_from_zip: Optional[str] = None
    dtn_splc: Optional[str] = None
    ship_to_number: Optional[str] = None
    ship_to_address: Optional[str] = None
    ship_to_address_2: Optional[str] = None
    ship_to_city: Optional[str] = None
    ship_to_state: Optional[str] = None
    ship_to_zip: Optional[str] = None
    carrier_description: Optional[str] = None
    carrier_fein_number: Optional[str] = None
    original_invoice_number: Optional[str] = None
    contract_number: Optional[str] = None
    order_number: Optional[str] = None
    vehicle_or_tank_number: Optional[str] = None
    rins_records: Optional[list["ItemRins"]] = None
    tax_records: Optional[list["ItemTax"]] = None

    def add_rins_record(self, rins_record: "ItemRins") -> None:
        if self.rins_records is None:
            self.rins_records = []
        self.rins_records.append(rins_record)

    def add_tax_record(self, tax_record: "ItemTax") -> None:
        if self.tax_records is None:
            self.tax_records = []
        self.tax_records.append(tax_record)

    @classmethod
    def parse(cls, row: list[str]) -> "Item":
        row = cls._pad_row(row, 34)
        common_date_fmt = "%Y%m%d"
        # Note that this is the only field in the invoice where date/time are both optional.
        # If the date is unavailable, time is useless, so we return None.
        # If time is not available, we can still return a datetime with hours/mins/seconds defaulted to 0.
        # If both are available, we'll parse them.
        date_str = row[13]
        time_str = row[14]
        if not date_str:
            ship_datetime = None
        elif date_str and not time_str:
            ship_datetime = datetime.strptime(date_str, common_date_fmt)
        else:
            ship_datetime = datetime.strptime(date_str + "T" + time_str, f"{common_date_fmt}T%H%M")
        return cls(
            invoice_number=row[1],
            bol_number=row[2],
            description=row[3],
            dtn_product_code=row[4],
            supplier_product_code=row[5],
            quantity_billed=cls._optional_float(row[6]),
            billed_quantity_indicator=BilledQuantityIndicator(row[7]),
            gross_quantity=cls._optional_float(row[8]),
            net_quantity=cls._optional_float(row[9]),
            unit_of_measure=row[10],
            rate=cls._optional_float(row[11]),
            line_total=float(row[12]),
            ship_datetime=ship_datetime,
            ship_from_name=row[15],
            ship_from_address=row[16],
            ship_from_address_2=row[17],
            ship_from_city=row[18],
            ship_from_state=row[19],
            ship_from_zip=row[20],
            dtn_splc=row[21],
            ship_to_number=row[22],
            ship_to_address=row[23],
            ship_to_address_2=row[24],
            ship_to_city=row[25],
            ship_to_state=row[26],
            ship_to_zip=row[27],
            carrier_description=row[28],
            carrier_fein_number=row[29],
            original_invoice_number=row[30],
            contract_number=row[31],
            order_number=row[32],
            vehicle_or_tank_number=row[33],
        )


class ItemRins(ParsableRow, BaseModel):
    """EPA Renewable Information Number record row - follows a specific invoice item, but may be omitted."""
    record_type: RecordType = RecordType.RINS
    rins: str
    supporting_document_number: Optional[str] = None
    reserved_1: str
    reserved_2: str
    reserved_3: str

    @classmethod
    def parse(cls, row: list[str]) -> "ItemRins":
        row = cls._pad_row(row, 6)
        return cls(
            rins=row[1],
            supporting_document_number=row[2],
            reserved_1=row[3],
            reserved_2=row[4],
            reserved_3=row[5],
        )


class ItemTax(ParsableRow, BaseModel):
    """Tax record for the preceding item. May be omitted, and may occur up to 100 times."""
    record_type: RecordType = RecordType.TAX
    invoice_number: str
    bol_number: Optional[str] = None
    description: str
    quantity_billed: Optional[float] = None
    unit_of_measure: Optional[str] = None
    deferred: bool
    rate: Optional[float] = None
    line_total: float
    reserved: Optional[str] = None
    tax_code: Optional[str] = None
    deferred_due_date: Optional[date] = None
    deferred_invoice_number: Optional[str] = None

    @classmethod
    def parse(cls, row: list[str]) -> "ItemTax":
        row = cls._pad_row(row, 13)
        common_date_fmt = "%Y%m%d"
        return cls(
            invoice_number=row[1],
            bol_number=row[2],
            description=row[3],
            quantity_billed=cls._optional_float(row[4]),
            unit_of_measure=row[5],
            deferred=cls._parse_bool(row[6]),
            rate=cls._optional_float(row[7]),
            line_total=cls._optional_float(row[8]),
            reserved=row[9],
            tax_code=row[10],
            deferred_due_date=cls._try_parse_date(row[11], common_date_fmt),
            deferred_invoice_number=row[12],
        )


class SummaryTax(ParsableRow, BaseModel):
    """Summary tax invoice rows."""
    record_type: RecordType = RecordType.SUMMARY_TAX
    invoice_number: str
    description: str
    quantity_billed: Optional[float] = None
    unit_of_measure: Optional[str] = None
    deferred: bool
    rate: Optional[float] = None
    line_total: float
    tax_code: Optional[str] = None
    deferred_due_date: Optional[date] = None
    deferred_invoice_number: Optional[str] = None

    @classmethod
    def parse(cls, row: list[str]) -> "SummaryTax":
        row = cls._pad_row(row, 11)
        common_date_fmt = "%Y%m%d"
        return cls(
            invoice_number=row[1],
            description=row[2],
            quantity_billed=cls._optional_float(row[3]),
            unit_of_measure=row[4],
            deferred=cls._parse_bool(row[5]),
            rate=cls._optional_float(row[6]),
            line_total=float(row[7]),
            tax_code=row[8],
            deferred_due_date=cls._try_parse_date(row[9], common_date_fmt),
            deferred_invoice_number=row[10]
        )


class DeferredTaxItem(BaseModel):
    index: int
    amount: Optional[float] = None
    description: Optional[Literal["STATE", "FEDERAL", "UNKNOWN"]] = None
    deferred_date: Optional[date] = None
    deferred_invoice_number: Optional[str] = None

    @property
    def all_none(self) -> bool:
        return (
                self.amount is None
                and self.description is None
                and self.deferred_date is None
                and self.deferred_invoice_number is None
        )


class DeferredTax(ParsableRow, BaseModel):
    """Deferred tax invoice row. Only expected once per invoice."""
    record_type: RecordType = RecordType.DEFERRED_TAX
    items: conlist(DeferredTaxItem, min_length=1)

    @classmethod
    def parse(cls, row: list[str]) -> "DeferredTax":
        row = cls._pad_row(row, 41)
        common_date_fmt = "%Y%m%d"

        # Iterate over the groups of columns of data that represent each item and extract them
        items = []
        chunked = [row[i:i + 4] for i in range(1, 41, 4)]
        index = 1
        # We pad the row with blank spaces which do not parse as Optionals.
        # 'or None' converts them to a NoneType so they do.
        for group in chunked:
            items.append(
                DeferredTaxItem(
                    index=index,
                    amount=cls._optional_float(group[0]),
                    description=group[1] or None,
                    deferred_date=cls._try_parse_date(group[2], common_date_fmt),
                    deferred_invoice_number=group[3] or None,
                )
            )
            index += 1
        if len(items) < 1:
            raise InvalidDTNInvoiceException("Malformed deferred tax item - must have at least 1 entry")
        items = list(filter(lambda x: not x.all_none, items))
        return DeferredTax(
            items=items
        )


class Footer(ParsableRow, BaseModel):
    """Footer row. Indicates the record is complete."""
    record_type: RecordType = RecordType.FOOTER
    dtn_transaction_number: str
    record_count: int

    @classmethod
    def parse(cls, row: list[str]) -> "Footer":
        return cls(
            dtn_transaction_number=row[1],
            record_count=int(row[2]),
        )


CSVRow: Union[Header, Item, ItemRins, ItemTax, SummaryTax, DeferredTax, Footer] = Field(discriminator="record_type")


class DTNSupplierInvoice(BaseModel):
    header: Header
    items: list[Item]
    summary_taxes: list[SummaryTax]
    deferred_taxes: Optional[DeferredTax] = None
    footer: Footer
    original_filename: Optional[str] = None


class InvalidDTNInvoiceException(BaseException):
    pass


class Parser:
    _record_cls = {
        RecordType.HEADER: Header,
        RecordType.ITEM: Item,
        RecordType.RINS: ItemRins,
        RecordType.TAX: ItemTax,
        RecordType.SUMMARY_TAX: SummaryTax,
        RecordType.DEFERRED_TAX: DeferredTax,
        RecordType.FOOTER: Footer,
    }

    def __init__(self):
        pass

    def _parse_row(self, row: list[str]) -> CSVRow:
        record_type = RecordType(row[0])
        return self._record_cls[record_type].parse(row)

    def _map_rows_by_type(self, rows: list[CSVRow]) -> dict[RecordType, list[CSVRow]]:
        types_map = {k: [] for k in self._record_cls.keys()}
        for row in rows:
            types_map[row.record_type].append(row)
        return types_map

    def parse_all(self, csv_file: TextIO) -> Generator[DTNSupplierInvoice, Any, None]:
        reader = csv.reader(csv_file, delimiter=",")
        abs_line = 0
        while True: # Until EOF is reached (StopIteration raised from next(reader) call)
            header = None
            footer = None
            items = []
            summary_taxes = []
            deferred_taxes = None
            last_item: Item | None = None
            line = 0
            while footer is None:
                abs_line += 1
                try:
                    row = next(reader)
                except StopIteration:
                    # If we've reached EOF but parsed any number of lines for an additional invoice, then the file is
                    # malformed.
                    if line > 0:
                        raise InvalidDTNInvoiceException("Unexpected EOF")
                    return
                line += 1
                parsed = self._parse_row(row)
                if line > 1 and header is None:
                    raise InvalidDTNInvoiceException(f"Header row not found before data rows started")
                match parsed.record_type:
                    case RecordType.HEADER:
                        if header is not None:
                            raise InvalidDTNInvoiceException(
                                f"Only one header row is allowed (got another at line {abs_line})")
                        header = parsed
                    case RecordType.FOOTER:
                        if footer is not None:
                            raise InvalidDTNInvoiceException(
                                f"Only one footer row is allowed (got another at line {abs_line})")
                        footer = parsed
                    case RecordType.ITEM:
                        items.append(parsed)
                        last_item = parsed
                    case RecordType.RINS:
                        if last_item is None:
                            raise InvalidDTNInvoiceException(
                                f"Unattached RINS record at line {abs_line} (encountered before any invoice items were)")
                        last_item.add_rins_record(parsed)
                    case RecordType.TAX:
                        if last_item is None:
                            raise InvalidDTNInvoiceException(
                                f"Unattached item tax record at line {abs_line} (encountered before any invoice items were)")
                        last_item.add_tax_record(parsed)
                    case RecordType.SUMMARY_TAX:
                        summary_taxes.append(parsed)
                    case RecordType.DEFERRED_TAX:
                        if deferred_taxes is not None:
                            raise InvalidDTNInvoiceException(
                                f"Only one deferred tax row is allowed (got another at line {abs_line})")
                        deferred_taxes = parsed
            yield DTNSupplierInvoice(
                header=header,
                items=items,
                summary_taxes=summary_taxes,
                deferred_taxes=deferred_taxes,
                footer=footer,
            )

    def parse(self, csv_file: TextIO) -> list[DTNSupplierInvoice]:
        return list(self.parse_all(csv_file))
