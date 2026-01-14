from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HierarchyKey(BaseModel):
    id: str | None = None
    name: str | None = None
    source_system: str | None = None
    source_id: str | None = None


class SiteKey(BaseModel):
    id: str | None = None
    number: str | None = None
    source_system: str | None = None
    source_id: str | None = None


class OrderKey(BaseModel):
    order_number: int | None
    order_id: str | None = None
    order_reference_number: str | None = None


class DeliveryWindow(BaseModel):
    start: datetime
    end: datetime
    timezone: str = "UTC"


class LoadsCreateRequest(BaseModel):
    terminal: HierarchyKey | None = None
    product: HierarchyKey | None = None
    supplier: HierarchyKey | None = None
    price_type: str | None = None


class DropCreateRequest(BaseModel):
    site: SiteKey
    tank_id: str | None = None
    product: HierarchyKey
    volume: int
    loads: list[LoadsCreateRequest] = []


class OrderCreateRequest(BaseModel):
    reference_order_number: str
    supply_owner: HierarchyKey | None = None
    sourcing_strategy: Literal["Specific Supply", "Tank Supply Default", "Use Best", "Manual"] = "Specific Supply"
    manual_supply_fallback: bool = True
    allow_alternate_products: bool = False
    delivery_window: DeliveryWindow
    fit_to_trailer: bool = False

    note: str | None = None
    drops: list[DropCreateRequest]
    extra_data: dict


class OrderStatusUpdateRequest(BaseModel):
    order_id: str
    order_number: str | None = None
    status: str
    location_id: str | None = None
    eta: datetime | None = None
    actual: datetime | None = None

class DropDetail(BaseModel):
    product_id: str
    quantity: float
    tank_id: int | None = None
    pre_drop_volume: float | None = None
    pre_drop_inches: float | None = None
    pre_drop_time: datetime | None = None
    post_drop_volume: float | None = None
    post_drop_inches: float | None = None
    post_drop_time: datetime | None = None

class SaveDropDetailsRequest(BaseModel):
    order_id: str
    location_id: str
    mode: Literal["replace", "append"]
    details: list[DropDetail]

class BOLDetail(BaseModel):
    supplier_id: str
    product_id: str
    contract: str | None = None
    price_type: str | None = None
    net_volume: float
    gross_volume: float

class SaveBOLDetailsRequest(BaseModel):
    order_id: str
    bol_number: str
    terminal_id: str
    bol_date: datetime
    details: list[BOLDetail]

class OrderUpdateRequest(BaseModel):
    order: OrderKey = Field(...)
    sourcing_strategy: Literal["Specific Supply", "Tank Supply Default", "Use Best", "Manual"] = Field(default="Use Best")
    delivery_window: DeliveryWindow | None = Field(default=None, description="If provided, replaces the existing delivery window.")
    note: str | None = Field(default=None, description="If provided, replaces the existing note.")
    drops: list[DropCreateRequest] = Field(default=[], description="If provided, replaces all existing drops.")
    extra_data: dict = Field(default={}, description="Merge this extra data with the existing extra data. New keys will be added, existing keys will be updated.")

class SendToCarrierRequest(BaseModel):
    order_ids: list[str]
    force: bool = False
    instant: bool = False
    actual_end_date: datetime | None = None
    send_email: bool = True