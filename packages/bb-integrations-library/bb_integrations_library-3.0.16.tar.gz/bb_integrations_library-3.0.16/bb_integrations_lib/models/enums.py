from enum import Enum


class ProbeEventType(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"


class CrossroadsEntityType(str, Enum):
    """Supported entities for crossroads integrations."""
    # For watching orders in a generic manner (i.e. report when created). Planned for use with Telapoint integration
    order = "order"

    # For watching orders specifically for the carrier order integration (which will only be kicked off when an order is assigned to a carrier)
    carrier_order = "carrier order integration"


class CrossroadsTaskStatus(str, Enum):
    created = "created"
    started = "started"
    succeeded = "succeeded"
    failed = "failed"


class ConnectorAction(str, Enum):
    carrier_integration_create_order = "carrier integration - create order for carrier"
    carrier_integration_update_order_status = "carrier integration - update order status for customer"
