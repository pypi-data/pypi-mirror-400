import io
import pprint
import warnings
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, Iterable, Union, Tuple, Literal, List, Self
import pandas as pd
from async_lru import alru_cache
from httpx import Response, HTTPStatusError
from loguru import logger
from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.models.sd_api import OrderUpdateRequest, SendToCarrierRequest
from bb_integrations_lib.secrets import SDCredential
from bb_integrations_lib.protocols.flat_file import TankReading, PriceRow, TankSales, DriverCredential, \
    SalesAdjustedDeliveryReading
from bb_integrations_lib.shared.model import SupplyPriceUpdateManyRequest, GetOrderBolsAndDropsRequest, \
    GetFreightInvoicesRequest, SDSupplierInvoiceCreateRequest, SDGetAllSupplierReconciliationInvoiceRequest, \
    SDDeliveryReconciliationMatchOverviewRequest, SDGetUnexportedOrdersRequest, SDSetOrderExportStatusRequest
from bb_integrations_lib.util.config.model import Config


class GravitateSDAPI(BaseAPI):
    def __init__(
            self,
            base_url: str,
            client_id: str | None = None,
            client_secret: str | None = None,
            username: str | None = None,
            password: str | None = None,
            raise_errors: bool = True,
    ):
        super().__init__(raise_errors)
        self.base_url = self.valid_url(base_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self._token = None

    @classmethod
    def from_config(cls, config_name: str, username: str | None = None, password: str | None = None):
        warnings.warn("Use gravitate.sd_api.from_credential instead", DeprecationWarning, stacklevel=2)

    @classmethod
    def from_global_config(cls, c: Config):
        warnings.warn("Use gravitate.sd_api.from_credential instead", DeprecationWarning, stacklevel=2)

    @classmethod
    def from_credential(cls, credential: SDCredential) -> Self:
        return cls(
            base_url=credential.host,
            username=credential.username,
            password=credential.password,
            client_id=credential.client_id,
            client_secret=credential.client_secret,
        )

    @staticmethod
    def valid_url(url: str) -> str:
        if not url:
            return ""
        if not url.endswith("/"):
            url += "/"
        if "api" not in url and ":80" not in url and "local" not in url:  # MOFO
            url += "api/"
        if not url.startswith("http"):
            raise ValueError(f"Invalid URL: {url} must begin with http or https")
        return url

    async def _get_user_pass_token(self) -> str:
        try:
            resp = await self.post(
                url=f"{self.base_url}token",
                data={
                    "username": self.username,
                    "password": self.password,
                    "scope": "bbd",
                },
                timeout=120
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
        except Exception as e:
            logger.error(f"Error requesting token from {self.base_url} with username {self.username}: {e}")
            raise e

    async def _get_api_key_token(self) -> str:
        try:
            resp = await self.post(
                url=f"{self.base_url}token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "bbd",
                },
                timeout=120
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
        except Exception as e:
            logger.error(f"Error requesting token from {self.base_url} with client ID {self.client_id}: {e}")
            raise e

    async def _get_token(self):
        if not (self.username and self.password) and not (self.client_id and self.client_secret):
            raise RuntimeError("Missing credentials for token request")

        if self.username and self.password:
            try:
                self._token = await self._get_user_pass_token()
                return self._token
            except:
                pass
        if self.client_id and self.client_secret:
            try:
                self._token = await self._get_api_key_token()
                return self._token
            except:
                pass

        raise Exception(
            "Could not get token with either username/password or client ID/secret. Check your credentials.")

    async def _auth_request(self, method: str, **kwargs):
        if not self._token:
            await self._get_token()

        headers = kwargs.pop("headers", {})
        headers["authorization"] = f"Bearer {self._token}"
        kwargs["headers"] = headers
        kwargs["url"] = f"{self.base_url}{kwargs.get('url', '')}"
        kwargs["timeout"] = kwargs.get("timeout", 90)

        response = await getattr(self, method)(**kwargs)

        if response.status_code == 401:
            await self._get_token()  # refresh token
            headers["authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers
            response = await getattr(self, method)(**kwargs)

        if response.status_code == 422:
            try:
                response_content = pprint.pformat(response.json())
            except JSONDecodeError:
                response_content = response.text
            raise HTTPStatusError(
                f"Bad request: \n{response_content}",
                request=response.request,
                response=response
            )

        return response

    async def token_post(self, **kwargs):
        return await self._auth_request("post", **kwargs)

    async def token_get(self, **kwargs):
        return await self._auth_request("get", **kwargs)

    async def call_ep(self, url: str, params: dict = None, json: dict = None, method: str = "POST") -> Response:
        if method == "POST":
            return await self.token_post(url=url, params=params, json=json)
        if json is not None:
            raise ValueError("JSON is not supported for GET requests")
        return await self.token_get(url=url, params=params)

    async def get_lp_config(self) -> Response:
        url = f"best_buy/get_lp_config"
        return await self.token_post(url=url)

    async def set_lp_config(self, payload: dict) -> Response:
        url = "best_buy/set_lp_config"
        return await self.token_post(url=url, json=payload)

    async def update_lp_config(self, updates: dict) -> Response:
        existing = self.get_lp_config()
        return await self.set_lp_config(payload={**existing, **updates})

    async def get_model_config(self) -> Response:
        url = "best_buy/get_model_config"
        return await self.token_post(url=url)

    async def set_model_config(self, payload: dict) -> Response:
        url = "best_buy/set_model_config"
        return await self.token_post(url=url, json=payload)

    async def update_model_config(self, updates: dict) -> Response:
        existing = await self.get_model_config()
        return await self.set_model_config(payload={**existing, **updates})

    async def update_tank_supply_many(self, payload: dict) -> Response:
        url = "store/tank/supply/assign_many"
        return await self.token_post(url=url, json=payload)

    async def valuation_delivery_send(self, params: dict) -> Response:
        url = "valuation/delivery/send"
        return await self.token_post(url=url, params=params)

    @alru_cache(maxsize=128)
    async def get_all_store_tanks(self) -> Response:
        url = "store/tank/all"
        return await self.token_post(url=url)

    @alru_cache(maxsize=128)
    async def get_all_stores(self, include_tanks: bool = False) -> Response:
        url = "v1/store/all"
        return await self.token_post(url=url,
                                     params={
                                         "include_tanks": include_tanks,
                                     },
                                     )

    async def get_all_store_tanks_lkp(self) -> Dict[str, dict]:
        """returns store tank lkp, key is store_number+tank_id"""
        try:
            data = await self.get_all_store_tanks()
            data = data.json()
            res = {f"{row['store_number']}{row['tank_id']}": row for row in data}
        except Exception as e:
            logger.error(f"Error while building Tank lookup: {e}")
            res = {}
        return res

    async def get_all_stores_lkp(self) -> Dict[str, dict]:
        """returns store lkp, key is store_number"""
        try:
            data = await self.get_all_stores()
            data = data.json()
            res = {f"{row['store_number']}": row for row in data}
        except Exception as e:
            logger.error(f"Error while building store lookup: {e}")
            res = {}
        return res

    async def get_valuation_report(self, start_date: str = None, end_date: str = None):
        url = "valuation/valuation/export"
        params = {"start_date": start_date, "end_date": end_date}
        resp = await self.token_post(url=url, params=params)
        if resp.status_code == 200:
            with io.BytesIO(resp.content) as f:
                df = pd.read_excel(f)
                df["Site"] = df["Site"].astype(str)
                df["Date"] = pd.to_datetime(df["Date"])
                return df[["Site", "Product", "Date", "Initial Volume", "Final Volume"]]
        else:
            logger.error("Valuation Export Failed.")

    async def upsert_many_counterparty(self, payload: list[dict]) -> Response:
        url = "v1/counterparty/upsert_many"
        return await self.token_post(url=url, json=payload)

    async def driver_schedule_template_upsert(self, payload: dict) -> Response:
        url = "driver_schedule/template/upsert"
        return await self.token_post(url=url, json=payload)

    async def import_sales_data(self, payload) -> Response:
        url = "forecast/import_sales_data"
        request_data = {"reqs": payload}
        return await self.token_post(url=url, json=request_data)

    async def update_store(self, payload) -> Response:
        url = "store/update"
        request_data = payload
        return await self.token_post(url=url, json=request_data)

    async def update_many_store(self, payload) -> Response:
        url = "v1/store/upsert_many"
        return await self.token_post(url=url, json=payload)

    async def update_many_locations(self, payload) -> Response:
        url = "v1/location/upsert_many"
        return await self.token_post(url=url, json=payload)

    async def forecast_import_sales_data(self, payload) -> Response:
        url = "v1/import_sales_data"
        return await self.token_post(url=url, json=payload)

    async def payroll_export_file(self, date: str):
        url = "v1/payroll/export_file"
        resp = await self.token_get(url=url, params={"date": date})
        resp.raise_for_status()
        return resp

    async def order_export_file(self, date: str, **kwargs):
        url = "backoffice_erp/export"
        resp = await self.token_get(url=url, params={"as_of": date, **kwargs})
        resp.raise_for_status()
        return resp

    async def payroll_export(self, date: str, **kwargs):
        url = "v1/payroll/export"
        return await self.token_get(url=url, params={"date": date, **kwargs})

    async def upload_readings(self, data: Iterable[TankReading], raise_error=True) -> Response:
        """Uploads tank readings to BBD. Set raise_error to false to squelch the exception that's thrown if at least one
        reading does not upload."""
        url = "v1/tank_readings/upload"
        resp = await self.token_post(url=url, json=data)
        if resp.status_code != 200:
            logger.error(resp.text)
        return resp

    async def upload_tank_sales(self, data: Iterable[TankSales]) -> Dict:
        url = "v1/import_sales_data"
        json_data = [item.model_dump() if hasattr(item, 'model_dump') else item for item in data]
        request_data = {"reqs": json_data}
        resp = await self.token_post(url=url, json=request_data)
        if resp.status_code != 200:
            logger.error(resp.text)
            raise Exception(f"Upload failed with status code {resp.status_code}: {resp.text}")
        return resp.json()

    async def upload_prices(self, data: Union[Iterable[PriceRow], Iterable[SupplyPriceUpdateManyRequest]]) -> Tuple[
        int, Dict]:
        url = "v1/price_update_many"
        json_data = [item.model_dump() if hasattr(item, 'model_dump') else item for item in data]
        resp = await self.token_post(url=url, json=json_data)
        if resp.status_code != 200:
            logger.error(resp.text)
            raise Exception(f"Upload failed with status code {resp.status_code}: {resp.text}")
        resp_data = resp.json()
        if not resp_data.get("created") and not resp_data.get("bad_data"):
            raise Exception(f"Uploaded prices responded with an error: {resp_data}")
        return resp_data.get("created", 0) + resp_data.get("end_dated", 0), resp_data

    async def upload_credentials(self, data: Iterable[DriverCredential]) -> Response:
        url = "v1/driver/credential/upsert_many",
        resp = await self.token_post(url=url, json=data)
        if resp.status_code != 200:
            logger.error(resp.text)
        return resp.json()

    async def upload_sales_adjusted_deliveries(self, data: Iterable[SalesAdjustedDeliveryReading]) -> int:
        """Upload many sales adjusted deliveries.

        :returns: The number of successfully uploaded deliveries.
        """
        url = "v1/sales_adjusted_delivery/upsert_many"
        json_data = [x.model_dump(mode="json") for x in data]
        resp = await self.token_post(url=url, json=json_data)
        if resp.status_code != 200:
            logger.error(resp.text)
        if resp.content == b"null":
            return 0
        else:
            uploaded_count = resp.json().get("inserted_count", 0)
            return uploaded_count

    async def upload_supplier_invoice(self, invoice: SDSupplierInvoiceCreateRequest) -> Response:
        url = "v1/supplier_reconciliation/invoice/create"
        resp = await self.token_post(url=url, json=invoice.model_dump(mode="json"))
        if resp.status_code != 200:
            logger.error(resp.text)
        return resp

    async def get_all_supplier_reconciliation_invoices(self,
                                                       req: SDGetAllSupplierReconciliationInvoiceRequest) -> Response:
        url = "v1/supplier_reconciliation/invoice/all"
        resp = await self.token_post(url=url, json=req.model_dump(mode="json"))
        resp.raise_for_status()
        return resp

    async def delivery_reconciliation_match_overview(self,
                                                     req: SDDeliveryReconciliationMatchOverviewRequest) -> Response:
        url = "v1/delivery_reconciliation/match/overview"
        resp = await self.token_post(url=url, json=req.model_dump(mode="json"))
        resp.raise_for_status()
        return resp

    async def all_counterparties(self) -> Response:
        return await self.token_post(url="v1/counterparty/all")

    async def all_locations(self) -> Response:
        return await self.token_post(url="v1/location/all")

    async def all_stores(self, include_tanks: bool = False) -> Response:
        return await self.token_post(url="v1/store/all", params={"include_tanks": include_tanks})

    async def all_drivers(self) -> Response:
        return await self.token_post(url="v1/driver/all")

    async def all_products(self) -> Response:
        return await self.token_post(url="v1/product/all")

    async def all_trailers(self) -> Response:
        return await self.token_post(url="v1/trailer/all")

    async def all_tractors(self) -> Response:
        return await self.token_post(url="v1/tractor/all")

    async def all_depots(self) -> Response:
        return await self.token_post(url="v1/depot/all")

    async def all_markets(self) -> Response:
        return await self.token_post(url="v1/market/all")

    async def get_unexported_orders(self, req: SDGetUnexportedOrdersRequest) -> Response:
        return await self.token_post(url="v1/order/unexported", json=req.model_dump(mode="json"))

    async def bulk_set_export_order_status(self, req: List[SDSetOrderExportStatusRequest]) -> Response:
        serialized = [row.model_dump(mode="json") for row in req]
        return await self.token_post(url="v1/order/set_export_status", json=serialized)

    async def upsert_directives(self, req: list[dict]) -> Response:
        return await self.token_post(url="v1/directive/upsert_many", json=req)

    async def export_single_order(self, order_number: int, function_name: str) -> Response:
        params = {"order_number": order_number, "function_name": function_name}
        return await self.token_post(url=f"backoffice_erp/export_single", params=params)

    async def mark_backhaul_exported(self, order_number: int) -> Response:
        params = {"order_number": order_number}
        return await self.token_post(url=f"backoffice_erp/mark_backhaul_exported", params=params)

    async def get_orders(
            self,
            order_id: str | None = None,
            order_number: str | int | None = None,
            order_type: Literal["Regular", "Backhaul"] | None = None,
            order_state: Literal["Accepted", "Assigned", "In Progress", "Complete", "Canceled"] | None = None,
            order_date_start: datetime | None = None,
            order_date_end: datetime | None = None,
            last_change_date: datetime | None = None,
            reference_order_number: str | None = None,
    ) -> Response:
        body = {
            k: v for k, v in {
                "order_id": order_id,
                "order_number": order_number,
                "order_type": order_type,
                "order_state": order_state,
                "order_date_start": order_date_start.isoformat(timespec='microseconds') if order_date_start else None,
                "order_date_end": order_date_end.isoformat(timespec='microseconds') if order_date_end else None,
                "last_change_date": last_change_date.isoformat(timespec='microseconds') if last_change_date else None,
                "reference_order_number": reference_order_number if reference_order_number else None,
            }.items()
            if v is not None
        }
        # POST null body instead of empty dict if we don't have any parameters
        resp = await self.token_post(url="v1/order/get_orders", json=body or None)
        resp.raise_for_status()
        return resp

    async def get_orders_overview(self, filter: dict):
        data = {"filter": filter}
        return await self.token_post(url="order/overview", json=data)

    async def get_bols_and_drops(self, req: GetOrderBolsAndDropsRequest) -> Response:
        url = "v1/bols_and_drops"
        response = await self.token_post(url=url, json=req.model_dump(mode="json", exclude_none=True))
        response.raise_for_status()
        return response

    async def get_order_allocations(self, order_number: str) -> Response:
        params = {'order_number': order_number, 'save': False}
        return await self.token_post(url='bol/allocate_bols', params=params)

    async def get_driver_schedules(self, driver_shift: str, driver_schedule_date: datetime) -> Response:
        data = {
            "shift": driver_shift,
            "date": driver_schedule_date,
        }
        return await self.token_post(url='driver_schedule/schedule', json=data)

    async def get_driver_tracking(self, order_numbers: list[int] | None = None,
                                  driver_schedule_ids: list[str] | None = None) -> Response:
        data = {
            "order_numbers": order_numbers,
            "driver_schedule_ids": driver_schedule_ids,
        }
        return await self.token_post(url="v1/driver_tracking/all", json=data)

    async def get_driver_schedules_tracking(self, driver_schedule_ids: list[str]) -> Response:
        data = {"driver_schedule_ids": driver_schedule_ids}
        return await self.token_post(url='v1/driver_tracking/all', json=data)

    async def get_route_overview(self, location_id: str) -> Response:
        data = {"location_id": location_id}
        return await self.token_post(url="logistics/route/overview", json=data)

    async def create_order(self, order: dict) -> Response:
        return await self.token_post(url="v1/order/create", json=order)

    async def run_smart_supply(self, req: dict) -> Response:
        return await self.token_post(url="smart_supply/run", json=req)

    async def get_smart_supply_state(self) -> Response:
        return await self.token_post(url="smart_supply/state", json={})

    async def cancel_smart_supply(self, id: str) -> Response:
        return await self.token_post(url="smart_supply/cancel", params={"smart_supply_id": id})

    async def update_allocations(self, req: dict) -> Response:
        return await self.token_post(url="directive_management/update_allocations", json=req)

    async def update_order_status(self, req: dict) -> Response:
        return await self.token_post(url="v1/order/update_status", json=req)

    async def cancel_order(self, req: dict) -> Response:
        return await self.token_post(url="order/cancel_order", json=req)

    async def save_bols(self, req: dict) -> Response:
        return await self.token_post(url="v1/order/save_bol", json=req)

    async def save_drop(self, req: dict) -> Response:
        return await self.token_post(url="v1/order/save_drop", json=req)

    async def get_tractors(self) -> Response:
        return await self.token_post(url="v1/tractor/all")

    async def get_drivers(self) -> Response:
        return await self.token_post(url="v1/driver/all")

    async def get_freight_invoices(self, req: GetFreightInvoicesRequest):
        url = "v1/freight/invoice/all"
        resp = await self.token_post(url=url, json=req.model_dump(mode="json", exclude_none=True))
        resp.raise_for_status()
        return resp

    async def mark_invoices_exported(self, invoice_numbers: list[str]):
        url = "v1/freight/invoice/mark_export"
        resp = await self.token_post(url=url, json={"invoice_numbers": invoice_numbers})
        resp.raise_for_status()
        return resp

    async def get_freight_v2(self, req: dict) -> Response:
        response = await self.token_post(url="v2/order/freight", json=req)
        response.raise_for_status()
        return response

    async def get_bol_images(self, order_numbers: list[str]) -> Response:
        response = await self.token_post(url="v1/bol_images", json={"order_numbers": order_numbers})
        return response

    async def upload_bol_image(self, bol_number: str, order_number: str, note: str, file_name: str, photo_bytes: bytes):
        params = {"bol_number": bol_number, "order_number": order_number, "load_or_drop": "load", "note": note}
        files = {"file": (file_name, photo_bytes)}
        response = await self.token_post(url="v1/order/upload_bol", params=params, files=files)
        return response

    async def update_order(self, req: OrderUpdateRequest) -> Response:
        response = await self.token_post(url="v1/order/update", json=req.model_dump(mode="json"))
        return response

    async def assign_carrier(self, req: dict) -> Response:
        response = await self.token_post(url="driver_schedule/assign_carrier_order", json=req)
        return response

    async def send_to_carrier(self, req: SendToCarrierRequest) -> Response:
        response = await self.token_post(url="order/send_to_carrier", json=req.model_dump(mode="json"))
        return response

    async def set_order_export_status(self, order_ids: list[str], status: str) -> Response:
        return await self.token_post(
            url="v1/order/set_export_status",
            json=[{
                "order_id": n,
                "status": status
            } for n in order_ids]
        )

    async def upsert_special_pay_requests(self, req: list[dict]) -> Response:
        return await self.token_post(url="v1/payroll/special_pay_request/upsert_many", json=req)

    async def all_ratebooks(self):
        params = {"book_type": "Revenue"}
        response = await self.token_post(url="freight/ratebook/overview", params=params)
        response.raise_for_status()
        return response


