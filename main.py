import docker
from dotenv import load_dotenv
import os
from rich.console import Console

load_dotenv()  # Load environment variables from .env file
cl = Console()

ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH").split(",")


def main() -> None:
    client: docker.DockerClient = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        cl.print(f"[bold yellow]ID[/bold yellow]: {container.id}")
        cl.print(f"[bold yellow]Name:[/bold yellow] {container.name}")
        if container.name in ctToWatch:
            cl.print("[bold yellow]Watch: [/bold yellow] [green]True[/green]")
        else:
            cl.print("[bold yellow]Watch: [/bold yellow] [red]False[/red]")

        cl.print(
            f"[bold yellow]Image:[/bold yellow] {container.image.tags[0] if container.image.tags else 'No tags'}"
        )
        cl.print(f"[bold yellow]Status:[/bold yellow]  {container.status}")

        cl.print(f"[bold yellow]Created:[/bold yellow] {container.attrs['Created']}")
        cl.print(f"[bold yellow]Ports:[/bold yellow] {container.ports}")
        cl.print("=" * 40)


def checkForNewVersion(image: docker.models.images.Image):
    pass


if __name__ == "__main__":
    main()
    # for ct in ctToWatch.split(",") if isinstance(ctToWatch, str) else []:
    #     cl.print(f"Checking container: {ct}")
    # checkForNewVersion("homepage")
