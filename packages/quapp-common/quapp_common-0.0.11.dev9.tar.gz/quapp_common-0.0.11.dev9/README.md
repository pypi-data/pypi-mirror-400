# quapp-common

Quapp common library supporting Quapp Platform for Quantum Computing.

## Overview

`quapp-common` is a Python library designed to support the Quapp Platform for
Quantum Computing by providing common utilities, configurations, and
abstractions for working with
quantum providers and devices.
Recent improvements add first-class asynchronous job processing with a
cross-process JobManager,
background task execution, and standardized result models for immediate client
responses while work
continues in the background.

## Features

- Provider and device factory for quantum computing platforms.
- Logging and configuration utilities with improved and detailed log messages.
- Support for AWS Braket, OQC Cloud, Qiskit, PennyLane, DWave Ocean, and Quapp
  quantum simulators.
- Refactored classes and utilities to remove tenant-specific request, response,
  and promise classes.
- Standardized naming by renaming `ProjectHeader` to `CustomHeader`.
- Enhanced error handling and job metadata update mechanisms.
- Simplified and cleaner HTTP request/response logging and URL parsing
  utilities.
- Asynchronous job processing:
    - AsyncInvocationTask to run handlers in a background thread pool and return
      immediate responses.
    - JobManager for cross-process job registry with atomic add/update/get and
      pub-sub updates.
    - Standard Event/Result (Success, Error) models for consistent async
      responses.
    - Scheduler integration via callback URL; local updates are patched to the
      scheduler.
    - Safety: updates to jobs already DONE/FAILED are ignored to prevent
      post-completion mutations.

## Installation

Install via pip:

```bash
pip install quapp-common
```

Notes:

- From version 0.0.11.dev7, `starlette` is a direct dependency to support
  background execution helpers.

## Recently Changes Highlights

- Version bump to 0.0.11.dev7 and dependency update (add `starlette`).
- Introduce asynchronous job processing primitives:
    - AsyncInvocationTask for background execution with immediate client
      response.
    - Event and standardized Result models (Success, Error).
- Introduce JobManager for cross-process job management and update publication.
- Integrate JobManager into Request to register jobs and carry scheduler
  callback URL.
- Modularize update_job_metadata with clearer helpers; patch scheduler on local
  state changes.
- Fix: ignore updates for jobs that are already DONE or FAILED.
- Improve logging and error handling (use full tracebacks, cleaner logs).

---

For detailed usage and API references, please refer to the in-code documentation
or contact the maintainers.
