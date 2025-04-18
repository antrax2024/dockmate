import os
from dotenv import load_dotenv
from rich.console import Console
from typing import Any, Optional
import docker
import docker.errors
import docker.models.containers
import time

load_dotenv()  # Load environment variables from .env file
cl = Console()

ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH", "").split(",")


def recreateContainer(
    container: docker.models.containers.Container,
) -> Optional[docker.models.containers.Container]:
    """
    Recreates a Docker container with the latest image version and removes the old image.

    Args:
        container: The Docker container object to recreate.

    Returns:
        The new container object if successful, None otherwise.
    """
    client: docker.DockerClient = docker.from_env()
    name = container.name  # Initialize name at the beginning to avoid UnboundLocalError
    try:
        # 1. Save necessary configurations
        container_attrs = container.attrs
        config = container_attrs["Config"]
        host_config = container_attrs["HostConfig"]
        image_name = config["Image"]
        old_image_id = (
            container.image.id if container.image else None
        )  # Store the old image ID for later removal
        command = config.get("Cmd")
        environment = config.get("Env")
        ports = host_config.get("PortBindings")
        volumes = host_config.get("Binds")
        network_mode = host_config.get("NetworkMode")
        restart_policy = host_config.get("RestartPolicy")

        cl.log(f"Recreating container [bold cyan]{name}[/bold cyan]...")
        cl.log(f"  Image: {image_name}")

        # 2. Stop and remove the container
        cl.log(f"  Stopping container [bold cyan]{name}[/bold cyan]...")
        container.stop()
        cl.log(f"  Removing container [bold cyan]{name}[/bold cyan]...")
        container.remove()
        cl.log(f"  Container [bold cyan]{name}[/bold cyan] stopped and removed.")

        # 3. Pull the new image
        cl.log(f"  Pulling latest image [bold yellow]{image_name}[/bold yellow]...")
        try:
            client.images.pull(image_name)
            cl.log(
                f"  Image [bold yellow]{image_name}[/bold yellow] pulled successfully."
            )
        except docker.errors.APIError as e:
            cl.log(f"[bold red]Error pulling image {image_name}: {e}[/bold red]")
            return None

        # 4. Start the new container
        cl.log(
            f"  Creating and starting new container [bold cyan]{name}[/bold cyan]..."
        )
        try:
            new_container = client.containers.run(
                image=image_name,
                command=command,
                environment=environment,
                ports=ports,
                volumes=volumes,
                name=name,
                network_mode=network_mode,
                restart_policy=restart_policy,
                detach=True,  # Run in the background
            )
            cl.log(
                f"  New container [bold cyan]{name}[/bold cyan] started successfully (ID: {new_container.short_id})."
            )

            # 5. Remove the old image if it exists
            try:
                if old_image_id:
                    cl.log(
                        f"  Removing old image [bold yellow]{old_image_id[:12]}[/bold yellow]..."
                    )
                    client.images.remove(old_image_id, force=False)
                    cl.log(
                        f"  Old image [bold yellow]{old_image_id[:12]}[/bold yellow] removed successfully."
                    )
            except docker.errors.APIError as e:
                cl.log(
                    f"  [bold yellow]Warning: Could not remove old image: {e}[/bold yellow]"
                )
                # Continue even if image removal fails

            # 6. Return the new container
            return new_container
        except docker.errors.APIError as e:
            cl.log(f"[bold red]Error creating container {name}: {e}[/bold red]")
            # Attempt to fetch the container if it was created but run failed
            try:
                if name is not None:
                    return client.containers.get(name)
                return None
            except docker.errors.NotFound:
                return None

    except docker.errors.APIError as e:
        cl.log(f"[bold red]API Error during recreation of {name}: {e}[/bold red]")
        return None
    except Exception as e:
        cl.log(
            f"[bold red]Unexpected error during recreation of {name}: {e}[/bold red]"
        )
        return None


def printLine() -> None:
    cl.print("-" * 80, style="cyan")


def getContainers() -> Any:
    client: docker.DockerClient = docker.from_env()
    containers = client.containers.list()
    return containers


def checkForNewVersion(imageName: str) -> bool:
    client: docker.DockerClient = docker.from_env()
    local_image = client.images.get(imageName)

    local_digest = local_image.attrs["RepoDigests"][0].split("@")[1]
    # cl.log(f"[bold yellow]Local Digest[/bold yellow]: {local_digest}")

    latest_image = client.images.pull(imageName)
    latest_digest = latest_image.attrs["RepoDigests"][0].split("@")[1]
    # cl.log(f"[bold yellow]Latest Digest[/bold yellow]: {latest_digest}")
    if latest_digest != local_digest:
        cl.log("[bold yellow]Version:[/bold yellow] [red]NEW version available![/red]")
        return True
    else:
        cl.log(
            "[bold yellow]Version:[/bold yellow] [green]NO new version available![/green]"
        )
        return False


def monitorContainers(ctToWatch: list[str], time_main_loop: int) -> None:
    try:
        while True:
            with cl.status(status="Working..."):  # Start a status bar
                containers = getContainers()
                for container in containers:
                    if container.name in ctToWatch:
                        printLine()
                        cl.log(f"[bold yellow]Checking:[/bold yellow] {container.name}")
                        cl.log("[bold yellow]Watch: [/bold yellow] [green]True[/green]")
                        if checkForNewVersion(container.image.tags[0]):
                            cl.log(
                                f"[bold yellow]Action: [/bold yellow] [green]Recreating container[/green] [ {container.name}]"
                            )
                            recreateContainer(container=container)
                            cl.log("[[bold green]OK[/ bold green]]")

                        printLine()

                        cl.log("waiting for next check...")

                    # time.sleep(5)

            cl.log(f"\n\nChecking again in {time_main_loop} seconds...")
            time.sleep(time_main_loop)
    except KeyboardInterrupt:
        cl.log("[bold red]Program interrupted by user. Exiting...[/bold red]")
        return


if __name__ == "__main__":
    client = docker.from_env()
    container = client.containers.get("homepage")
    recreateContainer(container)
