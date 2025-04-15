import os
from dotenv import load_dotenv
from rich.console import Console
import docker
from docker.types import Mount, NetworkingConfig, EndpointConfig
from docker.errors import NotFound, APIError
from typing import Optional

load_dotenv()  # Load environment variables from .env file
cl = Console()

ctToWatch: list[str] = os.environ.get("CONTAINERS_TO_WATCH").split(",")


def recreateContainer(
    container: docker.models.containers.Container,
) -> Optional[docker.models.containers.Container]:
    """
    Recria um container Docker usando a imagem mais recente disponível,
    preservando o máximo possível da configuração original.

    Args:
        container: Objeto Container existente da biblioteca docker.

    Returns:
        Container: Novo objeto Container criado ou None se ocorrer um erro.
    """
    client = docker.from_env()

    try:
        # 1. Salvar configurações do container usando o atributo .attrs
        original_attrs = container.attrs
        if not original_attrs:
            print(
                f"Error: Could not inspect container {container.id}."
            )  # Alternative feedback
            return None

        # Extrair informações essenciais
        config_data = original_attrs.get("Config", {})
        host_config_data = original_attrs.get("HostConfig", {})
        network_settings_data = original_attrs.get("NetworkSettings", {})

        image_name = config_data.get("Image")
        # Remove o SHA do ID da imagem, se presente
        if "@sha256:" in image_name:
            image_name = image_name.split("@sha256:")[0]

        container_name = original_attrs.get("Name", "").lstrip("/")

        if not image_name or not container_name:
            print(
                "Error: Could not extract image name or container name."
            )  # Alternative feedback
            return None

        # 2. Construir os argumentos para client.containers.create
        create_kwargs = {
            "image": image_name,
            "name": container_name,
            "detach": True,
            # --- Argumentos de Config ---
            "command": config_data.get("Cmd"),
            "entrypoint": config_data.get("Entrypoint"),
            "environment": config_data.get("Env"),
            "labels": config_data.get("Labels"),
            "working_dir": config_data.get("WorkingDir"),
            "user": config_data.get("User"),
            "hostname": config_data.get("Hostname"),
            "stop_signal": config_data.get("StopSignal"),
            "stdin_open": config_data.get("OpenStdin", False),
            "tty": config_data.get("Tty", False),
            "healthcheck": config_data.get("Healthcheck"),
        }

        # --- Argumentos de HostConfig ---
        host_config_dict = {
            "restart_policy": host_config_data.get("RestartPolicy"),
            "privileged": host_config_data.get("Privileged", False),
            "cap_add": host_config_data.get("CapAdd"),
            "cap_drop": host_config_data.get("CapDrop"),
            "security_opt": host_config_data.get("SecurityOpt"),
            "ulimits": host_config_data.get("Ulimits"),
            "log_config": host_config_data.get("LogConfig"),
            "dns": host_config_data.get("Dns"),
            "dns_search": host_config_data.get("DnsSearch"),
            "volumes_from": host_config_data.get("VolumesFrom"),
            "devices": host_config_data.get("Devices"),
            "sysctls": host_config_data.get("Sysctls"),
            "ipc_mode": host_config_data.get("IpcMode"),
            "pid_mode": host_config_data.get("PidMode"),
            "uts_mode": host_config_data.get("UTSMode"),
            "cpu_shares": host_config_data.get("CpuShares"),
            "cpuset_cpus": host_config_data.get("CpusetCpus"),
            "mem_limit": host_config_data.get("Memory"),
            "memswap_limit": host_config_data.get("MemorySwap"),
            "port_bindings": host_config_data.get("PortBindings"),
        }
        filtered_host_config = {
            k: v for k, v in host_config_dict.items() if v is not None
        }
        if filtered_host_config:
            create_kwargs["host_config"] = filtered_host_config

        # --- Tratamento de Montagens (Mounts) ---
        mounts_list = []
        if original_attrs.get("Mounts"):
            for mount_data in original_attrs["Mounts"]:
                mount_type = mount_data.get("Type")
                target = mount_data.get("Target")
                source = mount_data.get("Source")
                readonly = mount_data.get("RW", True) == False

                if not target:
                    continue

                mount_options = {}
                if mount_type == "volume" and mount_data.get("VolumeOptions"):
                    mount_options["volume_options"] = mount_data["VolumeOptions"]
                elif mount_type == "tmpfs" and mount_data.get("TmpfsOptions"):
                    mount_options["tmpfs_options"] = mount_data["TmpfsOptions"]
                elif mount_type == "bind" and mount_data.get("BindOptions"):
                    mount_options["bind_options"] = mount_data["BindOptions"]

                mounts_list.append(
                    Mount(
                        target=target,
                        source=source,
                        type=mount_type,
                        read_only=readonly,
                        **mount_options,
                    )
                )
            if mounts_list:
                create_kwargs["mounts"] = mounts_list

        # --- Tratamento de Rede ---
        original_networks = network_settings_data.get("Networks", {})
        network_mode = host_config_data.get("NetworkMode", "default")

        is_complex_network = len(original_networks) > 1 or (
            len(original_networks) == 1
            and network_mode not in ["default", "host", "none", "bridge"]
        )

        if "container:" in network_mode:
            # Cannot replicate this exactly. Fall back to default network.
            create_kwargs.get("host_config", {}).pop("network_mode", None)
        elif is_complex_network:
            endpoints_config = {}
            primary_network_name = network_mode
            for net_name, net_details in original_networks.items():
                ep_config = EndpointConfig(
                    aliases=net_details.get("Aliases"),
                    links=net_details.get("Links"),
                    ipv4_address=(
                        net_details.get("IPAddress")
                        if not net_details.get("IPPrefixLen") == 0
                        else None
                    ),
                )
                endpoints_config[net_name] = ep_config
                if net_name == primary_network_name:
                    create_kwargs.get("host_config", {}).pop("network_mode", None)

            if endpoints_config:
                networking_config = NetworkingConfig(endpoints_config=endpoints_config)
                create_kwargs["networking_config"] = networking_config
                if (
                    primary_network_name not in endpoints_config
                    and primary_network_name
                    not in ["default", "host", "none", "bridge"]
                ):
                    create_kwargs["network_mode"] = primary_network_name

        elif network_mode not in [
            "default",
            "bridge",
        ]:  # Simple non-default mode (host, none)
            create_kwargs["network_mode"] = network_mode
            create_kwargs.get("host_config", {}).pop("network_mode", None)
        else:  # Default bridge network
            create_kwargs.get("host_config", {}).pop("network_mode", None)

        # Limpar kwargs com valores None
        final_create_kwargs = {k: v for k, v in create_kwargs.items() if v is not None}

        # 3. Parar e Remover o container antigo
        container.stop()
        container.remove()

    except NotFound:
        print(
            f"Error: Container {container.id} not found during stop/remove."
        )  # Alt feedback
        return None
    except APIError as e:
        print(f"Error: Docker API error during stop/remove: {e}")  # Alt feedback
        return None
    except Exception as e:
        print(
            f"Error: An unexpected error occurred during config/stop/remove: {e}"
        )  # Alt feedback
        return None

    try:
        # 4. Baixar a imagem mais recente
        client.images.pull(image_name)

        # 5. Criar e iniciar o novo container
        new_container = client.containers.create(**final_create_kwargs)
        new_container.start()

        return new_container

    except APIError as e:
        print(f"Error: Docker API error during pull/create/start: {e}")  # Alt feedback
        return None
    except Exception as e:
        print(
            f"Error: An unexpected error occurred during pull/create/start: {e}"
        )  # Alt feedback
        return None


def printLine():
    cl.print("-" * 80, style="cyan")


def getContainers():
    client: docker.DockerClient = docker.from_env()
    containers = client.containers.list()
    return containers


def checkForNewVersion(imageName):
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


if __name__ == "__main__":
    client = docker.from_env()
    container = client.get("homepage")
    recreateContainer(container)
