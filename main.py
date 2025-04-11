from kernel import (
    os,
    cl,
    getContainers,
    checkForNewVersion,
    ctToWatch,
    printLine,
    recreateContainer,
)
import time

# Constants
TIME_MAIN_LOOP = int(os.getenv(key="TIME_MAIN_LOOP"))


def main() -> None:
    while True:
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

        cl.log(f"\n\nChecking again in {TIME_MAIN_LOOP} seconds...")
        time.sleep(TIME_MAIN_LOOP)


if __name__ == "__main__":
    main()
