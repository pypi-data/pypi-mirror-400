#!/usr/bin/env python

#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""A utility script that takes a pyspark script and runs it in the SAS environment.

Typical usage example:
    snowpark-submit ./tools/examples_row.py

"""
import argparse
import logging
import sys
from functools import partial
from typing import Any

from snowflake.snowpark_submit.cluster_mode.job_runner import StatusInfo
from snowflake.snowpark_submit.cluster_mode.spark_connect.spark_connect_job_runner import (
    SparkConnectJobRunner,
)
from snowflake.snowpark_submit.constants import SHARED_VOLUME_MOUNT_PATH

logger = logging.getLogger("snowpark-submit")


class DeprecatedAction(argparse.Action):
    # handles deprecated arguments that should show
    # warnings and be excluded from the final spark submit command

    def __init__(self, *args, **kwargs) -> None:
        if "help" in kwargs:
            kwargs["help"] = f"[DEPRECATED] {kwargs['help']}"
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        logger.warning(f"'{option_string}' is deprecated and will be ignored.")
        setattr(namespace, self.dest, values)
        # add marker to track deprecated arguments
        if not hasattr(namespace, "_deprecated_args"):
            namespace._deprecated_args = set()
        namespace._deprecated_args.add(self.dest)


class ExperimentalAction(argparse.Action):
    # handles experimental arguments that should show
    # warnings but still pass through to spark submit command

    def __init__(self, *args, **kwargs) -> None:
        if "help" in kwargs:
            kwargs["help"] = f"[EXPERIMENTAL] {kwargs['help']}"
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        logger.warning(f"'{option_string}' is experimental for Scala/Java workloads.")
        setattr(namespace, self.dest, values)


def setup_logging(log_level):
    logger = logging.getLogger("snowpark-submit")
    logger.setLevel(log_level)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        for handler in logger.handlers:
            handler.setLevel(log_level)


def init_args(args: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run a Spark script in SAS environment.",
        add_help=False,
        usage="""NOTE: All spark-submit options are displayed here, currently unsupported options are marked [DEPRECATED]
    Usage: snowpark-submit [options] <app jar | python file> [app arguments]
    """,
    )

    parser.register("action", "deprecated", DeprecatedAction)
    parser.register("action", "experimental", ExperimentalAction)

    # Other spark-submit usage (we may add support for these in the future):
    # Usage: snowpark-submit --kill [submission ID] --master [spark://...]
    # Usage: snowpark-submit --status [submission ID] --master [spark://...]
    # Usage: snowpark-submit run-example [options] example-class [example args]
    options_group = parser.add_argument_group("Options")
    spark_connect_group = parser.add_argument_group("Spark Connect only")
    cluster_deploy_group = parser.add_argument_group("Cluster Deploy mode only")
    spark_standalone_or_mesos_cluster_group = parser.add_argument_group(
        "Spark standalone or Mesos with cluster deploy mode only"
    )
    k8s_group = parser.add_argument_group(
        "Spark standalone, Mesos or K8s with cluster deploy mode only"
    )
    spark_standalone_mesos_group = parser.add_argument_group(
        "Spark standalone and Mesos only"
    )
    spark_standalone_yarn_group = parser.add_argument_group(
        "Spark standalone, YARN and Kubernetes only"
    )
    spark_yarn_k8s_group = parser.add_argument_group(
        "Spark on YARN and Kubernetes only"
    )
    spark_yarn_group = parser.add_argument_group("Spark on YARN only")
    snowflake_configs_group = parser.add_argument_group("Snowflake specific configs")

    options_group.add_argument(
        "--master",
        metavar="MASTER_URL",
        type=str,
        action="deprecated",
        help="spark://host:port, mesos://host:port, yarn, k8s://https://host:port, or local (Default: local[*]).",
    )
    options_group.add_argument(
        "--deploy-mode",
        metavar="DEPLOY_MODE",
        type=str,
        choices=["client", "cluster"],
        action="deprecated",
        help="Whether to launch the driver program locally ('client') or on one of the worker machines inside the cluster ('cluster') (Default: client).",
    )
    options_group.add_argument(
        "--class",
        metavar="CLASS_NAME",
        type=str,
        action="experimental",
        help="Your application's main class (for Java / Scala apps).",
    )
    options_group.add_argument(
        "--name",
        metavar="NAME",
        type=str,
        help="A name of your application.",
    )
    options_group.add_argument(
        "--jars",
        metavar="JAR",
        type=str,
        help="Comma-separated list of jars to include on the driver and executor classpaths.",
    )
    options_group.add_argument(
        "--packages",
        type=str,
        nargs="*",
        action="experimental",
        help="Comma-separated list of maven coordinates of jars to include on the driver and executor classpaths. Will search the local maven repo, then maven central and any additional remote repositories given through --repositories. The format for the coordinates should be groupId:artifactId:version.",
    )
    options_group.add_argument(
        "--exclude-packages",
        type=str,
        nargs="*",
        action="experimental",
        help="Comma-separated list of groupId:artifactId, to exclude while resolving the dependencies provided in --packages to avoid dependency conflicts.",
    )
    options_group.add_argument(
        "--repositories",
        type=str,
        nargs="*",
        action="experimental",
        help="Comma-separated list of additional remote repositories to search for the maven coordinates given with --packages.",
    )
    options_group.add_argument(
        "--py-files",
        metavar="PY_FILES",
        type=str,
        help="Comma-separated list of .zip, .egg, or .py files to place on the PYTHONPATH for Python apps.",
    )
    options_group.add_argument(
        "--files",
        metavar="FILES",
        type=str,
        help="Comma-separated list of files to be placed in the working directory of workload node.",
    )
    options_group.add_argument(
        "--archives",
        metavar="ARCHIVES",
        type=str,
        nargs="*",
        action="deprecated",
        help="Comma-separated list of archives to be extracted into the working directory of each executor.",
    )
    options_group.add_argument(
        "--conf",
        "-c",
        metavar="PROP=VALUE",
        type=str,
        nargs="*",
        help="Arbitrary Spark configuration property.",
    )
    options_group.add_argument(
        "--properties-file",
        metavar="FILE",
        type=str,
        action="deprecated",
        help="Path to a file from which to load extra properties. If not specified, this will look for conf/spark-defaults.conf.",
    )
    options_group.add_argument(
        "--driver-memory",
        metavar="MEM",
        type=str,
        action="deprecated",
        help="Memory for driver (e.g. 1000M, 2G) (Default: 1024M).",
    )
    options_group.add_argument(
        "--driver-java-options",
        type=str,
        action="experimental",
        help="Extra Java options to pass to the driver.",
    )
    options_group.add_argument(
        "--driver-library-path",
        type=str,
        action="experimental",
        help="Extra library path entries to pass to the driver.",
    )
    options_group.add_argument(
        "--driver-class-path",
        type=str,
        action="experimental",
        help="Extra class path entries to pass to the driver. Note that jars added with --jars are automatically included in the classpath.",
    )
    options_group.add_argument(
        "--executor-memory",
        metavar="MEM",
        type=str,
        action="deprecated",
        help="Memory per executor (e.g. 1000M, 2G) (Default: 1G).",
    )
    options_group.add_argument(
        "--proxy-user",
        type=str,
        action="deprecated",
        help="User to impersonate when submitting the application. This argument does not work with --principal / --keytab.",
    )
    options_group.add_argument(
        "--help",
        "-h",
        action="help",
        help="Show this help message and exit.",
    )
    options_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print additional debug output.",
    )
    options_group.add_argument(
        "--version",
        action="store_true",
        help="Print the version of current Spark.",
    )
    spark_connect_group.add_argument(
        "--remote",
        metavar="CONNECT_URL",
        type=str,
        action="deprecated",
        help="URL to connect to the server for Spark Connect, e.g., sc://host:port (default: sc://localhost:15002). --master and --deploy-mode cannot be set together with this option. This option is experimental, and might change between minor releases.",
    )
    cluster_deploy_group.add_argument(
        "--driver-cores",
        metavar="NUM",
        type=str,
        action="deprecated",
        help="Number of cores used by the driver, only in cluster mode (Default: 1).",
    )
    spark_standalone_or_mesos_cluster_group.add_argument(
        "--supervise",
        action="deprecated",
        help="If given, restart the driver on failure.",
    )
    k8s_group.add_argument(
        "--kill",
        metavar="SUBMISSION_ID",
        type=str,
        action="deprecated",
        help="If given, kills the driver specified.",
    )
    k8s_group.add_argument(
        "--status",
        metavar="SUBMISSION_ID",
        type=str,
        action="deprecated",
        help="If given, requests the status of the driver specified.",
    )
    spark_standalone_mesos_group.add_argument(
        "--total-executor-cores",
        metavar="NUM",
        type=str,
        action="deprecated",
        help="Total cores for all executors.",
    )
    spark_standalone_yarn_group.add_argument(
        "--executor-cores",
        metavar="NUM",
        type=str,
        action="deprecated",
        help="Number of cores per executor. (Default: 1 in YARN mode, or all available cores on the worker in standalone mode).",
    )
    spark_yarn_k8s_group.add_argument(
        "--num-executors",
        metavar="NUM",
        type=str,
        action="deprecated",
        help="Number of executors to launch (Default: 2).\nIf dynamic allocation is enabled, the initial number of executors will be at least NUM.",
    )
    spark_yarn_k8s_group.add_argument(
        "--principal",
        metavar="PRINCIPAL",
        type=str,
        action="deprecated",
        help="Principal to be used to login to KDC.",
    )
    spark_yarn_k8s_group.add_argument(
        "--keytab",
        metavar="KEYTAB",
        type=str,
        action="deprecated",
        help="The full path to the file that contains the keytab for the principal specified.",
    )
    spark_yarn_group.add_argument(
        "--queue",
        metavar="QUEUE_NAME",
        type=str,
        action="deprecated",
        help="The YARN queue to submit to (Default: 'default').",
    )

    # snowflake config validation functions start here
    def snowflake_stage_str(value: str) -> str:
        if not value.startswith("@"):
            raise argparse.ArgumentTypeError(
                "The --snowflake-stage argument must start with '@', e.g., '@my_stage'."
            )
        return value

    def validate_log_lines_count(value: str) -> int:
        try:
            int_value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid value '{value}' for --number-of-most-recent-log-lines. Must be an integer."
            )

        if int_value == -1 or int_value > 0:
            return int_value
        else:
            raise argparse.ArgumentTypeError(
                f"Invalid value '{int_value}' for --number-of-most-recent-log-lines. "
                "Valid values are positive integers greater than 0 or -1 (for all logs)."
            )

    snowflake_configs_group.add_argument(
        "--snowpark-connect-version",
        metavar="SNOWPARK_CONNECT_VERSION",
        type=str,
        help="Version for Snowpark Connect server and client images (default: latest). Accepts version in the form of `x.y.z` or `x.y` (points to latest patch version of x.y)",
    )
    snowflake_configs_group.add_argument(
        "--scala-version",
        metavar="SCALA_VERSION",
        type=str,
        default="2.12",
        choices=["2.12", "2.13"],
        help="Scala binary version for Scala/Java workloads (default: 2.12). Accepts 2.12 or 2.13.",
    )
    snowflake_configs_group.add_argument(
        "--account",
        metavar="SNOWFLAKE_ACCOUNT",
        type=str,
        help="Snowflake account to be used. Overrides the account in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--user",
        metavar="SNOWFLAKE_USER",
        type=str,
        help="Snowflake user to be used. Overrides the user in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--authenticator",
        metavar="SNOWFLAKE_AUTHENTICATOR",
        type=str,
        help="Authenticator for snowflake login. OAUTH, SNOWFLAKE_JWT, USERNAME_PASSWORD_MFA are supported. Overrides the authenticator in the connections.toml file if specified. If not specified, defaults to user password authenticator.",
    )
    snowflake_configs_group.add_argument(
        "--private-key-file",
        metavar="PRIVATE_KEY_FILE",
        type=str,
        help="Private key file path. Overrides the private_key_file in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--private-key-file-pwd",
        metavar="PRIVATE_KEY_PASSPHRASE",
        type=str,
        help="Private key passphrase. Overrides the private_key_file_pwd in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--token",
        metavar="SNOWFLAKE_TOKEN",
        type=str,
        help="OAuth token. Overrides the token in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--token-file-path",
        metavar="SNOWFLAKE_TOKEN_FILE_PATH",
        type=str,
        help="Path to a file containing the OAuth token for Snowflake. Overrides the token file path in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--password",
        metavar="SNOWFLAKE_PASSWORD",
        type=str,
        help="Password for snowflake user. Overrides the password in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--role",
        metavar="SNOWFLAKE_ROLE",
        type=str,
        help="Snowflake role to be used. Overrides the role in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--host",
        metavar="SNOWFLAKE_HOST",
        type=str,
        help="Host for snowflake deployment. Overrides the host in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--port",
        metavar="SNOWFLAKE_PORT",
        type=int,
        help="Port for snowflake deployment. Overrides the port in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--database",
        metavar="SNOWFLAKE_DATABASE_NAME",
        type=str,
        help="Snowflake database to be used in the session. Overrides the database in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--schema",
        metavar="SNOWFLAKE_SCHEMA_NAME",
        type=str,
        help="Snowflake schema to be used in the session. Overrides the schema in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--warehouse",
        metavar="SNOWFLAKE_WAREHOUSE_NAME",
        type=str,
        help="Snowflake warehouse to be used in the session. Overrides the warehouse in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--compute-pool",
        metavar="SNOWFLAKE_COMPUTE_POOL",
        type=str,
        help="Snowflake compute pool for running provided workload. Overrides the compute pool in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--comment",
        metavar="COMMENT",
        type=str,
        help="A message associated with the workload. Can be used to identify the workload in Snowflake.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-stage",
        metavar="SNOWFLAKE_STAGE",
        type=snowflake_stage_str,
        help="Snowflake stage, where workload files are uploaded.",
    )
    snowflake_configs_group.add_argument(
        "--external-access-integrations",
        metavar="SNOWFLAKE_EXTERNAL_ACCESS_INTEGRATIONS",
        type=str,
        help="Comma-separated list of Snowflake External Acccess Integrations required by the workload.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-log-level",
        metavar="SNOWFLAKE_LOG_LEVEL",
        type=str,
        choices=["INFO", "ERROR", "NONE"],
        help="Log level for Snowflake event table. ['INFO', 'ERROR', 'NONE'] (Default: INFO).",
    )
    # TODO: need a check for invalid name, e.g. should use underscore, not dash.
    snowflake_configs_group.add_argument(
        "--snowflake-workload-name",
        metavar="SNOWFLAKE_WORKLOAD_NAME",
        type=str,
        help="Base name for the workload to be run in Snowflake. "
        "A UTC timestamp (YYMMDD_HHMMSS) will be automatically appended to ensure uniqueness. "
        "Example: 'my_job' becomes 'MY_JOB_241112_143025'. "
        "When used with --list-workloads, acts as a prefix filter.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-connection-name",
        metavar="SNOWFLAKE_CONNECTION_NAME",
        type=str,
        default=None,
        help="Name of the connection in connections.toml file to use as base configuration. Command-line arguments will override any values from connections.toml.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-show-error-trace",
        action="store_true",
        help="Show error traceback in server logs (file paths are sanitized with placeholders). Default: false - no tracebacks shown.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-disable-otel-telemetry",
        action="store_true",
        default=False,
        help="Disable OpenTelemetry traces for Snowpark operations. Default: false - telemetry enabled.",
    )
    snowflake_configs_group.add_argument(
        "--workload-status",
        action="store_true",
        help="Print the detailed status of the workload.",
    )
    snowflake_configs_group.add_argument(
        "--display-logs",
        action="store_true",
        help="Whether to print application logs to console when --workload-status is specified.",
    )
    snowflake_configs_group.add_argument(
        "--number-of-most-recent-log-lines",
        metavar="NUMBER_OF_MOST_RECENT_LOG_LINES",
        type=validate_log_lines_count,
        default=100,
        help="Specifies the number of recent log lines to retrieve when --display-logs is enabled. Default: 100. Use -1 to fetch all available logs. Note: Fetching all logs (-1) may result in a slight delay in retrieving the most recent entries.",
    )
    snowflake_configs_group.add_argument(
        "--kill-workload",
        action="store_true",
        help="Adds tag to terminate the workload given by --workload-name.",
    )
    snowflake_configs_group.add_argument(
        "--list-workloads-with-name",
        metavar="PREFIX",
        type=str,
        default=None,  # Explicitly set default to None
        help="List all workloads in the compute pool with the specified name prefix (required). "
        "Cannot be used with any other operations (file submission, --workload-status, --kill-workload, etc.). "
        "Example: --list-workloads-with-name MY_JOB lists all workloads starting with 'MY_JOB'.",
    )
    snowflake_configs_group.add_argument(
        "--wait-for-completion",
        action="store_true",
        help="In cluster mode, when specified, run the workload in blocking mode and wait for completion. Can also be used with --workload-status to wait for an existing workload to complete.",
    )
    snowflake_configs_group.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Raise an exception if the workload fails. Only used when --wait-for-completion is specified.",
    )
    snowflake_configs_group.add_argument(
        "--requirements-file",
        metavar="REQUIREMENTS_FILE",
        type=str,
        help="Path to a requirements.txt file containing Python package dependencies to install before running the workload. Requires external access integration for PyPI.",
    )
    snowflake_configs_group.add_argument(
        "--wheel-files",
        metavar="WHEEL_FILES",
        type=str,
        help="Comma-separated list of .whl files to install before running the Python workload. Used for private dependencies not available on PyPI.",
    )
    snowflake_configs_group.add_argument(
        "--init-script",
        metavar="INIT_SCRIPT",
        type=str,
        help="Path to a shell script (.sh) to execute before running the Python workload. Used for system-level dependencies and configuration.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-grpc-max-message-size",
        metavar="SNOWFLAKE_GRPC_MAX_MESSAGE_SIZE",
        type=int,
        help="Maximum message size for gRPC communication in Snowpark Connect for Spark.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-grpc-max-metadata-size",
        metavar="SNOWFLAKE_GRPC_MAX_METADATA_SIZE",
        type=int,
        help="Maximum metadata size for gRPC communication in Snowpark Connect for Spark.",
    )
    snowflake_configs_group.add_argument(
        "--enable-local-file-access",
        action="store_true",
        help=f"Enable server access to local files in {SHARED_VOLUME_MOUNT_PATH} in the client environment.",
    )
    snowflake_configs_group.add_argument(
        "--workload-memory",
        metavar="WORKLOAD_MEMORY",
        type=str,
        help="Memory allocated to the workload (e.g., 1000M, 2G). (Default: 4G).",
    )
    snowflake_configs_group.add_argument(
        "--workload-cpus",
        metavar="WORKLOAD_CPUS",
        type=float,
        help="Number of virtual cpus allocated to the workload. (Default: 0.5).",
    )
    snowflake_configs_group.add_argument(
        "--workload-gpus",
        metavar="WORKLOAD_GPUS",
        type=int,
        help="Number of GPUs allocated to the workload (Default: 0). The compute infra must have GPU resources available.",
    )
    parser.add_argument(
        "filename",
        metavar="FILE",
        nargs="?",
        type=str,
        help=argparse.SUPPRESS,
    )

    args, unknown_args = parser.parse_known_args(args)
    args.app_arguments = unknown_args

    return args, [action.dest for action in snowflake_configs_group._group_actions]


# Cache for parser metadata to avoid rebuilding parser multiple times
_parser_cache: dict[str, Any] | None = None


def _get_parser_cache() -> dict[str, Any]:
    """Get cached parser metadata (config keys and defaults)."""
    global _parser_cache
    if _parser_cache is None:
        args, config_keys = init_args([])
        # Extract defaults from parsed args (excluding internal attributes)
        defaults = {
            k: v
            for k, v in vars(args).items()
            if not k.startswith("_") and k != "app_arguments"
        }
        _parser_cache = {
            "config_keys": config_keys,
            "defaults": defaults,
        }
    return _parser_cache


def get_snowflake_config_keys() -> list[str]:
    """Get the list of Snowflake-specific config keys.

    These are the argument destinations from the 'Snowflake specific configs'
    argument group. This list is used to filter out Snowflake-specific options
    when generating spark-submit commands.

    Returns:
        List of Snowflake config key names (e.g., ['account', 'user', 'compute_pool', ...])
    """
    return _get_parser_cache()["config_keys"]


def get_parser_defaults() -> dict[str, Any]:
    """Get the default values for all parser arguments.

    These are the default values that would be set when parsing with no arguments.
    Used by the Python API to ensure argparse.Namespace objects have all expected
    attributes with proper defaults.

    Returns:
        Dictionary mapping argument names to their default values.
    """
    return _get_parser_cache()["defaults"]


def generate_spark_submit_cmd(
    args: argparse.Namespace,
    snowflake_config_keys: list[str],
    entrypoint_arg: str = "spark-submit",
) -> list[str]:
    args_for_spark = [entrypoint_arg]

    deprecated_args = getattr(args, "_deprecated_args", set())

    for k, v in vars(args).items():
        if v is not None and k not in [
            "filename",
            "verbose",
            "version",
            "app_arguments",
            "_deprecated_args",  # Exclude our internal marker
        ] + snowflake_config_keys + list(
            deprecated_args
        ):  # Exclude deprecated arguments
            args_for_spark.append(f"--{k.replace('_', '-')}")
            if isinstance(v, list):
                args_for_spark.append(",".join(str(item) for item in v))
            else:
                args_for_spark.append(str(v))
    if args.verbose:
        args_for_spark.append("--verbose")
    if args.version:
        args_for_spark.append("--version")

    args_for_spark.extend(["--remote", "sc://localhost:15002"])

    args_for_spark.append(args.filename)
    args_for_spark.extend(args.app_arguments)
    return args_for_spark


def run():

    setup_logging(logging.INFO)

    args, snowflake_config_keys = init_args()

    if args.verbose:
        setup_logging(logging.DEBUG)

    # Check that exactly one of the main operations is specified
    operations_count = sum(
        [
            args.workload_status,
            args.kill_workload,
            args.list_workloads_with_name is not None,  # Check if flag was used
            bool(args.filename),
        ]
    )

    if operations_count != 1:
        error_msg = "You must specify exactly one operation at a time: 1) either a Python file to run, 2) --workload-status, 3) --kill-workload, or 4) --list-workloads-with-name"
        logger.error(error_msg)
        return StatusInfo(
            exit_code=1,
            error=error_msg,
        )

    # Special validation for --list-workloads-with-name
    if args.list_workloads_with_name is not None:
        # Cannot be combined with other operations
        if args.wait_for_completion:
            error_msg = (
                "--list-workloads-with-name cannot be used with --wait-for-completion"
            )
            logger.error(error_msg)
            return StatusInfo(exit_code=1, error=error_msg)
        if args.display_logs:
            error_msg = "--list-workloads-with-name cannot be used with --display-logs"
            logger.error(error_msg)
            return StatusInfo(exit_code=1, error=error_msg)

    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
    )

    if args.workload_status:
        result = job_runner.describe()
        if args.wait_for_completion and not result.terminated:
            result = job_runner.wait_for_service_completion(
                args.snowflake_workload_name
            )
        return result

    elif args.kill_workload:
        return job_runner.end_workload()

    elif args.list_workloads_with_name is not None:
        # List workloads with the specified prefix
        return job_runner.list_workloads(prefix=args.list_workloads_with_name)

    else:
        return job_runner.run()


def runner_wrapper(test_mode=False):
    logger.debug("Runner starts.")

    result = run()
    exit_status = result.exit_code
    # send the exit status in lower byte as 0/1 flag
    if exit_status != 0:
        logger.error("Unexpected Exit: non-zero exit code.")
        exit_status = 1
    if test_mode:
        return result
    else:
        sys.exit(exit_status)


if __name__ == "__main__":
    runner_wrapper()
