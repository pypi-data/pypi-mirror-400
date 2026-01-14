import json
import sys
from datetime import datetime, UTC
from typing import Any, Protocol, Tuple, TypeVar, Iterable, runtime_checkable, Optional, \
    AsyncIterable, AsyncGenerator, Type, Union, List, Dict, Generic, Self

from loguru import logger
from pydantic import BaseModel

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.mappers.rita_mapper import RitaMapper, RitaAPIMappingProvider, AsyncMappingProvider
from bb_integrations_lib.models.pipeline_structs import StopBranch, StopPipeline, PipelineContext, \
    NoPipelineData, NoPipelineSourceData
from bb_integrations_lib.models.rita.audit import CreateReportV2, ProcessReportV2Status, \
    UploadProcessReportFile
from bb_integrations_lib.models.rita.config import MaxSync
from bb_integrations_lib.models.rita.issue import IssueCategory
from bb_integrations_lib.secrets import IntegrationSecretProvider, SecretProvider, RITACredential
from bb_integrations_lib.secrets.factory import APIFactory
from bb_integrations_lib.shared.exceptions import StepConfigValidationError, MapperLoadError
from bb_integrations_lib.shared.model import MappingMode
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from bb_integrations_lib.util.utils import CustomJSONEncoder

Input = TypeVar("Input")
Output = TypeVar("Output")
StepConfig = TypeVar("StepConfig", bound=Optional[BaseModel])
T = TypeVar("T")


@runtime_checkable
class Step(Protocol[Input, Output]):
    """
    Protocol for pipeline steps that process data with optional configuration validation.
    
    A Step represents a single unit of work in a job pipeline, such as fetching files,
    transforming data, or uploading results. Each step receives input data, processes it,
    and produces output for the next step in the pipeline.
    
    Type Parameters:
        Input: The type of data this step accepts as input
        Output: The type of data this step produces as output  
        Config: Optional Pydantic BaseModel subclass for configuration validation, or None
    
    Configuration vs Input:
        - Configuration: Static settings provided at step creation (credentials, settings)
        - Input: Dynamic data passed from the previous step during execution
        
    Examples:
        Basic step without config validation:
        ```python
        class SimpleStep(Step[str, int, None]):
            def __init__(self, step_configuration=None):
                super().__init__(step_configuration)
            
            def describe(self) -> str:
                return "Converts string to length"
                
            async def execute(self, text: str) -> int:
                return len(text)
        ```
        
        Step with Pydantic configuration validation:
        ```python
        class DatabaseConfig(BaseModel):
            host: str
            port: int
            database: str
            
        class DatabaseStep(Step[dict, list, DatabaseConfig]):
            def __init__(self, step_configuration: dict):
                super().__init__(step_configuration, DatabaseConfig)
                self.validate_config()  # Validates against DatabaseConfig BaseModel
                
            async def execute(self, query_data: dict) -> list:
                # Access validated config properties: self.config_class.host, etc.
                return await self.fetch_data(query_data)
        ```
        
        Step with access to pipeline resources:
        ```python
        class APIStep(Step[dict, dict, None]):
            async def execute(self, data: dict) -> dict:
                # Access pipeline resources via context
                api_client = self.pipeline_context.api_clients.some_api
                return await api_client.process(data)
        ```
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a pipeline step.
        
        Attributes:
            config: Configuration data - dict before validation, BaseModel instance after
            config_class: Pydantic BaseModel subclass (if provided)
            pipeline_context: Context object set by the pipeline during execution
            config_manager: Global configuration manager for accessing secrets/APIs
        """
        self.pipeline_context: PipelineContext | None = kwargs.get("pipeline_context", None)
        self.config_manager = GlobalConfigManager()
        self.secret_provider: SecretProvider | None = None
        self.api_factory: APIFactory | None = None

    def describe(self) -> str:
        """
        Return a human-readable description of what this step does.
        
        Used for logging and debugging. Should be concise but descriptive.
        
        Returns:
            Brief description of the step's purpose
            
        Example:
            return "Upload files to FTP server"
        """
        # example: return "Unsubclassed Step"
        raise NotImplementedError()

    async def execute(self, i: Input) -> Output:
        """
        Execute the main work of this pipeline step.
        
        This is where the step performs its core functionality, processing
        the input data and producing output for the next step.
        
        Args:
            i: Input data from the previous step or initial pipeline input
            
        Returns:
            Output data to be passed to the next step in the pipeline
            
        Note:
            - Can access self.config for configuration data
            - Can access self.pipeline_context for shared pipeline state
            - Should handle errors gracefully or let them bubble up
        """
        ...

    def set_context(self, context: PipelineContext):
        """
        Set the pipeline context for this step.
        
        Called automatically by the pipeline when the step is added.
        Provides access to shared pipeline state and resources.
        
        Args:
            context: Pipeline context containing shared state, logs, and resources
        """
        self.pipeline_context = context

    def set_secret_provider(self, sp: SecretProvider):
        """
        Set the secret provider. Kept separate from pipeline context because it is not a Pydantic model and should not
        be saved accidentally if we were to log context.

        :param sp: The SecretProvider instance to use for retrieving secrets.
        """
        self.secret_provider = sp
        self.api_factory = APIFactory(sp)


@runtime_checkable
class GeneratorStep(Step[Input, Iterable[Output]], Protocol[Input, Output]):
    """
    Represents a subtask in a job pipeline that is a generator, that is, it can yield values for another
    step to accumulate.

    A GeneratorStep is a Step[Input, Iterable[Output]] for some Input and Output type.

    A pipeline that sees a Generator step will call next on that step's generator property, then send the
    output to next step as its input. The next step must either be a GeneratorStep or an AccumulatorStep.
    """

    async def generator(self, i: Input) -> AsyncIterable[Output]:
        """The generator function for this step. Each step will be called with the Input object."""
        ...


class JobStep(BaseModel):
    step: Any
    id: str
    parent_id: str | None = None
    alt_input: str | None = None  # If set, the input of a non-parent ancestor step will be provided to the step instead.

    class Config:
        arbitrary_types_allowed = True


class PipelineTenantConfig(BaseModel):
    tenant_name: str
    config_id: str


@runtime_checkable
class JobPipeline(Protocol):
    """
    Protocol for job pipelines that orchestrate multiple steps in sequence.
    
    A JobPipeline manages the execution of interconnected steps, handling data flow,
    error management, logging, and reporting. Steps are organized as a tree structure
    where each step processes input and passes output to its children.
    
    Features:
        - Sequential and parallel step execution
        - Automatic error handling and retry logic
        - Process reporting to RITA API
        - Issue tracking and reporting
        - Comprehensive logging with multiple sinks
        - Pipeline context sharing between steps
    
    Step Organization:
        Steps are defined as a tree where each step has:
        - id: Unique identifier
        - parent_id: ID of parent step (None for root)
        - alt_input: Optional alternative input from ancestor step
        
    Examples:
        Basic pipeline:
        ```python
        class MyPipeline(JobPipeline):
            def __init__(self):
                steps = [
                    {"step": FetchDataStep(), "id": "fetch", "parent_id": None},
                    {"step": ProcessStep(), "id": "process", "parent_id": "fetch"},
                    {"step": UploadStep(), "id": "upload", "parent_id": "process"}
                ]
                super().__init__(steps, initial_input="start_data")
        ```
        
        Pipeline with reporting:
        ```python
        report_config = PipelineProcessReportConfig(
            config_id="my-config",
            trigger="manual",
            rita_tenant="my-tenant",
            rita_client_id="client-id",
            rita_client_secret="secret"
        )
        
        pipeline = MyPipeline(
            job_steps=steps,
            process_report_config=report_config,
            catch_step_errors=True
        )
        await pipeline.execute()
        ```
    """

    def __init__(
            self,
            job_steps: list[dict],
            rita_client: GravitateRitaAPI,
            pipeline_name: str,
            pipeline_config_id: str,
            secret_provider: SecretProvider,
            initial_input: Any = None,
            catch_step_errors: bool = False,
            upload_process_report_on_stoppipeline: bool = True,
            send_reports: bool = True
    ):
        """
        Initialize a job pipeline with steps and configuration.
        
        Args:
            job_steps: List of step dictionaries, each containing:
                      - step: Step instance implementing Step protocol
                      - id: Unique string identifier for the step
                      - parent_id: ID of parent step (None for root step)
                      - alt_input: Optional ancestor step ID to use as input
            initial_input: Data to pass to the root step (default: None)
            catch_step_errors: If True, step errors don't stop the entire pipeline,
                              just the current branch (default: False)
            upload_process_report_on_stoppipeline: Whether to upload reports when
                                                  pipeline is stopped early (default: True)

        Raises:
            RuntimeError: If job_steps is empty
            ValueError: If step tree structure is invalid (cycles, multiple roots, etc.)
            
        Attributes:
            job_steps: List of JobStep objects created from input dictionaries
            pending_steps: Queue of steps ready for execution
            saved_outputs: Cache of step outputs for alt_input functionality
            context: Shared pipeline context accessible by all steps
            config_manager: Global configuration manager for accessing secrets/APIs
        """
        if len(job_steps) == 0:
            raise RuntimeError("Pipelines must have at least 1 step.")

        self.job_steps = [JobStep(**js) for js in job_steps]
        # Scan the list of job_steps and look for a step that has no parent. If multiple steps have no parent, throw
        # an error. Also throw an error if no step has a null parent.
        check_tree_res = self.check_tree(self.job_steps)
        if check_tree_res is not None:
            raise ValueError(check_tree_res)
        start = [s for s in self.job_steps if s.parent_id is None]
        self.pending_steps: list[Tuple[JobStep, Any]] = [(start[0], initial_input)]
        self.saved_outputs: dict[str, Any] = {}
        self.saved_logs: list[Any] = []
        self.catch_step_errors = catch_step_errors
        self.context = PipelineContext()
        self.rita_client = rita_client
        self.secret_provider = secret_provider
        self.pipeline_name = pipeline_name
        self.pipeline_config_id = pipeline_config_id
        self.upload_process_report_on_stoppipeline = upload_process_report_on_stoppipeline
        self.config_manager = GlobalConfigManager()
        self.send_reports = send_reports

        # Configure logging - resets existing loguru handlers
        logger.remove()
        # Route anything less than ERROR to stdout,
        logger.add(sink=sys.stdout, filter=lambda record: record["level"].no < 40)
        # anything ERROR and above to stderr
        logger.add(sink=sys.stderr, level="ERROR")
        # Also collect all logs to use in process reporting
        self.collect_handler_id = logger.add(self._collect_log)

        for js in self.job_steps:
            # Give each step a reference to the pipeline context
            js.step.set_context(self.context)
            # And outside of that context, a reference to the secret provider
            js.step.set_secret_provider(self.secret_provider)

    def _collect_log(self, log: Any):
        self.saved_logs.append(log)
        self.context.logs.append(log)

    def check_tree(self, job_steps: list[JobStep]) -> Optional[str]:
        # Starting from the first, I should reach each step in the list once and only once
        first_step = [x for x in job_steps if x.parent_id is None]
        if len(first_step) != 1:
            return "The tree of job steps did not have a unique step with parent_id=None"
        to_visit = first_step
        visited = set()
        while len(to_visit) != 0:
            step = to_visit.pop(0)
            if step.id in visited:
                return f"The tree has a cycle. Step {step.id} was visited twice."
            visited.add(step.id)
            children = [x for x in job_steps if x.parent_id == step.id]
            to_visit.extend(children)
        return None

    @logger.catch
    async def execute(self):
        """
        Execute the pipeline by processing all steps in the correct order.
        
        Processes steps from the pending_steps queue until empty. Handles both
        regular Steps and GeneratorSteps. Manages error recovery, logging,
        and report generation.
        
        Execution Flow:
            1. Pop next step from pending queue
            2. Execute step (regular or generator)
            3. Add child steps to pending queue
            4. Repeat until queue empty or error
            5. Generate final process report
        
        Error Handling:
            - StopBranch: Stops current execution branch, continues with other branches
            - StopPipeline: Stops entire pipeline execution
            - Other exceptions: Stops pipeline unless catch_step_errors=True
        
        Raises:
            Exception: Any unhandled step execution errors (unless catch_step_errors=True)
            
        Note:
            Always calls finish_pipeline() for cleanup and reporting, regardless
            of success or failure.
        """
        try:
            start_dt = datetime.now(UTC)
            if self.send_reports:
                await self.record_pipeline_start(start_dt)

            while len(self.pending_steps) > 0:
                jobstep, input = self.pending_steps.pop(0)
                step = jobstep.step
                if isinstance(step, GeneratorStep):
                    new_pending_steps = await self.handle_generator_step(jobstep, input)
                elif isinstance(step, Step):
                    new_pending_steps = await self.handle_step(jobstep, input)
                else:
                    raise RuntimeError(f"Step {step.id} doesn't implement either of Step or GeneratorStep.")
                self.pending_steps = new_pending_steps + self.pending_steps
            await self.finish_pipeline()
        except StopPipeline as e:
            await self.finish_pipeline(e)
        except Exception as e:
            await self.finish_pipeline(e)

    async def finish_pipeline(self, exc: Exception | None = None):
        """
        Finalize pipeline execution with cleanup, reporting, and issue tracking.
        
        Called automatically at the end of pipeline execution, regardless of success
        or failure. Handles process reporting to RITA, issue reporting, and final
        logging.
        
        Args:
            exc: Exception that caused pipeline termination (None for successful completion)
        
        Process Report Behavior:
            - Success: Status = 'stop', includes all logs and files
            - StopPipeline: Status = 'stop', may skip report if upload_process_report_on_stoppipeline=False
            - Error: Status = 'error', includes exception details and stack trace
        
        Issue Reporting:
            If issue_reporting_config is provided and issues were collected during
            execution, uploads all issues to RITA for tracking.
        
        Generated Reports Include:
            - Complete execution logs
            - Files added to context.included_files
            - Pipeline metadata (config_id, trigger, etc.)
            - Issue summaries (if any)
        """
        halted_early = False
        halted_with_error = False
        if exc is not None and not isinstance(exc, StopPipeline):
            logger.info("Pipeline exited with an error")
            logger.exception(exc)
            halted_with_error = True
        elif exc is not None and isinstance(exc, StopPipeline):
            logger.success("The pipeline was halted early")
            halted_early = True
        else:
            logger.success("Pipeline completed")

        # No matter how it ended, generate a process report if requested.
        if halted_early and self.upload_process_report_on_stoppipeline == False:
            logger.info("Did not upload process report because pipeline was halted early.")
        else:
            if self.send_reports:
                logger.info("Creating process report on RITA...")
                await self.rita_client.create_process_report(CreateReportV2(
                    trigger=self.pipeline_name,
                    status=ProcessReportV2Status.error if halted_with_error else ProcessReportV2Status.stop,
                    config_id=self.pipeline_config_id,
                    # Logs are one list item per line, newlines already included. Join into one string.
                    log=UploadProcessReportFile(file_base_name=f"log", content="".join(self.context.logs)),
                    included_files=[
                        UploadProcessReportFile(file_base_name=name, content=content)
                        for name, content in self.context.included_files.items()
                    ]
                ))
                logger.info("Uploaded process report")
            else:
                logger.info("Not sending process report (send_reports=False)")

        # If there were any issues reported, upload those to RITA.
        if self.send_reports:
            if len(self.context.issues) > 0:
                logger.info("Recording issues on RITA...")
                # Prepend the pipeline name to issue keys
                for issue in self.context.issues:
                    issue.key = f"{self.pipeline_name}__{issue.key}"
                await self.rita_client.record_many_issues(self.context.issues)
                logger.info("Recorded issues")
            else:
                logger.info("No issues to record")
        else:
            logger.info("Not recording issues (send_reports=False)")

    async def handle_step(self, jobstep: JobStep, input: Input):
        id = jobstep.id
        description = jobstep.step.describe()
        logger.info(f"Running step {id}: {description}")
        if jobstep.alt_input:
            self.check_if_ancestor(jobstep.id, jobstep.alt_input)
            alt_input = self.saved_outputs[jobstep.alt_input]
            self.context.previous_output = input
            output_coroutine = jobstep.step.execute(alt_input)
        else:
            self.context.previous_output = None
            output_coroutine = jobstep.step.execute(input)
        try:
            output = await output_coroutine
            self.maybe_save_output(jobstep, output)
            new_pending = [(s, output) for s in self.job_steps if s.parent_id == jobstep.id]
            return new_pending
        except StopBranch:
            logger.info(f"Branch execution stopped at step {id} due to StopBranch exception")
            return []
        except StopPipeline as e:
            raise e

        except NoPipelineData as npd:
            raise npd

        except NoPipelineSourceData as npsd:
            raise npsd

        except Exception as e:
            if self.catch_step_errors:
                # If we get an error in the step, we don't want to cancel the whole pipeline, just this "branch" of
                # execution. (On a pipeline without generator steps, there isn't any difference, but on a pipeline with
                # generator steps this will just move to the next invocation of the generator step.) Due to the
                # architecture of the pipeline we can "cancel" the current branch by simply returning no next jobsteps
                # to execute.
                logger.exception(e)
                logger.warning("Exception encountered; canceling further execution on this branch.")
                return []
            else:
                raise e

    async def handle_generator_step(self, jobstep: JobStep, input: Input | AsyncGenerator):
        id = jobstep.id
        description = jobstep.step.describe()
        logger.info(f"Generating next output for step {id}: {description}")

        if isinstance(input, AsyncGenerator):
            # This is a paused generator. The input parameter is the currently paused generator
            generator = input
        else:
            # This is not a paused generator. The input is a real input, and we need to construct the generator.
            assert isinstance(jobstep.step, GeneratorStep)
            if jobstep.alt_input:
                self.check_if_ancestor(jobstep.id, jobstep.alt_input)
                alt_input = self.saved_outputs[jobstep.alt_input]
                self.context.previous_output = input
                generator = jobstep.step.generator(alt_input)
            else:
                self.context.previous_output = None
                generator = jobstep.step.generator(input)

        # Run the generator once and get the output, or catch a StopIteration
        try:
            next_output = await anext(generator)
            self.maybe_save_output(jobstep, next_output)
            new_pending_steps = [(s, next_output) for s in self.job_steps if s.parent_id == jobstep.id]

            # Put the currently executing step at the back of the new_pending_steps list. It will execute once all of
            # the child steps of this job are done. We store the generator instead of the input so we can pick up where
            # execution left off.
            new_pending_steps += [(jobstep, generator)]
            return new_pending_steps
        except StopAsyncIteration:
            logger.info(f"Generator for step {id} completed.")
            return []

    def maybe_save_output(self, jobstep: JobStep, data: Any):
        id = jobstep.id
        alt_input_consumers = [s for s in self.job_steps if s.alt_input == id]
        if len(alt_input_consumers) > 0:
            self.saved_outputs[id] = data

    def check_if_ancestor(self, id: str, ancestor_id: str):
        if ancestor_id not in {s.id for s in self.job_steps}:
            raise RuntimeError(f"{ancestor_id} is not a step in this pipeline.")
        jobstep = [s for s in self.job_steps if s.id == id][0]
        parent = [s for s in self.job_steps if s.id == jobstep.parent_id][0]
        while parent is not None:
            if parent.id == ancestor_id:
                return
            else:
                parent = [s for s in self.job_steps if s.id == parent.parent_id][0]
        raise RuntimeError("A step tried to use input from a non-ancestor step. This is unsupported.")

    async def record_pipeline_start(self, dt: datetime):
        max_sync = MaxSync(
            max_sync_date=dt,
            context={
                "pipeline_name": self.__class__.__name__,
            }
        )
        try:
            latest = await self.rita_client.get_config_max_sync(config_id=self.pipeline_config_id)
            latest_sync_json = latest.json()
            self.context.max_sync = MaxSync.model_validate(latest_sync_json) if latest_sync_json is not None else None
            await self.rita_client.update_config_max_sync(
                config_id=self.pipeline_config_id,
                max_sync=max_sync,
            )
            logger.info(f"Pipeline {self.__class__.__name__} started at {dt}")
        except Exception as e:
            logger.exception(e)
            logger.warning(f"Failed to record pipeline start for {self.__class__.__name__}")


class FileParser(Protocol):
    """Protocol for file parsing implementations with RITA integration."""

    def get_records(self, rd: T) -> List[Dict]:
        """Parse file data into records based on configuration."""
        ...

    def get_translated_records(self, rd: T) -> Tuple[List[Dict], List[Dict]]:
        """Parse and translate file records, returning (records, errors)."""
        ...


@runtime_checkable
class ParserBase(Protocol):
    def __init__(self, source_system: str = None, **kwargs):
        self.source_system = source_system

    async def load_mapper(self) -> RitaMapper:
        """Load Rita Mapper"""
        ...

    async def parse(self, data: T, mapping_type: MappingMode | None = None) -> T:
        """Parse Data"""
        ...

    def get_issues(self) -> list[dict]:
        """Retrieve issues stored over the course of the parser run."""
        ...

    def record_issue(self, **kwargs):
        """Record an issue for later retrieval."""
        ...


class Parser(Generic[T]):
    """
    Mixin class providing RITA mapper functionality for parser implementations.
    This class provides common RITA integration functionality that can be inherited
    by various parser classes. It handles mapper loading, credential management,
    and issue recording.

    Attributes:
        source_system: Identifier for the source system
        mapping_provider: Optional mapping provider (can be used in testing).
    """

    def __init__(self,
                 source_system: str | None = None,
                 mapping_provider: Optional[AsyncMappingProvider] = None
                 ):
        """
        Initialize RITA parser mixin.
        
        Args:
            source_system: Source system identifier for RITA mapping
            mapping_provider: Provides mappings from RITA. Required if source_system is specified.
        """
        self.source_system = source_system
        self.mapping_provider = mapping_provider
        self._issue_parts = []
        self.logs = {}

    async def load_mapper(self) -> Optional[RitaMapper]:
        """
        Load and initialize RITA mapper for the configured source system.
        
        Uses the tenant's RITA credentials to create a mapper instance and
        loads the mapping configuration asynchronously.
        
        Returns:
            Initialized RitaMapper instance with loaded mappings
            
        Raises:
            MapperLoadError: If mapper initialization or loading fails
        """
        if not self.source_system:
            logger.warning("No source system configured for RITA mapper, skipping.")
            return None
        try:
            mapper = RitaMapper(
                provider=self.mapping_provider,
                source_system=self.source_system
            )
            await mapper.load_mappings_async()
            return mapper
        except Exception as e:
            msg = f"Failed to load mapper for source system '{self.source_system}': {e}"
            logger.error(msg)
            raise MapperLoadError(msg) from e

    async def parse(self, data: T, mapping_type: MappingMode | None = None) -> T:
        """Custom Parer implementation. Must be overridden by subclasses."""
        ...

    def get_issues(self) -> list[dict]:
        """Retrieve issues stored over the course of the parser run."""
        return self._issue_parts

    def get_logs(self) -> str:
        return json.dumps(self.logs, cls=CustomJSONEncoder)

    def record_issue(self, name: str,
                     category: IssueCategory,
                     problem_short: str,
                     problem_long: str,
                     key_suffix: Optional[str] = None):
        """Record an issue encountered during parser for later retrieval by the caller."""
        self._issue_parts.append({
            "key_suffix": key_suffix,
            "name": name,
            "category": category,
            "problem_short": problem_short,
            "problem_long": problem_long,
        })
