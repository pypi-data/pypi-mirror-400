#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""
Utility functions for handling Snowflake connections in Airflow operators.
"""

from typing import Dict, Optional

from airflow.hooks.base import BaseHook


def merge_airflow_connection_config(
    connections_config: Dict, snowflake_conn_id: Optional[str]
) -> Dict:
    """
    Merge Airflow connection details into connections_config without overwriting existing values.

    This function retrieves connection details from Airflow's connection management system
    and merges them into the provided connections_config dictionary. Existing keys in
    connections_config are never overwritten, allowing for selective overrides.

    :param connections_config: Dictionary containing Snowflake connection parameters.
        Existing values will not be overwritten.
    :param snowflake_conn_id: Airflow connection ID for Snowflake. If None, no merging occurs.
    :return: Updated connections_config dictionary with merged connection details.

    Basic connection fields that are merged:
    - host: Snowflake host URL
    - user: Username for authentication
    - password: Password for authentication
    - schema: Default schema name
    - port: Connection port (typically 443 for Snowflake)

    Extra configuration fields from connection.extra_dejson:
    - account: Snowflake account identifier
    - role: Default role to use
    - warehouse: Default warehouse name
    - database: Default database name
    - compute_pool: Snowpark Container Services compute pool
    - Any other custom fields stored in the connection's extra configuration

    Example usage:
        # Start with minimal config
        config = {'compute_pool': 'my_special_pool'}

        # Merge from Airflow connection 'snowflake_prod'
        merged_config = merge_airflow_connection_config(config, 'snowflake_prod')

        # Result: config now contains all connection details from 'snowflake_prod'
        # but 'compute_pool' retains its original value 'my_special_pool'

    Non-overwriting behavior:
        config = {'host': 'override.snowflakecomputing.com', 'user': 'custom_user'}
        merged = merge_airflow_connection_config(config, 'snowflake_conn')

        # 'host' and 'user' keep their original values
        # Other fields (password, role, warehouse, etc.) are added from the connection
    """
    # Return early if no connection ID provided
    if not snowflake_conn_id and not connections_config:
        raise ValueError(
            "connections_config and snowflake_conn_id cannot both be empty."
        )
    if not snowflake_conn_id:
        return connections_config

    # Get the Airflow connection
    snowflake_conn = BaseHook.get_connection(snowflake_conn_id)

    # Define basic connection field mappings
    # Maps connections_config keys to connection object attributes
    connection_mapping = {
        "host": snowflake_conn.host,
        "user": snowflake_conn.login,
        "password": snowflake_conn.password,
        "schema": snowflake_conn.schema,
        "port": snowflake_conn.port,
    }

    if connections_config is None:
        connections_config = {}

    # Merge basic connection details if not already present in connections_config
    for key, value in connection_mapping.items():
        if value is not None and key not in connections_config:
            connections_config[key] = value

    # Extract and merge extra configuration from connection.extra_dejson
    # This includes fields like account, role, warehouse, database, compute_pool, etc.
    extra_config = snowflake_conn.extra_dejson
    for key, value in extra_config.items():
        if value is not None and key not in connections_config:
            connections_config[key] = value

    return connections_config


def validate_connection_config(
    connections_config: Dict, required_fields: Optional[list] = None
) -> None:
    """
    Validate that required connection configuration fields are present and not empty.

    :param connections_config: Dictionary containing connection configuration
    :param required_fields: List of required field names. If None, uses default required fields.
    :raises ValueError: If any required fields are missing or empty

    Example usage:
        config = {'account': 'my_account', 'host': 'my_host.snowflakecomputing.com'}

        # Validate with default required fields
        validate_connection_config(config)

        # Validate with custom required fields
        validate_connection_config(config, ['account', 'host', 'user', 'password'])
    """
    if required_fields is None:
        # Default required fields for Snowflake connections
        required_fields = ["account", "host", "compute_pool"]

    missing_fields = []
    for field in required_fields:
        if field not in connections_config or not connections_config[field]:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(
            f"Missing required Snowflake configuration parameters: {', '.join(missing_fields)}"
        )
