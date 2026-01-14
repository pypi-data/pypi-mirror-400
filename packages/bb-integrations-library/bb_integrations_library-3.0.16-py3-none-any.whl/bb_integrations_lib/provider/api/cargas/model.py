from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateWholesaleFeeLineRequest(BaseModel):
    DocumentID: str
    ItemID: str
    Quantity: Optional[float] = None
    UnitPrice: Optional[float] = None
    UserName: str


class CreateWholesaleLineRequest(BaseModel):
    DocumentID: int
    ItemID: int
    TankID: int
    Quantity: float
    QuantityGross: float
    UnitPrice: Optional[float] = None
    FreightRateID: Optional[float] = None
    VendorLocationID: Optional[float] = None
    FreightAmount: Optional[float] = None
    SurchargeAmount: Optional[float] = None
    UnitCostOverride: Optional[float] = None
    CustomerPricingID: Optional[str] = None
    UserName: str


class CreateWholesaleTicketRequest(BaseModel):
    CustomerID: int
    DeliveryDate: datetime
    CustomerPONumber: Optional[str] = None
    DriverID: Optional[int] = None
    WholesaleTruckID: Optional[int] = None
    Message: Optional[str] = None
    InvoiceNotes: Optional[str] = None
    CostCenterID: Optional[int] = None
    SubTypeID: Optional[int] = None
    SalespersonID: Optional[int] = None
    AdditionalNotes: Optional[str] = None
    UserName: str


class CreateWholesaleTicketRequestBundle(BaseModel):
    ticket_request: CreateWholesaleTicketRequest
    line_requests: list[CreateWholesaleLineRequest] = []
    fee_line_requests: list[CreateWholesaleLineRequest] = []
