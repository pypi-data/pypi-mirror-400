#  Quapp Platform Project
#  job_manager.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from __future__ import annotations

import atexit
import threading
import time
from datetime import timezone, datetime
from multiprocessing import Manager, current_process
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from ...config.logging_config import logger

SCHEDULER_CALLBACK_URL = 'scheduler_callback_url'

JOB_ID = 'job_id'
STATUS = 'status'
UPDATED_AT = 'updated_at'
META = 'meta'


class JobManager:
    """
    Cross-process job registry backed by multiprocessing.Manager.

    - Stores job_id -> {"status": <str>, META: <dict>, "updated_at": <float>}
    - Provides atomic add/update/get operations across processes.
    - Publishes every change to a cross-process Queue so other processes/threads can react.
    - Offers:
        * subscribe(callback): run a background listener thread that invokes `callback(job_id, data)`
        * watch_updates(timeout=None): generator to pull updates from the queue manually
    """

    # Process-wide singletons (one per process)
    _manager: Optional[Manager] = None
    _jobs: Any = None  # proxy dict
    _updates_queue: Any = None  # proxy queue
    _init_lock = threading.Lock()
    _listener_threads: Dict[str, Tuple[threading.Thread, threading.Event]] = {}

    # --------------- Lifecycle ---------------

    @classmethod
    def _ensure_initialized(cls) -> None:
        """
        Lazily initialize the Manager, shared dict, and update queue.
        Safe to call multiple times across threads in the same process.
        """
        if cls._manager is not None:
            return
        with cls._init_lock:
            if cls._manager is not None:
                return
            mgr = Manager()
            cls._manager = mgr
            cls._jobs = mgr.dict()  # type: ignore[assignment]
            cls._updates_queue = mgr.Queue()  # type: ignore[assignment]

            # Ensure a clean shutdown in this process
            atexit.register(cls._shutdown)

    @classmethod
    def _shutdown(cls) -> None:
        """
        Stop any listener threads in this process and shutdown Manager.
        """
        # stop listeners
        for key, (t, stop_ev) in list(cls._listener_threads.items()):
            stop_ev.set()
            # Don't join forever; avoid atexit hang
            t.join(timeout=1.0)
            cls._listener_threads.pop(key, None)

        # close manager (safe to call multiple times)
        if cls._manager is not None:
            try:
                cls._manager.shutdown()
            except Exception as exception:
                # Manager may already be down if the parent exited
                logger.exception(f'Error shutting down manager: {exception}')
                pass
        cls._manager = None
        cls._jobs = None
        cls._updates_queue = None

    # --------------- Core operations ---------------

    @classmethod
    def add_job(cls, job_id: str, status: str = 'PENDING',
                meta: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new job. If a job exists, it will be overwritten.
        Publishes an 'added' event.
        """
        cls._ensure_initialized()
        data = {STATUS    : status, META: meta or {},
                UPDATED_AT: cls._get_current_utc_time()}
        cls._jobs[job_id] = data  # proxy is process-safe
        cls._publish(job_id, {"event": "added", **data})

    @classmethod
    def update_status(cls, job_id: str, status: str,
                      meta_update: Optional[Dict[str, Any]] = None) -> None:
        """
        Update status (and optionally merge meta) for an existing job.
        Publishes an 'updated' event.
        """
        cls._ensure_initialized()
        if job_id not in cls._jobs:
            # Create on the first update to be resilient
            return cls.add_job(job_id, status=status, meta=meta_update or {})

        current = dict(cls._jobs[job_id])  # materialize proxy value
        if meta_update:
            merged_meta = dict(current.get(META) or {})
            merged_meta.update(meta_update)
        else:
            merged_meta = current.get(META) or {}

        if current.get(STATUS) == 'DONE' or current.get(STATUS) == 'FAILED':
            logger.warning(f'Job {job_id} already completed, ignoring update')
            return None
        new_data = {STATUS    : status, META: merged_meta or {},
                    UPDATED_AT: cls._get_current_utc_time()}
        cls._jobs[job_id] = new_data
        cls._publish(job_id, {"event": "updated", **new_data})
        return None

    @classmethod
    def remove_job(cls, job_id: str) -> None:
        """
        Remove a job if it exists. Publishes a 'removed' event.
        """
        cls._ensure_initialized()
        existed = job_id in cls._jobs
        if existed:
            # Capture previous data for potential consumers
            prev = dict(cls._jobs[job_id])
            del cls._jobs[job_id]
            cls._publish(job_id, {"event": "removed", **prev})

    @classmethod
    def get_status(cls, job_id: str) -> Optional[str]:
        """
        Get the current status string for a job, or None if not present.
        """
        cls._ensure_initialized()
        data = cls._jobs.get(job_id)
        return None if data is None else data.get(STATUS)

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full job data: {"status", META, "updated_at"} or None.
        """
        cls._ensure_initialized()
        data = cls._jobs.get(job_id)
        return None if data is None else dict(data)

    @classmethod
    def list_jobs(cls) -> Dict[str, Dict[str, Any]]:
        """
        Snapshot of all jobs.
        """
        cls._ensure_initialized()
        # Materialize to plain dict (avoid holding proxies)
        return {k: dict(v) for k, v in dict(cls._jobs).items()}

    @classmethod
    def get_scheduler_callback_url(cls, job_id):
        """
        Get the scheduler callback URL of a job.
        """
        cls._ensure_initialized()
        data = cls._jobs.get(job_id)
        return None if data is None else data.get(META).get(
                SCHEDULER_CALLBACK_URL)

    # --------------- Change publication ---------------

    @classmethod
    def _publish(cls, job_id: str, payload: Dict[str, Any]) -> None:
        """
        Push an update notification to the shared queue.
        """
        cls._ensure_initialized()
        try:
            cls._updates_queue.put((job_id, payload))
            logger.debug(f'Published job update: {payload}')
        except Exception as exception:
            # If queue is not available (e.g., after shutdown), ignore
            logger.exception(f'Error publishing job update: {exception}')
            pass

    @classmethod
    def watch_updates(cls, timeout: Optional[float] = None) -> Iterable[
        Tuple[str, Dict[str, Any]]]:
        """
        Generator that yields (job_id, payload) for each change.
        Blocks waiting for new items if the queue is empty.
        - timeout=None: block indefinitely per item
        - timeout=float: block up to timeout seconds, yielding nothing if no item
        """
        cls._ensure_initialized()
        q = cls._updates_queue
        while True:
            try:
                item = q.get(
                        timeout=timeout) if timeout is not None else q.get()
            except Exception as exception:
                logger.exception(
                        f'Queue empty in job update listener: {exception}')
                # Timeout or queue failure
                if timeout is not None:
                    logger.info(f'Watch timeout reached: {timeout}s')
                    return

                logger.info('Watch terminated')
                continue
            yield item

    @classmethod
    def subscribe(cls, callback: Callable[[str, Dict[str, Any]], None],
                  name: Optional[str] = None, daemon: bool = True, ) -> str:
        """
        Start a background listener thread in the current process that consumes updates
        and invokes `callback(job_id, payload)`.

        Returns a subscription key that can be used to unsubscribe.
        """
        cls._ensure_initialized()
        proc = current_process().name
        sub_key = name or f'job_updates_listener@{proc}#{len(cls._listener_threads) + 1}'
        if sub_key in cls._listener_threads:
            # Stop existing and replace
            cls.unsubscribe(sub_key)

        stop_event = threading.Event()

        def _run() -> None:
            while not stop_event.is_set():
                try:
                    job_id, payload = cls._updates_queue.get(timeout=0.2)
                except Exception as exception:
                    logger.exception(
                            f'Queue empty in job update listener {sub_key}: {exception}')
                    continue
                try:
                    callback(job_id, payload)
                except Exception as exception:
                    # Keep the listener alive even if callback fails
                    logger.exception(f'Error in job update callback '
                                     f'{callback}: {exception}')
                    pass

        t = threading.Thread(target=_run, name=sub_key, daemon=daemon)
        t.start()
        cls._listener_threads[sub_key] = (t, stop_event)
        return sub_key

    @classmethod
    def unsubscribe(cls, key: str) -> None:
        """
        Stop a previously started subscription listener thread.
        """
        pair = cls._listener_threads.get(key)
        if not pair:
            return
        t, stop_event = pair
        stop_event.set()
        t.join(timeout=1.0)
        cls._listener_threads.pop(key, None)

    # --------------- Convenience helpers ---------------

    @classmethod
    def set_queued(cls, job_id: str,
                   meta_update: Optional[Dict[str, Any]] = None) -> None:
        cls.update_status(job_id, 'QUEUED', meta_update)

    @classmethod
    def set_running(cls, job_id: str,
                    meta_update: Optional[Dict[str, Any]] = None) -> None:
        cls.update_status(job_id, 'RUNNING', meta_update)

    @classmethod
    def set_done(cls, job_id: str,
                 meta_update: Optional[Dict[str, Any]] = None) -> None:
        cls.update_status(job_id, 'DONE', meta_update)

    @classmethod
    def set_failed(cls, job_id: str,
                   meta_update: Optional[Dict[str, Any]] = None) -> None:
        cls.update_status(job_id, 'FAILED', meta_update)

    @classmethod
    def _get_current_utc_time(cls) -> str:
        now = time.time()
        return datetime.fromtimestamp(now, tz=timezone.utc).isoformat().replace(
                '+00:00', 'Z')
