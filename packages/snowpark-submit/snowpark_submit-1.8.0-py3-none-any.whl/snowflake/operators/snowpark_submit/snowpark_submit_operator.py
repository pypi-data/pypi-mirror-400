#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import os
import random
import string
import sys
from io import StringIO
from typing import Optional

from airflow.models import BaseOperator
from airflow.utils.context import Context
from snowflake.operators.snowpark_submit.connection_utils import (
    merge_airflow_connection_config,
    validate_connection_config,
)
from snowflake.snowpark_submit.snowpark_submit import runner_wrapper


def generate_service_name(
    prefix: str = "SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_", length: int = 15
) -> str:
    choices = string.ascii_uppercase + string.digits
    random_id = "".join(random.choice(choices) for _ in range(length))
    return f"{prefix}{random_id}"


class SnowparkSubmitOperator(BaseOperator):
    """
    Apache Airflow operator for executing snowpark-submit commands.

    :param file: Path to the file to execute (Python or JAR file).
    :param main_class: Main class name for Java/Scala applications (required for JAR files)
    :param application_args: List of arguments to pass to the application
    :param connections_config: Dictionary containing Snowflake connection parameters
    :param service_name: Custom service name (auto-generated if not provided)
    :param py_files: Comma-separated list of Python dependencies (Python only)
    :param files: Comma-separated list of files to be placed in the working directory of workload node
    :param jars: Comma-separated list of JAR dependencies (Java/Scala only)
    :param name: A name of your application.
    :param comment: Comment/description for the workload
    :param snowflake_log_level: Log level for Snowflake events ('INFO', 'ERROR', 'NONE')
    :param wait_for_completion: Run workload in blocking mode and wait for completion (default: False)
    :param properties_file: Path to a file from which to load extra Spark properties
    :param fail_on_error: Whether to fail the Airflow task if the Spark job failed (only applies when wait_for_completion=True)
    :param requirements_file: Path to requirements.txt file containing Python package dependencies
    :param wheel_files: Comma-separated list of .whl files to install before running the workload
    :param init_script: Path to shell script (.sh) to execute before running the workload
    :param display_logs: Whether to fetch and display application logs (only applies when wait_for_completion=True)
    :param number_of_most_recent_log_lines: Number of most recent log lines to fetch if display_logs=True (default: 500). -1 for fetching all logs.
    :param external_access_integrations: Comma-separated list of external access integrations (docs.snowflake.com/sql-reference/sql/create-external-access-integration)
    :param snowflake_conn_id: Airflow connection ID for Snowflake. When provided, connection details
        (host, user, password, schema, port) and extra configuration (account, role, warehouse, database,
        compute_pool) will be automatically merged into connections_config without overwriting existing values.

    Ex:
        task = SnowparkSubmitOperator(
            task_id='my_python_job',
            file='/path/to/script.py',
            connections_config={
                'account': snowflake_conn.extra_dejson.get('account'),
                'host': snowflake_conn.host,
                'user': snowflake_conn.login,
                'password': snowflake_conn.password,
                'role': snowflake_conn.extra_dejson.get('role'),
                'warehouse': snowflake_conn.extra_dejson.get('warehouse'),
                'database': snowflake_conn.schema,
                'schema': snowflake_conn.extra_dejson.get('schema'),
                'compute_pool': snowflake_conn.extra_dejson.get('compute_pool'),
            },
            requirements_file='/path/to/requirements.txt',
            wheel_files='private-lib.whl,custom-utils.whl',
            init_script='/path/to/setup.sh',
            external_access_integrations='pypi_access_integration',
            wait_for_completion=True,
            display_logs=True,
            dag=dag
        )

    """

    template_fields = [
        "file",
        "main_class",
        "application_args",
        "service_name",
        "py_files",
        "files",
        "jars",
        "name",
        "connections_config",
        "comment",
        "snowflake_log_level",
        "wait_for_completion",
        "properties_file",
        "fail_on_error",
        "requirements_file",
        "wheel_files",
        "init_script",
        "display_logs",
        "number_of_most_recent_log_lines",
        "external_access_integrations",
        "snowflake_conn_id",
    ]

    def __init__(
        self,
        connections_config: Optional[dict] = None,
        file: Optional[str] = None,
        main_class: Optional[str] = None,
        application_args: Optional[list] = None,
        service_name: Optional[str] = None,
        py_files: Optional[str] = None,
        files: Optional[str] = None,
        jars: Optional[str] = None,
        name: Optional[str] = None,
        comment: Optional[str] = None,
        snowflake_log_level: Optional[str] = None,
        wait_for_completion: bool = False,
        properties_file: Optional[str] = None,
        fail_on_error: bool = False,
        requirements_file: Optional[str] = None,
        wheel_files: Optional[str] = None,
        init_script: Optional[str] = None,
        display_logs: bool = False,
        number_of_most_recent_log_lines: int = 500,
        external_access_integrations: Optional[str] = None,
        snowflake_conn_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.file = file
        self.main_class = main_class
        self.application_args = application_args or []
        self.connections_config = connections_config
        self.service_name = service_name
        self.py_files = py_files
        self.files = files
        self.jars = jars
        self.name = name
        self.comment = comment
        self.snowflake_log_level = snowflake_log_level
        self.wait_for_completion = wait_for_completion
        self.properties_file = properties_file
        self.fail_on_error = fail_on_error
        self.requirements_file = requirements_file
        self.wheel_files = wheel_files
        self.init_script = init_script
        self.display_logs = display_logs
        self.number_of_most_recent_log_lines = number_of_most_recent_log_lines
        self.external_access_integrations = external_access_integrations

        self.snowflake_conn_id = snowflake_conn_id

        # Merge Airflow connection details if snowflake_conn_id is provided
        self.connections_config = merge_airflow_connection_config(
            self.connections_config, self.snowflake_conn_id
        )

    def _validate_required_config(self):
        validate_connection_config(self.connections_config)

    def _validate_file(self):
        if not self.file:
            raise ValueError("file parameter must be specified")

        if not os.path.exists(self.file):
            raise FileNotFoundError(f"File not found: {self.file}")

        file_ext = os.path.splitext(self.file)[1].lower()
        if file_ext == ".py":
            self.log.info(f"Detected Python file: {self.file}")
        elif file_ext == ".jar":
            self.log.info(f"Detected JAR file: {self.file}")
            if not self.main_class:
                raise ValueError("main_class is required for JAR files")
        else:
            raise ValueError(
                f"Unsupported file type: {file_ext}. Only .py and .jar files are supported"
            )

    def _build_command(self) -> list:
        cmd = ["snowpark-submit"]

        if self.main_class:
            cmd.extend(["--class", self.main_class])
        for key, value in self.connections_config.items():
            if value is not None:
                cli_key = key.replace("_", "-")
                cmd.extend([f"--{cli_key}", str(value)])

        if self.name:
            cmd.extend(["--name", self.name])
        if self.comment:
            cmd.extend(["--comment", self.comment])
        if self.snowflake_log_level:
            cmd.extend(["--snowflake-log-level", self.snowflake_log_level])
        if self.jars:
            cmd.extend(["--jars", self.jars])
        if self.py_files:
            cmd.extend(["--py-files", self.py_files])
        if self.files:
            cmd.extend(["--files", self.files])
        if self.requirements_file:
            cmd.extend(["--requirements-file", self.requirements_file])
        if self.wheel_files:
            cmd.extend(["--wheel-files", self.wheel_files])
        if self.init_script:
            cmd.extend(["--init-script", self.init_script])
        if self.external_access_integrations:
            cmd.extend(
                ["--external-access-integrations", self.external_access_integrations]
            )

        if self.wait_for_completion:
            cmd.append("--wait-for-completion")
            self.log.info("Running in blocking mode will wait for completion")
            if self.display_logs:
                cmd.append("--display-logs")
                self.log.info("Will fetch and display application logs")
                cmd.extend(
                    [
                        "--number-of-most-recent-log-lines",
                        str(self.number_of_most_recent_log_lines),
                    ]
                )
                self.log.info(
                    f"Fetching {self.number_of_most_recent_log_lines} most recent log lines"
                )

        if self.properties_file:
            cmd.extend(["--properties-file", self.properties_file])
            self.log.info(f"Using properties file: {self.properties_file}")

        if not self.service_name:
            self.service_name = generate_service_name()
            self.log.info(f"generated service name: {self.service_name}")
        else:
            self.log.info(f"Using service name: {self.service_name}")

        cmd.append(f"--snowflake-workload-name={self.service_name}")

        if self.file:
            cmd.append(self.file)
        else:
            raise ValueError("file parameter must be specified")

        if self.application_args:
            cmd.extend(self.application_args)

        return cmd

    def execute(self, context: Context):
        self._validate_required_config()
        self._validate_file()

        if self.fail_on_error and not self.wait_for_completion:
            self.log.warning(
                "fail_on_error parameter is ignored when wait_for_completion=False. "
                "fail_on_error only applies to blocking mode."
            )

        if self.display_logs and not self.wait_for_completion:
            self.log.warning(
                "display_logs parameter is ignored when wait_for_completion=False. "
                "display_logs only applies to blocking mode."
            )

        if self.properties_file:
            if not os.path.exists(self.properties_file):
                raise FileNotFoundError(
                    f"Properties file not found: {self.properties_file}"
                )

        cmd = self._build_command()

        self.log.info(f"Executing snowpark-submit command: {' '.join(cmd)}")

        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_argv = sys.argv

        captured_stdout = StringIO()
        captured_stderr = StringIO()

        try:
            sys.stdout = captured_stdout
            sys.stderr = captured_stderr
            sys.argv = cmd

            result = runner_wrapper(test_mode=True)
            stdout_content = captured_stdout.getvalue()
            stderr_content = captured_stderr.getvalue()

            self.log.info(f"runner_wrapper returned with exit code: {result.exit_code}")
            # Use the actual workload name from the result (which includes timestamp)
            actual_service_name = (
                result.workload_name if result.workload_name else self.service_name
            )
            context["ti"].xcom_push(key="service_name", value=actual_service_name)  # type: ignore
            context["ti"].xcom_push(key="return_code", value=result.exit_code)  # type: ignore
            context["ti"].xcom_push(key="stdout", value=stdout_content)  # type: ignore
            context["ti"].xcom_push(key="stderr", value=stderr_content)  # type: ignore
            if result.logs:
                context["ti"].xcom_push(key="logs", value=result.logs)  # type: ignore

            job_failed = False

            # alwas fail if snowpark-submit command itself failed
            if result.exit_code != 0:
                job_failed = True
                self.log.error(
                    f"snowpark-submit command failed with exit code: {result.exit_code}"
                )

            # if submission succeeded but we're in blocking mode, check for Spark job failure
            elif self.wait_for_completion and self.fail_on_error:
                # check if the Spark job itself failed (even though submission succeeded)
                if "Workload Status: FAILED" in stdout_content:
                    job_failed = True
                    self.log.error("Spark job failed - workload status: FAILED")

            if not job_failed:
                if result.exit_code == 0:
                    self.log.info(
                        f"snowpark-submit completed successfully with exit code: {result.exit_code}"
                    )
                    self.log.info(
                        f"Job service created with name: {actual_service_name}"
                    )

            if job_failed:
                if result.exit_code != 0:
                    raise Exception(
                        f"snowpark-submit command failed with exit code: {result.exit_code}"
                    )
                else:
                    raise Exception("Spark job failed with status: FAILED")

            return {
                "service_name": actual_service_name,
                "return_code": result.exit_code,
                "stdout": stdout_content,
                "stderr": stderr_content,
                "logs": result.logs if result.logs else [],
            }

        except Exception as e:
            self.log.error(f"snowpark-submit failed: {e}")
            raise
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.argv = original_argv
