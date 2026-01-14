#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import argparse
import os
from pathlib import Path
from typing import Callable

from snowflake.snowpark_submit.cluster_mode.job_runner import JobRunner
from snowflake.snowpark_submit.constants import DOCKER_WORKDIR

from snowflake import snowpark


def _get_custom_scos_wheel_file_path_for_server_container_test_only() -> str:
    return os.getenv("TEST_ONLY_SERVER_CONTAINER_CUSTOM_SCOS_WHEEL_PATH", "")


def _get_custom_scos_wheel_file_path_for_client_container_test_only() -> str:
    return os.getenv("TEST_ONLY_CLIENT_CONTAINER_CUSTOM_SCOS_WHEEL_PATH", "")


class SparkConnectJobRunner(JobRunner):
    def __init__(
        self,
        args: argparse.Namespace,
        generate_spark_cmd_args: Callable[[argparse.Namespace], list[str]],
        session: snowpark.Session | None = None,
    ) -> None:
        super().__init__(
            args,
            generate_spark_cmd_args,
            client_working_dir=DOCKER_WORKDIR + "/",
            temp_stage_mount_dir=DOCKER_WORKDIR + "/temp-stage/",
            current_dir=os.path.dirname(os.path.abspath(__file__)),
            session=session,
        )

    def _generate_client_container_args(
        self, client_src_zip_file_path: str
    ) -> list[str]:
        args = []
        if client_src_zip_file_path:
            args.extend(["--zip", client_src_zip_file_path])
        args.append(" ".join(self.generate_spark_cmd_args(self.args)))
        return args

    def _get_image_tag(self, env_var_name: str) -> str:
        """
        First, it checks the provided parameter, then checks the environment variable, then defaults to "latest".
        """

        from_param = self.args.snowpark_connect_version
        from_env = os.getenv(env_var_name)

        if from_param == "latest" or (not from_param and not from_env):
            return "latest"
        if from_param == "jenkins":
            return "dev-latest"
        if not from_param:
            return from_env
        import re

        if re.match(r"^\d+\.\d+\.\d+$", from_param):
            return from_param
        else:
            raise Exception("Incorrect snowpark-connect-version parameter value.")

    def _server_image_path_sys_registry(self) -> str:
        version_tag = self._get_image_tag("SNOWFLAKE_SYSTEM_REGISTRY_SERVER_IMAGE_TAG")
        return f"/snowflake/images/snowflake_images/spark_connect_for_snowpark_server:{version_tag}"

    def _client_image_path_sys_registry(self) -> str:
        version_tag = self._get_image_tag("SNOWFLAKE_SYSTEM_REGISTRY_CLIENT_IMAGE_TAG")
        language_suffix = self.client_app_language
        if (
            self.client_app_language == "scala"
            and getattr(self.args, "scala_version", "2.12") == "2.13"
        ):
            language_suffix = "scala213"
        return f"/snowflake/images/snowflake_images/spark_connect_for_snowpark_client_{language_suffix}:{version_tag}"

    def _client_image_name_override(self) -> str:
        return f"snowpark-connect-client-{self.client_app_language}:latest"

    def _server_image_name_override(self) -> str:
        return "snowpark-connect-server:latest"

    def _add_additional_jars_to_classpath(self) -> None:
        # spark-connect-client-jvm_<scala_version>-3.5.3.jar is copied in the docker image.
        scala_version = getattr(self.args, "scala_version", "2.12")
        self._add_class_paths(
            [f"/app/spark_lib/spark-connect-client-jvm_{scala_version}-3.5.3.jar"]
        )

    def _use_system_registry(self) -> bool:
        return os.getenv("SNOWFLAKE_USE_SYSTEM_REGISTRY", "True").lower() == "true"

    def _override_args(self) -> None:
        pass

    def _customize_spcs_spec(self, spec: dict) -> None:
        server_container = spec["container"][0]
        client_container = spec["container"][1]

        custom_scos_wheel_path = (
            _get_custom_scos_wheel_file_path_for_server_container_test_only()
        )
        if custom_scos_wheel_path:
            server_container["env"]["CUSTOM_SCOS_WHEEL_PATH"] = (
                self.temp_stage_mount_dir + Path(custom_scos_wheel_path).name
            )

        custom_scos_wheel_file_for_client = (
            _get_custom_scos_wheel_file_path_for_client_container_test_only()
        )
        if custom_scos_wheel_file_for_client:
            client_container["env"]["CUSTOM_SCOS_WHEEL_PATH"] = (
                self.temp_stage_mount_dir + Path(custom_scos_wheel_file_for_client).name
            )

    def _custom_files_to_upload(self) -> list[str] | None:
        files = []
        if _get_custom_scos_wheel_file_path_for_server_container_test_only():
            files.append(
                _get_custom_scos_wheel_file_path_for_server_container_test_only()
            )
        if _get_custom_scos_wheel_file_path_for_client_container_test_only():
            files.append(
                _get_custom_scos_wheel_file_path_for_client_container_test_only()
            )
        return files
