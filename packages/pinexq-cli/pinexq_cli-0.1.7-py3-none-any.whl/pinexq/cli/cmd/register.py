from dataclasses import dataclass, field

from pinexq_client.core import ApiException
from pinexq_client.core.hco.upload_action_hco import UploadParameters
from pinexq_client.job_management.model import ProcessingStepQueryParameters, ProcessingStepFilterParameter, Pagination, FunctionNameMatchTypes, CreateProcessingStepParameters
from rich.console import Console

from pinexq_client.job_management import enter_jma, EntryPointHco, ProcessingStepsRootHco, ProcessingStepHco

from pinexq.cli.pinexq_tools.info import get_info
from pinexq.cli.pinexq_tools.manifest import generate_manifests, BuildOptions
from pinexq.cli.utils.const import PINEXQ_PREFIX as PREFIX, PINEXQ_ERROR_PREFIX as ERROR_PREFIX
from pinexq.cli.docker_tools.client import ContainerClient
from pinexq.cli.pinexq_tools.client import get_client
from pinexq.cli.pinexq_tools.project import PinexqProjectConfig
from pinexq.cli.utils.uv_utils import is_uv_lockfile_up_to_date

err_console = Console(stderr=True)
console = Console(highlight=False)


@dataclass
class RegisterOptions:
    dockerfile: str = "./Dockerfile"
    context_dir: str = "./"
    api_key: str = ""
    functions: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)


def register(options: RegisterOptions, container_client: ContainerClient, config: PinexqProjectConfig):
    try:
        pinexq_client = get_client(config.project.endpoint, options.api_key)
        info = get_info(pinexq_client)
        if 'grant:codeContributor' not in info.user_grants and 'role:admin' not in info.user_grants:
            err_console.print(
                f'{ERROR_PREFIX} You do not have permission to register or deploy functions. Please ask your administrator or support to grant you the permission.')
            exit(1)
        if not is_uv_lockfile_up_to_date():
            err_console.print(f'{ERROR_PREFIX} uv lockfile is not up to date. Please run `uv lock` to update it.')
            exit(1)

        manifests, functions = generate_manifests(container_client, options.functions, BuildOptions(
            dockerfile=options.dockerfile,
            context_dir=options.context_dir,
            tag=f'{config.project.name}:{config.project.version}',
            secrets=options.secrets,
            entrypoint=config.project.entrypoint
        ))
        if not manifests:
            err_console.print(f'{ERROR_PREFIX} Failed to list functions in procon.')
        console.print(f'{PREFIX} Register following functions: {functions}')

        # Start registering the PS
        entrypoint: EntryPointHco = enter_jma(pinexq_client)
        console.print(f'{PREFIX} Registering function at {config.project.endpoint}')
        for function_name in functions:
            version = manifests[function_name]['version']
            console.print(f'{PREFIX} Deploying function {function_name}:{version}')
            register_processing_step(entrypoint, function_name, version, manifests[function_name])
    except Exception as e:
        err_console.print(f'{ERROR_PREFIX} Error: {e}')
        exit(1)


def register_processing_step(entrypoint: EntryPointHco, function_name: str, version: str, manifest: dict[str, dict]) -> ProcessingStepHco:
    processing_step_root: ProcessingStepsRootHco = entrypoint.processing_step_root_link.navigate()
    ps_filter = ProcessingStepFilterParameter(FunctionName=function_name, Version=version, ShowDeprecated=False, FunctionNameMatchType=FunctionNameMatchTypes.match_exact)
    existing_steps = processing_step_root.query_action.execute(ProcessingStepQueryParameters(Filter=ps_filter, IncludeRemainingTags=False, Pagination=Pagination(PageSize=1, PageOffset=None)))
    if existing_steps.current_entities_count == 0:
        console.print(f'{PREFIX} Processing step for function {function_name}:{version} does not exist. Creating new one.')
        try:
            params = CreateProcessingStepParameters(FunctionName=function_name, Title=function_name,
                                                    Version=version)
            processing_step = processing_step_root.register_new_action.execute(params)
            processing_step.upload_configuration_action.execute(
                UploadParameters(filename='UploadFile', mediatype='application/json',
                                 json=manifest))
            return processing_step.self_link.navigate()
        except ApiException as e:
            if e.problem_details.detail == 'A processing step with the same function name already exists.':
                console.print(
                    f'{PREFIX} Processing step for function {function_name}:{version} in version [bold dark_orange]{version}[/bold dark_orange] already exists. Skipping deployment.')
                exit(0)
            else:
                err_console.print(
                    f'{ERROR_PREFIX} Error registering processing step for function {function_name}:{version}:')
                exit(1)
    else:
        console.print(
            f'{PREFIX} Processing step for function {function_name}:{version} in version [bold dark_orange]{version}[/bold dark_orange] already exists.')
        return existing_steps.processing_steps[0]
