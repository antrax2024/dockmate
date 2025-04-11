import docker
from dotenv import load_dotenv
import os
from rich.console import Console

load_dotenv()  # Load environment variables from .env file
cl = Console()
client: docker.DockerClient = docker.from_env()
ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH").split(",")


def main() -> None:
    containers = client.containers.list()
    for container in containers:
        cl.print(f"[bold yellow]ID[/bold yellow]: {container.id}")
        cl.print(f"[bold yellow]Name:[/bold yellow] {container.name}")
        if container.name in ctToWatch:
            cl.print("[bold yellow]Watch: [/bold yellow] [green]True[/green]")
            # Aqui tenho um container que precisa ser monitorado e atualizado
            checkForNewVersion(container.image.tags[0])
            # Aqui tenho que checar se há uma nova versão do container
            # Se houver, atualizar o container
            # Se não houver, continuar monitorando
        else:
            cl.print("[bold yellow]Watch: [/bold yellow] [red]False[/red]")

        cl.print(
            f"[bold yellow]Image:[/bold yellow] {container.image.tags[0] if container.image.tags else 'No tags'}"
        )
        cl.print(f"[bold yellow]Status:[/bold yellow]  {container.status}")

        cl.print(f"[bold yellow]Created:[/bold yellow] {container.attrs['Created']}")
        cl.print(f"[bold yellow]Ports:[/bold yellow] {container.ports}")
        cl.print("=" * 40)


def checkForNewVersion(imageName):
    local_image = client.images.get(imageName)

    local_digest = local_image.attrs["RepoDigests"][0].split("@")[1]
    cl.print(f"[bold yellow]Local Digest[/bold yellow]: {local_digest}")

    latest_image = client.images.pull(imageName)
    latest_digest = latest_image.attrs["RepoDigests"][0].split("@")[1]
    cl.print(f"[bold yellow]Latest Digest[/bold yellow]: {latest_digest}")
    if latest_digest != local_digest:
        cl.print(
            "[bold yellow]Version:[/bold yellow] [green]new version available![/green]"
        )
        return True
    else:
        cl.print(
            "[bold yellow]Version:[/bold yellow] [gray]NO new version available![/gray]"
        )
        return False


if __name__ == "__main__":
    main()
    # for ct in ctToWatch.split(",") if isinstance(ctToWatch, str) else []:
    #     cl.print(f"Checking container: {ct}")
    # checkForNewVersion("homepage")
