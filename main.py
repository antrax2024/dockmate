import docker
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def main() -> None:
    client: docker.DockerClient = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        print(f"ID: {container.id}")
        print(f"Name: {container.name}")
        print(
            f"Image: {container.image.tags[0] if container.image.tags else 'No tags'}"
        )
        print(f"Status: {container.status}")

        print(f"Created: {container.attrs['Created']}")
        print(f"Ports: {container.ports}")
        print("=" * 40)


if __name__ == "__main__":
    main()
