from typing import Generic, TypeVar, Type

from pydantic_xml import BaseXmlModel, element, attr

_nsmap = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "tel": "http://schemas.datacontract.org/2004/07/TelaPoint.Api.TelaFuel.Models",
    "v2": "http://api.telapoint.com/TelaFuel/v2",
    "i": "http://www.w3.org/2001/XMLSchema-instance",
    "wsse": "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
    "wsu": "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
}

####################### Copied from pydantic-xml docs for SOAP envelope tech. Probably don't touch.

AuthType = TypeVar('AuthType')


class SoapHeader(
    BaseXmlModel, Generic[AuthType],
    tag='Header',
    ns='soapenv',
    nsmap=_nsmap,
):
    auth: AuthType


class SoapMethod(BaseXmlModel):
    pass


MethodType = TypeVar('MethodType', bound=SoapMethod)


class SoapBody(
    BaseXmlModel, Generic[MethodType],
    tag='Body',
    ns='soapenv',
    nsmap=_nsmap,
):
    call: MethodType


HeaderType = TypeVar('HeaderType', bound=SoapHeader)
BodyType = TypeVar('BodyType', bound=SoapBody)


class _Password(BaseXmlModel, tag="Password", ns="wsse", nsmap=_nsmap):
    type: str = attr("Type",
                     default="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText")
    value: str


class _UsernameToken(BaseXmlModel, tag="UsernameToken", ns="wsse", nsmap=_nsmap):
    id: str = attr("Id", ns="wsu", default="uuid-3FE90A72-14E4-29C8-0782-232001AA1234-5")
    username: str = element("Username", ns="wsse", text=True)
    password: _Password


class Security(
    BaseXmlModel,
    tag='Security',
    ns='wsse',
    nsmap=_nsmap,
):
    must_understand: str = attr("mustUnderstand", ns="wsu", default="1")
    username_token: _UsernameToken


class SoapEnvelope(
    BaseXmlModel,
    Generic[MethodType],
    tag='Envelope',
    ns='soapenv',
    nsmap=_nsmap,
):
    header: SoapHeader[Security]
    body: SoapBody[MethodType]

    @classmethod
    def build(cls, username: str, password: str, method: Type[MethodType], **method_kwargs):
        return cls[method](
            header=SoapHeader[Security](
                auth=Security(
                    username_token=_UsernameToken(
                        username=username,
                        password=_Password(value=password)
                    )
                )
            ),
            body=SoapBody(call=method(**method_kwargs))
        )

    @classmethod
    def build_with_body(cls, username: str, password: str, method: Type[MethodType], body: MethodType):
        return cls[method](
            header=SoapHeader[Security](
                auth=Security(
                    username_token=_UsernameToken(
                        username=username,
                        password=_Password(value=password)
                    )
                )
            ),
            body=SoapBody(call=body)
        )


################################### End copy from pydantic-xml.


"""
Below this point you can define new methods. These are the things that go in the SOAP body in the request. They are
regular Pydantic XML models.
"""


class CheckConnectionMethod(SoapMethod, tag="CheckConnection", ns="v2", nsmap=_nsmap):
    pass


class OrderGetByOrderNumberMethod(SoapMethod, tag="OrderGetByOrderNumber", ns="v2", nsmap=_nsmap):
    order_number: str = element("orderNumber", ns="v2", text=True)


class DropProduct(BaseXmlModel, tag="DropProduct", ns="tel", nsmap=_nsmap):
    logical_tank_guid: str = element("LogicalTankGUID", ns="tel", text=True)
    order_quantity: int = element("OrderQuantity", ns="tel", text=True)
    product_guid: str = element("ProductGUID", ns="tel", text=True)
    source_lift_sequence_number: int = element("SourceLiftSequenceNumber", ns="tel", text=True, default=1)

class DropProducts(BaseXmlModel, tag="OrderDrops", ns="tel", nsmap=_nsmap):
    drop_products: list[DropProduct] = element("DropProduct", ns="tel")

class OrderDrop(BaseXmlModel, tag="OrderDrop", ns="tel", nsmap=_nsmap):
    drop_duration: int = element("DropDuration", ns="tel", text=True)
    drop_products: DropProducts = element("DropProducts", ns="tel")
    earliest_date_time: str = element("EarliestDateTime", ns="tel", text=True)
    latest_date_time: str = element("LatestDateTime", ns="tel", text=True)
    order_type_id: int = element("OrderTypeID", ns="tel", text=True)
    sequence_number: int = element("SequenceNumber", ns="tel", text=True, default=1)
    site_guid: str = element("SiteGUID", ns="tel", text=True)

class OrderDrops(BaseXmlModel, tag="OrderDrops", ns="tel", nsmap=_nsmap):
    order_drops: list[OrderDrop] = element("OrderDrop", ns="tel")

class LiftProduct(BaseXmlModel, tag="LiftProduct", ns="tel", nsmap=_nsmap):
    order_quantity: int = element("OrderQuantity", ns="tel", text=True)
    product_guid: str = element("ProductGUID", ns="tel", text=True)

class LiftProducts(BaseXmlModel, tag="LiftProducts", ns="tel", nsmap=_nsmap):
    lift_products: list[LiftProduct] = element("LiftProduct", ns="tel")

class OrderLift(BaseXmlModel, tag="OrderLift", ns="tel", nsmap=_nsmap):
    lift_products: LiftProducts = element("LiftProducts", ns="tel")
    planned_lift_date_time: str = element("PlannedLiftDateTime", ns="tel", text=True)
    sequence_number: int = element("SequenceNumber", ns="tel", text=True, default=1)

class OrderLifts(BaseXmlModel, tag="OrderLifts", ns="tel", nsmap=_nsmap):
    order_lifts: list[OrderLift] = element("OrderLift", ns="tel")

class TelapointNewOrder(BaseXmlModel, tag="newOrder", ns="v2", nsmap=_nsmap):
    bill_to_guid: str = element("BillToGUID", ns="tel", text=True)
    bill_to_type: str = element("BillToType", ns="tel", text=True)
    carrier_guid: str = element("CarrierGUID", ns="tel", text=True)
    freight_lane_guid: str = element("FreightLaneGUID", ns="tel", text=True)
    order_drops: OrderDrops = element("OrderDrops", ns="tel")
    order_lifts: OrderLifts = element("OrderLifts", ns="tel")
    order_status: str = element("OrderStatus", ns="tel", text=True)
    order_type: str = element("OrderType", ns="tel", text=True)
    po_number: str = element("PONumber", ns="tel", text=True)
    parent_company_guid: str = element("ParentCompanyGUID", ns="tel", text=True)

class OrderAdd(SoapMethod, tag="OrderAdd", ns="v2", nsmap=_nsmap):
    new_order: TelapointNewOrder

class OrderAddResponse(SoapMethod, tag="OrderAddResponse", ns="v2", nsmap=_nsmap):
    order_add_result: str = element("OrderAddResult", text=True)