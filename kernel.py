import docker
from dotenv import load_dotenv
import os
from rich.console import Console

load_dotenv()  # Load environment variables from .env file
cl = Console()
client: docker.DockerClient = docker.from_env()
ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH").split(",")


def printLine():
    cl.print("-" * 80, style="cyan")


def getContainers():
    containers = client.containers.list()
    return containers


def checkForNewVersion(imageName):
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
