#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import sys
from typing import Optional

from airflow.models import BaseOperator
from airflow.utils.context import Context
from snowflake.operators.snowpark_submit.connection_utils import (
    merge_airflow_connection_config,
)
from snowflake.snowpark_submit.cluster_mode.job_runner import StatusInfo
from snowflake.snowpark_submit.snowpark_submit import runner_wrapper


class SnowparkSubmitStatusOperator(BaseOperator):
    """
    Airflow operator for checking the status of snowpark-submit workloads.

    :param snowflake_workload_name: Name of the workload to check status for (required)
    :param connections_config: Dictionary containing Snowflake connection parameters
    :param snowflake_conn_id: Airflow connection ID for Snowflake. When provided, connection details
        (host, user, password, schema, port) and extra configuration (account, role, warehouse, database,
        compute_pool) will be automatically merged into connections_config without overwriting existing values.
    :param display_logs: Whether to fetch and display application logs (default: False)
    :param fail_on_error: Whether to fail the Airflow task if the Spark job failed (default: False)
    :param wait_for_completion: Whether to wait for the workload to complete before returning (default: False)

    Returns a StatusInfo object:
        - workload_name: The workload name that was checked
        - workload_status: Current workload status (e.g., "PENDING", "RUNNING", "DONE", "FAILED")
        - service_status: Service status (e.g., "PENDING", "RUNNING", "DONE", "FAILED")
        - created_on: When the workload was created
        - started_at: When the workload started execution
        - terminated_at: When the workload terminated (if applicable)
        - job_exit_code: Exit code of the workload (int, if terminated)
        - logs: Application logs (list, if display_logs=True)

    Example usage:
        # Check status once and return immediately
        check_status = SnowparkSubmitStatusOperator(
            task_id='check_job_status',
            snowflake_workload_name="{{ ti.xcom_pull(task_ids='submit_job', key='return_value')['service_name'] }}",
            connections_config=connection_config,
            display_logs=True,
            fail_on_error=True,
            dag=dag
        )

        # Wait for job completion before returning
        wait_for_completion = SnowparkSubmitStatusOperator(
            task_id='wait_for_job_completion',
            snowflake_workload_name="{{ ti.xcom_pull(task_ids='submit_job', key='return_value')['service_name'] }}",
            connections_config=connection_config,
            wait_for_completion=True,
            fail_on_error=True,
            dag=dag
        )

        # Alternative: Using Airflow connection ID
        check_status_with_conn_id = SnowparkSubmitStatusOperator(
            task_id='check_status_with_conn_id',
            snowflake_workload_name="{{ ti.xcom_pull(task_ids='submit_job', key='service_name') }}",
            snowflake_conn_id='snowflake_default',  # Uses Airflow connection
            connections_config={},  # Will be populated from connection
            display_logs=True,
            dag=dag
        )

        result = check_status.execute(context)
        print(f"Status: {result.workload_status}")
        print(f"Exit code: {result.job_exit_code}")
    """

    template_fields = [
        "snowflake_workload_name",
        "connections_config",
        "display_logs",
        "number_of_most_recent_log_lines",
        "fail_on_error",
        "wait_for_completion",
    ]

    def __init__(
        self,
        snowflake_workload_name: str,
        connections_config: Optional[dict] = None,
        snowflake_conn_id: Optional[str] = None,
        display_logs: bool = False,
        number_of_most_recent_log_lines: int = 500,
        fail_on_error: bool = False,
        wait_for_completion: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.snowflake_workload_name = snowflake_workload_name
        self.connections_config = connections_config
        self.display_logs = display_logs
        self.number_of_most_recent_log_lines = number_of_most_recent_log_lines
        self.fail_on_error = fail_on_error
        self.wait_for_completion = wait_for_completion

        self.snowflake_conn_id = snowflake_conn_id

        # Merge Airflow connection details if snowflake_conn_id is provided
        self.connections_config = merge_airflow_connection_config(
            self.connections_config, self.snowflake_conn_id
        )

    def _build_command(self) -> list:
        cmd = ["snowpark-submit"]

        cmd.append(f"--snowflake-workload-name={self.snowflake_workload_name}")

        for key, value in self.connections_config.items():
            if value is not None:
                cli_key = key.replace("_", "-")
                cmd.extend([f"--{cli_key}", str(value)])

        cmd.append("--workload-status")

        if self.display_logs:
            cmd.append("--display-logs")
            cmd.extend(
                [
                    "--number-of-most-recent-log-lines",
                    str(self.number_of_most_recent_log_lines),
                ]
            )
            self.log.info(
                f"Fetching {self.number_of_most_recent_log_lines} most recent log lines"
            )

        if self.wait_for_completion:
            cmd.append("--wait-for-completion")

        return cmd

    def execute(self, context: Context) -> StatusInfo:
        if not self.snowflake_workload_name:
            raise ValueError("snowflake_workload_name is required")

        cmd = self._build_command()

        self.log.info(f"Checking status for workload: {self.snowflake_workload_name}")
        self.log.info(f"Executing command: {' '.join(cmd)}")

        original_argv = sys.argv

        try:
            sys.argv = cmd

            result = runner_wrapper(test_mode=True)

            if result.error:
                self.log.error(f"snowpark-submit failed: {result.error}")
                raise RuntimeError(result.error)

            if result.workload_status == "FAILED":
                self.log.error(
                    f"Workload {self.snowflake_workload_name} failed with exit code: {result.job_exit_code}"
                )

            context["ti"].xcom_push(key="status", value=result.workload_status)
            context["ti"].xcom_push(key="service_status", value=result.service_status)
            context["ti"].xcom_push(key="created_on", value=result.created_on)
            context["ti"].xcom_push(key="started_at", value=result.started_at)
            context["ti"].xcom_push(key="terminated_at", value=result.terminated_at)
            context["ti"].xcom_push(key="exit_code", value=result.job_exit_code)
            context["ti"].xcom_push(key="logs", value=result.logs)

            if self.fail_on_error:
                if result.workload_status == "FAILED":
                    raise RuntimeError(
                        f"Spark job failed with status: FAILED. Status details: {result}"
                    )
                elif (
                    result.workload_status == "DONE"
                    and result.job_exit_code is not None
                    and result.job_exit_code != 0
                ):
                    raise RuntimeError(
                        f"Spark job completed with non-zero exit code: {result.job_exit_code}. Status details: {result}"
                    )

            return result

        except Exception as e:
            self.log.error(f"snowpark-submit status check failed: {e}")
            raise
        finally:
            sys.argv = original_argv
