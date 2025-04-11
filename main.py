from kernel import (
    cl,
    getContainers,
    checkForNewVersion,
    ctToWatch,
    printLine,
    recreateContainer,
)
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
                        f"[bold yellow]Action: [/bold yellow] [green]Recreating container[/green] [ {container.name}]"
                    )
                    recreateContainer(container=container)
                    cl.log("[[bold green]OK[/ bold green]]")

            else:
                cl.log("[bold yellow]Watch: [/bold yellow] [red]False[/red]")

            cl.log("waiting for next check...")
            printLine()
            time.sleep(5)


if __name__ == "__main__":
    main()
