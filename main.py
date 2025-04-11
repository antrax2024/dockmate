from kernel import cl, getContainers, checkForNewVersion, ctToWatch
import time


def main() -> None:
    with cl.status("Working..."):  # Start a status bar
        containers = getContainers()
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

            cl.print(
                f"[bold yellow]Created:[/bold yellow] {container.attrs['Created']}"
            )
            cl.print(f"[bold yellow]Ports:[/bold yellow] {container.ports}")
            cl.print("=" * 40)
            time.sleep(5)


if __name__ == "__main__":
    main()
    cl.print("ok")
