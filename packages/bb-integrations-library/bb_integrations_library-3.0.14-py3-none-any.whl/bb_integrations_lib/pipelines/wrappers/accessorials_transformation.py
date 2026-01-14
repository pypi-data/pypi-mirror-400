from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.mappers.prices.model import PricePublisher
from bb_integrations_lib.pipelines.parsers.price_engine.parse_accessorials_prices_parser import AccessorialPricesParser
from bb_integrations_lib.pipelines.steps.create_accessorials_step import BBDUploadAccessorialsStep
from bb_integrations_lib.pipelines.steps.exporting.pe_price_export_step import PEPriceExportStep
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.secrets import SecretProvider
from bb_integrations_lib.secrets.factory import APIFactory
from pydantic import BaseModel


class AccessorialPipelineConfig(BaseModel):
    price_publishers: list[PricePublisher]
    accessorial_date_timezone: str = "America/New_York"
    price_instrument_ids: list[int]
    source_system: str = "LCFS"
    hours_back: int = 24


class AccesorialsPriceTransformationPipeline(JobPipeline):
    @classmethod
    async def create(
            cls,
            config_id: str,
            rita_client: GravitateRitaAPI,
            pe_credentials: str,
            sd_credentials: str,
            secret_provider: SecretProvider,
            send_reports: bool = True
    ):
        api_factory = APIFactory(secret_provider)

        config = await rita_client.get_config_by_id(config_id)
        job_config: AccessorialPipelineConfig = AccessorialPipelineConfig.model_validate(config.config)

        steps = [
            {
                "id": "1",
                "parent_id": None,
                "step": PEPriceExportStep(
                    rita_client=rita_client,
                    pe_client=await api_factory.pe(pe_credentials),
                    price_publishers=job_config.price_publishers,
                    config_id=config_id,
                    hours_back=job_config.hours_back,
                    addl_endpoint_args={
                        "IsActiveFilterType": "ActiveOnly",
                        "PriceInstrumentIds": job_config.price_instrument_ids,
                        "IncludeSourceData": False,
                        "IncludeFormulaResultData": False
                    },
                    parser=AccessorialPricesParser,
                    parser_kwargs={
                        "source_system": job_config.source_system,
                        "timezone": job_config.accessorial_date_timezone,
                    }
                )
            },
            {
                "id": "2",
                "parent_id": "1",
                "step": BBDUploadAccessorialsStep(
                    sd_client=await api_factory.sd(sd_credentials),
                )
            }
        ]

        return cls(
            steps,
            rita_client=rita_client,
            pipeline_name=f"Custom Accessorials Price Integration",
            pipeline_config_id=config_id,
            secret_provider=secret_provider,
            send_reports=send_reports
        )
