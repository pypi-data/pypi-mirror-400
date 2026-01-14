#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from abc import ABC, abstractmethod
from pathlib import Path


class BaseFilePath(ABC):
    """
    Abstract base class for file path handling.
    """

    def __init__(self, client_path: str, base_path: str = "/tmp/") -> None:
        self.client_path_str = client_path
        self.base_path = base_path

    @staticmethod
    def parse_file_path(
        client_path: str, local_file_base_path: str, stage_file_base_path: str
    ) -> "BaseFilePath":
        match client_path:
            case _ if client_path.startswith("@"):
                return SnowflakeStageFilePath(client_path, stage_file_base_path)
            case _ if client_path.lower().startswith("s3://"):
                # Placeholder for future cloud storage path handling
                raise NotImplementedError(
                    f"S3 file path {client_path} is not yet supported."
                )
            case _ if client_path.lower().startswith(("wasbs://", "wasb://")):
                # Placeholder for future cloud storage path handling
                raise NotImplementedError(
                    f"Azure file path {client_path} is not yet supported."
                )
            case _ if client_path.lower().startswith("gs://"):
                # Placeholder for future cloud storage path handling
                raise NotImplementedError(
                    f"GCP file path {client_path} is not yet supported."
                )
            case _ if "://" in client_path and not client_path.startswith("file://"):
                raise NotImplementedError(
                    f"file path {client_path} is not yet supported."
                )
            case _:
                return LocalFilePath(client_path, local_file_base_path)

    @abstractmethod
    def get_file_path_in_container(self) -> str:
        """
        Abstract method to get the file path in docker container.
        """
        pass


class LocalFilePath(BaseFilePath):
    """
    Class for handling local file paths.
    """

    def __init__(self, client_path: str, docker_base_path: str = "/tmp/") -> None:
        super().__init__(client_path, docker_base_path)
        # Handle file:// protocol prefix
        if self.client_path_str.startswith("file://"):
            self.path = Path(client_path[7:])
        else:
            self.path = Path(self.client_path_str)

    def get_file_path_in_container(self) -> str:
        """
        Returns the local file path.

        Local files are all copied to the docker_base_path finally.
        """
        return self.base_path + self.path.name


class SnowflakeStageFilePath(BaseFilePath):
    """
    Class for handling Snowflake stage file paths.
    """

    def __init__(self, client_path: str, docker_base_path: str = "/tmp/") -> None:
        super().__init__(client_path, docker_base_path)
        self.path = self.client_path_str[self.client_path_str.find("/") + 1 :]

    def get_file_path_in_container(self) -> str:
        return self.base_path + self.path
