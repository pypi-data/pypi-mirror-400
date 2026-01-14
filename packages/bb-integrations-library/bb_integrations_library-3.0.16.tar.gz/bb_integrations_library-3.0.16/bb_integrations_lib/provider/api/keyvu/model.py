from datetime import datetime
from enum import Enum
from typing import Optional

# from pydantic import BaseModel
from pydantic_xml import BaseXmlModel, element

default_serialization_options = {
    "skip_empty": False, "exclude_none": False, "exclude_unset": True
}
"""To be passed to pydantic_xml.BaseXmlModel.to_xml when sending to the KeyVu API"""


class DeliveryStatus(str, Enum):
    planned = "Planned"
    on_route_not_loaded = "OnRouteNotLoaded"
    loading = "Loading"
    on_route_loaded = "OnRouteLoaded"
    unloading = "Unloading"
    delivered = "Delivered"
    confirmed = "Confirmed"
    canceled = "Canceled"


class UnitSystem(str, Enum):
    metric = "Metric"
    imperial = "Imperial"


class KeyVuDeliveryPlan(BaseXmlModel, tag="Loads", nsmap={"": "http://keyvu.com/schemas/carrierloads/v6",
                                                          "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                                          "xsd": "http://www.w3.org/2001/XMLSchema"}):
    start_date: datetime = element(tag="StartDate")
    end_date: datetime = element(tag="EndDate")
    export_date: datetime = element(tag="ExportDate")
    deliveries: Optional[list["Delivery"]] = element(tag="Delivery", default=None, nillable=True)

class GeoLocation(BaseXmlModel):
    longitude: Optional[float] = element(tag="Longitude", nillable=True, default=None)
    latitude: Optional[float] = element(tag="Latitude", nillable=True, default=None)
    heading: Optional[float] = element(tag="Heading", nillable=True, default=None)
    last_updated: Optional[datetime] = element(tag="LastUpdated", nillable=True, default=None)


class Delivery(BaseXmlModel):
    id: str = element(tag="Id")
    carrier_name: Optional[str] = element(tag="CarrierName", default=None)
    scac: Optional[str] = element(tag="Scac", default=None)
    station_deliveries_array: "StationDeliveryArray" = element(tag="StationDeliveries", default=None)
    trailer: Optional[str] = element(tag="Trailer", default=None)
    last_updated: datetime = element(tag="LastUpdated")
    geo_location: "GeoLocation" = element(tag="GeoLocation", default_factory=lambda: GeoLocation(longitude=None, latitude=None, heading=None, last_updated=None))
    unit: str = element(tag="Unit")

    def __init__(self, station_deliveries: list["StationDelivery"], **kwargs):
        super().__init__(**kwargs)
        self.station_deliveries = station_deliveries

    @property
    def station_deliveries(self) -> list["StationDelivery"] | None:
        return self.station_deliveries_array.station_deliveries

    @station_deliveries.setter
    def station_deliveries(self, new_deliveries: list["StationDelivery"]) -> None:
        self.station_deliveries_array = StationDeliveryArray(station_deliveries=new_deliveries)


class StationDeliveryArray(BaseXmlModel):
    station_deliveries: Optional[list["StationDelivery"]] = element(tag="StationDelivery", default=None)


class StationDelivery(BaseXmlModel):
    delivery_status: DeliveryStatus = element(tag="DeliveryStatus")
    site_id: Optional[str] = element(tag="SiteId", default=None)
    details_array: Optional["StationDeliveryDetailsArray"] = element(tag="Details", default=None)
    bill_of_ladings_array: Optional["StationDeliveryBOLArray"] = element(tag="BillOfLadings", default=None)
    tractor: Optional[str] = element(tag="Tractor", default=None)
    delivery_date: datetime = element(tag="DeliveryDate")
    carrier_delivery_status: Optional[str] = element(tag="CarrierDeliveryStatus", default=None)

    def __init__(self, details: list["StationDeliveryDetails"] | None = None,
                 bill_of_ladings: list["StationDeliveryBOL"] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.details = details
        self.bill_of_ladings = bill_of_ladings

    @property
    def details(self) -> list["StationDeliveryDetails"] | None:
        if not self.details_array:
            return None
        return self.details_array.details

    @details.setter
    def details(self, new_details: list["StationDeliveryDetails"]) -> None:
        self.details_array = StationDeliveryDetailsArray(details=new_details)

    @property
    def bill_of_ladings(self) -> list["StationDeliveryBOL"] | None:
        if not self.bill_of_ladings_array:
            return None
        return self.bill_of_ladings_array.bill_of_ladings

    @bill_of_ladings.setter
    def bill_of_ladings(self, new_bols: list["StationDeliveryBOL"]) -> None:
        self.bill_of_ladings_array = StationDeliveryBOLArray(bill_of_ladings=new_bols)


class StationDeliveryDetailsArray(BaseXmlModel):
    details: Optional[list["StationDeliveryDetails"]] = element(tag="StationDeliveryDetails", default=None)


class StationDeliveryDetails(BaseXmlModel, tag="StationDeliveryDetails", skip_empty=True):
    delivered_volume: Optional[float] = element(tag="DeliveredVolume", nillable=True)
    volume_unit: UnitSystem = element(tag="VolumeUnit")
    tank_sequence: Optional[int] = element(tag="TankSequence", default=None)
    product_id: Optional[str] = element(tag="ProductId", default=None)
    product: Optional[str] = element(tag="Product", default=None)
    is_retained: bool = element(tag="IsRetained")

    @staticmethod
    def from_v1_order_dict(details: dict) -> "StationDeliveryDetails":
        # Prefer using tank sequence, but fall back to product ID based matching. This is the behavior KeyVu prefers.
        tank_sequence = details.get("tank_id")
        product_id = None
        product = None
        if not tank_sequence:
            product_id = details.get("product_source_id")
            product = details.get("product_name")

        return StationDeliveryDetails(
            delivered_volume=details.get("quantity", 0.0),
            volume_unit=UnitSystem.imperial,
            tank_sequence=tank_sequence,
            product_id=product_id,
            product=product,
            is_retained=False # TODO: Support retains
        )


class StationDeliveryBOLArray(BaseXmlModel):
    bill_of_ladings: Optional[list["StationDeliveryBOL"]] = element(tag="StationDeliveryBillOfLadings")


class StationDeliveryBOL(BaseXmlModel):
    terminal_name: Optional[str] = element(tag="TerminalName", nillable=True)
    terminal_control_number: str = element(tag="TerminalControlNumber")
    bill_of_lading_number: str = element(tag="BillOfLadingNumber")
    supplier: str = element(tag="Supplier")
    consignee: str = element(tag="Consignee", default="")
