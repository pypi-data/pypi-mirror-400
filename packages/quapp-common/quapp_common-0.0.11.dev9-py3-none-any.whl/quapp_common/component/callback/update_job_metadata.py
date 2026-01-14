#  Quapp Platform Project
#  update_job_metadata.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import requests

from ..backend.job_manager import JobManager
from ...config.logging_config import job_logger
from ...data.response.job_response import JobResponse
from ...util.http_utils import create_application_json_header, \
    get_job_id_from_url
from ...util.response_utils import generate_response


def update_job_metadata(job_response: JobResponse, callback_url: str):
    # Helpers to improve readability and remove duplication
    def _log_http_result(tag: str, resp):
        logger.info(
                f"Request to {tag} completed with status code: {resp.status_code}")
        if not resp.ok:
            logger.warning(
                    f"Unexpected status code received from {tag}: {resp.status_code}, response content: {resp.content}")

    def _update_local_status() -> None:
        """
                Update local JobManager status based on callback URL semantics:
                - contains 'FAILED' => FAILED
                - contains 'FINALIZATION_PASSED' => DONE
                - otherwise => RUNNING
                """
        url_upper = (callback_url or "").upper()
        if "FAILED" in url_upper:
            JobManager.set_failed(job_id=job_id)
        elif "FINALIZATION_PASSED" in url_upper:
            JobManager.set_done(job_id=job_id)
        else:
            JobManager.set_running(job_id=job_id)

    def _patch_scheduler() -> None:
        job_details = JobManager.get_job(job_id)
        scheduler_callback_url = job_details.get('meta').get(
                'scheduler_callback_url')
        scheduler_payload = {'job_id'    : job_id,
                             'status'    : job_details.get('status'),
                             'updated_at': job_details.get('updated_at')}
        scheduler_response = requests.patch(url=scheduler_callback_url,
                                            json=scheduler_payload)
        _log_http_result('scheduler', scheduler_response)

    job_id = get_job_id_from_url(callback_url)
    logger = job_logger(job_id)
    logger.info(
            f'Calling backend to update job metadata at URL: {callback_url}')

    request_body = generate_response(job_response)

    try:
        # Update local job status and notify scheduler
        _update_local_status()
        _patch_scheduler()

        request_headers = create_application_json_header(
                token=job_response.user_token,
                project_header=job_response.project_header,
                workspace_header=job_response.workspace_header)

        response = requests.patch(url=callback_url, json={'data': request_body},
                                  headers=request_headers)

        # Log backend response
        _log_http_result('backend', response)

    except Exception as exception:
        logger.exception(f'Error occurred while calling backend: {exception}',
                         exc_info=True)

        raise exception
