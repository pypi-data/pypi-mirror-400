from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DriverExtraData(BaseModel):
    source_id: Optional[str] = None
    source_system_id: Optional[str] = None


class Drop(BaseModel):
    compartment_indexes: list[int]
    before_stick_inches: Optional[int] = None
    before_stick_time: Optional[datetime] = None
    after_stick_inches: Optional[int] = None
    after_stick_time: Optional[datetime] = None
    drop_id: str
    location: str
    location_id: str
    location_source_id: Optional[str] = None
    location_source_system: Optional[str] = None
    product: str
    product_id: str
    product_source_id: Optional[str] = None
    product_source_system: Optional[str] = None
    tank_id: Optional[int] = None
    tank_source_id: Optional[str] = None
    tank_source_system: Optional[str] = None
    volume: int
    driver_id: Optional[str] = None
    driver_username: Optional[str] = None
    driver_extra_data: Optional[DriverExtraData] = None
    driver_name: Optional[str] = None
    driver_date: Optional[datetime] = None
    driver_shift: Optional[str] = None
    driver_shift_id: Optional[str] = None
    tractor_number: Optional[str] = None
    trailer_number: Optional[str] = None
    blend_codes: list[str] = []
    site_counterparty_id: Optional[str] = None
    site_counterparty_name: Optional[str] = None
    freight_customer_id: Optional[str] = None
    freight_customer_name: Optional[str] = None


class BOLPriceDetails(BaseModel):
    price: Optional[float] = None
    price_id: Optional[str] = None
    curve_id: Optional[str] = None
    date: Optional[datetime] = None
    counterparty_id: Optional[str] = None


class BOLDetail(BaseModel):
    compartment_index: Optional[int] = None
    load_number: Optional[str] = None
    product: str
    product_id: str
    product_source_id: Optional[str] = None
    product_source_system: Optional[str] = None
    net_volume: int
    gross_volume: int
    supplier: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_source_id: Optional[str] = None
    supplier_source_system: Optional[str] = None
    contract: Optional[str] = None
    price_details: Optional[BOLPriceDetails] = None


class BOL(BaseModel):
    bol_number: str
    bol_id: str
    date: Optional[datetime] = None
    details: list[BOLDetail] = []
    load_or_drop: Optional[str] = None
    location: Optional[str] = None
    location_id: Optional[str] = None
    location_source_id: Optional[str] = None
    location_source_system: Optional[str] = None
    driver_id: Optional[str] = None
    driver_username: Optional[str] = None
    driver_extra_data: Optional[DriverExtraData] = None
    driver_name: Optional[str] = None
    driver_date: Optional[datetime] = None
    driver_shift: Optional[str] = None
    driver_shift_id: Optional[str] = None
    tractor_number: Optional[str] = None
    trailer_number: Optional[str] = None


class Cost(BaseModel):
    cost_type: str
    carrier: Optional[str] = None
    carrier_source_id: Optional[str] = None
    carrier_source_system: Optional[str] = None
    per_unit_price: Optional[float] = None
    cost_amount: Optional[float] = None


class FreightLeg(BaseModel):
    origin: str
    origin_id: str
    destination: str
    destination_id: str
    distance: Optional[float] = None


class FreightTransaction(BaseModel):
    model_type: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    total: Optional[float] = None
    uom: Optional[str] = None
    errors: list[str] = []
    id: str
    product_group: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    origin: Optional[str] = None
    origin_id: Optional[str] = None
    origin_override: Optional[str] = None
    origin_id_override: Optional[str] = None
    destination: Optional[str] = None
    destination_id: Optional[str] = None
    destination_override: Optional[str] = None
    destination_id_override: Optional[str] = None
    legs: list[FreightLeg] = []
    use_surcharge: Optional[bool] = None
    manual: Optional[bool] = None
    has_dependency: Optional[bool] = None
    created_date: Optional[datetime] = None
    requires_approval: Optional[bool] = None
    requires_approval_reason_code: Optional[bool] = None
    is_approved: Optional[bool] = None
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    approved_reason_code: Optional[str] = None
    amount_override: Optional[float] = None
    rate_override: Optional[float] = None
    product_id_override: Optional[str] = None
    product_name_override: Optional[str] = None
    product_group_override: Optional[str] = None
    subtype_override: Optional[str] = None
    uom_override: Optional[str] = None
    total_override: Optional[float] = None
    override_by: Optional[str] = None
    override_date: Optional[datetime] = None
    exclude_from_invoice: Optional[bool] = None
    credit_rebill_metadata: Optional[dict] = None
    extra_data: Optional[dict] = None
    gross_volume: Optional[int] = None
    net_volume: Optional[int] = None
    bol_date: Optional[datetime] = None
    bol_number: Optional[str] = None
    bol_number_override: Optional[str] = None
    delivery_date: Optional[datetime] = None


class Freight(BaseModel):
    id: str
    parent: Optional[str] = None
    created_at: Optional[datetime] = None
    type: Optional[str] = None
    status: Optional[str] = None
    reversed: Optional[bool] = None
    transactions: list[FreightTransaction] = []
    counterparty_id: Optional[str] = None
    book_type: Optional[str] = None
    effective_date_used: Optional[datetime] = None
    invoice_group_id: Optional[str] = None
    invoice_number: Optional[str] = None
    accessorial_invoice_number: Optional[str] = None
    new_version_available: Optional[bool] = None
    new_version_total: Optional[float] = None
    error: Optional[str] = None


class AllocatedBOLPrice(BaseModel):
    contract: Optional[str] = None
    price_type: Optional[str] = None
    price_id: Optional[str] = None
    curve_id: Optional[str] = None
    price: Optional[float] = None
    date: Optional[datetime] = None
    expired: Optional[bool] = None


class AllocatedBOL(BaseModel):
    bol_number: str
    bol_id: str
    bol_terminal_id: Optional[str] = None
    bol_terminal: Optional[str] = None
    bol_product: Optional[str] = None
    bol_product_id: Optional[str] = None
    bol_supplier: Optional[str] = None
    bol_supplier_id: Optional[str] = None
    bol_net_volume_original: Optional[int] = None
    bol_gross_volume_original: Optional[int] = None
    store_number: Optional[str] = None
    store_id: Optional[str] = None
    location_id: Optional[str] = None
    store_tank: Optional[int] = None
    store_product: Optional[str] = None
    store_product_id: Optional[str] = None
    store_timezone: Optional[str] = None
    bol_net_volume_allocated: Optional[int] = None
    bol_gross_volume_allocated: Optional[int] = None
    driver_schedule: Optional[str] = None
    bol_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    price: Optional[AllocatedBOLPrice] = None


class Order(BaseModel):
    order_number: str
    order_id: str
    po: Optional[str] = None
    carrier: Optional[str] = None
    carrier_id: Optional[str] = None
    manager: Optional[str] = None
    manager_id: Optional[str] = None
    last_movement_update: Optional[datetime] = None
    order_date: Optional[datetime] = None
    status: Optional[str] = None
    type: Optional[str] = None
    drops: list[Drop] = []
    bols: list[BOL] = []
    costs: list[Cost] = []
    validation_bypass_on: Optional[datetime] = None
    has_additives: Optional[bool] = None
    estimated_freight: Optional[Freight] = None
    actual_freight: Optional[Freight] = None
    allocated_bol_error: Optional[str] = None
    allocated_bol_issue: Optional[str] = None
    allocated_bols: list[AllocatedBOL] = []
    last_change_date: Optional[datetime] = None
    reference_order_number: Optional[str] = None