"""
Auto-generated validation tests for Pydantic models.
Generated on: 2025-07-08 20:08:26
"""
import pytest
from typing import Dict, Any
from pydantic import BaseModel, ValidationError
from bb_integrations_lib.gravitate.testing.TTE.sd.models import AllocatedBolResponse, BillableDateType, BillableVolumeType, BlendView, BolAndDropResponse, BolImageResponse, BolImagesRequest, BolImagesResponse, BolsAndDropsRequest, Card, ContractVolumeRequest, Coordinate, Counterparty, CounterpartyView, CreateGroupRequest, DateWindow, DaysOfWeek, DeliveryRequestStatus, DeliveryTicketById, DeliveryTicketByNumber, DeliveryWindow, DeliveryWindowDefault, DriverCredentialUpsertRequest, DriverCredentialView, DriverTerminalCardView, DriverView, DropCreateRequest, DropWorkflow, Dwell, EBolDetailRequest, EBolRequest, ExternalBOLDetailRequest, ExternalBOLRequest, ForecastApiCreateRequest, FormFieldResponse, FormResponseRow, FreightCost, FreightIntegrationReq, FreightItem, FreightTransactionDetailOutput, FreightTransactionOutput, FreightTransactionRowOutput, GetOrderRequestResponse, GetOrderResponse, GetOrdersRequest, HTTPValidationError, ImportRequest, InCabSupplyOptionMode, InCabTripMode, InNetworkSupplyZone, InNetworkTerminal, IntegrationFormResponseOverviewReq, InvoiceAllReq, InvoiceDynamicStatus, InvoiceRow, InvoiceStaticStatus, InvoiceType, Key, LocationResponse, LocationView, MarketSchemaSectorView, MarketView, MonitoringStrategy, NOSupplyOptionResponse, OptimalSupplyReportRequest, OptimalSupplyReportRow, OrderCreateRequest, OrderCreateResponse, OrderCreateStatus, OrderDriver, OrderFreightResp, OrderFreightRespV2, OrderReqNotificationStates, OrderResponse, OrderSchemaBolResponse, OrderSchemaDropResponse, OrderState, OrderStatusUpdateRequest, OrderType, PayrollExportDetailModel, PayrollExportDetailResponse, PriceAllRequest, PriceResponse, PriceType, ProductGroups, ProductIDName, ProductView, PydanticObjectId, RateBookType, RootModel, RouteUpsertReq, SalesAdjustedDeliveryUpsertReq, SaveDropDetail, SaveDropMode, SaveDropReq, Shift, SourceMap, SourcingStrategy, StatusUpdate, StoreStatus, StoreTank, StoreV2, SupplyPriceUpdateManyRequest, SupplyPriceUpdateResponse, SurchargeAllReq, SurchargeAllResp, SurchargeCreateReq, SurchargeType, SurchargeUpdateReq, TankLidEnum, TerminalType, TimezoneEnum, TractorView, TrailerConfigMatrixView, TrailerView, UnavailableHours, UnavailableHoursRequest, UpdateResponse, UploadIMSRequest, UpsertLocationRequest, UpsertManyCounterpartyRequest, UpsertManyDriverRequest, UpsertManyStoreRequest, UpsertProductRequest, UpsertTankRequest, UpsertTractorReq, UpsertTractorResp, UpsertTrailerReq, UpsertTrailerResp, ValidationError, VolumeDistributionRequest, WaterReadingRequirement


def generic_model_validation_test(model_to_test: BaseModel, example_input: Dict[str, Any]) -> None:
    """
    Generic test function that validates a model with example input.

    Args:
        model_to_test: The Pydantic model class to test
        example_input: Dictionary with example input data
    """
    try:
        validated_model = model_to_test.model_validate(example_input)
        assert validated_model is not None
        model_dict = validated_model.model_dump()
        assert isinstance(model_dict, dict)
    except ValidationError as e:
        pytest.fail(f"Validation failed for {model_to_test.__name__}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error for {model_to_test.__name__}: {e}")


# Individual test functions for each model

def test_allocatedbolresponse_validation():
    """Test validation for AllocatedBolResponse model."""
    example_input = {
    "root": "example_root"
}
    generic_model_validation_test(AllocatedBolResponse, example_input)


def test_allocatedbolresponse_validation_with_invalid_data():
    """Test validation failure for AllocatedBolResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        AllocatedBolResponse.model_validate(invalid_input)

def test_billabledatetype_validation():
    """Test validation for BillableDateType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(BillableDateType, example_input)


def test_billabledatetype_validation_with_invalid_data():
    """Test validation failure for BillableDateType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BillableDateType.model_validate(invalid_input)

def test_billablevolumetype_validation():
    """Test validation for BillableVolumeType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(BillableVolumeType, example_input)


def test_billablevolumetype_validation_with_invalid_data():
    """Test validation failure for BillableVolumeType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BillableVolumeType.model_validate(invalid_input)

def test_blendview_validation():
    """Test validation for BlendView model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(BlendView, example_input)


def test_blendview_validation_with_invalid_data():
    """Test validation failure for BlendView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BlendView.model_validate(invalid_input)

def test_bolanddropresponse_validation():
    """Test validation for BolAndDropResponse model."""
    example_input = {
    "order_number": "example_order_number",
    "order_id": "example_order_id",
    "po": "example_po",
    "carrier_id": "example_carrier_id",
    "last_movement_update": "example_last_movement_update",
    "order_date": "example_order_date",
    "status": "example_status",
    "type": "example_type",
    "drops": "example_drops",
    "bols": "example_bols",
    "costs": "example_costs",
    "validation_bypass_on": "example_validation_bypass_on",
    "has_additives": "example_has_additives",
    "estimated_freight": "example_estimated_freight",
    "actual_freight": "example_actual_freight",
    "allocated_bol_error": "example_allocated_bol_error",
    "allocated_bol_issue": "example_allocated_bol_issue",
    "allocated_bols": "example_allocated_bols",
    "last_change_date": "example_last_change_date",
    "reference_order_number": "example_reference_order_number"
}

    generic_model_validation_test(BolAndDropResponse, example_input)


def test_bolanddropresponse_validation_with_invalid_data():
    """Test validation failure for BolAndDropResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BolAndDropResponse.model_validate(invalid_input)

def test_bolimageresponse_validation():
    """Test validation for BolImageResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(BolImageResponse, example_input)


def test_bolimageresponse_validation_with_invalid_data():
    """Test validation failure for BolImageResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BolImageResponse.model_validate(invalid_input)

def test_bolimagesrequest_validation():
    """Test validation for BolImagesRequest model."""
    example_input = {
    "order_ids": "example_order_ids",
    "order_numbers": "example_order_numbers"
}

    generic_model_validation_test(BolImagesRequest, example_input)


def test_bolimagesrequest_validation_with_invalid_data():
    """Test validation failure for BolImagesRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BolImagesRequest.model_validate(invalid_input)

def test_bolimagesresponse_validation():
    """Test validation for BolImagesResponse model."""
    example_input = {
    "order_id": "example_order_id",
    "bol_id": "example_bol_id",
    "bol_number": "example_bol_number",
    "photos": "example_photos"
}

    generic_model_validation_test(BolImagesResponse, example_input)


def test_bolimagesresponse_validation_with_invalid_data():
    """Test validation failure for BolImagesResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BolImagesResponse.model_validate(invalid_input)

def test_bolsanddropsrequest_validation():
    """Test validation for BolsAndDropsRequest model."""
    example_input = {
    "order_date_start": "example_order_date_start",
    "order_date_end": "example_order_date_end",
    "movement_updated_start": "example_movement_updated_start",
    "movement_updated_end": "example_movement_updated_end",
    "order_ids": "example_order_ids",
    "order_numbers": "example_order_numbers",
    "order_states": "example_order_states",
    "order_types": "example_order_types",
    "include_invalid": "example_include_invalid",
    "include_bol_allocation": "example_include_bol_allocation",
    "last_change_date": "example_last_change_date",
    "reference_order_numbers": "example_reference_order_numbers"
}

    generic_model_validation_test(BolsAndDropsRequest, example_input)


def test_bolsanddropsrequest_validation_with_invalid_data():
    """Test validation failure for BolsAndDropsRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        BolsAndDropsRequest.model_validate(invalid_input)

def test_card_validation():
    """Test validation for Card model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Card, example_input)


def test_card_validation_with_invalid_data():
    """Test validation failure for Card model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Card.model_validate(invalid_input)

def test_contractvolumerequest_validation():
    """Test validation for ContractVolumeRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ContractVolumeRequest, example_input)


def test_contractvolumerequest_validation_with_invalid_data():
    """Test validation failure for ContractVolumeRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ContractVolumeRequest.model_validate(invalid_input)

def test_coordinate_validation():
    """Test validation for Coordinate model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Coordinate, example_input)


def test_coordinate_validation_with_invalid_data():
    """Test validation failure for Coordinate model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Coordinate.model_validate(invalid_input)

def test_counterparty_validation():
    """Test validation for Counterparty model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Counterparty, example_input)


def test_counterparty_validation_with_invalid_data():
    """Test validation failure for Counterparty model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Counterparty.model_validate(invalid_input)

def test_counterpartyview_validation():
    """Test validation for CounterpartyView model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "goid": "example_goid",
    "scac": "example_scac",
    "types": "example_types",
    "carrier_type": "example_carrier_type",
    "trailer_config": "example_trailer_config",
    "source_id": "example_source_id",
    "source_system": "example_source_system",
    "source_system_id": "example_source_system_id",
    "emails": "example_emails",
    "sourcing_strategy": "example_sourcing_strategy",
    "extra_data": "example_extra_data",
    "updated_on": "example_updated_on",
    "allow_short_loads": "example_allow_short_loads",
    "order_notification_preferences": "example_order_notification_preferences",
    "supply_map": "example_supply_map"
}

    generic_model_validation_test(CounterpartyView, example_input)


def test_counterpartyview_validation_with_invalid_data():
    """Test validation failure for CounterpartyView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        CounterpartyView.model_validate(invalid_input)

def test_creategrouprequest_validation():
    """Test validation for CreateGroupRequest model."""
    example_input = {
    "source_id": "example_source_id",
    "name": "example_name",
    "keys": "example_keys",
    "as_of": "example_as_of",
    "min": "example_min",
    "max": "example_max",
    "start_hour": "example_start_hour",
    "volume_distributions": "example_volume_distributions",
    "contract_volumes": "example_contract_volumes",
    "daily_percent": "example_daily_percent",
    "weekly_percent": "example_weekly_percent",
    "monthly_percent": "example_monthly_percent",
    "contract_start": "example_contract_start",
    "contract_end": "example_contract_end",
    "week_start_day": "example_week_start_day"
}

    generic_model_validation_test(CreateGroupRequest, example_input)


def test_creategrouprequest_validation_with_invalid_data():
    """Test validation failure for CreateGroupRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        CreateGroupRequest.model_validate(invalid_input)

def test_datewindow_validation():
    """Test validation for DateWindow model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DateWindow, example_input)


def test_datewindow_validation_with_invalid_data():
    """Test validation failure for DateWindow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DateWindow.model_validate(invalid_input)

def test_daysofweek_validation():
    """Test validation for DaysOfWeek model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DaysOfWeek, example_input)


def test_daysofweek_validation_with_invalid_data():
    """Test validation failure for DaysOfWeek model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DaysOfWeek.model_validate(invalid_input)

def test_deliveryrequeststatus_validation():
    """Test validation for DeliveryRequestStatus model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DeliveryRequestStatus, example_input)


def test_deliveryrequeststatus_validation_with_invalid_data():
    """Test validation failure for DeliveryRequestStatus model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DeliveryRequestStatus.model_validate(invalid_input)

def test_deliveryticketbyid_validation():
    """Test validation for DeliveryTicketById model."""
    example_input = {
    "order_id": "example_order_id",
    "store_id": "example_store_id"
}

    generic_model_validation_test(DeliveryTicketById, example_input)


def test_deliveryticketbyid_validation_with_invalid_data():
    """Test validation failure for DeliveryTicketById model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DeliveryTicketById.model_validate(invalid_input)

def test_deliveryticketbynumber_validation():
    """Test validation for DeliveryTicketByNumber model."""
    example_input = {
    "order_number": 42,
    "store_number": "example_store_number"
}

    generic_model_validation_test(DeliveryTicketByNumber, example_input)


def test_deliveryticketbynumber_validation_with_invalid_data():
    """Test validation failure for DeliveryTicketByNumber model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DeliveryTicketByNumber.model_validate(invalid_input)

def test_deliverywindow_validation():
    """Test validation for DeliveryWindow model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DeliveryWindow, example_input)


def test_deliverywindow_validation_with_invalid_data():
    """Test validation failure for DeliveryWindow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DeliveryWindow.model_validate(invalid_input)

def test_deliverywindowdefault_validation():
    """Test validation for DeliveryWindowDefault model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DeliveryWindowDefault, example_input)


def test_deliverywindowdefault_validation_with_invalid_data():
    """Test validation failure for DeliveryWindowDefault model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DeliveryWindowDefault.model_validate(invalid_input)

def test_drivercredentialupsertrequest_validation():
    """Test validation for DriverCredentialUpsertRequest model."""
    example_input = {
    "driver_id": "example_driver_id",
    "credential_id": "example_credential_id",
    "certification_date": "example_certification_date",
    "expiration_date": "example_expiration_date"
}

    generic_model_validation_test(DriverCredentialUpsertRequest, example_input)


def test_drivercredentialupsertrequest_validation_with_invalid_data():
    """Test validation failure for DriverCredentialUpsertRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DriverCredentialUpsertRequest.model_validate(invalid_input)

def test_drivercredentialview_validation():
    """Test validation for DriverCredentialView model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DriverCredentialView, example_input)


def test_drivercredentialview_validation_with_invalid_data():
    """Test validation failure for DriverCredentialView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DriverCredentialView.model_validate(invalid_input)

def test_driverterminalcardview_validation():
    """Test validation for DriverTerminalCardView model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DriverTerminalCardView, example_input)


def test_driverterminalcardview_validation_with_invalid_data():
    """Test validation failure for DriverTerminalCardView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DriverTerminalCardView.model_validate(invalid_input)

def test_driverview_validation():
    """Test validation for DriverView model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "username": "example_username",
    "depot_id": "example_depot_id",
    "depot_name": "example_depot_name",
    "in_cab_trip_mode": "example_in_cab_trip_mode",
    "in_cab_supply_option_mode": "example_in_cab_supply_option_mode",
    "trailer_number": "example_trailer_number",
    "tractor_number": "example_tractor_number",
    "updated_on": "example_updated_on",
    "extra_data": "example_extra_data",
    "cards": "example_cards",
    "credentials": "example_credentials"
}

    generic_model_validation_test(DriverView, example_input)


def test_driverview_validation_with_invalid_data():
    """Test validation failure for DriverView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DriverView.model_validate(invalid_input)

def test_dropcreaterequest_validation():
    """Test validation for DropCreateRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DropCreateRequest, example_input)


def test_dropcreaterequest_validation_with_invalid_data():
    """Test validation failure for DropCreateRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DropCreateRequest.model_validate(invalid_input)

def test_dropworkflow_validation():
    """Test validation for DropWorkflow model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(DropWorkflow, example_input)


def test_dropworkflow_validation_with_invalid_data():
    """Test validation failure for DropWorkflow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        DropWorkflow.model_validate(invalid_input)

def test_dwell_validation():
    """Test validation for Dwell model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Dwell, example_input)


def test_dwell_validation_with_invalid_data():
    """Test validation failure for Dwell model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Dwell.model_validate(invalid_input)

def test_eboldetailrequest_validation():
    """Test validation for EBolDetailRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(EBolDetailRequest, example_input)


def test_eboldetailrequest_validation_with_invalid_data():
    """Test validation failure for EBolDetailRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        EBolDetailRequest.model_validate(invalid_input)

def test_ebolrequest_validation():
    """Test validation for EBolRequest model."""
    example_input = {
    "source_system": "example_source_system",
    "bol_number": "example_bol_number",
    "date": "example_date",
    "terminal_id": "example_terminal_id",
    "supplier_id": "example_supplier_id",
    "details": "example_details"
}

    generic_model_validation_test(EBolRequest, example_input)


def test_ebolrequest_validation_with_invalid_data():
    """Test validation failure for EBolRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        EBolRequest.model_validate(invalid_input)

def test_externalboldetailrequest_validation():
    """Test validation for ExternalBOLDetailRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ExternalBOLDetailRequest, example_input)


def test_externalboldetailrequest_validation_with_invalid_data():
    """Test validation failure for ExternalBOLDetailRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ExternalBOLDetailRequest.model_validate(invalid_input)

def test_externalbolrequest_validation():
    """Test validation for ExternalBOLRequest model."""
    example_input = {
    "order_id": "example_order_id",
    "bol_number": "example_bol_number",
    "terminal_id": "example_terminal_id",
    "bol_date": "example_bol_date",
    "details": "example_details"
}

    generic_model_validation_test(ExternalBOLRequest, example_input)


def test_externalbolrequest_validation_with_invalid_data():
    """Test validation failure for ExternalBOLRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ExternalBOLRequest.model_validate(invalid_input)

def test_forecastapicreaterequest_validation():
    """Test validation for ForecastApiCreateRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ForecastApiCreateRequest, example_input)


def test_forecastapicreaterequest_validation_with_invalid_data():
    """Test validation failure for ForecastApiCreateRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ForecastApiCreateRequest.model_validate(invalid_input)

def test_formfieldresponse_validation():
    """Test validation for FormFieldResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FormFieldResponse, example_input)


def test_formfieldresponse_validation_with_invalid_data():
    """Test validation failure for FormFieldResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FormFieldResponse.model_validate(invalid_input)

def test_formresponserow_validation():
    """Test validation for FormResponseRow model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "description": "example_description",
    "order_number": 42,
    "driver_name": "example_driver_name",
    "date": "example_date",
    "shift": "example_shift",
    "location_name": "example_location_name",
    "address": "example_address",
    "latitude": "example_latitude",
    "longitude": "example_longitude",
    "market": "example_market",
    "sector": "example_sector",
    "supply_zones": "example_supply_zones",
    "tractor": "example_tractor",
    "trailer_number": "example_trailer_number",
    "required": "example_required",
    "response": "example_response"
}

    generic_model_validation_test(FormResponseRow, example_input)


def test_formresponserow_validation_with_invalid_data():
    """Test validation failure for FormResponseRow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FormResponseRow.model_validate(invalid_input)

def test_freightcost_validation():
    """Test validation for FreightCost model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FreightCost, example_input)


def test_freightcost_validation_with_invalid_data():
    """Test validation failure for FreightCost model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightCost.model_validate(invalid_input)

def test_freightintegrationreq_validation():
    """Test validation for FreightIntegrationReq model."""
    example_input = {
    "order_numbers": "example_order_numbers",
    "order_ids": "example_order_ids",
    "last_change_date": "example_last_change_date"
}

    generic_model_validation_test(FreightIntegrationReq, example_input)


def test_freightintegrationreq_validation_with_invalid_data():
    """Test validation failure for FreightIntegrationReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightIntegrationReq.model_validate(invalid_input)

def test_freightitem_validation():
    """Test validation for FreightItem model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FreightItem, example_input)


def test_freightitem_validation_with_invalid_data():
    """Test validation failure for FreightItem model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightItem.model_validate(invalid_input)

def test_freighttransactiondetailoutput_validation():
    """Test validation for FreightTransactionDetailOutput model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FreightTransactionDetailOutput, example_input)


def test_freighttransactiondetailoutput_validation_with_invalid_data():
    """Test validation failure for FreightTransactionDetailOutput model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightTransactionDetailOutput.model_validate(invalid_input)

def test_freighttransactionoutput_validation():
    """Test validation for FreightTransactionOutput model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FreightTransactionOutput, example_input)


def test_freighttransactionoutput_validation_with_invalid_data():
    """Test validation failure for FreightTransactionOutput model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightTransactionOutput.model_validate(invalid_input)

def test_freighttransactionrowoutput_validation():
    """Test validation for FreightTransactionRowOutput model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(FreightTransactionRowOutput, example_input)


def test_freighttransactionrowoutput_validation_with_invalid_data():
    """Test validation failure for FreightTransactionRowOutput model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        FreightTransactionRowOutput.model_validate(invalid_input)

def test_getorderrequestresponse_validation():
    """Test validation for GetOrderRequestResponse model."""
    example_input = {
    "type": "example_type",
    "number": 42,
    "order_id": "example_order_id",
    "order_number": "example_order_number",
    "order_date": "example_order_date",
    "order_state": "example_order_state",
    "reference_order_number": "example_reference_order_number",
    "last_change_date": "example_last_change_date",
    "site_name": "example_site_name",
    "site_id": "example_site_id",
    "customer_id": "example_customer_id",
    "customer_name": "example_customer_name",
    "delivery_window_start": "example_delivery_window_start",
    "delivery_window_end": "example_delivery_window_end",
    "products": "example_products",
    "extra_data": "example_extra_data",
    "status": "example_status"
}

    generic_model_validation_test(GetOrderRequestResponse, example_input)


def test_getorderrequestresponse_validation_with_invalid_data():
    """Test validation failure for GetOrderRequestResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        GetOrderRequestResponse.model_validate(invalid_input)

def test_getorderresponse_validation():
    """Test validation for GetOrderResponse model."""
    example_input = {
    "type": "example_type",
    "order_id": "example_order_id",
    "drivers": "example_drivers",
    "order_number": "example_order_number",
    "order_date": "example_order_date",
    "order_state": "example_order_state",
    "carrier_window_start": "example_carrier_window_start",
    "carrier_window_end": "example_carrier_window_end",
    "carrier_notify_state": "example_carrier_notify_state",
    "load_window_start": "example_load_window_start",
    "load_window_end": "example_load_window_end",
    "dispatch_window_start": "example_dispatch_window_start",
    "dispatch_window_end": "example_dispatch_window_end",
    "hauler_counterparty_id": "example_hauler_counterparty_id",
    "hauler_counterparty_name": "example_hauler_counterparty_name",
    "hauler_counterparty_source_id": "example_hauler_counterparty_source_id",
    "hauler_counterparty_source_system": "example_hauler_counterparty_source_system",
    "hauled_by_updated_by": "example_hauled_by_updated_by",
    "hauled_by_updated": "example_hauled_by_updated",
    "loads": "example_loads",
    "drops": "example_drops",
    "trip_status": "example_trip_status",
    "last_change_date": "example_last_change_date",
    "market": "example_market",
    "supply_option": "example_supply_option",
    "created_by": "example_created_by",
    "note": "example_note",
    "estimated_load_minutes": "example_estimated_load_minutes",
    "total_miles": "example_total_miles",
    "loaded_miles": "example_loaded_miles",
    "unloaded_miles": "example_unloaded_miles",
    "reference_order_number": "example_reference_order_number",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(GetOrderResponse, example_input)


def test_getorderresponse_validation_with_invalid_data():
    """Test validation failure for GetOrderResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        GetOrderResponse.model_validate(invalid_input)

def test_getordersrequest_validation():
    """Test validation for GetOrdersRequest model."""
    example_input = {
    "order_id": "example_order_id",
    "order_number": "example_order_number",
    "type": "example_type",
    "state": "example_state",
    "last_change_date": "example_last_change_date",
    "order_date_start": "example_order_date_start",
    "order_date_end": "example_order_date_end",
    "reference_order_number": "example_reference_order_number",
    "order_date": "example_order_date"
}

    generic_model_validation_test(GetOrdersRequest, example_input)


def test_getordersrequest_validation_with_invalid_data():
    """Test validation failure for GetOrdersRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        GetOrdersRequest.model_validate(invalid_input)

def test_httpvalidationerror_validation():
    """Test validation for HTTPValidationError model."""
    example_input = {
    "detail": "example_detail"
}

    generic_model_validation_test(HTTPValidationError, example_input)


def test_httpvalidationerror_validation_with_invalid_data():
    """Test validation failure for HTTPValidationError model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        HTTPValidationError.model_validate(invalid_input)

def test_importrequest_validation():
    """Test validation for ImportRequest model."""
    example_input = {
    "reqs": "example_reqs"
}

    generic_model_validation_test(ImportRequest, example_input)


def test_importrequest_validation_with_invalid_data():
    """Test validation failure for ImportRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ImportRequest.model_validate(invalid_input)

def test_incabsupplyoptionmode_validation():
    """Test validation for InCabSupplyOptionMode model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InCabSupplyOptionMode, example_input)


def test_incabsupplyoptionmode_validation_with_invalid_data():
    """Test validation failure for InCabSupplyOptionMode model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InCabSupplyOptionMode.model_validate(invalid_input)

def test_incabtripmode_validation():
    """Test validation for InCabTripMode model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InCabTripMode, example_input)


def test_incabtripmode_validation_with_invalid_data():
    """Test validation failure for InCabTripMode model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InCabTripMode.model_validate(invalid_input)

def test_innetworksupplyzone_validation():
    """Test validation for InNetworkSupplyZone model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InNetworkSupplyZone, example_input)


def test_innetworksupplyzone_validation_with_invalid_data():
    """Test validation failure for InNetworkSupplyZone model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InNetworkSupplyZone.model_validate(invalid_input)

def test_innetworkterminal_validation():
    """Test validation for InNetworkTerminal model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InNetworkTerminal, example_input)


def test_innetworkterminal_validation_with_invalid_data():
    """Test validation failure for InNetworkTerminal model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InNetworkTerminal.model_validate(invalid_input)

def test_integrationformresponseoverviewreq_validation():
    """Test validation for IntegrationFormResponseOverviewReq model."""
    example_input = {
    "form_name": "example_form_name",
    "from_date": "example_from_date",
    "to_date": "example_to_date",
    "market": "example_market"
}

    generic_model_validation_test(IntegrationFormResponseOverviewReq, example_input)


def test_integrationformresponseoverviewreq_validation_with_invalid_data():
    """Test validation failure for IntegrationFormResponseOverviewReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        IntegrationFormResponseOverviewReq.model_validate(invalid_input)

def test_invoiceallreq_validation():
    """Test validation for InvoiceAllReq model."""
    example_input = {
    "order_numbers": "example_order_numbers",
    "order_ids": "example_order_ids",
    "invoice_numbers": "example_invoice_numbers",
    "status": "example_status",
    "counterparty_name": "example_counterparty_name",
    "counterparty_id": "example_counterparty_id",
    "book_type": "example_book_type",
    "as_of": "example_as_of",
    "between": "example_between"
}

    generic_model_validation_test(InvoiceAllReq, example_input)


def test_invoiceallreq_validation_with_invalid_data():
    """Test validation failure for InvoiceAllReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InvoiceAllReq.model_validate(invalid_input)

def test_invoicedynamicstatus_validation():
    """Test validation for InvoiceDynamicStatus model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InvoiceDynamicStatus, example_input)


def test_invoicedynamicstatus_validation_with_invalid_data():
    """Test validation failure for InvoiceDynamicStatus model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InvoiceDynamicStatus.model_validate(invalid_input)

def test_invoicerow_validation():
    """Test validation for InvoiceRow model."""
    example_input = {
    "invoice_number": "example_invoice_number",
    "sent_date": "example_sent_date",
    "when_to_send_date": "example_when_to_send_date",
    "created_on": "example_created_on",
    "type": "example_type",
    "status": "example_status",
    "transactions": "example_transactions",
    "note": "example_note",
    "base_amount": 3.14,
    "base_distance": 3.14,
    "distance_uom": "example_distance_uom",
    "accessorial_amount": 3.14,
    "surcharge_amount": 3.14,
    "total_amount": 3.14
}

    generic_model_validation_test(InvoiceRow, example_input)


def test_invoicerow_validation_with_invalid_data():
    """Test validation failure for InvoiceRow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InvoiceRow.model_validate(invalid_input)

def test_invoicestaticstatus_validation():
    """Test validation for InvoiceStaticStatus model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InvoiceStaticStatus, example_input)


def test_invoicestaticstatus_validation_with_invalid_data():
    """Test validation failure for InvoiceStaticStatus model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InvoiceStaticStatus.model_validate(invalid_input)

def test_invoicetype_validation():
    """Test validation for InvoiceType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(InvoiceType, example_input)


def test_invoicetype_validation_with_invalid_data():
    """Test validation failure for InvoiceType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        InvoiceType.model_validate(invalid_input)

def test_key_validation():
    """Test validation for Key model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Key, example_input)


def test_key_validation_with_invalid_data():
    """Test validation failure for Key model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Key.model_validate(invalid_input)

def test_locationresponse_validation():
    """Test validation for LocationResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(LocationResponse, example_input)


def test_locationresponse_validation_with_invalid_data():
    """Test validation failure for LocationResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        LocationResponse.model_validate(invalid_input)

def test_locationview_validation():
    """Test validation for LocationView model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "short_name": "example_short_name",
    "market": "example_market",
    "market_id": "example_market_id",
    "freight_region_name": "example_freight_region_name",
    "freight_region_id": "example_freight_region_id",
    "type": "example_type",
    "lat": "example_lat",
    "lon": "example_lon",
    "address": "example_address",
    "phone": "example_phone",
    "city": "example_city",
    "state": "example_state",
    "active": "example_active",
    "postal_code": "example_postal_code",
    "source_id": "example_source_id",
    "source_system": "example_source_system",
    "source_system_id": "example_source_system_id",
    "timezone": "example_timezone",
    "supply_zones": "example_supply_zones",
    "updated_on": "example_updated_on",
    "cards": "example_cards",
    "dwells": "example_dwells",
    "requires_card": "example_requires_card",
    "geofence": "example_geofence",
    "supply_map": "example_supply_map",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(LocationView, example_input)


def test_locationview_validation_with_invalid_data():
    """Test validation failure for LocationView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        LocationView.model_validate(invalid_input)

def test_marketschemasectorview_validation():
    """Test validation for MarketSchemaSectorView model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(MarketSchemaSectorView, example_input)


def test_marketschemasectorview_validation_with_invalid_data():
    """Test validation failure for MarketSchemaSectorView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        MarketSchemaSectorView.model_validate(invalid_input)

def test_marketview_validation():
    """Test validation for MarketView model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "network_radius": "example_network_radius",
    "active": "example_active",
    "trailer_config": "example_trailer_config",
    "updated_on": "example_updated_on",
    "extra_data": "example_extra_data",
    "sectors": "example_sectors",
    "delivery_window_default": "example_delivery_window_default"
}

    generic_model_validation_test(MarketView, example_input)


def test_marketview_validation_with_invalid_data():
    """Test validation failure for MarketView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        MarketView.model_validate(invalid_input)

def test_monitoringstrategy_validation():
    """Test validation for MonitoringStrategy model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(MonitoringStrategy, example_input)


def test_monitoringstrategy_validation_with_invalid_data():
    """Test validation failure for MonitoringStrategy model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        MonitoringStrategy.model_validate(invalid_input)

def test_nosupplyoptionresponse_validation():
    """Test validation for NOSupplyOptionResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(NOSupplyOptionResponse, example_input)


def test_nosupplyoptionresponse_validation_with_invalid_data():
    """Test validation failure for NOSupplyOptionResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        NOSupplyOptionResponse.model_validate(invalid_input)

def test_optimalsupplyreportrequest_validation():
    """Test validation for OptimalSupplyReportRequest model."""
    example_input = {
    "order_numbers": "example_order_numbers",
    "order_ids": "example_order_ids",
    "order_date_start": "example_order_date_start",
    "order_date_end": "example_order_date_end",
    "movement_updated_start": "example_movement_updated_start",
    "movement_updated_end": "example_movement_updated_end",
    "last_change_date": "example_last_change_date"
}

    generic_model_validation_test(OptimalSupplyReportRequest, example_input)


def test_optimalsupplyreportrequest_validation_with_invalid_data():
    """Test validation failure for OptimalSupplyReportRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OptimalSupplyReportRequest.model_validate(invalid_input)

def test_optimalsupplyreportrow_validation():
    """Test validation for OptimalSupplyReportRow model."""
    example_input = {
    "order_number": 42,
    "order_id": "example_order_id",
    "site_number": "example_site_number",
    "actual_component_product": "example_actual_component_product",
    "actual_component_product_id": "example_actual_component_product_id",
    "optimal_component_product": "example_optimal_component_product",
    "optimal_component_product_id": "example_optimal_component_product_id",
    "actual_terminal": "example_actual_terminal",
    "actual_terminal_id": "example_actual_terminal_id",
    "optimal_terminal": "example_optimal_terminal",
    "optimal_terminal_id": "example_optimal_terminal_id",
    "actual_supplier": "example_actual_supplier",
    "actual_supplier_id": "example_actual_supplier_id",
    "optimal_supplier": "example_optimal_supplier",
    "optimal_supplier_id": "example_optimal_supplier_id",
    "actual_price_type": "example_actual_price_type",
    "optimal_price_type": "example_optimal_price_type",
    "actual_contract": "example_actual_contract",
    "optimal_contract": "example_optimal_contract",
    "actual_curve_id": "example_actual_curve_id",
    "optimal_curve_id": "example_optimal_curve_id",
    "actual_price_id": "example_actual_price_id",
    "optimal_price_id": "example_optimal_price_id",
    "actual_loaded_miles": 3.14,
    "optimal_loaded_miles": 3.14,
    "actual_product_price": 3.14,
    "optimal_product_price": 3.14,
    "actual_freight_rate": 3.14,
    "optimal_freight_rate": 3.14,
    "actual_total_price": 3.14,
    "optimal_total_price": 3.14,
    "total_price_delta": 3.14,
    "actual_volume": 3.14,
    "optimal_volume": 3.14,
    "last_change_date": "example_last_change_date",
    "last_updated_date": "example_last_updated_date",
    "reason_code": "example_reason_code"
}

    generic_model_validation_test(OptimalSupplyReportRow, example_input)


def test_optimalsupplyreportrow_validation_with_invalid_data():
    """Test validation failure for OptimalSupplyReportRow model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OptimalSupplyReportRow.model_validate(invalid_input)

def test_ordercreaterequest_validation():
    """Test validation for OrderCreateRequest model."""
    example_input = {
    "reference_order_number": "example_reference_order_number",
    "supply_owner": "example_supply_owner",
    "sourcing_strategy": "example_sourcing_strategy",
    "manual_supply_fallback": "example_manual_supply_fallback",
    "allow_alternate_products": "example_allow_alternate_products",
    "delivery_window": "example_delivery_window",
    "fit_to_trailer": "example_fit_to_trailer",
    "note": "example_note",
    "drops": "example_drops",
    "accept_by": "example_accept_by",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(OrderCreateRequest, example_input)


def test_ordercreaterequest_validation_with_invalid_data():
    """Test validation failure for OrderCreateRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(invalid_input)

def test_ordercreateresponse_validation():
    """Test validation for OrderCreateResponse model."""
    example_input = {
    "status": "example_status",
    "order_number": "example_order_number",
    "order": "example_order",
    "errors": "example_errors",
    "accept_by": "example_accept_by",
    "reference_order_number": "example_reference_order_number",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(OrderCreateResponse, example_input)


def test_ordercreateresponse_validation_with_invalid_data():
    """Test validation failure for OrderCreateResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderCreateResponse.model_validate(invalid_input)

def test_ordercreatestatus_validation():
    """Test validation for OrderCreateStatus model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderCreateStatus, example_input)


def test_ordercreatestatus_validation_with_invalid_data():
    """Test validation failure for OrderCreateStatus model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderCreateStatus.model_validate(invalid_input)

def test_orderdriver_validation():
    """Test validation for OrderDriver model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderDriver, example_input)


def test_orderdriver_validation_with_invalid_data():
    """Test validation failure for OrderDriver model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderDriver.model_validate(invalid_input)

def test_orderfreightresp_validation():
    """Test validation for OrderFreightResp model."""
    example_input = {
    "number": 42,
    "po": "example_po",
    "freight_rate": 3.14,
    "freight_total": 3.14,
    "freight_items": "example_freight_items"
}

    generic_model_validation_test(OrderFreightResp, example_input)


def test_orderfreightresp_validation_with_invalid_data():
    """Test validation failure for OrderFreightResp model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderFreightResp.model_validate(invalid_input)

def test_orderfreightrespv2_validation():
    """Test validation for OrderFreightRespV2 model."""
    example_input = {
    "number": 42,
    "po": "example_po",
    "freight_rate": 3.14,
    "freight_total": 3.14,
    "freight_items": "example_freight_items"
}

    generic_model_validation_test(OrderFreightRespV2, example_input)


def test_orderfreightrespv2_validation_with_invalid_data():
    """Test validation failure for OrderFreightRespV2 model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderFreightRespV2.model_validate(invalid_input)

def test_orderreqnotificationstates_validation():
    """Test validation for OrderReqNotificationStates model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderReqNotificationStates, example_input)


def test_orderreqnotificationstates_validation_with_invalid_data():
    """Test validation failure for OrderReqNotificationStates model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderReqNotificationStates.model_validate(invalid_input)

def test_orderresponse_validation():
    """Test validation for OrderResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderResponse, example_input)


def test_orderresponse_validation_with_invalid_data():
    """Test validation failure for OrderResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderResponse.model_validate(invalid_input)

def test_orderschemabolresponse_validation():
    """Test validation for OrderSchemaBolResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderSchemaBolResponse, example_input)


def test_orderschemabolresponse_validation_with_invalid_data():
    """Test validation failure for OrderSchemaBolResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderSchemaBolResponse.model_validate(invalid_input)

def test_orderschemadropresponse_validation():
    """Test validation for OrderSchemaDropResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderSchemaDropResponse, example_input)


def test_orderschemadropresponse_validation_with_invalid_data():
    """Test validation failure for OrderSchemaDropResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderSchemaDropResponse.model_validate(invalid_input)

def test_orderstate_validation():
    """Test validation for OrderState model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderState, example_input)


def test_orderstate_validation_with_invalid_data():
    """Test validation failure for OrderState model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderState.model_validate(invalid_input)

def test_orderstatusupdaterequest_validation():
    """Test validation for OrderStatusUpdateRequest model."""
    example_input = {
    "order_id": "example_order_id",
    "order_number": "example_order_number",
    "status": "example_status",
    "location_id": "example_location_id",
    "eta": "example_eta",
    "actual": "example_actual"
}

    generic_model_validation_test(OrderStatusUpdateRequest, example_input)


def test_orderstatusupdaterequest_validation_with_invalid_data():
    """Test validation failure for OrderStatusUpdateRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderStatusUpdateRequest.model_validate(invalid_input)

def test_ordertype_validation():
    """Test validation for OrderType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(OrderType, example_input)


def test_ordertype_validation_with_invalid_data():
    """Test validation failure for OrderType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        OrderType.model_validate(invalid_input)

def test_payrollexportdetailmodel_validation():
    """Test validation for PayrollExportDetailModel model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(PayrollExportDetailModel, example_input)


def test_payrollexportdetailmodel_validation_with_invalid_data():
    """Test validation failure for PayrollExportDetailModel model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PayrollExportDetailModel.model_validate(invalid_input)

def test_payrollexportdetailresponse_validation():
    """Test validation for PayrollExportDetailResponse model."""
    example_input = {
    "driver_name": "example_driver_name",
    "driver_source_id": "example_driver_source_id",
    "driver_source_system": "example_driver_source_system",
    "end_date": "example_end_date",
    "hours_worked": 3.14,
    "pay_earned": 3.14,
    "payroll_config": "example_payroll_config",
    "start_date": "example_start_date",
    "status": "example_status",
    "updated": "example_updated",
    "detail": "example_detail"
}

    generic_model_validation_test(PayrollExportDetailResponse, example_input)


def test_payrollexportdetailresponse_validation_with_invalid_data():
    """Test validation failure for PayrollExportDetailResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PayrollExportDetailResponse.model_validate(invalid_input)

def test_priceallrequest_validation():
    """Test validation for PriceAllRequest model."""
    example_input = {
    "as_of": "example_as_of",
    "last_change_date": "example_last_change_date",
    "terminals": "example_terminals",
    "suppliers": "example_suppliers",
    "products": "example_products",
    "price_types": "example_price_types",
    "product_groups": "example_product_groups"
}

    generic_model_validation_test(PriceAllRequest, example_input)


def test_priceallrequest_validation_with_invalid_data():
    """Test validation failure for PriceAllRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PriceAllRequest.model_validate(invalid_input)

def test_priceresponse_validation():
    """Test validation for PriceResponse model."""
    example_input = {
    "curve_id": "example_curve_id",
    "price_id": "example_price_id",
    "city": "example_city",
    "contract": "example_contract",
    "product": "example_product",
    "product_id": "example_product_id",
    "supplier": "example_supplier",
    "supplier_id": "example_supplier_id",
    "counterparty": "example_counterparty",
    "counterparty_id": "example_counterparty_id",
    "terminal": "example_terminal",
    "terminal_id": "example_terminal_id",
    "store_number": "example_store_number",
    "store_id": "example_store_id",
    "price_type": "example_price_type",
    "product_group": "example_product_group",
    "price": 3.14,
    "effective_from": "example_effective_from",
    "effective_to": "example_effective_to",
    "expire": "example_expire",
    "disabled": true,
    "disabled_by": "example_disabled_by",
    "disabled_until": "example_disabled_until",
    "disabled_reason": "example_disabled_reason",
    "updated_by": "example_updated_by",
    "updated_on": "example_updated_on",
    "extra_data": "example_extra_data",
    "group_id": "example_group_id",
    "group_effective_cutover": "example_group_effective_cutover",
    "group_effective_cutover_timezone": "example_group_effective_cutover_timezone",
    "group_identifier": "example_group_identifier",
    "group_name": "example_group_name",
    "min_constraint": "example_min_constraint",
    "max_constraint": "example_max_constraint",
    "created_on": "example_created_on",
    "net_or_gross_type": "example_net_or_gross_type",
    "contract_lifting_valuation_method": "example_contract_lifting_valuation_method"
}

    generic_model_validation_test(PriceResponse, example_input)


def test_priceresponse_validation_with_invalid_data():
    """Test validation failure for PriceResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PriceResponse.model_validate(invalid_input)

def test_pricetype_validation():
    """Test validation for PriceType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(PriceType, example_input)


def test_pricetype_validation_with_invalid_data():
    """Test validation failure for PriceType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PriceType.model_validate(invalid_input)

def test_productgroups_validation():
    """Test validation for ProductGroups model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ProductGroups, example_input)


def test_productgroups_validation_with_invalid_data():
    """Test validation failure for ProductGroups model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ProductGroups.model_validate(invalid_input)

def test_productidname_validation():
    """Test validation for ProductIDName model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ProductIDName, example_input)


def test_productidname_validation_with_invalid_data():
    """Test validation failure for ProductIDName model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ProductIDName.model_validate(invalid_input)

def test_productview_validation():
    """Test validation for ProductView model."""
    example_input = {
    "id": "example_id",
    "name": "example_name",
    "short_name": "example_short_name",
    "group": "example_group",
    "weight_group": "example_weight_group",
    "icon": "example_icon",
    "source_id": "example_source_id",
    "source_system": "example_source_system",
    "source_system_id": "example_source_system_id",
    "extra_data": "example_extra_data",
    "blends": "example_blends",
    "alternate_products": "example_alternate_products",
    "updated_on": "example_updated_on",
    "tank_lid_code_id": "example_tank_lid_code_id",
    "supply_map": "example_supply_map"
}

    generic_model_validation_test(ProductView, example_input)


def test_productview_validation_with_invalid_data():
    """Test validation failure for ProductView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ProductView.model_validate(invalid_input)

def test_pydanticobjectid_validation():
    """Test validation for PydanticObjectId model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(PydanticObjectId, example_input)


def test_pydanticobjectid_validation_with_invalid_data():
    """Test validation failure for PydanticObjectId model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        PydanticObjectId.model_validate(invalid_input)

def test_ratebooktype_validation():
    """Test validation for RateBookType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(RateBookType, example_input)


def test_ratebooktype_validation_with_invalid_data():
    """Test validation failure for RateBookType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        RateBookType.model_validate(invalid_input)

def test_rootmodel_validation():
    """Test validation for RootModel model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(RootModel, example_input)


def test_rootmodel_validation_with_invalid_data():
    """Test validation failure for RootModel model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        RootModel.model_validate(invalid_input)

def test_routeupsertreq_validation():
    """Test validation for RouteUpsertReq model."""
    example_input = {
    "origin_name": "example_origin_name",
    "destination_name": "example_destination_name",
    "api_distance_miles": "example_api_distance_miles",
    "api_travel_time_seconds": "example_api_travel_time_seconds",
    "override_travel_time_seconds": "example_override_travel_time_seconds",
    "override_distance_miles": "example_override_distance_miles",
    "override_payroll_miles": "example_override_payroll_miles"
}

    generic_model_validation_test(RouteUpsertReq, example_input)


def test_routeupsertreq_validation_with_invalid_data():
    """Test validation failure for RouteUpsertReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        RouteUpsertReq.model_validate(invalid_input)

def test_salesadjusteddeliveryupsertreq_validation():
    """Test validation for SalesAdjustedDeliveryUpsertReq model."""
    example_input = {
    "source": "example_source",
    "store_id": "example_store_id",
    "tank_id": "example_tank_id",
    "product_id": "example_product_id",
    "volume": 3.14,
    "date": "example_date"
}

    generic_model_validation_test(SalesAdjustedDeliveryUpsertReq, example_input)


def test_salesadjusteddeliveryupsertreq_validation_with_invalid_data():
    """Test validation failure for SalesAdjustedDeliveryUpsertReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SalesAdjustedDeliveryUpsertReq.model_validate(invalid_input)

def test_savedropdetail_validation():
    """Test validation for SaveDropDetail model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SaveDropDetail, example_input)


def test_savedropdetail_validation_with_invalid_data():
    """Test validation failure for SaveDropDetail model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SaveDropDetail.model_validate(invalid_input)

def test_savedropmode_validation():
    """Test validation for SaveDropMode model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SaveDropMode, example_input)


def test_savedropmode_validation_with_invalid_data():
    """Test validation failure for SaveDropMode model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SaveDropMode.model_validate(invalid_input)

def test_savedropreq_validation():
    """Test validation for SaveDropReq model."""
    example_input = {
    "mode": "example_mode",
    "order_id": "example_order_id",
    "location_id": "example_location_id",
    "details": "example_details"
}

    generic_model_validation_test(SaveDropReq, example_input)


def test_savedropreq_validation_with_invalid_data():
    """Test validation failure for SaveDropReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SaveDropReq.model_validate(invalid_input)

def test_shift_validation():
    """Test validation for Shift model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(Shift, example_input)


def test_shift_validation_with_invalid_data():
    """Test validation failure for Shift model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        Shift.model_validate(invalid_input)

def test_sourcemap_validation():
    """Test validation for SourceMap model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SourceMap, example_input)


def test_sourcemap_validation_with_invalid_data():
    """Test validation failure for SourceMap model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SourceMap.model_validate(invalid_input)

def test_sourcingstrategy_validation():
    """Test validation for SourcingStrategy model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SourcingStrategy, example_input)


def test_sourcingstrategy_validation_with_invalid_data():
    """Test validation failure for SourcingStrategy model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SourcingStrategy.model_validate(invalid_input)

def test_statusupdate_validation():
    """Test validation for StatusUpdate model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(StatusUpdate, example_input)


def test_statusupdate_validation_with_invalid_data():
    """Test validation failure for StatusUpdate model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        StatusUpdate.model_validate(invalid_input)

def test_storestatus_validation():
    """Test validation for StoreStatus model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(StoreStatus, example_input)


def test_storestatus_validation_with_invalid_data():
    """Test validation failure for StoreStatus model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        StoreStatus.model_validate(invalid_input)

def test_storetank_validation():
    """Test validation for StoreTank model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(StoreTank, example_input)


def test_storetank_validation_with_invalid_data():
    """Test validation failure for StoreTank model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        StoreTank.model_validate(invalid_input)

def test_storev2_validation():
    """Test validation for StoreV2 model."""
    example_input = {
    "field_id": "example_field_id",
    "store_number": "example_store_number",
    "name": "example_name",
    "market": "example_market",
    "market_id": "example_market_id",
    "sector": "example_sector",
    "sector_id": "example_sector_id",
    "tanks": "example_tanks",
    "lat": "example_lat",
    "lon": "example_lon",
    "address": "example_address",
    "city": "example_city",
    "state": "example_state",
    "postal_code": "example_postal_code",
    "contact_name": "example_contact_name",
    "phone_number": "example_phone_number",
    "emails": "example_emails",
    "hours": "example_hours",
    "timezone": "example_timezone",
    "status": "example_status",
    "drop_workflow": "example_drop_workflow",
    "open_date": "example_open_date",
    "close_date": "example_close_date",
    "unavailable_hours": "example_unavailable_hours",
    "counterparty_id": "example_counterparty_id",
    "counterparty_name": "example_counterparty_name",
    "in_network_terminals": "example_in_network_terminals",
    "in_network_supply_zones": "example_in_network_supply_zones",
    "supply_owner_id": "example_supply_owner_id",
    "supply_owner_name": "example_supply_owner_name",
    "freight_customer_id": "example_freight_customer_id",
    "freight_customer_name": "example_freight_customer_name",
    "freight_region_name": "example_freight_region_name",
    "freight_region_id": "example_freight_region_id",
    "layout_file": "example_layout_file",
    "layout_file_uploaded": "example_layout_file_uploaded",
    "auto_order_disabled": "example_auto_order_disabled",
    "updated_id": "example_updated_id",
    "trailer_config": "example_trailer_config",
    "monitoring_strategy": "example_monitoring_strategy",
    "estick_monitor_override": "example_estick_monitor_override",
    "notes": "example_notes",
    "updated_on": "example_updated_on",
    "updated_by": "example_updated_by",
    "extra_data": "example_extra_data",
    "credit_hold": "example_credit_hold",
    "compliance_hold_date": "example_compliance_hold_date",
    "delivery_window_default_name": "example_delivery_window_default_name",
    "delivery_window_default_id": "example_delivery_window_default_id",
    "allow_by_product_request": "example_allow_by_product_request",
    "geofence": "example_geofence"
}

    generic_model_validation_test(StoreV2, example_input)


def test_storev2_validation_with_invalid_data():
    """Test validation failure for StoreV2 model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        StoreV2.model_validate(invalid_input)

def test_supplypriceupdatemanyrequest_validation():
    """Test validation for SupplyPriceUpdateManyRequest model."""
    example_input = {
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "contract": "example_contract",
    "timezone": "example_timezone",
    "effective_from": "example_effective_from",
    "effective_to": "example_effective_to",
    "price": 3.14,
    "price_type": "example_price_type",
    "terminal_id": "example_terminal_id",
    "terminal_source_id": "example_terminal_source_id",
    "terminal_source_system_id": "example_terminal_source_system_id",
    "terminal": "example_terminal",
    "product_id": "example_product_id",
    "product_source_id": "example_product_source_id",
    "product_source_system_id": "example_product_source_system_id",
    "product": "example_product",
    "supplier_id": "example_supplier_id",
    "supplier_source_id": "example_supplier_source_id",
    "supplier_source_system_id": "example_supplier_source_system_id",
    "supplier": "example_supplier",
    "counterparty_id": "example_counterparty_id",
    "counterparty_source_id": "example_counterparty_source_id",
    "counterparty_source_system_id": "example_counterparty_source_system_id",
    "counterparty": "example_counterparty",
    "store_id": "example_store_id",
    "store_source_id": "example_store_source_id",
    "store_source_system_id": "example_store_source_system_id",
    "store_number": "example_store_number",
    "enabled": "example_enabled",
    "disabled_until": "example_disabled_until",
    "expire": "example_expire",
    "min_quantity": "example_min_quantity",
    "max_quantity": "example_max_quantity",
    "curve_id": "example_curve_id",
    "error": "example_error",
    "row": "example_row",
    "net_or_gross_type": "example_net_or_gross_type",
    "contract_lifting_valuation_method": "example_contract_lifting_valuation_method"
}

    generic_model_validation_test(SupplyPriceUpdateManyRequest, example_input)


def test_supplypriceupdatemanyrequest_validation_with_invalid_data():
    """Test validation failure for SupplyPriceUpdateManyRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SupplyPriceUpdateManyRequest.model_validate(invalid_input)

def test_supplypriceupdateresponse_validation():
    """Test validation for SupplyPriceUpdateResponse model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SupplyPriceUpdateResponse, example_input)


def test_supplypriceupdateresponse_validation_with_invalid_data():
    """Test validation failure for SupplyPriceUpdateResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SupplyPriceUpdateResponse.model_validate(invalid_input)

def test_surchargeallreq_validation():
    """Test validation for SurchargeAllReq model."""
    example_input = {
    "counterparty_name": "example_counterparty_name",
    "counterparty_id": "example_counterparty_id",
    "book_type": "example_book_type",
    "as_of": "example_as_of",
    "product_group": "example_product_group",
    "freight_region_name": "example_freight_region_name",
    "freight_region_id": "example_freight_region_id"
}

    generic_model_validation_test(SurchargeAllReq, example_input)


def test_surchargeallreq_validation_with_invalid_data():
    """Test validation failure for SurchargeAllReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SurchargeAllReq.model_validate(invalid_input)

def test_surchargeallresp_validation():
    """Test validation for SurchargeAllResp model."""
    example_input = {
    "id": "example_id",
    "counterparty": "example_counterparty",
    "counterparty_id": "example_counterparty_id",
    "product_group": "example_product_group",
    "book_type": "example_book_type",
    "freight_region_id": "example_freight_region_id",
    "freight_region_name": "example_freight_region_name",
    "type": "example_type",
    "effective_from": "example_effective_from",
    "effective_to": "example_effective_to",
    "surcharge": "example_surcharge",
    "created_on": "example_created_on",
    "created_by": "example_created_by"
}

    generic_model_validation_test(SurchargeAllResp, example_input)


def test_surchargeallresp_validation_with_invalid_data():
    """Test validation failure for SurchargeAllResp model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SurchargeAllResp.model_validate(invalid_input)

def test_surchargecreatereq_validation():
    """Test validation for SurchargeCreateReq model."""
    example_input = {
    "counterparty_name": "example_counterparty_name",
    "counterparty_id": "example_counterparty_id",
    "product_group": "example_product_group",
    "book_type": "example_book_type",
    "freight_region_id": "example_freight_region_id",
    "freight_region_name": "example_freight_region_name",
    "type": "example_type",
    "effective_from": "example_effective_from",
    "effective_to": "example_effective_to",
    "surcharge": "example_surcharge"
}

    generic_model_validation_test(SurchargeCreateReq, example_input)


def test_surchargecreatereq_validation_with_invalid_data():
    """Test validation failure for SurchargeCreateReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SurchargeCreateReq.model_validate(invalid_input)

def test_surchargetype_validation():
    """Test validation for SurchargeType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(SurchargeType, example_input)


def test_surchargetype_validation_with_invalid_data():
    """Test validation failure for SurchargeType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SurchargeType.model_validate(invalid_input)

def test_surchargeupdatereq_validation():
    """Test validation for SurchargeUpdateReq model."""
    example_input = {
    "id": "example_id",
    "effective_from": "example_effective_from",
    "effective_to": "example_effective_to",
    "surcharge": "example_surcharge"
}

    generic_model_validation_test(SurchargeUpdateReq, example_input)


def test_surchargeupdatereq_validation_with_invalid_data():
    """Test validation failure for SurchargeUpdateReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        SurchargeUpdateReq.model_validate(invalid_input)

def test_tanklidenum_validation():
    """Test validation for TankLidEnum model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(TankLidEnum, example_input)


def test_tanklidenum_validation_with_invalid_data():
    """Test validation failure for TankLidEnum model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TankLidEnum.model_validate(invalid_input)

def test_terminaltype_validation():
    """Test validation for TerminalType model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(TerminalType, example_input)


def test_terminaltype_validation_with_invalid_data():
    """Test validation failure for TerminalType model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TerminalType.model_validate(invalid_input)

def test_timezoneenum_validation():
    """Test validation for TimezoneEnum model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(TimezoneEnum, example_input)


def test_timezoneenum_validation_with_invalid_data():
    """Test validation failure for TimezoneEnum model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TimezoneEnum.model_validate(invalid_input)

def test_tractorview_validation():
    """Test validation for TractorView model."""
    example_input = {
    "id": "example_id",
    "tractor_number": "example_tractor_number",
    "depot": "example_depot",
    "vin": "example_vin",
    "model": "example_model",
    "make": "example_make",
    "year": "example_year",
    "weight": "example_weight",
    "next_maintenance": "example_next_maintenance",
    "next_tractor_maintenance_required": "example_next_tractor_maintenance_required",
    "updated_on": "example_updated_on",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(TractorView, example_input)


def test_tractorview_validation_with_invalid_data():
    """Test validation failure for TractorView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TractorView.model_validate(invalid_input)

def test_trailerconfigmatrixview_validation():
    """Test validation for TrailerConfigMatrixView model."""
    example_input = {
    "id": "example_id",
    "importance": 42,
    "trailer_config": "example_trailer_config",
    "code": "example_code",
    "values": "example_values",
    "updated_on": "example_updated_on"
}

    generic_model_validation_test(TrailerConfigMatrixView, example_input)


def test_trailerconfigmatrixview_validation_with_invalid_data():
    """Test validation failure for TrailerConfigMatrixView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TrailerConfigMatrixView.model_validate(invalid_input)

def test_trailerview_validation():
    """Test validation for TrailerView model."""
    example_input = {
    "id": "example_id",
    "trailer_number": "example_trailer_number",
    "configuration": "example_configuration",
    "depot": "example_depot",
    "make": "example_make",
    "model": "example_model",
    "weight": "example_weight",
    "updated_on": "example_updated_on",
    "extra_data": "example_extra_data"
}

    generic_model_validation_test(TrailerView, example_input)


def test_trailerview_validation_with_invalid_data():
    """Test validation failure for TrailerView model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        TrailerView.model_validate(invalid_input)

def test_unavailablehours_validation():
    """Test validation for UnavailableHours model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(UnavailableHours, example_input)


def test_unavailablehours_validation_with_invalid_data():
    """Test validation failure for UnavailableHours model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UnavailableHours.model_validate(invalid_input)

def test_unavailablehoursrequest_validation():
    """Test validation for UnavailableHoursRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(UnavailableHoursRequest, example_input)


def test_unavailablehoursrequest_validation_with_invalid_data():
    """Test validation failure for UnavailableHoursRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UnavailableHoursRequest.model_validate(invalid_input)

def test_updateresponse_validation():
    """Test validation for UpdateResponse model."""
    example_input = {
    "created": "example_created",
    "end_dated": "example_end_dated",
    "bad_data": "example_bad_data",
    "duplicates": "example_duplicates",
    "exact_match": "example_exact_match"
}

    generic_model_validation_test(UpdateResponse, example_input)


def test_updateresponse_validation_with_invalid_data():
    """Test validation failure for UpdateResponse model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpdateResponse.model_validate(invalid_input)

def test_uploadimsrequest_validation():
    """Test validation for UploadIMSRequest model."""
    example_input = {
    "store": "example_store",
    "tank": "example_tank",
    "timezone": "example_timezone",
    "date": "example_date",
    "inches": "example_inches",
    "volume": "example_volume",
    "payload": "example_payload"
}

    generic_model_validation_test(UploadIMSRequest, example_input)


def test_uploadimsrequest_validation_with_invalid_data():
    """Test validation failure for UploadIMSRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UploadIMSRequest.model_validate(invalid_input)

def test_upsertlocationrequest_validation():
    """Test validation for UpsertLocationRequest model."""
    example_input = {
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "name": "example_name",
    "short_name": "example_short_name",
    "address": "example_address",
    "type": "example_type",
    "city": "example_city",
    "state": "example_state",
    "postal_code": "example_postal_code",
    "market_id": "example_market_id",
    "market": "example_market",
    "lat": 3.14,
    "lon": 3.14,
    "hours": "example_hours",
    "contact": "example_contact",
    "contact_phone": "example_contact_phone",
    "active": "example_active",
    "include_in_backhaul": "example_include_in_backhaul",
    "start_time": "example_start_time",
    "end_time": "example_end_time",
    "requires_card": "example_requires_card",
    "splash_blending": "example_splash_blending",
    "split_load_terminals": "example_split_load_terminals",
    "authorized_carriers": "example_authorized_carriers",
    "extra_data": "example_extra_data",
    "geofence": "example_geofence",
    "supply_zones": "example_supply_zones",
    "supply_map": "example_supply_map"
}

    generic_model_validation_test(UpsertLocationRequest, example_input)


def test_upsertlocationrequest_validation_with_invalid_data():
    """Test validation failure for UpsertLocationRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertLocationRequest.model_validate(invalid_input)

def test_upsertmanycounterpartyrequest_validation():
    """Test validation for UpsertManyCounterpartyRequest model."""
    example_input = {
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "name": "example_name",
    "types": "example_types",
    "carrier_type": "example_carrier_type",
    "trailer_config": "example_trailer_config",
    "emails": "example_emails",
    "sourcing_strategy": "example_sourcing_strategy",
    "extra_data": "example_extra_data",
    "goid": "example_goid",
    "allow_short_loads": "example_allow_short_loads",
    "order_notification_preferences": "example_order_notification_preferences",
    "supply_map": "example_supply_map",
    "available_credit": "example_available_credit",
    "hold": "example_hold"
}

    generic_model_validation_test(UpsertManyCounterpartyRequest, example_input)


def test_upsertmanycounterpartyrequest_validation_with_invalid_data():
    """Test validation failure for UpsertManyCounterpartyRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertManyCounterpartyRequest.model_validate(invalid_input)

def test_upsertmanydriverrequest_validation():
    """Test validation for UpsertManyDriverRequest model."""
    example_input = {
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "name": "example_name",
    "username": "example_username",
    "email": "example_email",
    "title": "example_title",
    "hire_date": "example_hire_date",
    "termination_date": "example_termination_date",
    "depot": "example_depot",
    "depot_id": "example_depot_id",
    "in_cab_trip_mode": "example_in_cab_trip_mode",
    "in_cab_supply_option_mode": "example_in_cab_supply_option_mode",
    "preferred_template": "example_preferred_template",
    "shift_preference": "example_shift_preference",
    "shift_length_hours": "example_shift_length_hours",
    "tractor_number": "example_tractor_number",
    "tractor_id": "example_tractor_id",
    "trailer_number": "example_trailer_number",
    "trailer_id": "example_trailer_id",
    "carded_terminals": "example_carded_terminals",
    "supervisor": "example_supervisor",
    "active": "example_active"
}

    generic_model_validation_test(UpsertManyDriverRequest, example_input)


def test_upsertmanydriverrequest_validation_with_invalid_data():
    """Test validation failure for UpsertManyDriverRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertManyDriverRequest.model_validate(invalid_input)

def test_upsertmanystorerequest_validation():
    """Test validation for UpsertManyStoreRequest model."""
    example_input = {
    "id": "example_id",
    "store_number": "example_store_number",
    "name": "example_name",
    "address": "example_address",
    "city": "example_city",
    "state": "example_state",
    "postal_code": "example_postal_code",
    "phone_number": "example_phone_number",
    "emails": "example_emails",
    "hours": "example_hours",
    "market": "example_market",
    "market_id": "example_market_id",
    "sector": "example_sector",
    "sector_id": "example_sector_id",
    "trailer_config": "example_trailer_config",
    "lat": 3.14,
    "lon": 3.14,
    "timezone": "example_timezone",
    "status": "example_status",
    "contact_name": "example_contact_name",
    "open_date": "example_open_date",
    "close_date": "example_close_date",
    "unavailable_hours": "example_unavailable_hours",
    "counterparty_id": "example_counterparty_id",
    "counterparty_name": "example_counterparty_name",
    "supply_owner_id": "example_supply_owner_id",
    "supply_owner_name": "example_supply_owner_name",
    "freight_customer_id": "example_freight_customer_id",
    "freight_customer_name": "example_freight_customer_name",
    "freight_region_name": "example_freight_region_name",
    "freight_region_id": "example_freight_region_id",
    "extra_data": "example_extra_data",
    "monitoring_strategy": "example_monitoring_strategy",
    "estick_monitor_override": "example_estick_monitor_override",
    "drop_workflow": "example_drop_workflow",
    "credit_hold": "example_credit_hold",
    "compliance_hold_date": "example_compliance_hold_date",
    "allow_by_product_request": "example_allow_by_product_request",
    "in_network_terminals": "example_in_network_terminals",
    "delivery_window_default_name": "example_delivery_window_default_name",
    "delivery_window_default_id": "example_delivery_window_default_id",
    "geofence": "example_geofence"
}

    generic_model_validation_test(UpsertManyStoreRequest, example_input)


def test_upsertmanystorerequest_validation_with_invalid_data():
    """Test validation failure for UpsertManyStoreRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertManyStoreRequest.model_validate(invalid_input)

def test_upsertproductrequest_validation():
    """Test validation for UpsertProductRequest model."""
    example_input = {
    "group": "example_group",
    "weight_group": "example_weight_group",
    "extra_data": "example_extra_data",
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "name": "example_name",
    "alias": "example_alias",
    "enabled": "example_enabled",
    "specific_gravity": "example_specific_gravity",
    "short_name": "example_short_name",
    "icon": "example_icon",
    "tank_lid_code_id": "example_tank_lid_code_id",
    "supply_map": "example_supply_map"
}

    generic_model_validation_test(UpsertProductRequest, example_input)


def test_upsertproductrequest_validation_with_invalid_data():
    """Test validation failure for UpsertProductRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertProductRequest.model_validate(invalid_input)

def test_upserttankrequest_validation():
    """Test validation for UpsertTankRequest model."""
    example_input = {
    "id": "example_id",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id",
    "store_id": "example_store_id",
    "tank_id": "example_tank_id",
    "island": "example_island",
    "icon": "example_icon",
    "product_id": "example_product_id",
    "product": "example_product",
    "description": "example_description",
    "tank_chart": "example_tank_chart",
    "storage_max": "example_storage_max",
    "tank_size": "example_tank_size",
    "fuel_bottom": "example_fuel_bottom",
    "manufacturer": "example_manufacturer",
    "dimensions": "example_dimensions",
    "tank_color": "example_tank_color",
    "minimum_load_size": "example_minimum_load_size",
    "maximum_load_size": "example_maximum_load_size",
    "strapping_table": "example_strapping_table",
    "target_min": "example_target_min",
    "target_max": "example_target_max",
    "inventory_strategy": "example_inventory_strategy",
    "load_tags": "example_load_tags",
    "filter_tags": "example_filter_tags",
    "split_me": "example_split_me",
    "water_reading_requirement": "example_water_reading_requirement",
    "requires_pump": "example_requires_pump",
    "carrier_id": "example_carrier_id",
    "carrier": "example_carrier",
    "extra_data": "example_extra_data",
    "active": "example_active",
    "manifold_id": "example_manifold_id",
    "apportion_percentage": "example_apportion_percentage",
    "compliance_hold": "example_compliance_hold",
    "demand_model_tank_profile": "example_demand_model_tank_profile",
    "store_number": "example_store_number"
}

    generic_model_validation_test(UpsertTankRequest, example_input)


def test_upserttankrequest_validation_with_invalid_data():
    """Test validation failure for UpsertTankRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertTankRequest.model_validate(invalid_input)

def test_upserttractorreq_validation():
    """Test validation for UpsertTractorReq model."""
    example_input = {
    "id": "example_id",
    "tractor_number": "example_tractor_number",
    "depot": "example_depot",
    "vin": "example_vin",
    "make": "example_make",
    "model": "example_model",
    "year": "example_year",
    "weight": "example_weight",
    "next_maintenance": "example_next_maintenance",
    "next_tractor_maintenance_required": "example_next_tractor_maintenance_required",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id"
}

    generic_model_validation_test(UpsertTractorReq, example_input)


def test_upserttractorreq_validation_with_invalid_data():
    """Test validation failure for UpsertTractorReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertTractorReq.model_validate(invalid_input)

def test_upserttractorresp_validation():
    """Test validation for UpsertTractorResp model."""
    example_input = {
    "created": "example_created",
    "updated": "example_updated",
    "errors": "example_errors"
}

    generic_model_validation_test(UpsertTractorResp, example_input)


def test_upserttractorresp_validation_with_invalid_data():
    """Test validation failure for UpsertTractorResp model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertTractorResp.model_validate(invalid_input)

def test_upserttrailerreq_validation():
    """Test validation for UpsertTrailerReq model."""
    example_input = {
    "id": "example_id",
    "trailer_number": "example_trailer_number",
    "configuration": "example_configuration",
    "depot": "example_depot",
    "make": "example_make",
    "model": "example_model",
    "weight": "example_weight",
    "source_id": "example_source_id",
    "source_system_id": "example_source_system_id"
}

    generic_model_validation_test(UpsertTrailerReq, example_input)


def test_upserttrailerreq_validation_with_invalid_data():
    """Test validation failure for UpsertTrailerReq model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertTrailerReq.model_validate(invalid_input)

def test_upserttrailerresp_validation():
    """Test validation for UpsertTrailerResp model."""
    example_input = {
    "created": "example_created",
    "updated": "example_updated",
    "errors": "example_errors"
}

    generic_model_validation_test(UpsertTrailerResp, example_input)


def test_upserttrailerresp_validation_with_invalid_data():
    """Test validation failure for UpsertTrailerResp model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        UpsertTrailerResp.model_validate(invalid_input)

def test_validationerror_validation():
    """Test validation for ValidationError model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(ValidationError, example_input)


def test_validationerror_validation_with_invalid_data():
    """Test validation failure for ValidationError model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        ValidationError.model_validate(invalid_input)

def test_volumedistributionrequest_validation():
    """Test validation for VolumeDistributionRequest model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(VolumeDistributionRequest, example_input)


def test_volumedistributionrequest_validation_with_invalid_data():
    """Test validation failure for VolumeDistributionRequest model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        VolumeDistributionRequest.model_validate(invalid_input)

def test_waterreadingrequirement_validation():
    """Test validation for WaterReadingRequirement model."""
    example_input = {
    "root": "example_root"
}

    generic_model_validation_test(WaterReadingRequirement, example_input)


def test_waterreadingrequirement_validation_with_invalid_data():
    """Test validation failure for WaterReadingRequirement model with invalid data."""
    invalid_input = {"invalid_field": "should_fail"}

    with pytest.raises(ValidationError):
        WaterReadingRequirement.model_validate(invalid_input)


# Parametrized test for all models
@pytest.mark.parametrize("model_class,example_input", [
    (AllocatedBolResponse, {"root": "example_root"}),
    (BillableDateType, {"root": "example_root"}),
    (BillableVolumeType, {"root": "example_root"}),
    (BlendView, {"root": "example_root"}),
    (BolAndDropResponse, {"order_number": "example_order_number", "order_id": "example_order_id", "po": "example_po", "carrier_id": "example_carrier_id", "last_movement_update": "example_last_movement_update", "order_date": "example_order_date", "status": "example_status", "type": "example_type", "drops": "example_drops", "bols": "example_bols", "costs": "example_costs", "validation_bypass_on": "example_validation_bypass_on", "has_additives": "example_has_additives", "estimated_freight": "example_estimated_freight", "actual_freight": "example_actual_freight", "allocated_bol_error": "example_allocated_bol_error", "allocated_bol_issue": "example_allocated_bol_issue", "allocated_bols": "example_allocated_bols", "last_change_date": "example_last_change_date", "reference_order_number": "example_reference_order_number"}),
    (BolImageResponse, {"root": "example_root"}),
    (BolImagesRequest, {"order_ids": "example_order_ids", "order_numbers": "example_order_numbers"}),
    (BolImagesResponse, {"order_id": "example_order_id", "bol_id": "example_bol_id", "bol_number": "example_bol_number", "photos": "example_photos"}),
    (BolsAndDropsRequest, {"order_date_start": "example_order_date_start", "order_date_end": "example_order_date_end", "movement_updated_start": "example_movement_updated_start", "movement_updated_end": "example_movement_updated_end", "order_ids": "example_order_ids", "order_numbers": "example_order_numbers", "order_states": "example_order_states", "order_types": "example_order_types", "include_invalid": "example_include_invalid", "include_bol_allocation": "example_include_bol_allocation", "last_change_date": "example_last_change_date", "reference_order_numbers": "example_reference_order_numbers"}),
    (Card, {"root": "example_root"}),
    (ContractVolumeRequest, {"root": "example_root"}),
    (Coordinate, {"root": "example_root"}),
    (Counterparty, {"root": "example_root"}),
    (CounterpartyView, {"id": "example_id", "name": "example_name", "goid": "example_goid", "scac": "example_scac", "types": "example_types", "carrier_type": "example_carrier_type", "trailer_config": "example_trailer_config", "source_id": "example_source_id", "source_system": "example_source_system", "source_system_id": "example_source_system_id", "emails": "example_emails", "sourcing_strategy": "example_sourcing_strategy", "extra_data": "example_extra_data", "updated_on": "example_updated_on", "allow_short_loads": "example_allow_short_loads", "order_notification_preferences": "example_order_notification_preferences", "supply_map": "example_supply_map"}),
    (CreateGroupRequest, {"source_id": "example_source_id", "name": "example_name", "keys": "example_keys", "as_of": "example_as_of", "min": "example_min", "max": "example_max", "start_hour": "example_start_hour", "volume_distributions": "example_volume_distributions", "contract_volumes": "example_contract_volumes", "daily_percent": "example_daily_percent", "weekly_percent": "example_weekly_percent", "monthly_percent": "example_monthly_percent", "contract_start": "example_contract_start", "contract_end": "example_contract_end", "week_start_day": "example_week_start_day"}),
    (DateWindow, {"root": "example_root"}),
    (DaysOfWeek, {"root": "example_root"}),
    (DeliveryRequestStatus, {"root": "example_root"}),
    (DeliveryTicketById, {"order_id": "example_order_id", "store_id": "example_store_id"}),
    (DeliveryTicketByNumber, {"order_number": 42, "store_number": "example_store_number"}),
    (DeliveryWindow, {"root": "example_root"}),
    (DeliveryWindowDefault, {"root": "example_root"}),
    (DriverCredentialUpsertRequest, {"driver_id": "example_driver_id", "credential_id": "example_credential_id", "certification_date": "example_certification_date", "expiration_date": "example_expiration_date"}),
    (DriverCredentialView, {"root": "example_root"}),
    (DriverTerminalCardView, {"root": "example_root"}),
    (DriverView, {"id": "example_id", "name": "example_name", "username": "example_username", "depot_id": "example_depot_id", "depot_name": "example_depot_name", "in_cab_trip_mode": "example_in_cab_trip_mode", "in_cab_supply_option_mode": "example_in_cab_supply_option_mode", "trailer_number": "example_trailer_number", "tractor_number": "example_tractor_number", "updated_on": "example_updated_on", "extra_data": "example_extra_data", "cards": "example_cards", "credentials": "example_credentials"}),
    (DropCreateRequest, {"root": "example_root"}),
    (DropWorkflow, {"root": "example_root"}),
    (Dwell, {"root": "example_root"}),
    (EBolDetailRequest, {"root": "example_root"}),
    (EBolRequest, {"source_system": "example_source_system", "bol_number": "example_bol_number", "date": "example_date", "terminal_id": "example_terminal_id", "supplier_id": "example_supplier_id", "details": "example_details"}),
    (ExternalBOLDetailRequest, {"root": "example_root"}),
    (ExternalBOLRequest, {"order_id": "example_order_id", "bol_number": "example_bol_number", "terminal_id": "example_terminal_id", "bol_date": "example_bol_date", "details": "example_details"}),
    (ForecastApiCreateRequest, {"root": "example_root"}),
    (FormFieldResponse, {"root": "example_root"}),
    (FormResponseRow, {"id": "example_id", "name": "example_name", "description": "example_description", "order_number": 42, "driver_name": "example_driver_name", "date": "example_date", "shift": "example_shift", "location_name": "example_location_name", "address": "example_address", "latitude": "example_latitude", "longitude": "example_longitude", "market": "example_market", "sector": "example_sector", "supply_zones": "example_supply_zones", "tractor": "example_tractor", "trailer_number": "example_trailer_number", "required": "example_required", "response": "example_response"}),
    (FreightCost, {"root": "example_root"}),
    (FreightIntegrationReq, {"order_numbers": "example_order_numbers", "order_ids": "example_order_ids", "last_change_date": "example_last_change_date"}),
    (FreightItem, {"root": "example_root"}),
    (FreightTransactionDetailOutput, {"root": "example_root"}),
    (FreightTransactionOutput, {"root": "example_root"}),
    (FreightTransactionRowOutput, {"root": "example_root"}),
    (GetOrderRequestResponse, {"type": "example_type", "number": 42, "order_id": "example_order_id", "order_number": "example_order_number", "order_date": "example_order_date", "order_state": "example_order_state", "reference_order_number": "example_reference_order_number", "last_change_date": "example_last_change_date", "site_name": "example_site_name", "site_id": "example_site_id", "customer_id": "example_customer_id", "customer_name": "example_customer_name", "delivery_window_start": "example_delivery_window_start", "delivery_window_end": "example_delivery_window_end", "products": "example_products", "extra_data": "example_extra_data", "status": "example_status"}),
    (GetOrderResponse, {"type": "example_type", "order_id": "example_order_id", "drivers": "example_drivers", "order_number": "example_order_number", "order_date": "example_order_date", "order_state": "example_order_state", "carrier_window_start": "example_carrier_window_start", "carrier_window_end": "example_carrier_window_end", "carrier_notify_state": "example_carrier_notify_state", "load_window_start": "example_load_window_start", "load_window_end": "example_load_window_end", "dispatch_window_start": "example_dispatch_window_start", "dispatch_window_end": "example_dispatch_window_end", "hauler_counterparty_id": "example_hauler_counterparty_id", "hauler_counterparty_name": "example_hauler_counterparty_name", "hauler_counterparty_source_id": "example_hauler_counterparty_source_id", "hauler_counterparty_source_system": "example_hauler_counterparty_source_system", "hauled_by_updated_by": "example_hauled_by_updated_by", "hauled_by_updated": "example_hauled_by_updated", "loads": "example_loads", "drops": "example_drops", "trip_status": "example_trip_status", "last_change_date": "example_last_change_date", "market": "example_market", "supply_option": "example_supply_option", "created_by": "example_created_by", "note": "example_note", "estimated_load_minutes": "example_estimated_load_minutes", "total_miles": "example_total_miles", "loaded_miles": "example_loaded_miles", "unloaded_miles": "example_unloaded_miles", "reference_order_number": "example_reference_order_number", "extra_data": "example_extra_data"}),
    (GetOrdersRequest, {"order_id": "example_order_id", "order_number": "example_order_number", "type": "example_type", "state": "example_state", "last_change_date": "example_last_change_date", "order_date_start": "example_order_date_start", "order_date_end": "example_order_date_end", "reference_order_number": "example_reference_order_number", "order_date": "example_order_date"}),
    (HTTPValidationError, {"detail": "example_detail"}),
    (ImportRequest, {"reqs": "example_reqs"}),
    (InCabSupplyOptionMode, {"root": "example_root"}),
    (InCabTripMode, {"root": "example_root"}),
    (InNetworkSupplyZone, {"root": "example_root"}),
    (InNetworkTerminal, {"root": "example_root"}),
    (IntegrationFormResponseOverviewReq, {"form_name": "example_form_name", "from_date": "example_from_date", "to_date": "example_to_date", "market": "example_market"}),
    (InvoiceAllReq, {"order_numbers": "example_order_numbers", "order_ids": "example_order_ids", "invoice_numbers": "example_invoice_numbers", "status": "example_status", "counterparty_name": "example_counterparty_name", "counterparty_id": "example_counterparty_id", "book_type": "example_book_type", "as_of": "example_as_of", "between": "example_between"}),
    (InvoiceDynamicStatus, {"root": "example_root"}),
    (InvoiceRow, {"invoice_number": "example_invoice_number", "sent_date": "example_sent_date", "when_to_send_date": "example_when_to_send_date", "created_on": "example_created_on", "type": "example_type", "status": "example_status", "transactions": "example_transactions", "note": "example_note", "base_amount": 3.14, "base_distance": 3.14, "distance_uom": "example_distance_uom", "accessorial_amount": 3.14, "surcharge_amount": 3.14, "total_amount": 3.14}),
    (InvoiceStaticStatus, {"root": "example_root"}),
    (InvoiceType, {"root": "example_root"}),
    (Key, {"root": "example_root"}),
    (LocationResponse, {"root": "example_root"}),
    (LocationView, {"id": "example_id", "name": "example_name", "short_name": "example_short_name", "market": "example_market", "market_id": "example_market_id", "freight_region_name": "example_freight_region_name", "freight_region_id": "example_freight_region_id", "type": "example_type", "lat": "example_lat", "lon": "example_lon", "address": "example_address", "phone": "example_phone", "city": "example_city", "state": "example_state", "active": "example_active", "postal_code": "example_postal_code", "source_id": "example_source_id", "source_system": "example_source_system", "source_system_id": "example_source_system_id", "timezone": "example_timezone", "supply_zones": "example_supply_zones", "updated_on": "example_updated_on", "cards": "example_cards", "dwells": "example_dwells", "requires_card": "example_requires_card", "geofence": "example_geofence", "supply_map": "example_supply_map", "extra_data": "example_extra_data"}),
    (MarketSchemaSectorView, {"root": "example_root"}),
    (MarketView, {"id": "example_id", "name": "example_name", "network_radius": "example_network_radius", "active": "example_active", "trailer_config": "example_trailer_config", "updated_on": "example_updated_on", "extra_data": "example_extra_data", "sectors": "example_sectors", "delivery_window_default": "example_delivery_window_default"}),
    (MonitoringStrategy, {"root": "example_root"}),
    (NOSupplyOptionResponse, {"root": "example_root"}),
    (OptimalSupplyReportRequest, {"order_numbers": "example_order_numbers", "order_ids": "example_order_ids", "order_date_start": "example_order_date_start", "order_date_end": "example_order_date_end", "movement_updated_start": "example_movement_updated_start", "movement_updated_end": "example_movement_updated_end", "last_change_date": "example_last_change_date"}),
    (OptimalSupplyReportRow, {"order_number": 42, "order_id": "example_order_id", "site_number": "example_site_number", "actual_component_product": "example_actual_component_product", "actual_component_product_id": "example_actual_component_product_id", "optimal_component_product": "example_optimal_component_product", "optimal_component_product_id": "example_optimal_component_product_id", "actual_terminal": "example_actual_terminal", "actual_terminal_id": "example_actual_terminal_id", "optimal_terminal": "example_optimal_terminal", "optimal_terminal_id": "example_optimal_terminal_id", "actual_supplier": "example_actual_supplier", "actual_supplier_id": "example_actual_supplier_id", "optimal_supplier": "example_optimal_supplier", "optimal_supplier_id": "example_optimal_supplier_id", "actual_price_type": "example_actual_price_type", "optimal_price_type": "example_optimal_price_type", "actual_contract": "example_actual_contract", "optimal_contract": "example_optimal_contract", "actual_curve_id": "example_actual_curve_id", "optimal_curve_id": "example_optimal_curve_id", "actual_price_id": "example_actual_price_id", "optimal_price_id": "example_optimal_price_id", "actual_loaded_miles": 3.14, "optimal_loaded_miles": 3.14, "actual_product_price": 3.14, "optimal_product_price": 3.14, "actual_freight_rate": 3.14, "optimal_freight_rate": 3.14, "actual_total_price": 3.14, "optimal_total_price": 3.14, "total_price_delta": 3.14, "actual_volume": 3.14, "optimal_volume": 3.14, "last_change_date": "example_last_change_date", "last_updated_date": "example_last_updated_date", "reason_code": "example_reason_code"}),
    (OrderCreateRequest, {"reference_order_number": "example_reference_order_number", "supply_owner": "example_supply_owner", "sourcing_strategy": "example_sourcing_strategy", "manual_supply_fallback": "example_manual_supply_fallback", "allow_alternate_products": "example_allow_alternate_products", "delivery_window": "example_delivery_window", "fit_to_trailer": "example_fit_to_trailer", "note": "example_note", "drops": "example_drops", "accept_by": "example_accept_by", "extra_data": "example_extra_data"}),
    (OrderCreateResponse, {"status": "example_status", "order_number": "example_order_number", "order": "example_order", "errors": "example_errors", "accept_by": "example_accept_by", "reference_order_number": "example_reference_order_number", "extra_data": "example_extra_data"}),
    (OrderCreateStatus, {"root": "example_root"}),
    (OrderDriver, {"root": "example_root"}),
    (OrderFreightResp, {"number": 42, "po": "example_po", "freight_rate": 3.14, "freight_total": 3.14, "freight_items": "example_freight_items"}),
    (OrderFreightRespV2, {"number": 42, "po": "example_po", "freight_rate": 3.14, "freight_total": 3.14, "freight_items": "example_freight_items"}),
    (OrderReqNotificationStates, {"root": "example_root"}),
    (OrderResponse, {"root": "example_root"}),
    (OrderSchemaBolResponse, {"root": "example_root"}),
    (OrderSchemaDropResponse, {"root": "example_root"}),
    (OrderState, {"root": "example_root"}),
    (OrderStatusUpdateRequest, {"order_id": "example_order_id", "order_number": "example_order_number", "status": "example_status", "location_id": "example_location_id", "eta": "example_eta", "actual": "example_actual"}),
    (OrderType, {"root": "example_root"}),
    (PayrollExportDetailModel, {"root": "example_root"}),
    (PayrollExportDetailResponse, {"driver_name": "example_driver_name", "driver_source_id": "example_driver_source_id", "driver_source_system": "example_driver_source_system", "end_date": "example_end_date", "hours_worked": 3.14, "pay_earned": 3.14, "payroll_config": "example_payroll_config", "start_date": "example_start_date", "status": "example_status", "updated": "example_updated", "detail": "example_detail"}),
    (PriceAllRequest, {"as_of": "example_as_of", "last_change_date": "example_last_change_date", "terminals": "example_terminals", "suppliers": "example_suppliers", "products": "example_products", "price_types": "example_price_types", "product_groups": "example_product_groups"}),
    (PriceResponse, {"curve_id": "example_curve_id", "price_id": "example_price_id", "city": "example_city", "contract": "example_contract", "product": "example_product", "product_id": "example_product_id", "supplier": "example_supplier", "supplier_id": "example_supplier_id", "counterparty": "example_counterparty", "counterparty_id": "example_counterparty_id", "terminal": "example_terminal", "terminal_id": "example_terminal_id", "store_number": "example_store_number", "store_id": "example_store_id", "price_type": "example_price_type", "product_group": "example_product_group", "price": 3.14, "effective_from": "example_effective_from", "effective_to": "example_effective_to", "expire": "example_expire", "disabled": true, "disabled_by": "example_disabled_by", "disabled_until": "example_disabled_until", "disabled_reason": "example_disabled_reason", "updated_by": "example_updated_by", "updated_on": "example_updated_on", "extra_data": "example_extra_data", "group_id": "example_group_id", "group_effective_cutover": "example_group_effective_cutover", "group_effective_cutover_timezone": "example_group_effective_cutover_timezone", "group_identifier": "example_group_identifier", "group_name": "example_group_name", "min_constraint": "example_min_constraint", "max_constraint": "example_max_constraint", "created_on": "example_created_on", "net_or_gross_type": "example_net_or_gross_type", "contract_lifting_valuation_method": "example_contract_lifting_valuation_method"}),
    (PriceType, {"root": "example_root"}),
    (ProductGroups, {"root": "example_root"}),
    (ProductIDName, {"root": "example_root"}),
    (ProductView, {"id": "example_id", "name": "example_name", "short_name": "example_short_name", "group": "example_group", "weight_group": "example_weight_group", "icon": "example_icon", "source_id": "example_source_id", "source_system": "example_source_system", "source_system_id": "example_source_system_id", "extra_data": "example_extra_data", "blends": "example_blends", "alternate_products": "example_alternate_products", "updated_on": "example_updated_on", "tank_lid_code_id": "example_tank_lid_code_id", "supply_map": "example_supply_map"}),
    (PydanticObjectId, {"root": "example_root"}),
    (RateBookType, {"root": "example_root"}),
    (RootModel, {"root": "example_root"}),
    (RouteUpsertReq, {"origin_name": "example_origin_name", "destination_name": "example_destination_name", "api_distance_miles": "example_api_distance_miles", "api_travel_time_seconds": "example_api_travel_time_seconds", "override_travel_time_seconds": "example_override_travel_time_seconds", "override_distance_miles": "example_override_distance_miles", "override_payroll_miles": "example_override_payroll_miles"}),
    (SalesAdjustedDeliveryUpsertReq, {"source": "example_source", "store_id": "example_store_id", "tank_id": "example_tank_id", "product_id": "example_product_id", "volume": 3.14, "date": "example_date"}),
    (SaveDropDetail, {"root": "example_root"}),
    (SaveDropMode, {"root": "example_root"}),
    (SaveDropReq, {"mode": "example_mode", "order_id": "example_order_id", "location_id": "example_location_id", "details": "example_details"}),
    (Shift, {"root": "example_root"}),
    (SourceMap, {"root": "example_root"}),
    (SourcingStrategy, {"root": "example_root"}),
    (StatusUpdate, {"root": "example_root"}),
    (StoreStatus, {"root": "example_root"}),
    (StoreTank, {"root": "example_root"}),
    (StoreV2, {"field_id": "example_field_id", "store_number": "example_store_number", "name": "example_name", "market": "example_market", "market_id": "example_market_id", "sector": "example_sector", "sector_id": "example_sector_id", "tanks": "example_tanks", "lat": "example_lat", "lon": "example_lon", "address": "example_address", "city": "example_city", "state": "example_state", "postal_code": "example_postal_code", "contact_name": "example_contact_name", "phone_number": "example_phone_number", "emails": "example_emails", "hours": "example_hours", "timezone": "example_timezone", "status": "example_status", "drop_workflow": "example_drop_workflow", "open_date": "example_open_date", "close_date": "example_close_date", "unavailable_hours": "example_unavailable_hours", "counterparty_id": "example_counterparty_id", "counterparty_name": "example_counterparty_name", "in_network_terminals": "example_in_network_terminals", "in_network_supply_zones": "example_in_network_supply_zones", "supply_owner_id": "example_supply_owner_id", "supply_owner_name": "example_supply_owner_name", "freight_customer_id": "example_freight_customer_id", "freight_customer_name": "example_freight_customer_name", "freight_region_name": "example_freight_region_name", "freight_region_id": "example_freight_region_id", "layout_file": "example_layout_file", "layout_file_uploaded": "example_layout_file_uploaded", "auto_order_disabled": "example_auto_order_disabled", "updated_id": "example_updated_id", "trailer_config": "example_trailer_config", "monitoring_strategy": "example_monitoring_strategy", "estick_monitor_override": "example_estick_monitor_override", "notes": "example_notes", "updated_on": "example_updated_on", "updated_by": "example_updated_by", "extra_data": "example_extra_data", "credit_hold": "example_credit_hold", "compliance_hold_date": "example_compliance_hold_date", "delivery_window_default_name": "example_delivery_window_default_name", "delivery_window_default_id": "example_delivery_window_default_id", "allow_by_product_request": "example_allow_by_product_request", "geofence": "example_geofence"}),
    (SupplyPriceUpdateManyRequest, {"id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "contract": "example_contract", "timezone": "example_timezone", "effective_from": "example_effective_from", "effective_to": "example_effective_to", "price": 3.14, "price_type": "example_price_type", "terminal_id": "example_terminal_id", "terminal_source_id": "example_terminal_source_id", "terminal_source_system_id": "example_terminal_source_system_id", "terminal": "example_terminal", "product_id": "example_product_id", "product_source_id": "example_product_source_id", "product_source_system_id": "example_product_source_system_id", "product": "example_product", "supplier_id": "example_supplier_id", "supplier_source_id": "example_supplier_source_id", "supplier_source_system_id": "example_supplier_source_system_id", "supplier": "example_supplier", "counterparty_id": "example_counterparty_id", "counterparty_source_id": "example_counterparty_source_id", "counterparty_source_system_id": "example_counterparty_source_system_id", "counterparty": "example_counterparty", "store_id": "example_store_id", "store_source_id": "example_store_source_id", "store_source_system_id": "example_store_source_system_id", "store_number": "example_store_number", "enabled": "example_enabled", "disabled_until": "example_disabled_until", "expire": "example_expire", "min_quantity": "example_min_quantity", "max_quantity": "example_max_quantity", "curve_id": "example_curve_id", "error": "example_error", "row": "example_row", "net_or_gross_type": "example_net_or_gross_type", "contract_lifting_valuation_method": "example_contract_lifting_valuation_method"}),
    (SupplyPriceUpdateResponse, {"root": "example_root"}),
    (SurchargeAllReq, {"counterparty_name": "example_counterparty_name", "counterparty_id": "example_counterparty_id", "book_type": "example_book_type", "as_of": "example_as_of", "product_group": "example_product_group", "freight_region_name": "example_freight_region_name", "freight_region_id": "example_freight_region_id"}),
    (SurchargeAllResp, {"id": "example_id", "counterparty": "example_counterparty", "counterparty_id": "example_counterparty_id", "product_group": "example_product_group", "book_type": "example_book_type", "freight_region_id": "example_freight_region_id", "freight_region_name": "example_freight_region_name", "type": "example_type", "effective_from": "example_effective_from", "effective_to": "example_effective_to", "surcharge": "example_surcharge", "created_on": "example_created_on", "created_by": "example_created_by"}),
    (SurchargeCreateReq, {"counterparty_name": "example_counterparty_name", "counterparty_id": "example_counterparty_id", "product_group": "example_product_group", "book_type": "example_book_type", "freight_region_id": "example_freight_region_id", "freight_region_name": "example_freight_region_name", "type": "example_type", "effective_from": "example_effective_from", "effective_to": "example_effective_to", "surcharge": "example_surcharge"}),
    (SurchargeType, {"root": "example_root"}),
    (SurchargeUpdateReq, {"id": "example_id", "effective_from": "example_effective_from", "effective_to": "example_effective_to", "surcharge": "example_surcharge"}),
    (TankLidEnum, {"root": "example_root"}),
    (TerminalType, {"root": "example_root"}),
    (TimezoneEnum, {"root": "example_root"}),
    (TractorView, {"id": "example_id", "tractor_number": "example_tractor_number", "depot": "example_depot", "vin": "example_vin", "model": "example_model", "make": "example_make", "year": "example_year", "weight": "example_weight", "next_maintenance": "example_next_maintenance", "next_tractor_maintenance_required": "example_next_tractor_maintenance_required", "updated_on": "example_updated_on", "extra_data": "example_extra_data"}),
    (TrailerConfigMatrixView, {"id": "example_id", "importance": 42, "trailer_config": "example_trailer_config", "code": "example_code", "values": "example_values", "updated_on": "example_updated_on"}),
    (TrailerView, {"id": "example_id", "trailer_number": "example_trailer_number", "configuration": "example_configuration", "depot": "example_depot", "make": "example_make", "model": "example_model", "weight": "example_weight", "updated_on": "example_updated_on", "extra_data": "example_extra_data"}),
    (UnavailableHours, {"root": "example_root"}),
    (UnavailableHoursRequest, {"root": "example_root"}),
    (UpdateResponse, {"created": "example_created", "end_dated": "example_end_dated", "bad_data": "example_bad_data", "duplicates": "example_duplicates", "exact_match": "example_exact_match"}),
    (UploadIMSRequest, {"store": "example_store", "tank": "example_tank", "timezone": "example_timezone", "date": "example_date", "inches": "example_inches", "volume": "example_volume", "payload": "example_payload"}),
    (UpsertLocationRequest, {"id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "name": "example_name", "short_name": "example_short_name", "address": "example_address", "type": "example_type", "city": "example_city", "state": "example_state", "postal_code": "example_postal_code", "market_id": "example_market_id", "market": "example_market", "lat": 3.14, "lon": 3.14, "hours": "example_hours", "contact": "example_contact", "contact_phone": "example_contact_phone", "active": "example_active", "include_in_backhaul": "example_include_in_backhaul", "start_time": "example_start_time", "end_time": "example_end_time", "requires_card": "example_requires_card", "splash_blending": "example_splash_blending", "split_load_terminals": "example_split_load_terminals", "authorized_carriers": "example_authorized_carriers", "extra_data": "example_extra_data", "geofence": "example_geofence", "supply_zones": "example_supply_zones", "supply_map": "example_supply_map"}),
    (UpsertManyCounterpartyRequest, {"id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "name": "example_name", "types": "example_types", "carrier_type": "example_carrier_type", "trailer_config": "example_trailer_config", "emails": "example_emails", "sourcing_strategy": "example_sourcing_strategy", "extra_data": "example_extra_data", "goid": "example_goid", "allow_short_loads": "example_allow_short_loads", "order_notification_preferences": "example_order_notification_preferences", "supply_map": "example_supply_map", "available_credit": "example_available_credit", "hold": "example_hold"}),
    (UpsertManyDriverRequest, {"id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "name": "example_name", "username": "example_username", "email": "example_email", "title": "example_title", "hire_date": "example_hire_date", "termination_date": "example_termination_date", "depot": "example_depot", "depot_id": "example_depot_id", "in_cab_trip_mode": "example_in_cab_trip_mode", "in_cab_supply_option_mode": "example_in_cab_supply_option_mode", "preferred_template": "example_preferred_template", "shift_preference": "example_shift_preference", "shift_length_hours": "example_shift_length_hours", "tractor_number": "example_tractor_number", "tractor_id": "example_tractor_id", "trailer_number": "example_trailer_number", "trailer_id": "example_trailer_id", "carded_terminals": "example_carded_terminals", "supervisor": "example_supervisor", "active": "example_active"}),
    (UpsertManyStoreRequest, {"id": "example_id", "store_number": "example_store_number", "name": "example_name", "address": "example_address", "city": "example_city", "state": "example_state", "postal_code": "example_postal_code", "phone_number": "example_phone_number", "emails": "example_emails", "hours": "example_hours", "market": "example_market", "market_id": "example_market_id", "sector": "example_sector", "sector_id": "example_sector_id", "trailer_config": "example_trailer_config", "lat": 3.14, "lon": 3.14, "timezone": "example_timezone", "status": "example_status", "contact_name": "example_contact_name", "open_date": "example_open_date", "close_date": "example_close_date", "unavailable_hours": "example_unavailable_hours", "counterparty_id": "example_counterparty_id", "counterparty_name": "example_counterparty_name", "supply_owner_id": "example_supply_owner_id", "supply_owner_name": "example_supply_owner_name", "freight_customer_id": "example_freight_customer_id", "freight_customer_name": "example_freight_customer_name", "freight_region_name": "example_freight_region_name", "freight_region_id": "example_freight_region_id", "extra_data": "example_extra_data", "monitoring_strategy": "example_monitoring_strategy", "estick_monitor_override": "example_estick_monitor_override", "drop_workflow": "example_drop_workflow", "credit_hold": "example_credit_hold", "compliance_hold_date": "example_compliance_hold_date", "allow_by_product_request": "example_allow_by_product_request", "in_network_terminals": "example_in_network_terminals", "delivery_window_default_name": "example_delivery_window_default_name", "delivery_window_default_id": "example_delivery_window_default_id", "geofence": "example_geofence"}),
    (UpsertProductRequest, {"group": "example_group", "weight_group": "example_weight_group", "extra_data": "example_extra_data", "id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "name": "example_name", "alias": "example_alias", "enabled": "example_enabled", "specific_gravity": "example_specific_gravity", "short_name": "example_short_name", "icon": "example_icon", "tank_lid_code_id": "example_tank_lid_code_id", "supply_map": "example_supply_map"}),
    (UpsertTankRequest, {"id": "example_id", "source_id": "example_source_id", "source_system_id": "example_source_system_id", "store_id": "example_store_id", "tank_id": "example_tank_id", "island": "example_island", "icon": "example_icon", "product_id": "example_product_id", "product": "example_product", "description": "example_description", "tank_chart": "example_tank_chart", "storage_max": "example_storage_max", "tank_size": "example_tank_size", "fuel_bottom": "example_fuel_bottom", "manufacturer": "example_manufacturer", "dimensions": "example_dimensions", "tank_color": "example_tank_color", "minimum_load_size": "example_minimum_load_size", "maximum_load_size": "example_maximum_load_size", "strapping_table": "example_strapping_table", "target_min": "example_target_min", "target_max": "example_target_max", "inventory_strategy": "example_inventory_strategy", "load_tags": "example_load_tags", "filter_tags": "example_filter_tags", "split_me": "example_split_me", "water_reading_requirement": "example_water_reading_requirement", "requires_pump": "example_requires_pump", "carrier_id": "example_carrier_id", "carrier": "example_carrier", "extra_data": "example_extra_data", "active": "example_active", "manifold_id": "example_manifold_id", "apportion_percentage": "example_apportion_percentage", "compliance_hold": "example_compliance_hold", "demand_model_tank_profile": "example_demand_model_tank_profile", "store_number": "example_store_number"}),
    (UpsertTractorReq, {"id": "example_id", "tractor_number": "example_tractor_number", "depot": "example_depot", "vin": "example_vin", "make": "example_make", "model": "example_model", "year": "example_year", "weight": "example_weight", "next_maintenance": "example_next_maintenance", "next_tractor_maintenance_required": "example_next_tractor_maintenance_required", "source_id": "example_source_id", "source_system_id": "example_source_system_id"}),
    (UpsertTractorResp, {"created": "example_created", "updated": "example_updated", "errors": "example_errors"}),
    (UpsertTrailerReq, {"id": "example_id", "trailer_number": "example_trailer_number", "configuration": "example_configuration", "depot": "example_depot", "make": "example_make", "model": "example_model", "weight": "example_weight", "source_id": "example_source_id", "source_system_id": "example_source_system_id"}),
    (UpsertTrailerResp, {"created": "example_created", "updated": "example_updated", "errors": "example_errors"}),
    (ValidationError, {"root": "example_root"}),
    (VolumeDistributionRequest, {"root": "example_root"}),
    (WaterReadingRequirement, {"root": "example_root"}),

])
def test_all_models_validation(model_class: BaseModel, example_input: Dict[str, Any]):
    """Parametrized test for all models."""
    generic_model_validation_test(model_class, example_input)
