import os
from typing import Any
from confz import BaseConfig, FileSource
from .constants import APP_NAME


def createConfigFile(configFile: str) -> None:
    """
    Create the config file if it doesn't exist.
    """
    try:
        if not os.path.exists(configFile):
            dir_name = os.path.dirname(configFile)
            if dir_name:
                os.makedirs(
                    name=dir_name,
                    exist_ok=True,
                )
            with open(file=configFile, mode="w") as f:
                f.write(
                    """# docker-whatch configuration file

    # docker_host represents the Docker host URL used for communication with the Docker daemon.
    # This allows the Docker client to connect to the Docker Engine, which could be local or remote.
    # Example values include: "unix:///var/run/docker.sock" for local Unix socket connection
    # or "tcp://hostname:port" for a remote Docker host.
    docker_host: "tcp://127.0.0.1:2375"

    # containers: Docker containers that will be monitored by the application.
    # This configuration defines the list of Docker containers that the application
    # will track and monitor for status, resource usage, and other metrics.
    # ex: containers: ["container1", "container2"]
    containers: []

    # time_main_loop: This parameter specifies the interval between each main loop iteration.
    time_main_loop: 7200
    """
                )
    except Exception as e:
        print(f"Error creating config file: {e}")
        raise e


class AppConfig(BaseConfig):

    CONFIG_SOURCES = FileSource(
        file=os.path.join(
            os.path.expanduser(path="~"), ".config", f"{APP_NAME}", "config.yaml"
        )
    )

    docker_host: str
    containers: list[str]
    time_main_loop: int


if __name__ == "__main__":
    pass
