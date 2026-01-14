#!/usr/bin/env python

#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""The utility file for running spark-submit cluster mode."""

import argparse
import logging
import os
import random
import string
import tempfile
import textwrap
import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml
from snowflake.snowpark_submit.constants import (
    DOCKER_WORKDIR,
    SHARED_VOLUME_MOUNT_PATH,
    SHARED_VOLUME_NAME,
)
from snowflake.snowpark_submit.file_path import BaseFilePath

from snowflake import snowpark
from snowflake.connector.backoff_policies import exponential_backoff
from snowflake.connector.config_manager import CONFIG_MANAGER
from snowflake.connector.errors import Error


@dataclass
class StatusInfo:
    """Result information from workload operations.

    This dataclass is returned by SnowparkSubmit methods (submit, status, kill,
    list_workloads) and contains information about the operation result and
    workload state.

    Attributes:
        exit_code: Operation exit code (0 = success, non-zero = failure).
        terminated: Whether the workload has terminated.
        workload_name: The full name of the workload (includes timestamp suffix).
        service_status: SPCS service status (PENDING, RUNNING, DONE, etc.).
        workload_status: Workload-level status.
        created_on: Timestamp when the workload was created.
        started_at: Timestamp when the workload started running.
        terminated_at: Timestamp when the workload terminated.
        job_exit_code: Exit code from the Spark job itself.
        logs: List of log lines from the workload.
        error: Error message if the operation failed.
    """

    exit_code: int
    terminated: bool | None = None
    workload_name: str | None = None
    service_status: str | None = None
    workload_status: str | None = None
    created_on: str | None = None
    started_at: str | None = None
    terminated_at: str | None = None
    job_exit_code: int | None = None
    logs: list[str] = field(default_factory=list)
    error: str | None = None


SPCS_SPEC_FILE = "spcs_spec.yaml"
COMMON_NEEDED_CONFIGS = [
    "compute_pool",
    "warehouse",
]

logger = logging.getLogger("snowpark-submit")


def generate_random_name(
    length: int = 8,
    prefix: str = "",
    suffix: str = "",
    choices: Sequence[str] = string.ascii_lowercase,
) -> str:
    """Our convenience function to generate random string for object names.
    Args:
        length: How many random characters to choose from choices.
            length would be at least 6 for avoiding collision
        prefix: Prefix to add to random string generated.
        suffix: Suffix to add to random string generated.
        choices: A generator of things to choose from.
    """
    random_part = "".join([random.choice(choices) for _ in range(length)]) + str(
        time.time_ns()
    )

    return "".join([prefix, random_part, suffix])


class JobRunner(ABC):
    @abstractmethod
    def _generate_client_container_args(
        self, client_src_zip_file_path: str
    ) -> list[str]:
        """
        Generates the args list for client container.

        Args:
            client_src_zip_file_path: zip file path inside container that contains customers'
            local dependencies.

        Returns:
            args list of client container.
        """
        pass

    @abstractmethod
    def _client_image_path_sys_registry(self) -> str:
        """
        Docker image full path inside SPCS system registry for client container.
        """
        pass

    @abstractmethod
    def _server_image_path_sys_registry(self) -> str:
        """
        Docker image full path inside SPCS system registry for server container.
        """
        pass

    @abstractmethod
    def _client_image_name_override(self) -> str:
        """
        Docker image override relative path inside SPCS account registry for client container.
        """
        pass

    @abstractmethod
    def _server_image_name_override(self) -> str:
        """
        Docker image override relative path inside SPCS account registry for server container.
        """
        pass

    @abstractmethod
    def _add_additional_jars_to_classpath(self) -> None:
        """
        Adds additional jar resources to Spark's classpath.
        """
        pass

    @abstractmethod
    def _use_system_registry(self) -> bool:
        """
        Whether to use system registry for client and server container images.
        """
        pass

    @abstractmethod
    def _override_args(self) -> None:
        """
        Override the default args if needed.
        """
        pass

    def _customize_spcs_spec(self, spec: dict) -> None:
        """
        Customize the server container if needed.
        """
        return None

    def _custom_files_to_upload(self) -> list[str] | None:
        """
        Additional files to upload to the temporary stage.
        """
        return None

    def __init__(
        self,
        args: argparse.Namespace,
        generate_spark_cmd_args: Callable[[argparse.Namespace], list[str]],
        client_working_dir: str,
        temp_stage_mount_dir: str,
        current_dir: str,
        session: snowpark.Session | None = None,
    ) -> None:
        self.args = args
        self._snowpark_session: snowpark.Session | None = session
        self._session_provided = session is not None

        # Overrides args if needed
        self._override_args()

        self.generate_spark_cmd_args = (
            generate_spark_cmd_args  # need to generate on the fly
        )
        assert client_working_dir.endswith(
            "/"
        ), "client_working_dir should end with '/'"
        self.client_working_dir = client_working_dir
        assert temp_stage_mount_dir.endswith(
            "/"
        ), "temp_stage_mount_dir should end with '/'"
        self.temp_stage_mount_dir = temp_stage_mount_dir
        self.current_dir = current_dir
        self.client_app_language = "scala"  # default to scala

        # If session is provided, extract configs from it
        if self._session_provided:
            self._init_from_session(session)
        else:
            self._init_from_args()

    def _init_from_session(self, session: snowpark.Session) -> None:
        """Initialize JobRunner using an existing Snowpark session."""
        # Get configs from session or args
        # Note: compute_pool must come from args as it's not a session property
        self.compute_pool = getattr(self.args, "compute_pool", None)
        if not self.compute_pool:
            raise Error(
                "compute_pool is required. Provide it via WorkloadConfig.compute_pool"
            )

        # Get warehouse from session if available
        warehouse = session.get_current_warehouse()
        self.warehouse = getattr(self.args, "warehouse", None) or (
            warehouse.strip('"') if warehouse else None
        )

        # Get database/schema from session for non-system registry
        if not self._use_system_registry():
            database = session.get_current_database()
            schema = session.get_current_schema()
            self.database = getattr(self.args, "database", None) or (
                database.strip('"') if database else None
            )
            self.schema = getattr(self.args, "schema", None) or (
                schema.strip('"') if schema else None
            )
            self.spcs_repo_name = getattr(self.args, "spcs_repo_name", None)
            if self.database and self.schema and self.spcs_repo_name:
                self.spcs_repo_path = (
                    f"/{self.database}/{self.schema}/{self.spcs_repo_name}"
                )

        self.custom_session_configs = {}  # Not needed when session is provided

    def _init_from_args(self) -> None:
        """Initialize JobRunner from CLI arguments."""
        needed_configs = list(COMMON_NEEDED_CONFIGS)
        if not self._use_system_registry():
            needed_configs.extend(["database", "schema", "spcs_repo_name"])

        configs = {}
        # only load from connections.toml if connection name is provided
        if self.args.snowflake_connection_name:
            try:
                if self.args.snowflake_connection_name in CONFIG_MANAGER["connections"]:
                    configs = CONFIG_MANAGER["connections"][
                        self.args.snowflake_connection_name
                    ]
                else:
                    logger.error(
                        f"Connection name '{self.args.snowflake_connection_name}' not found in connections.toml"
                    )
                    raise Error(
                        f"Connection name '{self.args.snowflake_connection_name}' not found in connections.toml"
                    )
            except Exception as e:
                logger.error(
                    "Failed to load connection configs from connections.toml. Error: %s",
                    e,
                )
                raise e

        for config in needed_configs:
            default = str(configs[config]) if config in configs else None
            setattr(self, config, getattr(self.args, config, None) or default)

        if not self._use_system_registry():
            self.spcs_repo_path = (
                f"/{self.database}/{self.schema}/{self.spcs_repo_name}"
            )

        custom_session_configs = {}
        if self.args.snowflake_connection_name:
            custom_session_configs[
                "connection_name"
            ] = self.args.snowflake_connection_name
        if self.args.account:
            custom_session_configs["account"] = self.args.account
        if self.args.user:
            custom_session_configs["user"] = self.args.user
        if self.args.authenticator:
            custom_session_configs["authenticator"] = self.args.authenticator
        if self.args.private_key_file:
            custom_session_configs["private_key_file"] = self.args.private_key_file
        if self.args.private_key_file_pwd:
            custom_session_configs[
                "private_key_file_pwd"
            ] = self.args.private_key_file_pwd
        if self.args.token:
            custom_session_configs["token"] = self.args.token
        if self.args.token_file_path:
            custom_session_configs["token_file_path"] = self.args.token_file_path
        if self.args.password:
            custom_session_configs["password"] = self.args.password
        if self.args.role:
            custom_session_configs["role"] = self.args.role
        if self.args.host:
            custom_session_configs["host"] = self.args.host
        if self.args.port:
            custom_session_configs["port"] = self.args.port
        if self.args.database:
            custom_session_configs["database"] = self.args.database
        if self.args.schema:
            custom_session_configs["schema"] = self.args.schema
        if self.args.warehouse:
            custom_session_configs["warehouse"] = self.args.warehouse
        custom_session_configs["protocol"] = "https"
        custom_session_configs["port"] = 443
        self.custom_session_configs = custom_session_configs

        if not self.args.snowflake_connection_name:
            missing_params = []
            if "account" not in custom_session_configs:
                missing_params.append("--account")
            if "host" not in custom_session_configs:
                missing_params.append("--host")
            if not self.args.workload_status and not self.args.compute_pool:
                missing_params.append("--compute-pool")

            if missing_params:
                raise Error(
                    f"Missing required connection parameters: {', '.join(missing_params)}. "
                    "Provide these parameters via command line, and/or use --snowflake-connection-name "
                    "to load from connections.toml (CLI args will override connections.toml values)."
                )

    def init_snowflake_session(self):
        """Initialize Snowflake session if not already provided."""
        if self._session_provided:
            # Session was provided in constructor, just set query tag
            self._snowpark_session.sql(
                "alter session set query_tag = 'snowpark-submit'"
            ).collect()
            self._log_session_info()
            return

        self._snowpark_session = snowpark.Session.builder.configs(
            self.custom_session_configs
        ).create()
        # set query tag for tracking
        self._snowpark_session.sql(
            "alter session set query_tag = 'snowpark-submit'"
        ).collect()
        self._log_session_info()  # log session info to help users debug connection issues

    def prepare_spcs_spec(
        self,
        temp_stage_name: str,
        client_src_zip_file_path: str,
        server_image_name: str = "snowpark-connect-server:latest",
        client_image_name: str = "snowpark-connect-client:latest",
        service_name: str = "snowpark_connect_job_service",
    ) -> str:
        # TODO: more options can be added
        #  secrets
        #  serviceRoles
        logger.debug("start preparing spcs_spec")
        spcs_spec_template_path = os.path.join(
            self.current_dir, "resources/spcs_spec.template.yaml"
        )
        with open(spcs_spec_template_path) as f:
            spcs_spec_dict = yaml.safe_load(f)

        spec = spcs_spec_dict["spec"]

        # snowpark connect server container
        server_container = spec["container"][0]

        logger.debug("USE_SYSTEM_IMAGE_REGISTRY: %s", self._use_system_registry())
        if self._use_system_registry():
            server_container["image"] = self._server_image_path_sys_registry()
        else:
            server_container["image"] = self.spcs_repo_path + f"/{server_image_name}"

        if getattr(self, "warehouse", None):
            server_container["env"]["SNOWFLAKE_WAREHOUSE"] = self.warehouse

        if getattr(self.args, "snowflake_grpc_max_message_size", None):
            server_container["env"][
                "SNOWFLAKE_GRPC_MAX_MESSAGE_SIZE"
            ] = self.args.snowflake_grpc_max_message_size

        if getattr(self.args, "snowflake_grpc_max_metadata_size", None):
            server_container["env"][
                "SNOWFLAKE_GRPC_MAX_METADATA_SIZE"
            ] = self.args.snowflake_grpc_max_metadata_size

        # Set environment variable for traceback display control
        show_error_traceback = getattr(self.args, "snowflake_show_error_trace", False)
        logger.debug("SHOW_ERROR_TRACEBACK: %s", show_error_traceback)
        if show_error_traceback:
            server_container["env"]["SNOWFLAKE_SHOW_ERROR_TRACE"] = "true"

        # Set environment variable for OpenTelemetry control
        disable_otel_telemetry = getattr(
            self.args, "snowflake_disable_otel_telemetry", False
        )
        logger.debug("DISABLE_OTEL_TELEMETRY: %s", disable_otel_telemetry)
        if disable_otel_telemetry:
            server_container["env"]["SNOWPARK_TELEMETRY_ENABLED"] = "false"
        # Note: If flag is not provided, we don't set the env var, letting the server use its default (enabled)

        # snowpark connect client container
        client_container = spec["container"][1]
        if self._use_system_registry():
            client_container["image"] = self._client_image_path_sys_registry()
        else:
            client_container["image"] = self.spcs_repo_path + f"/{client_image_name}"
        client_container["env"]["SERVICE_NAME"] = service_name
        if getattr(self.args, "requirements_file", None):
            client_container["env"]["REQUIREMENTS_FILE"] = self.args.requirements_file
        if getattr(self.args, "wheel_files", None):
            client_container["env"]["WHEEL_FILES"] = self.args.wheel_files
        if getattr(self.args, "init_script", None):
            client_container["env"]["INIT_SCRIPT"] = self.args.init_script
        client_container["args"] = self._generate_client_container_args(
            client_src_zip_file_path
        )

        if self.args.workload_memory:
            client_container["resources"]["requests"][
                "memory"
            ] = self.args.workload_memory
        if self.args.workload_cpus:
            client_container["resources"]["requests"]["cpu"] = self.args.workload_cpus
        if self.args.workload_gpus:
            client_container["resources"]["requests"][
                "nvidia.com/gpu"
            ] = self.args.workload_gpus
            client_container["resources"]["limits"] = {
                "nvidia.com/gpu": self.args.workload_gpus
            }

        spec["volumes"][0]["source"] = f"@{temp_stage_name}"
        if self.args.snowflake_stage:
            spec["volumes"].append(
                {"name": "snowflake-stage", "source": self.args.snowflake_stage}
            )
            server_container["volumeMounts"].append(
                {
                    "name": "snowflake-stage",
                    "mountPath": DOCKER_WORKDIR
                    + "/"
                    + self.args.snowflake_stage[1:],  # remove '@' prefix
                }
            )
            client_container["volumeMounts"].append(
                {
                    "name": "snowflake-stage",
                    "mountPath": DOCKER_WORKDIR
                    + "/"
                    + self.args.snowflake_stage[1:],  # remove '@' prefix
                }
            )
        if self.args.enable_local_file_access:
            spec["volumes"].append({"name": SHARED_VOLUME_NAME, "source": "local"})
            server_container["volumeMounts"].append(
                {
                    "name": SHARED_VOLUME_NAME,
                    "mountPath": SHARED_VOLUME_MOUNT_PATH,
                }
            )
            client_container["volumeMounts"].append(
                {
                    "name": SHARED_VOLUME_NAME,
                    "mountPath": SHARED_VOLUME_MOUNT_PATH,
                }
            )

        if self.args.snowflake_log_level:
            spec["logExporters"]["eventTableConfig"][
                "logLevel"
            ] = self.args.snowflake_log_level

        self._customize_spcs_spec(spec)

        spcs_spec_yaml = yaml.dump(spcs_spec_dict, default_flow_style=False)
        logger.debug(spcs_spec_yaml)

        return spcs_spec_yaml

    def upload_client_files(self, temp_stage_name):
        file_path = Path(self.args.filename)
        files_for_zip = [(file_path, file_path.name)]

        if self.client_app_language == "python":
            if self.args.py_files:
                py_file_paths = [
                    Path(py_file) for py_file in self.args.py_files.split(",")
                ]
                files_for_zip.extend(
                    [(py_path, py_path.name) for py_path in py_file_paths]
                )

        # Add files specified via --files (works for both Python and Scala)
        if hasattr(self.args, "files") and self.args.files:
            file_paths = [
                Path(file_path.strip()) for file_path in self.args.files.split(",")
            ]
            files_for_zip.extend(
                [(file_path, file_path.name) for file_path in file_paths]
            )

        if self.args.jars:
            jar_paths = [Path(jar.strip()) for jar in self.args.jars.split(",")]
            files_for_zip.extend([(jar_path, jar_path.name) for jar_path in jar_paths])

        if hasattr(self.args, "requirements_file") and self.args.requirements_file:
            requirements_path = Path(self.args.requirements_file)
            files_for_zip.append((requirements_path, requirements_path.name))

        if hasattr(self.args, "wheel_files") and self.args.wheel_files:
            wheel_paths = [
                Path(wheel.strip()) for wheel in self.args.wheel_files.split(",")
            ]
            for wheel_path in wheel_paths:
                if wheel_path.suffix == ".whl":
                    files_for_zip.append((wheel_path, wheel_path.name))
                else:
                    logger.warning(
                        "File does not have .whl extension: %s. Ignored", wheel_path
                    )

        if hasattr(self.args, "init_script") and self.args.init_script:
            init_script_path = Path(self.args.init_script)
            if init_script_path.suffix == ".sh":
                files_for_zip.append((init_script_path, init_script_path.name))
            else:
                logger.warning(
                    "File does not have .sh extension: %s. Ignored", init_script_path
                )

        import zipfile

        empty_zipfile = True
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            zip_file_name = (
                generate_random_name(prefix="snowpark_submit_files_") + ".zip"
            )
            zip_file_path = tmp_path / zip_file_name
            with zipfile.ZipFile(zip_file_path, "w") as zipf:
                for file_path, arcname in files_for_zip:
                    if not file_path.exists():
                        # If the file is a stage file (e.g., starts with '@'), skip it.
                        if str(file_path).startswith("@"):
                            logger.debug(
                                f"Skipping stage file {file_path} (not local)."
                            )
                            continue
                        # Otherwise, raise an error for missing local files.
                        raise FileNotFoundError(
                            f"Local file {file_path} does not exist."
                        )
                    logger.debug(f"zipping file {file_path.name} as {arcname}")
                    zipf.write(file_path, arcname=arcname)
                    empty_zipfile = False

            if empty_zipfile:
                logger.debug("No local files to upload. Skip uploading zip file.")
                return None

            logger.debug(
                f"Created archive {zip_file_path} for uploading the client src file and other dependencies."
            )

            # Upload the archive
            upload_zip_sql = f"PUT file://{zip_file_path.resolve()} @{temp_stage_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
            self.get_snowpark_session().sql(upload_zip_sql).collect()
            logger.debug(
                f"Uploaded the archive {zip_file_path} to the temporary stage {temp_stage_name}."
            )

        return self.temp_stage_mount_dir + zip_file_name

    def _adjust_file_path_arg(
        self, arg_value: str, separator: str | None = None
    ) -> str:
        if not arg_value:
            return ""

        file_paths = [
            BaseFilePath.parse_file_path(
                client_path=path,
                local_file_base_path=self.client_working_dir,
                stage_file_base_path=(
                    DOCKER_WORKDIR + "/" + self.args.snowflake_stage[1:] + "/"
                    if self.args.snowflake_stage
                    else ""
                ),
            ).get_file_path_in_container()
            for path in arg_value.split(separator)
        ]
        return separator.join(file_paths) if separator else file_paths[0]

    def adjust_file_paths(self):
        if self.client_app_language == "scala":
            if self.args.driver_class_path:
                self.args.driver_class_path = self._adjust_file_path_arg(
                    self.args.driver_class_path, separator=":"
                )
        elif self.client_app_language == "python":
            if self.args.py_files:
                self.args.py_files = self._adjust_file_path_arg(
                    self.args.py_files, separator=","
                )

            # Add sitecustomize.py for automatic Spark Connect debug patching
            # Only disabled if OpenTelemetry is disabled (since stack traces are used for telemetry)
            disable_otel = getattr(self.args, "snowflake_disable_otel_telemetry", False)

            if not disable_otel:
                if self.args.py_files:
                    self.args.py_files += ",/app/sitecustomize.py"
                else:
                    self.args.py_files = "/app/sitecustomize.py"
            # Note: requirements_file, wheel_files, and init_script don't work with stage at the moment
            if hasattr(self.args, "requirements_file") and self.args.requirements_file:
                self.args.requirements_file = self._adjust_file_path_arg(
                    self.args.requirements_file
                )

            if hasattr(self.args, "wheel_files") and self.args.wheel_files:
                self.args.wheel_files = self._adjust_file_path_arg(
                    self.args.wheel_files, separator=","
                )

            if hasattr(self.args, "init_script") and self.args.init_script:
                self.args.init_script = self._adjust_file_path_arg(
                    self.args.init_script
                )

        # Adjust --files paths (works for both Python and Scala)
        if hasattr(self.args, "files") and self.args.files:
            self.args.files = self._adjust_file_path_arg(self.args.files, separator=",")

        if self.args.jars:
            self.args.jars = self._adjust_file_path_arg(self.args.jars, separator=",")

        # TODO: what if program args have file paths?
        self.args.filename = self._adjust_file_path_arg(self.args.filename)

    def _add_class_paths(self, jar_paths: list[str]):
        if self.args.driver_class_path is None:
            self.args.driver_class_path = ":".join(jar_paths)
        else:
            self.args.driver_class_path = ":".join(
                [jar_paths] + [self.args.driver_class_path]
            )
        logger.debug("driver_class_path: %s", self.args.driver_class_path)

    def wait_for_service_completion(self, service_name: str) -> StatusInfo:
        backoff_gen = exponential_backoff()()
        while True:
            result = self.describe(service_name=service_name)
            if result.terminated or result.terminated is None:
                return result
            sleep = next(backoff_gen)
            logger.debug("sleep for %d seconds", sleep)
            time.sleep(sleep)

    def generate_execute_service_sql(
        self, service_name: str, spcs_spec_yaml: str
    ) -> str:
        return f"""
EXECUTE JOB SERVICE
    IN COMPUTE POOL {self.compute_pool}
    NAME = {service_name}
    COMMENT = 'snowpark-submit{f": {self.args.comment}" if self.args.comment else ""}'
    ASYNC = TRUE{f'''
    EXTERNAL_ACCESS_INTEGRATIONS = ({self.args.external_access_integrations})''' if self.args.external_access_integrations else ''}
    FROM SPECIFICATION $$
{textwrap.indent(spcs_spec_yaml, ' ' * 4)}
    $$
    """

    def generate_service_name(self) -> str:
        """
        Generate a unique service name for the workload.
        Can be overridden by subclasses for custom naming schemes.

        Returns:
            A unique service name with timestamp suffix
        """
        if self.args.snowflake_workload_name:
            # Append UTC timestamp to ensure unique workload names
            timestamp = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S")
            service_name = f"{self.args.snowflake_workload_name}_{timestamp}".upper()

            # Validate the generated name length
            MAX_SERVICE_NAME_LENGTH = 255
            if len(service_name) > MAX_SERVICE_NAME_LENGTH:
                timestamp_suffix_length = len("_YYMMDD_HHMMSS")  # 15 characters
                max_allowed_user_length = (
                    MAX_SERVICE_NAME_LENGTH - timestamp_suffix_length
                )
                raise ValueError(
                    f"Workload name '{self.args.snowflake_workload_name}' is too long. "
                    f"After adding the timestamp suffix, the total length ({len(service_name)}) "
                    f"exceeds the maximum allowed length of {MAX_SERVICE_NAME_LENGTH} characters. "
                    f"Please use a workload name with at most {max_allowed_user_length} characters."
                )

            logger.info(f"Generated workload name: {service_name}")
            logger.info(
                f"Original name: {self.args.snowflake_workload_name}, Timestamp suffix: {timestamp} (UTC)"
            )
        else:
            # No workload name provided, generate a random one with timestamp for consistency
            base_name = generate_random_name(
                prefix="snowpark_submit_job_service_"
            ).upper()
            timestamp = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S")
            service_name = f"{base_name}_{timestamp}"
            logger.info(f"Generated workload name: {service_name}")

        return service_name

    def run(self):
        # TODO: required deps - pyyaml.
        # TODO: currently this experiment app supports only scala 2.12 and spark 3.5.3. We need a way for customer to specify which version of scala and spark to use.
        # TODO: support following arguments
        #  trace level
        #  metrics level
        #  snowflake secrets
        self.init_snowflake_session()

        server_image_name = self._server_image_name_override()
        if self.args.filename.endswith(".jar"):
            self.client_app_language = "scala"
        elif self.args.filename.endswith(".py"):
            self.client_app_language = "python"
        else:
            raise ValueError(
                f"Only .jar and .py files are supported now. {self.args.filename} is provided."
            )

        client_image_name = self._client_image_name_override()
        if (
            hasattr(self.args, "requirements_file")
            and self.args.requirements_file
            and self.client_app_language != "python"
        ):
            raise ValueError(
                f"--requirements-file can only be used with Python files, not with {self.args.filename}. "
            )

        # step 1, upload client files to stage
        temp_stage_name = self.create_temp_stage_for_upload()
        client_src_zip_file_path = self.upload_client_files(temp_stage_name)

        custom_files = self._custom_files_to_upload()
        if custom_files:
            for file in custom_files:
                file_path = Path(file)
                upload_sql = f"PUT file://{file_path.resolve()} @{temp_stage_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
                self.get_snowpark_session().sql(upload_sql).collect()
                logger.debug(
                    f"Uploaded the custom file {file_path} to the temporary stage {temp_stage_name}."
                )

        if logger.isEnabledFor(logging.DEBUG):
            stage_content = (
                self.get_snowpark_session().sql(f"ls @{temp_stage_name}").collect()
            )
            logger.debug(f"files in temp stage: {stage_content}")

        # step 1.5, adjusts file path related args
        self.adjust_file_paths()
        if self.client_app_language == "scala":
            # Adds additional jars to classpath if needed
            self._add_additional_jars_to_classpath()

        # step 2, prepare SPCS specs
        service_name = self.generate_service_name()
        logger.debug("service_name: %s", service_name)
        spcs_spec_yaml = self.prepare_spcs_spec(
            temp_stage_name=temp_stage_name,
            client_src_zip_file_path=client_src_zip_file_path,
            server_image_name=server_image_name,
            client_image_name=client_image_name,
            service_name=service_name,
        )

        # step 3, spins up SPCS service
        logger.debug("Start running SPCS job service %s", service_name)
        execute_spcs_sql = self.generate_execute_service_sql(
            service_name, spcs_spec_yaml
        )
        logger.debug(execute_spcs_sql)  # TODO: return -1 when error
        # Note: We no longer drop existing services since we append timestamps for uniqueness
        try:
            res = self.get_snowpark_session().sql(execute_spcs_sql).collect()
            logger.debug(res)
            if self.args.wait_for_completion:
                logger.info(
                    "Job %s has been submitted and is running in blocking mode. Waiting for completion...\n"
                    "Note: This is the full workload name including the UTC timestamp suffix.",
                    service_name,
                )
            else:
                logger.info(
                    "Job %s has been submitted and is running asynchronously in SPCS.\n"
                    "Note: This is the full workload name including the UTC timestamp suffix.\n"
                    "To check status, use: snowpark-submit --workload-status --snowflake-workload-name %s\n"
                    "To terminate, use: snowpark-submit --kill-workload --snowflake-workload-name %s",
                    service_name,
                    service_name,
                    service_name,
                )

            # SQLs to extract logs from event table. The SYSTEM$GET_SERVICE_LOGS function is not available after service is dropped.
            # And SPCS team is working on an easy function to extract logs from event table. ETA early May.
            log_line = f"""
            SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT;
            select *
            from <event table from above query result>
            where RESOURCE_ATTRIBUTES['snow.service.type'] = 'Job'
            and RESOURCE_ATTRIBUTES['snow.service.container.name'] = 'client' -- or 'server' for server log
            and RESOURCE_ATTRIBUTES['snow.service.name'] = '{service_name}'
            and RECORD_TYPE = 'LOG'
            and timestamp > dateadd('minute', -10, current_timestamp()) -- adjust timestamp for your case
            order by timestamp
            ;
            """
            logger.info(
                "To fetch logs from event table, please run the following SQLs: %s",
                log_line,
            )

            logger.info(
                f"To monitor the progress of the job, run following command:\n"
                f"snowpark-submit --workload-status --snowflake-workload-name {service_name} [--snowflake-connection-name ...] [--display-logs]\n"
                f"(Note: Use the full name with timestamp suffix)"
            )
            if self.args.wait_for_completion:
                result = self.wait_for_service_completion(service_name)
                return result
        except Exception as e:
            logger.error(e)
            return StatusInfo(exit_code=1, error=str(e))
        finally:
            # Only close the session if we created it ourselves
            # If the session was provided externally, the caller is responsible for closing it
            if not self._session_provided:
                self.get_snowpark_session().close()

        return StatusInfo(exit_code=0, workload_name=service_name)

    def create_temp_stage_for_upload(self):
        # Create a temporary stage for uploading files
        temp_stage_name = generate_random_name(prefix="sf_spark_submit_temp_stage_")

        # currently azure only supports SNOWFLAKE_SSE encryption type. aws supports both SNOWFLAKE_FULL/SSE
        create_stage_sql = f"CREATE OR REPLACE TEMPORARY STAGE {temp_stage_name} ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );"
        self.get_snowpark_session().sql(create_stage_sql).collect()

        return temp_stage_name

    def get_snowpark_session(self) -> snowpark.Session:
        """
        Returns the Snowpark session.
        """
        if self._snowpark_session is None:
            self.init_snowflake_session()
        return self._snowpark_session

    def _get_service_logs(self, workload_name: str) -> list[str]:
        logs = []
        logger.debug("Attempting to retrieve service logs...")
        try:
            logs_sql = f"""
SELECT SYSTEM$GET_SERVICE_LOGS('{workload_name}', 0, 'client', {self.args.number_of_most_recent_log_lines})
"""

            logs_result = self.get_snowpark_session().sql(logs_sql).collect()

            if logs_result and logs_result[0][0]:
                log_content = logs_result[0][0]
                logs = log_content.split("\n") if log_content else []
            else:
                logger.debug("No logs returned from SYSTEM$GET_SERVICE_LOGS")

        except Exception as e:
            logger.debug(
                f"Failed to retrieve logs using SYSTEM$GET_SERVICE_LOGS: {str(e)}"
            )

        return logs

    def _get_logs_from_event_table(
        self, workload_name: str, log_start_time: str, log_end_time: str
    ) -> list[str]:
        logs = []

        try:
            logger.warning(
                "Could not get service logs directly. Retrieving logs from EVENT_TABLE..."
            )

            event_table_result = (
                self.get_snowpark_session()
                .sql("SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT;")
                .collect()
            )

            if not event_table_result or not event_table_result[0]["value"]:
                logger.error("Event table has not been configured.")
                return logs

            if self.args.number_of_most_recent_log_lines == -1:
                # extract full logs
                event_table_sql = f"""
select timestamp, value
from {event_table_result[0]["value"]}
where RESOURCE_ATTRIBUTES['snow.service.type'] = 'Job'
and RESOURCE_ATTRIBUTES['snow.service.container.name'] = 'client'
and RESOURCE_ATTRIBUTES['snow.service.name'] = '{workload_name}'
and RECORD_TYPE = 'LOG'
and timestamp >= '{log_start_time}'
and timestamp <= '{log_end_time}'
order by timestamp asc
;
"""
            else:
                event_table_sql = f"""
select * from (
select timestamp, value
from {event_table_result[0]["value"]}
where RESOURCE_ATTRIBUTES['snow.service.type'] = 'Job'
and RESOURCE_ATTRIBUTES['snow.service.container.name'] = 'client'
and RESOURCE_ATTRIBUTES['snow.service.name'] = '{workload_name}'
and RECORD_TYPE = 'LOG'
and timestamp >= '{log_start_time}'
and timestamp <= '{log_end_time}'
order by timestamp desc
limit {self.args.number_of_most_recent_log_lines}
) as subquery
order by timestamp asc
;
"""

            logs_df = self.get_snowpark_session().sql(event_table_sql)
            rows = logs_df.collect()

            for row in rows:
                log_line = " ".join(str(x) for x in row)
                logs.append(log_line)

        except Exception as e:
            logger.error(f"Failed to retrieve logs from EVENT_TABLE: {str(e)}")

        return logs

    def _log_session_info(self) -> None:
        """
        Log current session information to help users debug connection.
        """
        try:
            session = self._snowpark_session
            logger.info("-" * 60)
            logger.info("SNOWFLAKE SESSION INFO")
            logger.info("-" * 60)
            quote = '"'
            logger.info(
                f"Account    : {(session.get_current_account() or 'N/A').strip(quote)}"
            )
            logger.info(
                f"User       : {(session.get_current_user() or 'N/A').strip(quote)}"
            )
            logger.info(
                f"Role       : {(session.get_current_role() or 'N/A').strip(quote)}"
            )
            logger.info(
                f"Database   : {(session.get_current_database() or 'N/A').strip(quote)}"
            )
            logger.info(
                f"Schema     : {(session.get_current_schema() or 'N/A').strip(quote)}"
            )
            logger.info(
                f"Warehouse  : {(session.get_current_warehouse() or 'N/A').strip(quote)}"
            )
            logger.info(f"Session ID : {session.session_id}")
            logger.info("-" * 60)
        except Exception as e:
            logger.warning(f"Failed to retrieve session information: {e}")

    def describe(
        self,
        service_name: str | None = None,
        display_logs: bool = False,
    ) -> StatusInfo:
        """
        Returns a StatusInfo object containing structured status information for the workload.
        """
        workload_name = service_name or self.args.snowflake_workload_name
        if not workload_name:
            logger.error("Missing mandatory option --snowflake-workload-name")
            return StatusInfo(
                exit_code=1,
                error="Missing mandatory option --snowflake-workload-name",
            )

        workload_name = workload_name.upper()

        try:
            service_status_result = (
                self.get_snowpark_session()
                .sql(f"DESCRIBE SERVICE {workload_name};")
                .collect()
            )
        except Exception as e:
            logger.error(f"Failed to describe service {workload_name}: {e}")
            return StatusInfo(
                exit_code=1,
                error=f"Failed to describe service {workload_name}: {e}",
            )

        # Gets the job status information from JOB SERVICE from SPCS
        service_status = service_status_result[0]["status"]
        service_created_on = (
            service_status_result[0]["created_on"]
            .astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
        )
        terminated = service_status.upper() in [
            "FAILED",
            "DONE",
            "SUSPENDED",
            "DELETED",
            "INTERNAL_ERROR",
        ]
        terminated_at = None
        if terminated:
            terminated_at = (
                service_status_result[0]["updated_on"]
                .astimezone(timezone.utc)
                .isoformat(timespec="microseconds")
            )

        # Gets the job status information from JOB SERVICE containers from SPCS
        job_status_result = (
            self.get_snowpark_session()
            .sql(f"SHOW SERVICE CONTAINERS IN SERVICE {workload_name};")
            .collect()
        )
        job_status = job_status_result[0]["service_status"]

        # Format job start time if it exists
        job_start_time_result = job_status_result[0]["start_time"]
        job_start_time = None
        if job_start_time_result:
            # Handle both 'Z' suffix and standard timezone formats
            timestamp_str = job_start_time_result
            if timestamp_str.endswith("Z"):
                # Replace 'Z' with '+00:00' for fromisoformat compatibility
                timestamp_str = timestamp_str[:-1] + "+00:00"
            try:
                job_start_time = (
                    datetime.fromisoformat(timestamp_str)
                    .astimezone(timezone.utc)
                    .isoformat(timespec="microseconds")
                )
            except (ValueError, TypeError) as e:
                logger.error(
                    f"Invalid timestamp format: {job_start_time_result} {str(e)}"
                )
                job_start_time = None
        job_exit_code = job_status_result[0]["last_exit_code"]

        # Prints the unified status. All timestamp are in UTC.
        logger.info(f"Snowflake Workload Name: {workload_name}")
        logger.info(f"Service Status: {service_status}")
        logger.info(f"Workload Status: {job_status}")
        logger.info(f"Created On: {service_created_on}")
        logger.info(f"Started At: {job_start_time}")
        logger.info(f"Terminated At: {terminated_at}")
        logger.info(f"Exit Code: {job_exit_code}")

        logs = []
        if display_logs or self.args.display_logs:

            if service_status == "PENDING":
                logger.debug("Service is PENDING, no logs available yet.")
            else:
                logs = (
                    self._get_service_logs(workload_name)
                    if self.args.number_of_most_recent_log_lines != -1
                    else None
                )

                # If no service logs found or full logs is requested, fallback to EVENT_TABLE
                if not logs:
                    log_start_time = job_start_time or service_created_on
                    log_end_time = terminated_at
                    if not terminated:
                        now = datetime.now().astimezone(
                            timezone.utc
                        )  # Attach local timezone
                        log_end_time = now.isoformat(timespec="microseconds")

                    logs = self._get_logs_from_event_table(
                        workload_name=workload_name,
                        log_start_time=log_start_time,
                        log_end_time=log_end_time,
                    )

                logger.info("Application Logs:")
                for log_line in logs:
                    logger.info(log_line)

        return StatusInfo(
            exit_code=0,
            terminated=terminated,
            workload_name=workload_name,
            service_status=service_status,
            workload_status=job_status,
            created_on=service_created_on,
            started_at=job_start_time,
            terminated_at=terminated_at,
            job_exit_code=job_exit_code,
            logs=logs,
        )

    def end_workload(self) -> StatusInfo:
        """
        Returns a StatusInfo object containing exit code: 0 for success, 1 for failure.
        """
        workload_name = self.args.snowflake_workload_name
        if not workload_name:
            logger.error("Missing mandatory option --snowflake-workload-name")
            return StatusInfo(
                exit_code=1,
                error="Missing mandatory option --snowflake-workload-name",
            )

        workload_name = workload_name.upper()
        try:
            drop_service_result = (
                self.get_snowpark_session()
                .sql(f"DROP SERVICE IF EXISTS {workload_name} FORCE;")
                .collect()
            )

            if not drop_service_result:
                logger.error(f"Failed to drop workload: {workload_name}")
                return StatusInfo(
                    exit_code=1,
                    error=f"Failed to drop workload: {workload_name}",
                )

            logger.info(f"Workload {workload_name} terminated successfully.")
            return StatusInfo(exit_code=0)

        except Exception as e:
            logger.error(e)
            return StatusInfo(
                exit_code=1,
                error=f"Failed to complete operation due to: {str(e)}",
            )

    def list_workloads(self, prefix: str) -> StatusInfo:
        """
        List workloads in the compute pool filtered by prefix.

        Args:
            prefix: Required prefix to filter workload names (case-insensitive)

        Returns:
            StatusInfo object with list of workloads
        """
        try:
            # Check both args and self for compute_pool
            # Priority: CLI args (self.args) override connection config (self)
            compute_pool = getattr(self.args, "compute_pool", None) or getattr(
                self, "compute_pool", None
            )
            if not compute_pool:
                logger.error("Compute pool must be specified to list workloads")
                return StatusInfo(
                    exit_code=1,
                    error="Compute pool must be specified to list workloads. Use --compute-pool option or define it in your connection configuration.",
                )

            # Build query with the required prefix
            # SHOW SERVICES LIKE pattern is case-insensitive in Snowflake
            query = (
                f"SHOW SERVICES LIKE '{prefix.upper()}%' IN COMPUTE POOL {compute_pool}"
            )
            logger.info(f"Listing workloads with prefix: {prefix}")

            # Execute SHOW command and get results directly
            results = self.get_snowpark_session().sql(query).collect()

            # Sort results by created_on in descending order
            sorted_results = sorted(
                results,
                key=lambda row: row["created_on"] if "created_on" in row else "",
                reverse=True,
            )

            # Format and display results
            if not sorted_results:
                message = f"No workloads found in compute pool {compute_pool} with prefix '{prefix}'"
                logger.info(message)
                return StatusInfo(exit_code=0)

            # Create formatted output
            logger.info(
                f"Found {len(sorted_results)} workload(s) matching prefix '{prefix}'"
            )

            # Format as table with appropriate column widths
            logger.info(f"{'NAME':<60} {'STATUS':<12} {'CREATED_ON':<22}")
            logger.info("-" * 95)

            for row in sorted_results:
                # Snowpark Row objects use indexing, not .get() method
                name = str(row["name"] if "name" in row else "")
                status = str(row["status"] if "status" in row else "")
                created = str(row["created_on"] if "created_on" in row else "")[
                    :19
                ]  # Trim microseconds if present
                logger.info(f"{name:<60} {status:<12} {created:<22}")

            # Add helpful instructions with current connection parameters
            connection_args = []
            if self.args.snowflake_connection_name:
                connection_args.append(
                    f"--snowflake-connection-name {self.args.snowflake_connection_name}"
                )
            if self.args.compute_pool:
                connection_args.append(f"--compute-pool {self.args.compute_pool}")
            if self.args.account:
                connection_args.append(f"--account {self.args.account}")
            if self.args.host:
                connection_args.append(f"--host {self.args.host}")

            connection_str = (
                " ".join(connection_args) if connection_args else "[connection-options]"
            )

            logger.info(
                f"\nTo check status: snowpark-submit --workload-status --snowflake-workload-name <NAME> {connection_str}\n"
                f"To terminate: snowpark-submit --kill-workload --snowflake-workload-name <NAME> {connection_str}"
            )

            return StatusInfo(exit_code=0)

        except Exception as e:
            error_msg = f"Failed to list workloads: {str(e)}"
            logger.error(error_msg)
            return StatusInfo(exit_code=1, error=error_msg)
