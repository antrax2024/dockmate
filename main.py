import docker
from dotenv import load_dotenv
import os
from rich.console import Console

load_dotenv()  # Load environment variables from .env file
cl = Console()

ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH")


def main() -> None:
    client: docker.DockerClient = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        cl.print(f"ID: {container.id}")
        cl.print(f"Name: {container.name}")
        cl.print(
            f"Image: {container.image.tags[0] if container.image.tags else 'No tags'}"
        )
        cl.print(f"Status: {container.status}")

        cl.print(f"Created: {container.attrs['Created']}")
        cl.print(f"Ports: {container.ports}")
        cl.print("=" * 40)


def checkForNewVersion(image: docker.models.images.Image):
    pass


if __name__ == "__main__":
    main()
    # for ct in ctToWatch.split(",") if isinstance(ctToWatch, str) else []:
    #     cl.print(f"Checking container: {ct}")
    # checkForNewVersion("homepage")
