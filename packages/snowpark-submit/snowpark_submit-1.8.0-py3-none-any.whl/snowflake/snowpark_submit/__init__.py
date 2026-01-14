#!/usr/bin/env python

#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""Snowpark Submit - Submit Spark workloads to Snowflake.

This package provides both a CLI tool and a Python API for submitting
Spark (PySpark, Scala, Java) workloads to Snowflake's Snowpark Container Services.

CLI Usage:
    snowpark-submit [options] <app.py | app.jar> [app arguments]

Python API Usage:
    >>> from snowflake.snowpark import Session
    >>> from snowflake.snowpark_submit import SnowparkSubmit, WorkloadConfig
    >>>
    >>> # Create a Snowpark session
    >>> session = Session.builder.configs({...}).create()
    >>>
    >>> # Create client and configure workload
    >>> client = SnowparkSubmit(session)
    >>> workload = WorkloadConfig(
    ...     file="my_script.py",
    ...     compute_pool="my_pool",
    ...     comment="My job"
    ... )
    >>> result = client.submit(workload, wait_for_completion=True)
    >>> print(f"Exit code: {result.exit_code}")

Workload Management:
    >>> # Check status
    >>> status = client.status("MY_JOB_241211_120000", "my_pool")
    >>>
    >>> # Kill workload
    >>> client.kill("MY_JOB_241211_120000", "my_pool")
    >>>
    >>> # List workloads
    >>> client.list_workloads("my_pool", prefix="MY_JOB")
"""

# Import main API classes
from snowflake.snowpark_submit.api import SnowparkSubmit
from snowflake.snowpark_submit.cluster_mode.job_runner import StatusInfo
from snowflake.snowpark_submit.config import WorkloadConfig

__all__ = [
    "SnowparkSubmit",
    "WorkloadConfig",
    "StatusInfo",
]
