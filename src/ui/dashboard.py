from typing import Dict, Optional
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

console = Console()

class CloneDashboard:
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[white]{task.description}"),
            BarColumn(bar_width=30, style="cyan", complete_style="green"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False
        )
        self.tasks: Dict[str, TaskID] = {}

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

    def add_task(self, name: str, total: int) -> TaskID:
        task_id = self.progress.add_task(f"{name}", total=total)
        self.tasks[name] = task_id
        return task_id

    def update_task(self, name: str, advance: int = 1, description: Optional[str] = None):
        if name in self.tasks:
            kwargs = {"advance": advance}
            if description:
                kwargs["description"] = f"{name}: {description}"
            self.progress.update(self.tasks[name], **kwargs)


def show_summary(
    source_name: str,
    target_name: str,
    roles_count: int,
    channels_count: int,
    emojis_count: int,
    elapsed_time: float,
    backup_file: Optional[str] = None
):
    table = Table(title="Cloning Summary", title_style="bold white", border_style="dim")
    table.add_column("Property", style="cyan", justify="left")
    table.add_column("Value", style="white", justify="right")

    table.add_row("Source", source_name)
    table.add_row("Target", target_name)
    table.add_row("Roles", str(roles_count))
    table.add_row("Channels (incl. restricted)", str(channels_count))
    table.add_row("Emojis", str(emojis_count))
    table.add_row("Elapsed Time", f"{elapsed_time:.1f}s")
    table.add_row("Status", "[green]Completed[/]")

    if backup_file:
        table.add_row("Backup Path", backup_file)

    console.print()
    console.print(table)
    console.print()
