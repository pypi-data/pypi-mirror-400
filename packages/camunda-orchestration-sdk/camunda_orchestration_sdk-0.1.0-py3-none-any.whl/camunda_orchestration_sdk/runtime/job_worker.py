from __future__ import annotations
import asyncio
import inspect
import threading
import functools
import attrs
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Literal, Protocol, Any, runtime_checkable, TYPE_CHECKING, Awaitable, cast, Coroutine, Union, Tuple
from dataclasses import dataclass
from loguru import logger
from camunda_orchestration_sdk.models.activate_jobs_data import ActivateJobsData
from camunda_orchestration_sdk.models.activate_jobs_response_200_jobs_item import ActivateJobsResponse200JobsItem
from camunda_orchestration_sdk.models.complete_job_data import CompleteJobData
from camunda_orchestration_sdk.models.complete_job_data_variables_type_0 import CompleteJobDataVariablesType0
from camunda_orchestration_sdk.models.fail_job_data import FailJobData
from camunda_orchestration_sdk.models.throw_job_error_data import ThrowJobErrorData
from camunda_orchestration_sdk.types import UNSET

if TYPE_CHECKING:
    from camunda_orchestration_sdk import CamundaClient

_EFFECTIVE_EXECUTION_STRATEGY = Literal["thread", "process", "async"]
EXECUTION_STRATEGY = _EFFECTIVE_EXECUTION_STRATEGY | Literal["auto"]

# Define action types for type narrowing
ActionComplete = Tuple[Literal["complete"], Union[dict[str, Any], CompleteJobData, None]]
ActionFail = Tuple[Literal["fail"], Tuple[str, int | None, int]]
ActionError = Tuple[Literal["error"], Tuple[str, str]]
ActionSubprocessError = Tuple[Literal["subprocess_error"], str]

JobAction = Union[ActionComplete, ActionFail, ActionError, ActionSubprocessError]

@runtime_checkable
class HintedCallable(Protocol):
    _execution_hint: _EFFECTIVE_EXECUTION_STRATEGY
    def __call__(self, job: Any) -> dict[str, Any] | None | Awaitable[dict[str, Any] | None]: ...

AsyncJobHandler = Callable[["JobContext"], Coroutine[Any, Any, dict[str, Any] | None]]
SyncJobHandler = Callable[["JobContext"], dict[str, Any] | None]
JobHandler = AsyncJobHandler | SyncJobHandler | HintedCallable

@dataclass
class WorkerConfig:
    """User-facing configuration"""
    job_type: str
    """How long the job is reserved for this worker only"""
    job_timeout_milliseconds: int
    max_concurrent_jobs: int = 10  # Max jobs executing at once
    execution_strategy: EXECUTION_STRATEGY = "auto"
    fetch_variables: list[str] | None = None
    worker_name: str = "camunda-python-sdk-worker"

class ExecutionHint:
    """Decorators for users to hint at their workload execution potential"""
    
    @staticmethod
    def prefer(strategy: _EFFECTIVE_EXECUTION_STRATEGY) -> Callable[[Callable[..., Any]], HintedCallable]:
        def decorator(func: Callable[..., Any]) -> HintedCallable:
            func._execution_preference = strategy # type: ignore
            # Implicitly permit the preferred strategy
            if not hasattr(func, "_execution_permits"):
                func._execution_permits = set() # type: ignore
            func._execution_permits.add(strategy) # type: ignore
            return func # type: ignore
        return decorator

    @staticmethod
    def permit(strategy: _EFFECTIVE_EXECUTION_STRATEGY) -> Callable[[Callable[..., Any]], HintedCallable]:
        def decorator(func: Callable[..., Any]) -> HintedCallable:
            if not hasattr(func, "_execution_permits"):
                func._execution_permits = set() # type: ignore
            func._execution_permits.add(strategy) # type: ignore
            return func # type: ignore
        return decorator

@attrs.define
class JobContext(ActivateJobsResponse200JobsItem):
    """Read-only context for a job execution."""

    @classmethod
    def from_job(cls, job: ActivateJobsResponse200JobsItem) -> "JobContext":
        # Extract init fields
        init_fields = {
            f.name: getattr(job, f.name)
            for f in attrs.fields(ActivateJobsResponse200JobsItem)
            if f.init
        }
        return cls(**init_fields)

class JobError(Exception):
    """Raise this exception to throw a BPMN error."""
    def __init__(self, error_code: str, message: str = ""):
        self.error_code = error_code
        self.message = message
        super().__init__(f"JobError[{error_code}]: {message}")

class JobFailure(Exception):
    """Raise this exception to explicitly fail a job with custom retries/backoff."""
    def __init__(self, message: str, retries: int | None = None, retry_back_off: int = 0):
        self.message = message
        self.retries = retries
        self.retry_back_off = retry_back_off
        super().__init__(f"JobFailure: {message}")

def _execute_task_isolated(callback: JobHandler, job_context: JobContext) -> JobAction | None:
    """
    Universal wrapper to execute a job in an isolated context (Thread or Process).
    Handles both sync and async callbacks by creating a fresh event loop for async code.
    Returns the result action to be executed by the main loop.
    """
    try:
        # Unwrap partials to find the real function for inspection
        actual_func = callback
        while isinstance(actual_func, functools.partial):
            actual_func = actual_func.func

        result = None
        if inspect.iscoroutinefunction(actual_func):
            # Async callback in isolated context: needs a fresh loop
            async_callback = cast(AsyncJobHandler, callback)
            result = asyncio.run(async_callback(job_context))
        else:
            # Sync callback: run directly
            sync_callback = cast(SyncJobHandler, callback)
            result = sync_callback(job_context)
        
        # If we got here, the job completed successfully
        return ("complete", result)
        
    except JobError as e:
        return ("error", (e.error_code, e.message))
    except JobFailure as e:
        return ("fail", (e.message, e.retries, e.retry_back_off))
    except Exception as e:
        # Catch-all for other exceptions -> Fail job
        return ("fail", (str(e), None, 0))


class JobWorker:
    _strategy: _EFFECTIVE_EXECUTION_STRATEGY = "async"
    def __init__(self, client: "CamundaClient", callback: JobHandler, config: WorkerConfig):
        self.callback = callback
        self.config = config
        self.client = client
        
        # Bind logger with context
        self.logger = logger.bind(
            sdk="camunda_orchestration_sdk",
            worker=config.worker_name,
            job_type=config.job_type
        )

        # Execution strategy detection
        self._strategy = self._determine_strategy()
        self._validate_strategy()
        
        # Resource pools
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_concurrent_jobs)
        self.process_pool = ProcessPoolExecutor(max_workers=config.max_concurrent_jobs)
        
        # Semaphore to limit concurrent executions
        self.semaphore = asyncio.Semaphore(config.max_concurrent_jobs)
        
        self.running = False
        self.polling_task = None
        
        self.active_jobs = 0
        self.lock = threading.Lock()

        # Dedicated event loop for async user code
        self.worker_loop = asyncio.new_event_loop()
        self.worker_thread = threading.Thread(target=self._run_worker_loop, daemon=True)
        self.worker_thread.start()
        
        self.logger.info(f"Using execution strategy: {self._strategy}")
    
    def _run_worker_loop(self):
        """Runs the dedicated event loop for async user code"""
        asyncio.set_event_loop(self.worker_loop)
        self.worker_loop.run_forever()
    
    def _determine_strategy(self) -> _EFFECTIVE_EXECUTION_STRATEGY:
        """Smart detection of execution strategy"""
        # User explicitly configured?
        if self.config.execution_strategy != "auto":
            return self.config.execution_strategy
        
        # Unwrap partials to check the actual function
        actual_func = self.callback
        while isinstance(actual_func, functools.partial):
            actual_func = actual_func.func

        # Check for preference
        if hasattr(actual_func, "_execution_preference"):
            return getattr(actual_func, "_execution_preference")
        
        # Auto-detect default preference based on function signature
        if inspect.iscoroutinefunction(actual_func):
            return "async"
        
        # Default to thread for sync functions (safe for most I/O work)
        return "thread"
    
    def _validate_strategy(self):
        """Ensure the strategy matches the callback type"""
        # Validation relaxed to allow dynamic exploration.
        pass

    def _decrement_active_jobs(self):
        with self.lock:
            self.active_jobs -= 1
            self.logger.trace(f"Active jobs: {self.active_jobs}")

    def start(self):
        if not self.running:
            self.running = True
            self.polling_task = asyncio.create_task(self.poll_loop())
            self.logger.info("Worker started")

    def stop(self):
        if self.running:
            self.running = False
            if self.polling_task:
                self.polling_task.cancel()
            
            # Stop the worker loop
            if self.worker_loop.is_running():
                self.worker_loop.call_soon_threadsafe(self.worker_loop.stop)
            if self.worker_thread.is_alive():
                self.worker_thread.join(timeout=1.0)

            self.logger.info("Worker stopped")

    async def poll_loop(self):
        """Background polling loop - always async"""
        while self.running:
            try:
                # Non-blocking HTTP poll using httpx
                jobs = await self._poll_for_jobs()
                
                # Spawn tasks for each job
                if jobs:
                    tasks = [self._execute_job(job) for job in jobs]
                    # Don't await - let them run in background
                    for task in tasks:
                        asyncio.create_task(task)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error polling: {e}")
            
            await asyncio.sleep(1)  # Polling interval
    
    async def _poll_for_jobs(self):
        """SDK's async HTTP polling logic"""
        with self.lock:
            current_active = self.active_jobs
        
        capacity = self.config.max_concurrent_jobs - current_active
        if capacity <= 0:
            self.logger.trace("Max concurrent jobs reached, skipping poll")
            empty_jobs: list[ActivateJobsResponse200JobsItem] = []
            return empty_jobs

        self.logger.debug(f'Polling for jobs (capacity: {capacity})...')
        jobsResult = await self.client.activate_jobs_async(data=
            ActivateJobsData(
                type_=self.config.job_type, 
                timeout=self.config.job_timeout_milliseconds, 
                max_jobs_to_activate=capacity,
                request_timeout=0, # This allows the server to autonegotiate the poll timeout
                fetch_variable = self.config.fetch_variables if self.config.fetch_variables is not None else UNSET,
                worker=self.config.worker_name
            )
        )
        self.logger.trace(f'Received {len(jobsResult.jobs)}')
        self.logger.trace(f'Jobs received: {[job.job_key for job in jobsResult.jobs]}')
        if jobsResult.jobs:
            with self.lock:
                self.active_jobs += len(jobsResult.jobs)
        return jobsResult.jobs  # Return list of jobs
    
    async def _execute_job(self, job_item: ActivateJobsResponse200JobsItem):
        """Execute a single job with appropriate strategy"""
        
        # Create context (picklable data container)
        job_context = JobContext.from_job(job_item)
        
        # Unwrap partials to check the actual function
        actual_func = self.callback
        while isinstance(actual_func, functools.partial):
            actual_func = actual_func.func
        is_async_callback = inspect.iscoroutinefunction(actual_func)

        try:
            async with self.semaphore:  # Limit concurrent executions
                action: JobAction | None = None
                
                if self._strategy == "async":
                    # Run on dedicated worker loop
                    try:
                        result = None
                        if is_async_callback:
                            async_callback = cast(AsyncJobHandler, self.callback)
                            # Schedule on worker loop and wait for result in main loop
                            future = asyncio.run_coroutine_threadsafe(
                                async_callback(job_context), 
                                self.worker_loop
                            )
                            result = await asyncio.wrap_future(future)
                        else:
                            # Warning: Sync callback on Async strategy blocks the loop!
                            result = self.callback(job_context)
                        action = cast(ActionComplete, ("complete", result))
                    except JobError as e:
                        action = ("error", (e.error_code, e.message))
                    except JobFailure as e:
                        action = ("fail", (e.message, e.retries, e.retry_back_off))
                    except Exception as e:
                        action = ("fail", (str(e), None, 0))
                
                elif self._strategy in ["thread", "process"]:
                    # Run in Pool (Isolated)
                    pool = self.thread_pool if self._strategy == "thread" else self.process_pool
                    
                    action = await asyncio.get_event_loop().run_in_executor(
                        pool, 
                        _execute_task_isolated, 
                        self.callback, 
                        job_context
                    )
                
                # Handle the returned action
                if action:
                    if action[0] == "complete":
                        _, action_data = action
                        # Ensure data is in correct format
                        complete_data = CompleteJobData()
                        if isinstance(action_data, dict):
                            complete_data = CompleteJobData(variables=CompleteJobDataVariablesType0.from_dict(action_data))
                        elif isinstance(action_data, CompleteJobData):
                            complete_data = action_data
                            
                        await self.client.complete_job_async(job_key=job_context.job_key, data=complete_data)
                        self.logger.debug(f"Job completed: {job_context.job_key}")
                        
                    elif action[0] == "fail":
                        _, (error_message, retries, retry_back_off) = action
                        # Calculate retries if not provided
                        if retries is None:
                            retries = job_context.retries - 1 if job_context.retries > 0 else 0
                            
                        await self.client.fail_job_async(
                            job_key=job_context.job_key, 
                            data=FailJobData(
                                error_message=error_message,
                                retries=retries,
                                retry_back_off=retry_back_off
                            )
                        )
                        self.logger.info(f"Job failed: {job_context.job_key} - {error_message}")
                        
                    elif action[0] == "error":
                        _, (error_code, error_message) = action
                        await self.client.throw_job_error_async(
                            job_key=job_context.job_key, 
                            data=ThrowJobErrorData(
                                error_code=error_code,
                                error_message=error_message
                            )
                        )
                        self.logger.info(f"Job error thrown: {job_context.job_key} - {error_code}")
                    
                    elif action[0] == "subprocess_error":
                        _, error_details = action
                        # This is a system error in the worker infrastructure, not the job logic
                        raise RuntimeError(f"Worker execution error: {error_details}")
                
        except Exception as e:
            self.logger.error(f"System error executing job {job_item.job_key}: {e}")
            # Try to fail the job if possible
            try:
                await self.client.fail_job_async(
                    job_key=job_item.job_key,
                    data=FailJobData(
                        error_message=f"System error: {str(e)}",
                        retries=job_item.retries - 1 if job_item.retries else 0,
                    )
                )
            except Exception:
                pass # Best effort
        finally:
            self._decrement_active_jobs()


