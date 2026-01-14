import os

from setuptools import find_namespace_packages, setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# read the version
VERSION = "1.8.0"


setup(
    name="snowpark-submit",
    version=VERSION,
    description="Snowpark Submit",
    long_description="The snowpark-submit is designed for running non-interactive, batch-oriented Spark workloads directly on Snowflake's infrastructure using familiar Spark semantics. It eliminates the need to manage a dedicated Spark cluster while allowing you to maintain your existing Spark development workflows. This tool is ideal for submitting production-ready Spark applications—such as ETL pipelines, and scheduled data transformations—using a simple CLI interface.",
    long_description_content_type="text/markdown",
    author="Snowflake, Inc",
    license="Apache License, Version 2.0",
    license_files=["LICENSE.txt"],
    packages=find_namespace_packages(
        where="src",
        exclude=[
            "snowflake.snowpark_submit.example_spark_applications*",
            "snowflake.snowpark_submit.cluster_mode.spark_classic*",
        ],
    ),
    package_data={
        "snowflake.snowpark_submit": [
            "cluster_mode/spark_connect/resources/spcs_spec.template.yaml",
        ],
    },
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "snowpark-submit=snowflake.snowpark_submit.snowpark_submit:runner_wrapper",
        ],
    },
    python_requires=">=3.10,<3.13",
    install_requires=[
        "snowflake-snowpark-python>=1.32.0",
        "pyyaml>=6.0.2,<7.0.0",
    ],
)
