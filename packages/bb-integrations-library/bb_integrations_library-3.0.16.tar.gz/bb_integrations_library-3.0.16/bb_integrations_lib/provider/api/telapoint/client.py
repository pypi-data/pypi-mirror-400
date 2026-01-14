import httpx
import loguru
from bb_integrations_lib.provider.api.telapoint.model import CheckConnectionMethod, SoapEnvelope, OrderGetByOrderNumberMethod, TelapointNewOrder, OrderAdd

namespaces = {
    'soapenv': "http://schemas.xmlsoap.org/soap/envelope/",
    'tel': "http://schemas.datacontract.org/2004/07/TelaPoint.Api.TelaFuel.Models",
    'v2': "http://api.telapoint.com/TelaFuel/v2",
    'i': "http://www.w3.org/2001/XMLSchema-instance",
    'wsse': "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
    'wsu': "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
}


class TelapointClient(httpx.AsyncClient):
    def __init__(self, username: str, password: str):
        super().__init__(
            base_url="https://api.telapoint.com/APIv2/TelaFuelService.svc",
            headers={"Content-Type": "text/xml"}
        )
        self.base_url = "https://api.telapoint.com/APIv2/TelaFuelService.svc"
        self.username = username
        self.password = password

    async def check_connection(self):
        req = SoapEnvelope.build(self.username, self.password, CheckConnectionMethod)

        response = await super().post(
            url="",
            headers={"SOAPAction": "http://api.telapoint.com/TelaFuel/v2/ITelaFuelService/CheckConnection"},
            content=req.to_xml()
        )
        loguru.logger.debug(response.status_code)
        return response

    async def get_order_by_order_number(self, order_number: str):
        req = SoapEnvelope.build(self.username, self.password, OrderGetByOrderNumberMethod, order_number=order_number)

        response = await super().post(
            url="",
            headers={"SOAPAction": "http://api.telapoint.com/TelaFuel/v2/ITelaFuelService/OrderGetByOrderNumber"},
            content=req.to_xml()
        )
        loguru.logger.debug(response.status_code)
        return response

    async def create_order(self, new_order: TelapointNewOrder):
        req = SoapEnvelope.build_with_body(self.username, self.password, OrderAdd, OrderAdd(new_order=new_order))

        response = await super().post(
            url="",
            headers={"SOAPAction": "http://api.telapoint.com/TelaFuel/v2/ITelaFuelService/OrderAdd"},
            content=req.to_xml()
        )
        loguru.logger.debug(response.status_code)
        return response


if __name__ == "__main__":
    import asyncio

    async def main():
        tc = TelapointClient("<>", "<>")
        resp = await tc.check_connection()
        resp = await tc.get_order_by_order_number(order_number="51412828")
        pass

    asyncio.run(main())
