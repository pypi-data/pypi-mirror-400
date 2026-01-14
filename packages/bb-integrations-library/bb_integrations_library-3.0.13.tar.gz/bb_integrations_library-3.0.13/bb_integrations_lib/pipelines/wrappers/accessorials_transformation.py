from bb_integrations_lib.mappers.prices.model import  PricePublisher
from bb_integrations_lib.models.pipeline_structs import PipelineProcessReportConfig
from bb_integrations_lib.pipelines.parsers.price_engine.parse_accessorials_prices_parser import AccessorialPricesParser
from bb_integrations_lib.pipelines.steps.create_accessorials_step import BBDUploadAccessorialsStep
from bb_integrations_lib.pipelines.wrappers.wrapper import PipelineWrapper
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.pipelines.steps.exporting.pe_price_export_step import PEPriceExportStep
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from loguru import logger
from pydantic import BaseModel



class AccessorialPipelineConfig(BaseModel):
    price_publishers: list[PricePublisher]
    accessorial_date_timezone: str = "America/New_York"
    price_instrument_ids: list[int]
    source_system: str = "LCFS"
    hours_back: int = 24



class AccesorialsPriceTransformationPipeline(JobPipeline):
    def __init__(self,
                 config: AccessorialPipelineConfig,
                 config_id: str,
                 tenant_name: str = "Loves",
                 mode: str = "development",
                 ):
        self.mode = mode
        self.tenant_name = tenant_name
        self.config_manager = GlobalConfigManager()
        self.secret_data = self.config_manager.get_environment(environment_name=self.tenant_name)
        self.config = config
        self.config_id = config_id
        self.process_report_config = PipelineProcessReportConfig(
            config_id=self.config_id,
            trigger=f"{self.tenant_name} Custom Accessorials Price Integration",
            rita_url=self.secret_data.prod.rita.base_url,
            rita_client_id=self.secret_data.prod.rita.client_id,
            rita_client_secret=self.secret_data.prod.rita.client_secret,
            rita_tenant=self.tenant_name,
        )
        steps = [
            {
                "id": "1",
                "parent_id": None,
                "step": PEPriceExportStep({
                    "tenant_name": self.tenant_name,
                    "price_publishers": self.config.price_publishers,
                    "mode": self.mode,
                    "config_id": self.config_id,
                    "hours_back": self.config.hours_back,
                    "additional_endpoint_arguments": {
                        "IsActiveFilterType": "ActiveOnly",
                        "PriceInstrumentIds": self.config.price_instrument_ids,
                        "IncludeSourceData": False,
                        "IncludeFormulaResultData": False
                    },
                    "parser": AccessorialPricesParser,
                    "parser_kwargs": {
                        "source_system":self.config.source_system,
                        "timezone": self.config.accessorial_date_timezone,
                    }
                })
            },
            {
                "id": "2",
                "parent_id": "1",
                "step": BBDUploadAccessorialsStep({
                    "tenant_name": self.tenant_name,
                    "mode": self.mode,
                })
            }

        ]
        super().__init__(steps, None, catch_step_errors=True, process_report_config=self.process_report_config)


class CreateAccessorialReportPipeline(PipelineWrapper):
    def __init__(self,
                 tenant_name: str,
                 bucket_name: str,
                 mode: str = "test",
                 config_class=AccessorialPipelineConfig,
                 ):
        super().__init__(
            tenant_name=tenant_name,
            bucket_name=bucket_name,
            config_class=config_class,
            mode=mode
        )

    async def create(self,
                     config_name: str,
                     ) -> AccesorialsPriceTransformationPipeline:
        config, config_id, name = await self.load_config(config_name)
        logger.info(
            f"Loaded config for tenant '{self.tenant_name}' with name '{name}': {config.model_dump()}"
        )
        return AccesorialsPriceTransformationPipeline(config_id=config_id,
                                                              tenant_name=self.tenant_name,
                                                              config=config,
                                                              mode=self.mode)