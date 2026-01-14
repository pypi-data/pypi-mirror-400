import typer
from copier import run_copy, CopierAnswersInterrupt
from copier.errors import CopierError
from rich.console import Console

generate_app = typer.Typer(name="generate", no_args_is_help=True)

# REUSABLE OPTIONS
Template = typer.Option("gh:data-cybernetics/pinexq-project-starter.git", "--template", show_default=True)
Version = typer.Option("latest", "--template-version", show_default=True)
Path = typer.Option("./", "--path", show_default=True)

err_console = Console(stderr=True)


@generate_app.command(name="project-toml", help="Generate project.toml")
def generate_project_toml(
        template: str = Template,
        version: str = Version,
        path: str = Path,
):
    data = {'python_versions': ['3.14'], 'default_python_version': '3.14'}
    generate_project_file(path, template, version, target_files=["pinexq.toml"], data=data)


@generate_app.command(name="dockerfile", help="Generate Dockerfile")
def generate_dockerfile(
        template: str = Template,
        version: str = Version,
        path: str = Path,
        python_version: str = typer.Option(None, "--python-version", help="Python version to use in Dockerfile")
):
    allowed_versions = ['3.14', '3.13', '3.12', '3.11']
    data = {'project_name': 'dummy', 'pinexq_endpoint': 'dummy', 'python_versions': allowed_versions}
    if python_version:
        if python_version not in allowed_versions:
            raise typer.BadParameter(f'Provided version ({python_version}) is not allowed. Allowed versions are: {allowed_versions}')
        data['default_python_version'] = python_version
    generate_project_file(
        path,
        template,
        version,
        target_files=["Dockerfile", ".dockerignore"],
        data=data
    )


def generate_project_file(path: str, template: str, template_version: str, target_files: list[str], data: dict = None):
    try:
        run_copy(
            template,
            path,
            vcs_ref=template_version if template_version != "latest" else None,
            exclude=["*", *[f"!{target_files}" for target_files in target_files]],
            data=data
        )
    except CopierAnswersInterrupt:
        err_console.print("Project generation aborted")
    except CopierError as e:
        err_console.print(f"Error during project generation: {e}")
