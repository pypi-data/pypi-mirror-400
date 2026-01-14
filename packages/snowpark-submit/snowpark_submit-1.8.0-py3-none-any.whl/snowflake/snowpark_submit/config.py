#!/usr/bin/env python

#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""Configuration classes for Snowpark Submit Python API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("snowpark-submit")


@dataclass
class WorkloadConfig:
    """Configuration for a Spark workload.

    This dataclass holds all configuration for a Spark workload. Use it with
    SnowparkSubmit to submit workloads to Snowflake.

    Example:
        >>> from snowflake.snowpark import Session
        >>> from snowflake.snowpark_submit import SnowparkSubmit, WorkloadConfig
        >>>
        >>> # Create session using standard Snowpark methods
        >>> session = Session.builder.configs({...}).create()
        >>>
        >>> # Create client and configure workload
        >>> client = SnowparkSubmit(session)
        >>> workload = WorkloadConfig(
        ...     file="my_job.py",
        ...     compute_pool="my_pool",
        ...     py_files="utils.py",
        ...     comment="My ETL job"
        ... )
        >>> result = client.submit(workload, wait_for_completion=True)
        >>> print(f"Exit code: {result.exit_code}")

    Args:
        file: Path to the file to execute (.py or .jar)
        compute_pool: Snowflake compute pool for running the workload (required)
        workload_name: Base name for the workload (optional, auto-generated if not provided)
        main_class: Main class name for Java/Scala apps (required for .jar files)
        application_args: List of arguments to pass to the application
        name: Application name for display
        comment: Comment/description for the workload
        py_files: Comma-separated list of Python dependencies (.py, .zip, .egg)
        files: Comma-separated list of files to distribute to working directory
        jars: Comma-separated list of JAR dependencies
        requirements_file: Path to requirements.txt for PyPI packages
        wheel_files: Comma-separated list of .whl files
        init_script: Path to shell script (.sh) to run before workload
        external_access_integrations: Comma-separated list of external access integrations
        properties_file: Path to Spark properties file
        conf: Dictionary of Spark configuration properties
        snowflake_stage: Snowflake stage for uploading files (must start with @)
        snowflake_log_level: Log level for Snowflake event table (INFO, ERROR, NONE)
        snowpark_connect_version: Version for Snowpark Connect images
        enable_local_file_access: Enable server access to local files
        workload_memory: Memory allocated to workload (e.g., '4G')
        workload_cpus: Number of CPUs allocated to workload
        workload_gpus: Number of GPUs allocated to workload
        show_error_trace: Show error traceback in server logs
        disable_otel_telemetry: Disable OpenTelemetry traces
    """

    file: str
    compute_pool: str
    workload_name: str | None = None
    main_class: str | None = None
    application_args: list[str] | None = None
    name: str | None = None
    comment: str | None = None
    py_files: str | None = None
    files: str | None = None
    jars: str | None = None
    requirements_file: str | None = None
    wheel_files: str | None = None
    init_script: str | None = None
    external_access_integrations: str | None = None
    properties_file: str | None = None
    conf: dict[str, str] | None = None
    snowflake_stage: str | None = None
    snowflake_log_level: str | None = None
    snowpark_connect_version: str | None = None
    enable_local_file_access: bool = False
    workload_memory: str | None = None
    workload_cpus: float | None = None
    workload_gpus: int | None = None
    show_error_trace: bool = False
    disable_otel_telemetry: bool = False

    def __post_init__(self):
        """Validate required fields after initialization."""
        if not self.file:
            raise ValueError("file is required and cannot be empty")
        if not self.compute_pool:
            raise ValueError("compute_pool is required and cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
