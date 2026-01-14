#  Quapp Platform Project
#  async_invocation_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
import asyncio
import sys

from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from ..async_tasks.async_task import AsyncTask
from ..component.backend.job_manager import JobManager
from ..config.logging_config import logger
from ..factory.handler_factory import HandlerFactory
from ..model.invocation import Event, Error, Success


class AsyncInvocationTask(AsyncTask):
    """
    Handles asynchronous invocation tasks, designed to process events with
    specific handlers and generate immediate responses.

    The class is aimed at enabling tasks to be processed asynchronously, involving
    a handler factory and functions for event processing and post-processing. It
    executes operations in a background thread pool to ensure quick response to
    clients, allowing them to poll for job status updates. Its primary purpose is
    to facilitate efficient asynchronous processing of jobs without blocking the
    main application flow.

    Attributes:
        handler_factory: Factory instance that produces job handlers.
        event: Event to be processed by the created handler.
        processing_fn: Function to be executed during the job processing stage.
        post_processing_fn: Function to be executed post-job processing.
    """

    def __init__(self, handler_factory: HandlerFactory, event: Event,
                 processing_fn, post_processing_fn):
        super().__init__()
        self.handler_factory = handler_factory
        self.event = event
        self.processing_fn = processing_fn
        self.post_processing_fn = post_processing_fn

    def do(self) -> JSONResponse:
        """
        Handles executing a job asynchronously and provides an immediate response with the job's ID and
        status. Logging is configured dynamically based on the provided job ID.

        Returns:
            JSONResponse: A response object with the status and job ID if the job submission succeeds,
            or an error message if there is an issue.

        Raises:
            Exception: If any error occurs during job processing, it is logged, and an appropriate error
            response is returned.
        """
        try:
            job_id = self.event.json().get('jobId')
            if job_id is None:
                raise Exception("Job ID is missing from event")
            logger.add(sink=sys.stderr,
                       format="[ConsoleJobLog][" + job_id + "] " + "{level} : {time} : {message}: {process}",
                       level='DEBUG')

            # Define the blocking work
            def _run_handle():
                return self.handler_factory.create_handler(self.event,
                                                           self.processing_fn,
                                                           self.post_processing_fn).handle()

            # Run in the background threadpool so this request can return immediately
            asyncio.create_task(run_in_threadpool(_run_handle))

            # Respond immediately so clients can poll GET /jobs/{job_id}
            return JSONResponse(status_code=200, content=Success(
                    JobManager.get_job(job_id)).serialize())
        except Exception as exception:
            logger.exception(f"An error occurred: {exception}")
            return JSONResponse(status_code=400,
                                content=Error(exception).serialize())
