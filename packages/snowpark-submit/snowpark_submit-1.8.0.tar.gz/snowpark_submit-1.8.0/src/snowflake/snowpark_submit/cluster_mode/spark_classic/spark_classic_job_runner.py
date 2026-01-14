#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import argparse
import os
from typing import Callable

from snowflake.snowpark_submit.cluster_mode.job_runner import JobRunner


class SparkClassicJobRunner(JobRunner):
    def __init__(
        self,
        args: argparse.Namespace,
        generate_spark_cmd_args: Callable[[argparse.Namespace], list[str]],
    ) -> None:
        super().__init__(
            args,
            generate_spark_cmd_args,
            client_working_dir="/home/spark/",
            temp_stage_mount_dir="/home/spark/client-src/",
            current_dir=os.path.dirname(os.path.abspath(__file__)),
        )

    def _generate_client_container_args(
        self, client_src_zip_file_path: str
    ) -> list[str]:
        args = []
        if client_src_zip_file_path:
            args.extend(["--zip", client_src_zip_file_path])
        args.extend(
            self.generate_spark_cmd_args(args=self.args, entrypoint_arg="driver")
        )
        return args

    def _client_image_path_sys_registry(self) -> str:
        return (
            "/snowflake/images/snowflake_images/snowflake-managed-spark:0.0.1-preview"
        )

    def _server_image_path_sys_registry(self) -> str:
        return "/snowflake/images/snowflake_images/spark_connect_for_snowpark_server:0.0.2-preview"

    def _client_image_name_override(self) -> str:
        return "spark_0_0_1:preview"

    def _server_image_name_override(self) -> str:
        return "sas_server_0_0_2:preview"

    def _add_additional_jars_to_classpath(self) -> None:
        # Spark image already contains all needed dependency jars. No need to add more
        pass

    def _use_system_registry(self) -> bool:
        return False

    def _override_args(self) -> None:
        # For classic Spark driver, we do not pass --remote in order to start up
        # full Spark driver context.
        self.args.remote = None
