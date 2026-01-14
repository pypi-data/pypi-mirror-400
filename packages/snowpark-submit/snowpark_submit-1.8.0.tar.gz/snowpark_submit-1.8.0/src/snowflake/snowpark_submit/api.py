#!/usr/bin/env python

#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""Python API for Snowpark Submit."""

from __future__ import annotations

import argparse
import logging
from functools import partial
from typing import TYPE_CHECKING, Any

from snowflake.snowpark_submit.cluster_mode.job_runner import StatusInfo
from snowflake.snowpark_submit.cluster_mode.spark_connect.spark_connect_job_runner import (
    SparkConnectJobRunner,
)
from snowflake.snowpark_submit.snowpark_submit import (
    generate_spark_submit_cmd,
    get_parser_defaults,
    get_snowflake_config_keys,
)

from snowflake import snowpark

if TYPE_CHECKING:
    from snowflake.snowpark_submit.config import WorkloadConfig

logger = logging.getLogger("snowpark-submit")


def _setup_logging(log_level: int = logging.INFO) -> None:
    """Setup logging for snowpark-submit."""
    logger.setLevel(log_level)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def _set_defaults(args: argparse.Namespace) -> None:
    """Set default values for CLI arguments not provided.

    Uses the defaults extracted from the parser to ensure consistency
    between CLI and Python API usage.
    """
    for key, value in get_parser_defaults().items():
        if not hasattr(args, key):
            setattr(args, key, value)


def _build_args_from_workload(
    workload_config: WorkloadConfig,
    wait_for_completion: bool = False,
    display_logs: bool = False,
    fail_on_error: bool = False,
    number_of_most_recent_log_lines: int = 100,
    operation: str = "submit",
    workload_name: str | None = None,
    list_prefix: str | None = None,
) -> argparse.Namespace:
    """Build argparse.Namespace from WorkloadConfig.

    Args:
        workload_config: Workload configuration
        wait_for_completion: Wait for completion
        display_logs: Display logs
        fail_on_error: Fail on error
        number_of_most_recent_log_lines: Number of log lines
        operation: Type of operation (submit, status, kill, list)
        workload_name: Workload name for status/kill operations
        list_prefix: Prefix for list operation

    Returns:
        argparse.Namespace with all configurations
    """
    args = argparse.Namespace()

    # Add workload config
    workload_dict = workload_config.to_dict()

    # Handle filename
    args.filename = workload_dict.pop("file", None)

    # Handle compute_pool
    args.compute_pool = workload_dict.pop("compute_pool", None)

    # Handle workload_name
    if "workload_name" in workload_dict:
        args.snowflake_workload_name = workload_dict.pop("workload_name")
    else:
        args.snowflake_workload_name = workload_name

    # Handle conf (convert dict to list of "key=value" strings)
    if "conf" in workload_dict:
        conf_dict = workload_dict.pop("conf")
        args.conf = [f"{k}={v}" for k, v in conf_dict.items()]
    else:
        args.conf = None

    # Handle application_args
    if "application_args" in workload_dict:
        args.app_arguments = workload_dict.pop("application_args") or []
    else:
        args.app_arguments = []

    # Rename some fields to match CLI argument names
    if "main_class" in workload_dict:
        workload_dict["class"] = workload_dict.pop("main_class")
    if "show_error_trace" in workload_dict:
        args.snowflake_show_error_trace = workload_dict.pop("show_error_trace")
    if "disable_otel_telemetry" in workload_dict:
        args.snowflake_disable_otel_telemetry = workload_dict.pop(
            "disable_otel_telemetry"
        )

    # Add remaining workload config
    for key, value in workload_dict.items():
        arg_name = key.replace("-", "_")
        setattr(args, arg_name, value)

    # Add submit options
    args.wait_for_completion = wait_for_completion
    args.display_logs = display_logs
    args.fail_on_error = fail_on_error
    args.number_of_most_recent_log_lines = number_of_most_recent_log_lines

    # Set operation flags
    args.workload_status = operation == "status"
    args.kill_workload = operation == "kill"
    args.list_workloads_with_name = list_prefix

    # Set defaults for other CLI arguments
    _set_defaults(args)

    return args


def _build_args_minimal(
    compute_pool: str,
    workload_name: str | None = None,
    wait_for_completion: bool = False,
    display_logs: bool = False,
    number_of_most_recent_log_lines: int = 100,
    operation: str = "status",
    list_prefix: str | None = None,
) -> argparse.Namespace:
    """Build minimal argparse.Namespace for status/kill/list operations."""
    args = argparse.Namespace()

    args.compute_pool = compute_pool
    args.snowflake_workload_name = workload_name
    args.filename = None
    args.app_arguments = []
    args.conf = None

    # Add submit options
    args.wait_for_completion = wait_for_completion
    args.display_logs = display_logs
    args.fail_on_error = False
    args.number_of_most_recent_log_lines = number_of_most_recent_log_lines

    # Set operation flags
    args.workload_status = operation == "status"
    args.kill_workload = operation == "kill"
    args.list_workloads_with_name = list_prefix

    # Set defaults
    _set_defaults(args)

    return args


def _submit_workload(
    session: snowpark.Session,
    workload_config: WorkloadConfig,
    wait_for_completion: bool = False,
    display_logs: bool = False,
    fail_on_error: bool = False,
    number_of_most_recent_log_lines: int = 100,
) -> StatusInfo:
    """Submit a Spark workload to Snowflake.

    This is the internal implementation called by WorkloadConfig.submit().

    Args:
        session: Snowpark Session to use for submission
        workload_config: Workload configuration
        wait_for_completion: Wait for the workload to complete before returning
        display_logs: Fetch and display application logs
        fail_on_error: Raise exception if workload fails
        number_of_most_recent_log_lines: Number of recent log lines to retrieve

    Returns:
        StatusInfo object with workload status and details
    """
    _setup_logging()

    # Build args
    args = _build_args_from_workload(
        workload_config=workload_config,
        wait_for_completion=wait_for_completion,
        display_logs=display_logs,
        fail_on_error=fail_on_error,
        number_of_most_recent_log_lines=number_of_most_recent_log_lines,
        operation="submit",
    )

    # Create job runner with existing session
    snowflake_config_keys = get_snowflake_config_keys()
    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
        session=session,
    )

    # Submit the job
    result = job_runner.run()

    if fail_on_error and result.exit_code != 0:
        error_msg = result.error or "Workload failed"
        raise RuntimeError(
            f"Workload failed with exit code {result.exit_code}: {error_msg}"
        )

    return result


def _get_workload_status(
    session: snowpark.Session,
    workload_name: str,
    compute_pool: str,
    wait_for_completion: bool = False,
    display_logs: bool = False,
    number_of_most_recent_log_lines: int = 100,
) -> StatusInfo:
    """Get the status of a workload.

    Args:
        session: Snowpark Session to use
        workload_name: Name of the workload (with timestamp)
        compute_pool: Compute pool where the workload is running
        wait_for_completion: Wait for the workload to complete
        display_logs: Fetch and display application logs
        number_of_most_recent_log_lines: Number of recent log lines to retrieve

    Returns:
        StatusInfo object with workload status and details
    """
    _setup_logging()

    # Build args
    args = _build_args_minimal(
        compute_pool=compute_pool,
        workload_name=workload_name,
        wait_for_completion=wait_for_completion,
        display_logs=display_logs,
        number_of_most_recent_log_lines=number_of_most_recent_log_lines,
        operation="status",
    )

    # Create job runner with existing session
    snowflake_config_keys = get_snowflake_config_keys()
    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
        session=session,
    )

    # Get status
    result = job_runner.describe()

    # Wait for completion if requested
    if wait_for_completion and not result.terminated:
        result = job_runner.wait_for_service_completion(workload_name)

    return result


def _kill_workload(
    session: snowpark.Session,
    workload_name: str,
    compute_pool: str,
) -> StatusInfo:
    """Kill a running workload.

    Args:
        session: Snowpark Session to use
        workload_name: Name of the workload to kill
        compute_pool: Compute pool where the workload is running

    Returns:
        StatusInfo object with operation result
    """
    _setup_logging()

    # Build args
    args = _build_args_minimal(
        compute_pool=compute_pool,
        workload_name=workload_name,
        operation="kill",
    )

    # Create job runner with existing session
    snowflake_config_keys = get_snowflake_config_keys()
    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
        session=session,
    )

    # Kill the workload
    return job_runner.end_workload()


def _list_workloads(
    session: snowpark.Session,
    compute_pool: str,
    prefix: str = "",
) -> StatusInfo:
    """List workloads in the compute pool.

    Args:
        session: Snowpark Session to use
        compute_pool: Compute pool to list workloads from
        prefix: Filter workloads by name prefix

    Returns:
        StatusInfo object with list results
    """
    _setup_logging()

    # Build args
    args = _build_args_minimal(
        compute_pool=compute_pool,
        operation="list",
        list_prefix=prefix,
    )

    # Create job runner with existing session
    snowflake_config_keys = get_snowflake_config_keys()
    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
        session=session,
    )

    # List workloads
    return job_runner.list_workloads(prefix=prefix)


class SnowparkSubmit:
    """Client for submitting and managing Spark workloads on Snowflake.

    This class provides the main interface for submitting Spark workloads to Snowflake
    using an existing Snowpark Session.

    Example:
        >>> from snowflake.snowpark import Session
        >>> from snowflake.snowpark_submit import SnowparkSubmit, WorkloadConfig
        >>>
        >>> # Create a Snowpark session
        >>> session = Session.builder.configs({"connection_name": "default"}).create()
        >>>
        >>> # Create client
        >>> client = SnowparkSubmit(session)
        >>>
        >>> # Configure and submit workload
        >>> workload = WorkloadConfig(
        ...     file="my_job.py",
        ...     compute_pool="my_pool",
        ...     comment="My ETL job"
        ... )
        >>> result = client.submit(workload, wait_for_completion=True)
        >>> print(f"Exit code: {result.exit_code}")

    Args:
        session: Snowpark Session to use for all operations
        log_level: Logging level (default: logging.INFO)
    """

    def __init__(
        self,
        session: snowpark.Session,
        log_level: int = logging.INFO,
    ) -> None:
        """Initialize SnowparkSubmit client.

        Args:
            session: Snowpark Session to use for all operations
            log_level: Logging level (default: logging.INFO)
        """
        _setup_logging(log_level)
        self._session = session

    @property
    def session(self) -> snowpark.Session:
        """Get the Snowpark session."""
        return self._session

    def submit(
        self,
        workload_config: WorkloadConfig | dict[str, Any],
        wait_for_completion: bool = False,
        display_logs: bool = False,
        fail_on_error: bool = False,
        number_of_most_recent_log_lines: int = 100,
    ) -> StatusInfo:
        """Submit a Spark workload to Snowflake.

        Args:
            workload_config: WorkloadConfig object or dictionary with workload configuration
            wait_for_completion: Wait for the workload to complete before returning
            display_logs: Fetch and display application logs (only with wait_for_completion)
            fail_on_error: Raise exception if workload fails (only with wait_for_completion)
            number_of_most_recent_log_lines: Number of recent log lines to retrieve

        Returns:
            StatusInfo object with workload status and details

        Raises:
            RuntimeError: If fail_on_error=True and workload fails

        Example:
            >>> workload = WorkloadConfig(file="job.py", compute_pool="my_pool")
            >>> result = client.submit(workload, wait_for_completion=True)
            >>> print(f"Job: {result.workload_name}, Exit code: {result.exit_code}")
        """
        # Convert dict to WorkloadConfig if needed
        if isinstance(workload_config, dict):
            from snowflake.snowpark_submit.config import WorkloadConfig

            workload_config = WorkloadConfig(**workload_config)

        return _submit_workload(
            session=self._session,
            workload_config=workload_config,
            wait_for_completion=wait_for_completion,
            display_logs=display_logs,
            fail_on_error=fail_on_error,
            number_of_most_recent_log_lines=number_of_most_recent_log_lines,
        )

    def status(
        self,
        workload_name: str,
        compute_pool: str,
        wait_for_completion: bool = False,
        display_logs: bool = False,
        number_of_most_recent_log_lines: int = 100,
    ) -> StatusInfo:
        """Get the status of a workload.

        Args:
            workload_name: Name of the workload (with timestamp, e.g., "MY_JOB_241211_120000")
            compute_pool: Compute pool where the workload is running
            wait_for_completion: Wait for the workload to complete before returning
            display_logs: Fetch and display application logs
            number_of_most_recent_log_lines: Number of recent log lines to retrieve

        Returns:
            StatusInfo object with workload status and details

        Example:
            >>> status = client.status("MY_JOB_241211_120000", "my_pool")
            >>> print(f"Status: {status.workload_status}")
        """
        return _get_workload_status(
            session=self._session,
            workload_name=workload_name,
            compute_pool=compute_pool,
            wait_for_completion=wait_for_completion,
            display_logs=display_logs,
            number_of_most_recent_log_lines=number_of_most_recent_log_lines,
        )

    def kill(
        self,
        workload_name: str,
        compute_pool: str,
    ) -> StatusInfo:
        """Kill a running workload.

        Args:
            workload_name: Name of the workload to kill (with timestamp)
            compute_pool: Compute pool where the workload is running

        Returns:
            StatusInfo object with operation result

        Example:
            >>> result = client.kill("MY_JOB_241211_120000", "my_pool")
            >>> print(f"Kill result: {result.exit_code}")
        """
        return _kill_workload(
            session=self._session,
            workload_name=workload_name,
            compute_pool=compute_pool,
        )

    def list_workloads(
        self,
        compute_pool: str,
        prefix: str = "",
    ) -> StatusInfo:
        """List workloads in the compute pool.

        Args:
            compute_pool: Compute pool to list workloads from
            prefix: Filter workloads by name prefix (empty for all workloads)

        Returns:
            StatusInfo object (exit_code 0 on success, workload list is logged to console)

        Example:
            >>> result = client.list_workloads("my_pool", prefix="ETL")
            >>> # Workload list is printed to console via logger
        """
        return _list_workloads(
            session=self._session,
            compute_pool=compute_pool,
            prefix=prefix,
        )
