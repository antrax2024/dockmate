import os
import docker
from dotenv import load_dotenv
from rich.console import Console
from docker.models.containers import Container

load_dotenv()  # Load environment variables from .env file
cl = Console()
client: docker.DockerClient = docker.from_env()
ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH").split(",")


def printLine():
    cl.print("-" * 80, style="cyan")


def recreateContainer(container: Container) -> Container:
    """
    Recria um container usando a imagem mais recente disponível.

    Args:
        container: Objeto Container existente da biblioteca docker

    Returns:
        Container: Novo objeto Container criado
    """
    # Cliente Docker
    client = docker.from_env()

    # 1. Salvar configurações do container em variável local
    info = client.api.inspect_container(container.id)

    # Extrair informações essenciais
    image_name = info["Config"]["Image"]
    container_name = info["Name"].lstrip("/")

    # Coletar configurações relevantes
    config = {}

    # Comando
    if info["Config"]["Cmd"]:
        config["command"] = info["Config"]["Cmd"]

    # Entrypoint
    if info["Config"]["Entrypoint"]:
        config["entrypoint"] = info["Config"]["Entrypoint"]

    # Variáveis de ambiente
    if info["Config"]["Env"]:
        config["environment"] = info["Config"]["Env"]

    # Volumes
    if info["HostConfig"]["Binds"]:
        config["volumes"] = info["HostConfig"]["Binds"]

    # Mapeamento de portas
    if info["HostConfig"]["PortBindings"]:
        ports = {}
        for container_port, host_bindings in info["HostConfig"]["PortBindings"].items():
            if host_bindings:
                host_port = host_bindings[0]["HostPort"]
                ports[container_port] = host_port
        if ports:
            config["ports"] = ports

    # Configurações de rede
    if (
        "NetworkMode" in info["HostConfig"]
        and info["HostConfig"]["NetworkMode"] != "default"
    ):
        config["network_mode"] = info["HostConfig"]["NetworkMode"]

    # 2. Parar o container
    container.stop()

    # 3. Remover o container
    container.remove()

    # 4. Baixar a imagem mais recente
    client.images.pull(image_name)

    # 5. Criar e iniciar o novo container
    new_container = client.containers.create(
        image=image_name, name=container_name, detach=True, **config
    )

    new_container.start()

    return new_container


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


if __name__ == "__main__":
    container = client.containers.get("homepage")
    # cl.log(container.attrs)
    recreateContainer(container)
