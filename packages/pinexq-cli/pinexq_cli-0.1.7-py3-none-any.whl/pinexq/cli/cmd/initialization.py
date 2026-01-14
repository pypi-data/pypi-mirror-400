from __future__ import annotations
from rich.console import Console
from copier import run_copy, CopierAnswersInterrupt
from copier.errors import CopierError

err_console = Console(stderr=True)
console = Console(highlight=False)


def init_project(path: str, template: str, version: str, project_name: str | None = None, pinexq_endpoint: str | None = None) -> None:
    data = {}
    if project_name:
        data["project_name"] = project_name
    if pinexq_endpoint:
        data["pinexq_endpoint"] = pinexq_endpoint
    try:
        run_copy(template,
                 path,
                 vcs_ref=version if version != "latest" else None,
                 data=data)
    except CopierAnswersInterrupt:
        console.print("Project generation aborted")
    except CopierError as e:
        err_console.print(f"Error during project generation: {e}")
