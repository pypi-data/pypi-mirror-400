from pydantic_xml import BaseXmlModel, element


class Sender(
    BaseXmlModel,
):
    load_id: str = element("LoadID")

class Requestor(
    BaseXmlModel,
):
    mpid: str = element("MPID")
    load_id: str = element("LoadID")

class AllowAccessFrom(
    BaseXmlModel,
):
    mpid: str = element("MPID")

class Coordinates(
    BaseXmlModel,
):
    latitude: float = element("Latitude")
    longitude: float = element("Longitude")

class Location(
    BaseXmlModel,
):
    coordinates: Coordinates = element("Coordinates")
    created_date_time: str = element("CreatedDateTime")

class LocationUpdateRequest(
    BaseXmlModel,
    tag="TMSLocationData",
    nsmap={"": 'http://macropoint-lite.com/xml/1.0'}
):
    sender: Sender = element("Sender")
    requestor: Requestor = element("Requestor")
    allow_access_from: AllowAccessFrom = element("AllowAccessFrom")
    location: Location = element("Location")
