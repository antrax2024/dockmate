import os
import sys
import click
from .config import AppConfig, FileSource, createConfigFile
from .constants import APP_NAME, APP_VERSION, DEFAULT_CONFIG_FILE
from .kernel import monitorContainers


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(exists=False, dir_okay=False),
    default=DEFAULT_CONFIG_FILE,
    help=f"Specifies the file config.yaml file (default: {DEFAULT_CONFIG_FILE})",
)
def cli(config_file) -> None:
    """Monitors a list of Docker containers and upgrades them when new images are released."""
    click.echo(message=f"{APP_NAME} v{APP_VERSION}\n")

    if config_file:
        # determine if file exists
        if not os.path.exists(config_file):
            click.echo(
                message=f"Configuration file does not exist: {config_file}. Creating a new one."
            )
            # create the directory if it does not exist
            dir_name = os.path.dirname(config_file)
            try:
                os.makedirs(
                    name=dir_name,
                    exist_ok=True,
                )
            except Exception as e:
                click.echo(message=f"Error creating directory {dir_name}: {e}")
                sys.exit(1)

            if dir_name:
                os.makedirs(
                    name=dir_name,
                    exist_ok=True,
                )
            # create the config file
            createConfigFile(configFile=config_file)
        else:
            click.echo(message=f"Using config from: {config_file}")

    AppConfig.CONFIG_SOURCES = FileSource(file=config_file)
    appConfig = AppConfig()
    monitorContainers(
        ctToWatch=appConfig.containers,
        time_main_loop=appConfig.time_main_loop,
    )
