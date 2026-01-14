from io import TextIOWrapper
from loguru import logger
from typing import Dict, AsyncIterable

from bb_integrations_lib.models.dtn_supplier_invoice import DTNSupplierInvoice, Parser
from bb_integrations_lib.protocols.pipelines import GeneratorStep
from bb_integrations_lib.shared.model import RawData


class ParseDTNInvoiceStep(GeneratorStep):
    def __init__(self, skip_failed: bool = True, *args, **kwargs) -> None:
        """
        Parse a DTN invoice and convert it into one or more modeled invoice items.

        :param skip_failed: Whether to skip any invoices in this file that fail to parse.
        """
        super().__init__(*args, **kwargs)
        self.skip_failed = skip_failed

    def describe(self) -> str:
        return "Parse a DTN supplier invoice file into one or more invoice models"

    async def generator(self, i: RawData) -> AsyncIterable[DTNSupplierInvoice]:
        try:
            p = Parser()
            tio = TextIOWrapper(i.data, encoding="utf-8")
            tio.seek(0)
            res = p.parse(tio)
            tio.detach() # Don't allow the CSV module to close the underlying BytesIO in case another step wants to use it
            for invoice in res:
                invoice.original_filename = i.file_name
                yield invoice
        except Exception as e:
            if self.skip_failed:
                logger.exception(f"Failed to process file {i.file_name}, skipping")
                return
            else:
                raise e
