import re
from datetime import datetime, UTC, timezone, timedelta
from typing import List, override, Literal, Any, Self

from bson import ObjectId
from loguru import logger
from pydantic import BaseModel, Field

from bb_integrations_lib.gravitate.testing.TTE.sd.models import PydanticObjectId
from bb_integrations_lib.models.sd_api import DeliveryWindow


class RequestDataSerializationHalted(Exception):
    """Thrown by a probe when it is not serializing a certain event, but for a non-error reason. E.g. this may be thrown
    by a probe that only serializes some kinds of events but ignores others."""
    pass


class RequestData(BaseModel):
    """This represents a data structure for a worker to use for its operation. This is a discriminated union."""
    request_type: str

    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        """
        Constructs BUT DOES NOT VALIDATE a RequestData object from the database info provided. Workers will know what
        data value they expect and call model_validate appropriately.
        """
        ...

    @classmethod
    def get_id(cls, obj: dict):
        if type(obj.get("_id")) is PydanticObjectId:
            order_id = str(obj["_id"])
        elif type(obj.get("_id")) is ObjectId:
            order_id = str(obj["_id"])
        elif type(obj.get("_id")) is dict and "$oid" in obj["_id"]:
            order_id = obj["_id"].get("$oid")
        else:
            raise Exception("Couldn't find an id on object.")
        return order_id

    @classmethod
    def get_dt(cls, val: Any) -> datetime | None:
        if type(val) is datetime:
            return val.replace(tzinfo=timezone.utc)
        elif type(val) is str:
            return datetime.fromisoformat(val).replace(tzinfo=timezone.utc)
        elif type(val) is dict:
            return val.get("$date").replace(tzinfo=timezone.utc)
        return None


class ErrorRequestData(RequestData):
    """Probes create worker requests with this type when they encounter an error. This is just to expose a breakage to the logging system."""
    request_type: Literal["probe_error"]
    error: str | None = None

#### Other Request Data

class MacropointLocationUpdate(RequestData):
    """Data for the MacropointIntegrationRunnable. Uses the Macropoint API to update the location as we get them from S&D"""
    request_type: Literal["MacropointLocationUpdate"] = "MacropointLocationUpdate"
    order_number: int = Field(..., description="The order number of the order in S&D.")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    date: datetime = Field(..., description="Date of the location update")
    po: str = Field(..., description="The raw PO number on the order. This has not been parsed to find the relevant LD number for Macropoint")

    @override
    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        order_number = obj.get("in_cab_context", {}).get("order_number")
        lat = obj.get("gps", {}).get("lat")
        lon = obj.get("gps", {}).get("lon")
        date = cls.get_dt(obj.get("date"))
        po = obj.get("po", "")
        return MacropointLocationUpdate.model_construct(order_number=order_number, lat=lat, lon=lon, date=date, po=po)



#### Crossroads Request Datas

class CreateOrderFromSDOrder_Drop(BaseModel):
    location_name: str = Field(..., description="Name of drop location")
    location_id: str = Field(..., description="ID of the drop location")
    tank_id: str = Field(..., description="ID of the drop tank")
    product_name: str = Field(..., description="Name of the product to drop")
    product_id: str = Field(..., description="ID of the product to drop")
    volume: float = Field(..., description="Drop volume")
    from_compartments: list[int] = Field([], description="The list of compartments that the drop is sourced from.")
    delivery_window_start: datetime | None = Field(None, description="The earliest date this drop can be made.")
    delivery_window_end: datetime | None = Field(None, description="The latest date this drop can be made.")


class CreateOrderFromSDOrder_Load(BaseModel):
    location_name: str = Field("", description="Name of lift location")
    location_id: str = Field(..., description="ID of the lift location")
    product_name: str = Field("", description="Name of the lift product")
    product_id: str = Field(..., description="ID of the lift product")
    supplier_name: str = Field("", description="Name of the supplier")
    supplier_id: str = Field(..., description="ID of the supplier")
    volume: float = Field(..., description="Load volume")
    compartments: list[int] = Field([], description="The list of compartments the load is put into.")


class CreateOrderFromSDOrder_Compartment(BaseModel):
    compartment_index: int = Field(..., description="Compartment index")
    product_id: str = Field(..., description="ID of the product in the compartment.")
    product_name: str = Field(..., description="Name of the product in the compartment.")
    volume: int = Field(..., description="Volume loaded into the compartment")

class CreateOrderFromSDOrder(RequestData):
    request_type: Literal["CreateOrderFromSDOrder"] = "CreateOrderFromSDOrder"
    order_id: str = Field(..., description="Order database ID")
    order_number: int = Field(..., description="Order number")
    note: str | None = Field(None, description="Order note, if available")
    extra_data: dict = Field({}, description="The order's original extra_data. Crossroads integrations can update the extra data and need to know the original value to prevent clobbering.")
    supply_owner_id: str = Field(..., description="Counterparty ID of the supply owner in the order's S&D instance.")
    freight_customer_id: str = Field(..., description="Counterparty ID for the freight customer on this order.")
    market: str = Field(..., description="Market name for this order")
    drop_details: List[CreateOrderFromSDOrder_Drop] = Field([], description="Order drops")
    load_details: List[CreateOrderFromSDOrder_Load] = Field([], description="Order loads")
    compartments: List[CreateOrderFromSDOrder_Compartment] = Field([], description="Order compartments, by index")
    state: str | None = Field(default=None, description="Order state")

    def get_delivery_window(self, default_span_days = 7):
        """Calculates the delivery window from the drops on this object. If multiple drops have delivery windows, the
        start time is the latest possible start time and the end time is the earliest possible end time. If the order
        does not have delivery windows set on its drops, which may happen when it is very new, the delivery window
        defaults to the current time plus 7 days. If the delivery window is impossible (the end of the window is before
        the start of the window) then also fallback to that basic window."""
        window_starts = [x.delivery_window_start for x in self.drop_details if x.delivery_window_start is not None]
        window_ends = [x.delivery_window_end for x in self.drop_details if x.delivery_window_end is not None]
        default_start = datetime.now()
        default_end = default_start + timedelta(days=default_span_days)

        if len(window_starts) > 0:
            window_start = max(window_starts)
        else:
            window_start = default_start
        if len(window_ends) > 0:
            window_end = min(window_ends)
        else:
            window_end = default_end

        if window_end < window_start:
            # Impossible delivery window; S&D API won't let us create an order with this. Adjust by setting end to be start
            # + the default span days (this may be different than the "no delivery window" case because we may know the
            # start date
            window_end = window_start + timedelta(days=default_span_days)

        return DeliveryWindow(start=window_start, end=window_end)

    @override
    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        compartments = []
        drop_details = []
        load_details = []
        order_id = cls.get_id(obj)
        for comp in obj.get("compartments"):
            compartments.append(CreateOrderFromSDOrder_Compartment.model_construct(
                compartment_index=comp.get("compartment_index"),
                product_id=comp.get("product_id"),
                product_name=comp.get("product_name"),
                volume=comp.get("volume")
            ))
        for drop in obj.get("drops"):
            for detail in drop.get("details"):
                drop_details.append(CreateOrderFromSDOrder_Drop.model_construct(
                    location_name=drop.get("location_name"),
                    location_id=drop.get("location_id"),
                    product_name=detail.get("product_name"),
                    product_id=detail.get("product_id"),
                    tank_id=str(detail.get("tank_id")),
                    volume=int(sum([x.get("volume", 0) for x in detail.get("sources")])),
                    from_compartments=[x.get("compartment_index") for x in detail.get("sources")],
                    delivery_window_start=detail.get("window_start"),
                    delivery_window_end=detail.get("window_end"),
                ))
        for load in obj.get("loads"):
            for detail in load.get("details"):
                load_details.append(CreateOrderFromSDOrder_Load.model_construct(
                    location_name=load.get("location_name"),
                    location_id=load.get("location_id"),
                    product_name=detail.get("product_name"),
                    product_id=detail.get("product_id"),
                    supplier_name=detail.get("counterparty"),
                    supplier_id=detail.get("counterparty_id"),
                    volume=int(sum([x.get("volume", 0) for x in detail.get("targets")])),
                    compartments=[x.get("compartment_index") for x in detail.get("targets")]
                ))
        return CreateOrderFromSDOrder.model_construct(
            order_id=order_id,
            order_number=obj.get("number"),
            note=obj.get("note", {}).get("content"),
            extra_data=obj.get("extra_data", {}),
            supply_owner_id=obj.get("supply_option", {}).get("supply_owner_id"),
            freight_customer_id=obj.get("supply_option", {}).get("freight_customer_id"),
            market=obj.get("market"),
            drop_details=drop_details,
            load_details=load_details,
            compartments=compartments,
            state=obj.get("state"),
        )


class UpdateStatusFromSD(RequestData):
    request_type: Literal["UpdateStatusFromSD"] = "UpdateStatusFromSD"
    origin_order_id: str = Field(..., description="Order database ID")
    origin_order_number: int = Field(..., description="Order number")
    crossroads_target_order_number: int = Field(..., description="Order number of the target order to be updated. This is captured from the extra_data on the order object in the origin database.")
    crossroads_target_order_id: str = Field(..., description="Order database ID of the target order to be updated. This is captured from the extra_data on the order object in the origin database.")
    date: str = Field(..., description="Date from the change. ISO formatted datetime string.")
    status: str = Field(..., description="New status from the update.")
    location_id: str | None = Field(..., description="location ID of the update, if applicable.")

    @override
    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        origin_order_id = cls.get_id(obj)
        origin_order_number = obj.get("number")
        crossroads_target_order_number = int(obj.get("extra_data").get("crossroads_target_number"))
        crossroads_target_order_id = obj.get("extra_data").get("crossroads_target_order_id")

        logger.debug(f"parsing object: {obj}, updated_fields: {updated_fields}")
        if obj.get("state") == "assigned":
            raise RequestDataSerializationHalted("The order is in the 'assigned' state.")
        elif obj.get("state") == "accepted":
            raise RequestDataSerializationHalted("The order is in the 'accepted' state.")
        elif obj.get("state") == "canceled":
            raise RequestDataSerializationHalted("The order is in the 'canceled' state.")
        elif obj.get("state") == "complete":
            # The order has completed. We don't need to do the rest, we can just send a request to complete the order to the target and be done.
            return UpdateStatusFromSD.model_construct(
                origin_order_id=origin_order_id, origin_order_number=origin_order_number,
                crossroads_target_order_number=crossroads_target_order_number, crossroads_target_order_id=crossroads_target_order_id,
                date=cls.get_dt(obj.get("movement_updated")).isoformat(timespec="seconds"), status="complete", location_id=None
            )
        else:
            try:
                update = cls.extract_status_update_without_route_events(crossroads_target_order_number, origin_order_id,
                                                                      crossroads_target_order_id, origin_order_number, obj,
                                                                      updated_fields)
                return update
            except Exception as e:
                try:
                    update = cls.extract_status_update_with_route_events(origin_order_id, origin_order_number,
                                                                         crossroads_target_order_number,
                                                                         crossroads_target_order_id, obj)
                    return update
                except Exception as e:
                    # Both attempts to construct a status update failed. Bail out.
                    raise e

    @classmethod
    def extract_status_update_with_route_events(cls, origin_order_id: str, origin_order_number: str,
                                                crossroads_target_order_number: str, crossroads_target_order_id: str,
                                                obj: dict):
        # Loop over the route events for loads and drops, selecting the latest one.
        latest_re = None
        selected_obj = None
        selected_is = "drop"
        for load in obj.get("loads", []):
            for route_event in load.get("route_events", []):
                if latest_re is None or route_event.get("timestamp") > latest_re.get("timestamp"):
                    latest_re = route_event
                    selected_obj = load
                    selected_is = "load"
        for drop in obj.get("drops", []):
            for route_event in drop.get("route_events", []):
                if latest_re is None or route_event.get("timestamp") > latest_re.get("timestamp"):
                    latest_re = route_event
                    selected_obj = drop
                    selected_is = "drop"

        # We now have the latest event.
        new_status = selected_obj.get("route_status")

        # Check for some statuses that we don't want to copy:
        if new_status == "preview":
            raise RequestDataSerializationHalted("The latest route status is a 'preview' status.")

        # BUT there's a problem: when I hit the source with a "completed load" event, what I see is just "complete" for
        # the load. So I need to do some extra checks. If the load was complete, I change the status I received to
        # "completed load". If the drop was complete, I change the status to "completed drop". I ONLY use the completed
        # status when the order state itself is "complete". Otherwise we would be closing it out early. Very annoying.
        if new_status == "complete":
            if selected_is == "load":
                new_status = "completed load"
            elif selected_is == "drop":
                new_status = "completed drop"
        location_id = selected_obj.get("location_id")
        new_eta = cls.get_dt(selected_obj.get("updated"))
        return UpdateStatusFromSD.model_construct(
            origin_order_id=origin_order_id, origin_order_number=origin_order_number,
            crossroads_target_order_number=crossroads_target_order_number, crossroads_target_order_id=crossroads_target_order_id,
            date=new_eta.isoformat(timespec="seconds"), status=new_status, location_id=location_id,
        )

    @classmethod
    def extract_status_update_without_route_events(cls, origin_order_id: str, origin_order_number: str,
                                                   crossroads_target_order_id: str, crossroads_target_order_number: str,
                                                   obj: dict, updated_fields: dict) -> Self:
        # We need to inspect the updated fields description to figure out which order was updated. This is because we're
        # not receiving an update notify from S&D but inspecting the database instead, and the S&D endpoint values for
        # status don't exactly match the database values.
        loads_eta_regex = r"loads\.(\d+)\.eta"
        loads_status_regex = r"loads\.(\d+)\.route_status"
        drops_eta_regex = r"drops\.(\d+)\.eta"
        drops_status_regex = r"drops\.(\d+)\.route_status"
        loads_matched_set = set()
        drops_matched_set = set()
        for field in updated_fields:
            load_eta_match = re.match(loads_eta_regex, field)
            load_status_match = re.match(loads_status_regex, field)
            drop_eta_match = re.match(drops_eta_regex, field)
            drop_status_match = re.match(drops_status_regex, field)
            if load_eta_match:
                loads_matched_set.add(int(load_eta_match.group(1)))
            elif load_status_match:
                loads_matched_set.add(int(load_status_match.group(1)))
            elif drop_eta_match:
                drops_matched_set.add(int(drop_eta_match.group(1)))
            elif drop_status_match:
                drops_matched_set.add(int(drop_status_match.group(1)))
        max_updated_date = datetime(1, 1, 1, tzinfo=UTC)
        max_updated_obj = {}
        max_is = ""
        for load_idx in loads_matched_set:
            load = obj.get("loads")[load_idx]
            dt = cls.get_dt(load.get("updated", None))
            if dt and dt > max_updated_date:
                max_updated_obj = load
                max_is = "load"
        for drop_idx in drops_matched_set:
            drop = obj.get("drops")[drop_idx]
            dt = cls.get_dt(drop.get("updated", None))
            if dt and dt > max_updated_date:
                max_updated_obj = drop
                max_is = "drop"
        new_status: str = max_updated_obj.get("route_status", "")
        location_id = max_updated_obj.get("location_id")
        # From testing it seems like all events just touch the ETA field? So I only have to parse that out, and
        # not worry about Actual.
        new_eta = cls.get_dt(max_updated_obj.get("eta"))
        if not new_eta:
            new_eta = cls.get_dt(max_updated_obj.get("actual"))
        # BUT there's a problem: when I hit the source with a "completed load" event, what I see is just "complete" for
        # the load. So I need to do some extra checks. If the load was complete, I change the status I received to
        # "completed load". If the drop was complete, I change the status to "completed drop". I ONLY use the completed
        # status when the order state itself is "complete". Otherwise we would be closing it out early. Very annoying.
        if new_status == "complete":
            if max_is == "load":
                new_status = "completed load"
            elif max_is == "drop":
                new_status = "completed drop"
        return UpdateStatusFromSD.model_construct(
            origin_order_id=origin_order_id,
            origin_order_number=origin_order_number,
            crossroads_target_order_number=crossroads_target_order_number,
            crossroads_target_order_id=crossroads_target_order_id,
            location_id=location_id,
            date=new_eta.isoformat(timespec="seconds"),
            status=new_status
        )


class CancelOrderFromSD(RequestData):
    request_type: Literal["CancelOrderFromSD"] = "CancelOrderFromSD"
    origin_order_number: int = Field(..., description="The origin order number of the order to cancel.")
    crossroads_target_order_id: str = Field(..., description="Database ID of the order to cancel in the target. This is captured from the extra_data on the order object in the origin database.")
    crossroads_target_order_number: int = Field(..., description="Order number of the order to cancel in the target. This is captured from the extra_data on the order object in the origin database.")

    @override
    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        return CancelOrderFromSD.model_construct(
            origin_order_number = obj.get("number"),
            crossroads_target_order_id=obj.get("extra_data", {}).get("crossroads_target_order_id"),
            crossroads_target_order_number=int(obj.get("extra_data", {}).get("crossroads_target_number")),
        )


class SaveBOLsAndDropsFromSD_ExecutedDropDetails(BaseModel):
    product_id: str = Field(..., description="Dropped product")
    product_name: str = Field(..., description="Dropped product name")
    before_gallons: int | None = Field(default=None, description="Gallons in tank before drop")
    before_inches: int | None = Field(default=None, description="Inches in tank before drop")
    after_gallons: int | None = Field(default=None, description="Gallons in tank after drop")
    after_inches: int | None = Field(None, description="Inches in tank after drop")
    volume: int = Field(..., description="Dropped volume")
    time: datetime = Field(..., description="Time drop ended, if available. If unavailable, time drop started.")
    destination_site: str = Field(..., description="The site that this drop was at")
    destination_tank_id: int = Field(..., description="The tank ID that the product was dropped into")


class SaveBOLsAndDropsFromSD(RequestData):
    request_type: Literal["SaveBOLsAndDropsFromSD"] = "SaveBOLsAndDropsFromSD"
    origin_order_number: int = Field(..., description="The origin order number of the order to save BOLs and Drops to.")
    crossroads_target_order_id: str = Field(..., description="Database ID of the order to save BOLs and Drops to in the target. This is captured from extra_data on the order object in the origin database.")
    crossroads_target_order_number: int = Field(..., description="The crossroads_target_order_number from the order.")
    bol_numbers: list[int] = Field(..., description="The BOL numbers tied to the order. The worker will retrieve these BOL numbers and mirror them to the target.")
    executed_drop_details: list[SaveBOLsAndDropsFromSD_ExecutedDropDetails] = Field(..., description="The drops executed on the order.")

    @override
    @classmethod
    def from_db_obj(cls, obj: dict, updated_fields: dict | None = None):
        details = []
        for drop in obj.get("drops", []):
            for ex_detail in drop.get("executed_details", []):
                details.append(SaveBOLsAndDropsFromSD_ExecutedDropDetails.model_construct(
                    product_id=ex_detail.get("product_id"),
                    product_name=ex_detail.get("product_name"),
                    before_gallons=ex_detail.get("before_gallons"),
                    before_inches=ex_detail.get("before_inches"),
                    after_gallons=ex_detail.get("after_gallons"),
                    after_inches=ex_detail.get("after_inches"),
                    volume=ex_detail.get("volume"),
                    time=ex_detail.get("after_stick_time", ex_detail.get("before_stick_time")),
                    destination_site=drop.get("location_name"),
                    destination_tank_id=ex_detail.get("tank_id"),
                ))
        return SaveBOLsAndDropsFromSD.model_construct(
            origin_order_number=obj.get("number"),
            crossroads_target_order_id=obj.get("extra_data", {}).get("crossroads_target_order_id"),
            crossroads_target_order_number=obj.get("extra_data", {}).get("crossroads_target_number"),
            bol_numbers=obj.get("supply_option", {}).get("actual_freight", {}).get("bol_numbers", []),
            executed_drop_details=details
        )
