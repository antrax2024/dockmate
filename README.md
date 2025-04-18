# dockerautoupdate

**dockerautoupdate** is a Python application that monitors a list of specified Docker containers and automatically upgrades them when new images are released.

## Features

- Monitors specified Docker containers for available image updates.
- Automatically pulls the latest image and restarts the container with the new image.
- Configurable monitoring interval.
- Supports connection to local or remote Docker daemons.

## Installation

You can install **dockerautoupdate** using several methods:

### PyPI

Install the latest stable version from [PyPI](https://pypi.org/https:/):

```bash
pip install dockerautoupdate
```

or using uv:

```bash
uv pip install dockerautoupdate
```

### Docker Container (Recomended)

You can run **dockerautoupdate** as a Docker container. Pull the image from [Docker Hub](https://hub.docker.com/) (replace `yourusername` with the actual username or organization if applicable):

```bash
docker pull yourusername/dockerautoupdate:latest
```

To run the container, you need to mount the Docker socket and your configuration file:

```bash
docker run -d \
  --name dockerautoupdate \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /path/to/your/config.yaml:/root/.config/dockerautoupdate/config.yaml \
  yourusername/dockerautoupdate:latest
```

*Note: Ensure the path `/path/to/your/config.yaml` points to your actual configuration file on the host.*

### Arch User Repository (AUR)

If you are using an Arch-based Linux distribution, you can install dockerautoupdate from the AUR using an AUR helper like `yay` or `paru`:

```bash
yay -S dockerautoupdate
```

or

```bash
paru -S dockerautoupdate
```




## Command-Line Interface

The application uses `click` for its command-line interface.

```bash
dockerautoupdate [OPTIONS]
```

### Options

- `-h`, `--help`: Show the help message and exit.
- `-c`, `--config FILE`: Specifies the path to the `config.yaml` file.
  - Default: `~/.config/dockerautoupdate/config.yaml`
  - If the specified file does not exist, dockerautoupdate will create a default configuration file at that location.

## Configuration

dockerautoupdate uses a YAML file (`config.yaml`) for configuration.

### Default Location

By default, dockerautoupdate looks for the configuration file at: `~/.config/dockerautoupdate/config.yaml`

You can specify a different location using the `-c` or `--config` command-line option.

### Configuration Parameters

The `config.yaml` file contains the following parameters:

- `docker_host`: (String) The URL of the Docker daemon API endpoint.

  - Use `"unix:///var/run/docker.sock"` for the local Docker daemon via Unix socket.
  - Use `"tcp://hostname:port"` (e.g., `"tcp://192.168.1.100:2375"`) to connect to a remote Docker daemon.
  - *Example:* `docker_host: "tcp://192.168.1.16:2375"`
- `containers`: (List of Strings) A list of Docker container names that dockerautoupdate should monitor and update.

  - These names must match the actual names of your running containers.
  - *Example:* `containers: ["adguardhome", "homepage", "portainer"]`
- `time_main_loop`: (Integer) The interval in seconds between checks for container image updates.

  - The application will pause for this duration after completing a check cycle.
  - *Example:* `time_main_loop: 7200` (Check every 2 hours)

### Example `config.yaml`

```yaml
# docker-watch configuration file

# docker_host represents the Docker host URL used for communication with the Docker daemon.
# This allows the Docker client to connect to the Docker Engine, which could be local or remote.
# Example values include: "unix:///var/run/docker.sock" for local Unix socket connection
# or "tcp://hostname:port" for a remote Docker host.
docker_host: "tcp://192.168.1.16:2375" # Docker host URL

# containers: Docker containers that will be monitored by the application.
# This configuration defines the list of Docker containers that the application
# will track and monitor for status, resource usage, and other metrics.
containers: ["adguardhome", "homepage", "open-webui", "portainer"]

# time_main_loop: This parameter specifies the interval between each main loop iteration.
time_main_loop: 7200
```

## Usage

Once installed and configured, simply run the command:

```bash
dockerautoupdate
```

Or, if you need to specify a custom configuration file path:

```bash
dockerautoupdate --config /path/to/your/custom_config.yaml
```

dockerautoupdate will then start monitoring the specified containers according to the configuration.
