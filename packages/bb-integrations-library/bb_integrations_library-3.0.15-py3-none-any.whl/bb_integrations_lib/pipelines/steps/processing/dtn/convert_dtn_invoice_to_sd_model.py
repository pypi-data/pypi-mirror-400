import itertools
from datetime import datetime
from operator import attrgetter
from typing import Callable

from bb_integrations_lib.models.dtn_supplier_invoice import DTNSupplierInvoice, Item, ItemTax, SummaryTax, \
    DeferredTaxItem
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import SDSupplierInvoiceCreateRequest, SDSupplierInvoiceDetail, \
    SDSupplierInvoiceDetailType


class ConvertDTNInvoiceToSDModel(Step):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self) -> str:
        return "Convert DTN invoice data model to SD supplier invoice data model"

    async def execute(self, i: DTNSupplierInvoice) -> SDSupplierInvoiceCreateRequest:
        return self.convert_dtn_invoice(i)

    def convert_dtn_invoice_deferred_tax_item(self, deferred_tax: DeferredTaxItem) -> SDSupplierInvoiceDetail:
        return SDSupplierInvoiceDetail(
            bol_number=None, # Not present for summary taxes, since they're invoice level
            bol_date_local=None,
            type=SDSupplierInvoiceDetailType.tax,
            product=None,
            tax_type=None,
            tax_description=deferred_tax.description,
            tax_authority=None,
            tax_non_deferred=False,
            rate=deferred_tax.amount,
            amount=1,
            total=deferred_tax.amount,
            uom=None,
            gross_volume=None,
            net_volume=None,
        )

    def convert_dtn_invoice_summary_tax(self, summary_tax: SummaryTax) -> SDSupplierInvoiceDetail:
        return SDSupplierInvoiceDetail(
            bol_number=None, # Not present for summary taxes, since they're invoice level
            bol_date_local=None,
            type=SDSupplierInvoiceDetailType.tax,
            product=None,
            tax_type=summary_tax.tax_code,
            tax_description=summary_tax.description,
            tax_authority=None,
            tax_non_deferred=not summary_tax.deferred,
            rate=summary_tax.rate,
            amount=summary_tax.quantity_billed,
            total=summary_tax.line_total,
            uom=summary_tax.unit_of_measure,
            gross_volume=None,
            net_volume=None,
        )

    def convert_dtn_invoice_item_tax(
            self, item_tax: ItemTax, item_product: str, bol_date: datetime | None
    ) -> SDSupplierInvoiceDetail:
        return SDSupplierInvoiceDetail(
            bol_number=item_tax.bol_number,
            bol_date_local=bol_date,
            type=SDSupplierInvoiceDetailType.tax,
            product={"source_name": item_product},
            tax_type=item_tax.tax_code,
            tax_description=item_tax.description,
            tax_authority=None,
            tax_non_deferred=not item_tax.deferred,
            rate=item_tax.rate,
            amount=item_tax.quantity_billed,
            total=item_tax.line_total,
            uom=item_tax.unit_of_measure,
            gross_volume=item_tax.quantity_billed,
            net_volume=item_tax.quantity_billed,
        )

    def convert_dtn_invoice_item(self, invoice_detail: Item) -> list[SDSupplierInvoiceDetail]:
        product = invoice_detail.description
        bol_date = invoice_detail.ship_datetime
        item_detail = SDSupplierInvoiceDetail(
            bol_number=invoice_detail.bol_number,
            bol_date_local=bol_date,
            type=SDSupplierInvoiceDetailType.supply,
            product={"source_name": product},
            rate=invoice_detail.rate,
            amount=invoice_detail.quantity_billed,
            total=invoice_detail.line_total,
            uom=invoice_detail.unit_of_measure,
            gross_volume=invoice_detail.gross_quantity or invoice_detail.quantity_billed,
            net_volume=invoice_detail.net_quantity or invoice_detail.quantity_billed
        )
        tax_details = [
            self.convert_dtn_invoice_item_tax(tax, product, bol_date) for tax in invoice_detail.tax_records or []
        ]
        # Should we support RINS numbers here? How?
        return [item_detail] + tax_details

    @staticmethod
    def resolve_field(invoice: DTNSupplierInvoice, attr_getter: Callable[[Item], str]) -> str | None:
        """
        Resolve a specific field from the invoice line items, if they are all the same.
         :return: The return value retrieved by calling attr_getter on each invoice item, if all are the same (or if
           only one item is present), or None if no items are present or if any items disagree with each other.
        """
        # Get a list of terminals from the invoice line items, where the terminal is not blank
        item_fields = list(map(attr_getter, invoice.items))
        if len(set(item_fields)) == 1:
            return item_fields[0]
        return None

    def convert_dtn_invoice(self, invoice: DTNSupplierInvoice) -> SDSupplierInvoiceCreateRequest:
        deferred_tax_details = []
        summary_tax_details = []
        if invoice.deferred_taxes is not None:
            deferred_tax_details.extend([
                self.convert_dtn_invoice_deferred_tax_item(detail_item)
                for detail_item in invoice.deferred_taxes.items
            ])
        for summary_tax in invoice.summary_taxes:
            summary_tax_details.append(
                self.convert_dtn_invoice_summary_tax(summary_tax)
            )
        return SDSupplierInvoiceCreateRequest(
            invoice_number=invoice.header.invoice_number,
            source_name=invoice.header.sold_to_name,
            supplier=invoice.header.seller_name,
            terminal=self.resolve_field(invoice, attrgetter("ship_from_name")) or None,
            due_date_local=invoice.header.invoice_due_date,
            # Convert date to datetime at midnight
            invoice_date_local=datetime.combine(invoice.header.invoice_date, datetime.min.time()),
            # Get a flattened list, since each call to convert_dtn_invoice_item yields a list of 1 or more detail items
            # Then tack on summary and deferred tax details, when applicable.
            details=list(itertools.chain.from_iterable(
                [self.convert_dtn_invoice_item(item) for item in invoice.items]
            )) + summary_tax_details + deferred_tax_details,
            extra_data={
                "invoice_filename": invoice.original_filename
            } if invoice.original_filename else {},
            ship_to_city=self.resolve_field(invoice, attrgetter("ship_to_city")) or None,
            ship_to_state=self.resolve_field(invoice, attrgetter("ship_to_state")) or None,
            ship_from_city=self.resolve_field(invoice, attrgetter("ship_from_city")) or None,
            ship_from_state=self.resolve_field(invoice, attrgetter("ship_from_state")) or None,
        )
