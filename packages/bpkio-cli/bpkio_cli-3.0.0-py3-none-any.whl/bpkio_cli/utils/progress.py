from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)

from bpkio_cli.writers.colorizer_rich import theme

# Use stderr for transient progress output so redirected stdout stays clean.
progress_console = Console(theme=theme, force_terminal=True, stderr=True)


def make_progress(label: str, *, console_instance=progress_console) -> Progress:
    """Create a Rich Progress configured for short-lived CLI tasks."""
    return Progress(
        SpinnerColumn(),
        TextColumn(label),
        # Use a warmer color while running; keep success green when finished
        BarColumn(complete_style="orange3", finished_style="green"),
        TextColumn("{task.description}", justify="left"),
        MofNCompleteColumn(),  # shows n/m
        console=console_instance,
        transient=True,
    )


def list_with_progress(
    endpoint, hydrate: bool, label: str, *, console_instance=progress_console
):
    """List resources with optional hydration and progress feedback."""
    task = None
    seen = 0
    with make_progress(f"{label}:", console_instance=console_instance) as progress:

        def hook(total, resource, hook_label=None):
            nonlocal task, seen
            if task is None:
                task = progress.add_task("", total=total)
            if total != progress.tasks[task].total:
                progress.update(
                    task,
                    total=total,
                    completed=seen,
                    finished=False,
                )
            if hook_label is not None:
                progress.update(task, description=str(hook_label))
            else:
                progress.update(task, description="")
            seen += 1
            progress.update(task, advance=1, finished=False)

        return endpoint.list(sparse=not hydrate, progress_hook=hook)


def search_with_progress(
    endpoint, filters, label: str, *, console_instance=progress_console
):
    """Search resources with hydration and progress feedback."""
    task = None
    seen = 0
    with make_progress(f"{label}:", console_instance=console_instance) as progress:

        def hook(total, resource, hook_label=None):
            nonlocal task, seen
            if task is None:
                task = progress.add_task("", total=total)
            if total != progress.tasks[task].total:
                progress.update(
                    task,
                    total=total,
                    completed=seen,
                    finished=False,
                )
            if hook_label is not None:
                progress.update(task, description=str(hook_label))
            else:
                progress.update(task, description="")
            seen += 1
            progress.update(task, advance=1, finished=False)

        return endpoint.search(filters=filters, progress_hook=hook)
