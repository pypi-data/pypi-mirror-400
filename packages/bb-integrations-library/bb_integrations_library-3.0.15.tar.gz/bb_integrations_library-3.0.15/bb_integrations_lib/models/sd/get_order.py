from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Driver(BaseModel):
    driver_id: str
    driver_schedule_id: Optional[str] = None
    name: Optional[str] = None
    username: Optional[str] = None


class LoadDetail(BaseModel):
    detail_id: str
    counterparty_id: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_source_id: Optional[str] = None
    counterparty_source_system: Optional[str] = None
    price_type: Optional[str] = None
    contract: Optional[str] = None
    product_id: str
    product_name: Optional[str] = None
    product_source_id: Optional[str] = None
    product_source_system: Optional[str] = None
    drop_product_id: Optional[str] = None
    drop_product_name: Optional[str] = None
    drop_product_source_id: Optional[str] = None
    drop_product_source_system: Optional[str] = None
    quantity: int
    compartment_index: Optional[int] = None
    blend_code: Optional[str] = None
    product_codes: list[str] = []
    load_number: Optional[str] = None


class Load(BaseModel):
    location_id: str
    location_name: Optional[str] = None
    location_source_id: Optional[str] = None
    location_source_system: Optional[str] = None
    location_type: Optional[str] = None
    details: list[LoadDetail] = []
    eta: Optional[datetime] = None
    status: Optional[str] = None


class DropSource(BaseModel):
    compartment_index: int
    volume: int


class DropDetail(BaseModel):
    detail_id: str
    counterparty_id: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_source_id: Optional[str] = None
    counterparty_source_system: Optional[str] = None
    product_id: str
    product_name: Optional[str] = None
    product_source_id: Optional[str] = None
    product_source_system: Optional[str] = None
    quantity: int
    tank_id: Optional[int] = None
    sources: list[DropSource] = []
    destination_codes: list[str] = []
    blend_codes: list[str] = []


class Drop(BaseModel):
    location_id: str
    location_name: Optional[str] = None
    location_source_id: Optional[str] = None
    location_source_system: Optional[str] = None
    location_type: Optional[str] = None
    details: list[DropDetail] = []
    eta: Optional[datetime] = None
    status: Optional[str] = None


class Detour(BaseModel):
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    eta: Optional[datetime] = None
    status: Optional[str] = None


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


class EstimatedFreight(BaseModel):
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


class PriceComponent(BaseModel):
    timezone_data: Optional[str] = None
    curve_id: Optional[str] = None
    price_id: Optional[str] = None
    terminal_id: Optional[str] = None
    terminal: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier: Optional[str] = None
    price_type: Optional[str] = None
    product_id: Optional[str] = None
    product: Optional[str] = None
    supply_owner_id: Optional[str] = None
    supply_owner: Optional[str] = None
    price: Optional[float] = None
    contract: Optional[str] = None
    volume: Optional[int] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    group_id: Optional[str] = None
    group_effective_cutover: Optional[datetime] = None
    group_effective_cutover_timezone: Optional[str] = None
    group_identifier: Optional[str] = None
    group_name: Optional[str] = None
    min_constraint: Optional[float] = None
    max_constraint: Optional[float] = None
    load_number: Optional[str] = None
    load_numbers: list[str] = []
    directive_info: Optional[dict] = None


class Price(BaseModel):
    product_name: Optional[str] = None
    volume: Optional[int] = None
    components: list[PriceComponent] = []
    product_total: Optional[float] = None
    blend_code: Optional[str] = None


class SupplyOwnerDefinition(BaseModel):
    location_name: Optional[str] = None
    product: Optional[str] = None
    supply_owner_id: Optional[str] = None


class SupplyOwnerMap(BaseModel):
    definitions: list[SupplyOwnerDefinition] = []


class SupplyOption(BaseModel):
    option: Optional[str] = None
    carrier_id: Optional[str] = None
    carrier: Optional[str] = None
    loaded_miles: Optional[float] = None
    freight: Optional[float] = None
    freight_cost: Optional[float] = None
    stops: Optional[int] = None
    prices: list[Price] = []
    product_total: Optional[float] = None
    landed_cost: Optional[float] = None
    supply_owner_map: Optional[SupplyOwnerMap] = None
    freight_customer_id: Optional[str] = None
    delivered: Optional[bool] = None
    out_of_network: Optional[bool] = None
    estimated_freight: Optional[EstimatedFreight] = None
    legs: list[FreightLeg] = []
    freight_distance: Optional[float] = None
    supply_owner_id: Optional[str] = None


class GetOrderResponse(BaseModel):
    type: str
    order_id: Optional[str] = None
    drivers: list[Driver] = []
    order_number: Optional[int] = None
    order_date: Optional[datetime] = None
    order_state: Optional[str] = None
    carrier_window_start: Optional[datetime] = None
    carrier_window_end: Optional[datetime] = None
    carrier_window_start_local: Optional[datetime] = None
    carrier_window_end_local: Optional[datetime] = None
    carrier_notify_state: Optional[str] = None
    load_window_start: Optional[datetime] = None
    load_window_end: Optional[datetime] = None
    dispatch_window_start: Optional[datetime] = None
    dispatch_window_end: Optional[datetime] = None
    hauler_counterparty_id: Optional[str] = None
    hauler_counterparty_name: Optional[str] = None
    hauler_counterparty_source_id: Optional[str] = None
    hauler_counterparty_source_system: Optional[str] = None
    hauled_by_updated_by: Optional[str] = None
    hauled_by_updated: Optional[datetime] = None
    loads: list[Load] = []
    drops: list[Drop] = []
    detours: list[Detour] = []
    trip_status: Optional[str] = None
    last_change_date: Optional[datetime] = None
    market: Optional[str] = None
    supply_option: Optional[SupplyOption] = None
    created_by: Optional[str] = None
    note: Optional[str] = None
    estimated_load_minutes: Optional[int] = None
    total_miles: Optional[float] = None
    loaded_miles: Optional[float] = None
    unloaded_miles: Optional[float] = None
    reference_order_number: Optional[str] = None
    extra_data: Optional[dict] = None
    tractor: Optional[str] = None
    trailer: Optional[str] = None
    po_number: Optional[str] = None


class GetOrderRequestProduct(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None


class GetOrderRequestResponse(BaseModel):
    type: Optional[str] = None
    number: int
    order_id: Optional[str] = None
    order_number: Optional[int] = None
    order_date: Optional[datetime] = None
    order_state: Optional[str] = None
    reference_order_number: Optional[str] = None
    last_change_date: Optional[datetime] = None
    site_name: Optional[str] = None
    site_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_window_start: datetime
    delivery_window_end: datetime
    products: list[GetOrderRequestProduct] = []
    extra_data: Optional[dict] = None