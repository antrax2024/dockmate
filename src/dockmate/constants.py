# This is the version of the application.
import os


APP_VERSION = "0.1.7"
# This is the name of the application.
APP_NAME = "dockmate"

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.expanduser(path="~"), ".config", f"{APP_NAME}", "config.yaml"
)
