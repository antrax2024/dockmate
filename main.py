from kernel import cl, getContainers, checkForNewVersion, ctToWatch, printLine
import time


def main() -> None:
    with cl.status("Working..."):  # Start a status bar
        containers = getContainers()
        for container in containers:
            # cl.log(f"[bold yellow]ID[/bold yellow]: {container.id}")
            printLine()
            cl.log(f"[bold yellow]Checking:[/bold yellow] {container.name}")
            if container.name in ctToWatch:
                cl.log("[bold yellow]Watch: [/bold yellow] [green]True[/green]")
                if checkForNewVersion(container.image.tags[0]):
                    cl.log(
                        f"[bold yellow]Action: [/bold yellow] [green]Stopping container[/green] [ {container.name}]"
                    )
                    container.stop()  # Stop the container
                    container.recreate()  # Recreate the container

            else:
                cl.log("[bold yellow]Watch: [/bold yellow] [red]False[/red]")

            # cl.log(
            #     f"[bold yellow]Image:[/bold yellow] {container.image.tags[0] if container.image.tags else 'No tags'}"
            # )
            # cl.log(f"[bold yellow]Status:[/bold yellow]  {container.status}")

            # cl.log(f"[bold yellow]Created:[/bold yellow] {container.attrs['Created']}")
            # cl.log(f"[bold yellow]Ports:[/bold yellow] {container.ports}")
            cl.log("waiting for next check...")
            printLine()
            time.sleep(5)


if __name__ == "__main__":
    main()
