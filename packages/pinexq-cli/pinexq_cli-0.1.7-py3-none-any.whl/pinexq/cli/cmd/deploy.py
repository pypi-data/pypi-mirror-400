from __future__ import annotations

from dataclasses import dataclass, field

from pinexq_client.job_management import enter_jma, EntryPointHco
from pinexq_client.job_management.model import ConfigureDeploymentParameters, \
    ScalingConfiguration, ScalingBehaviours, AssignCodeHashParameters, DeploymentStates

from pinexq.cli.cmd.register import register_processing_step
from pinexq.cli.docker_tools.client import ContainerClient
from pinexq.cli.pinexq_tools.client import get_client
from pinexq.cli.pinexq_tools.info import get_info
from pinexq.cli.pinexq_tools.manifest import generate_manifests, BuildOptions
from pinexq.cli.pinexq_tools.project import PinexqProjectConfig
from pinexq.cli.utils.console import console, err_console
from pinexq.cli.utils.const import PINEXQ_PREFIX as PREFIX, PINEXQ_ERROR_PREFIX as ERROR_PREFIX
from pinexq.cli.utils.uv_utils import is_uv_lockfile_up_to_date


@dataclass
class DeployOptions:
    dockerfile: str = "./Dockerfile"
    context_dir: str = "./"
    api_key: str = ""
    functions: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)


def deploy(deploy_command: DeployOptions, container_client: ContainerClient, config: PinexqProjectConfig):
    try:
        pinexq_client = get_client(config.project.endpoint, deploy_command.api_key)
        info = get_info(pinexq_client)
        if 'grant:codeContributor' not in info.user_grants and 'role:admin' not in info.user_grants:
            err_console.print(
                f'{ERROR_PREFIX} You do not have permission to deploy functions. Please ask your administrator or support to grant you the permission.')
            exit(1)
        if not is_uv_lockfile_up_to_date():
            err_console.print(f'{ERROR_PREFIX} uv lockfile is not up to date. Please run `uv lock` to update it.')
            exit(1)

        manifests, functions = generate_manifests(container_client, deploy_command.functions, BuildOptions(
            dockerfile=deploy_command.dockerfile,
            context_dir=deploy_command.context_dir,
            tag=f'{config.project.name}:{config.project.version}',
            secrets=deploy_command.secrets,
            entrypoint=config.project.entrypoint
        ))
        if not manifests:
            err_console.print(f'{ERROR_PREFIX} Failed to list functions in procon.')
        console.print(f'{PREFIX} Deploying following functions: {functions}')

        # This will build the base image again for the destination architecture amd64
        base_image = container_client.build_base_image(deploy_command.context_dir, deploy_command.dockerfile,
                                                       f'{config.project.name}:{config.project.version}',
                                                       secrets=deploy_command.secrets)
        if not base_image:
            console.print(f'{ERROR_PREFIX} Failed to build base image.')
            exit(1)

        # Start registering the PS
        entrypoint: EntryPointHco = enter_jma(pinexq_client)
        console.print(f'{PREFIX} Registering function{"s" if len(functions) > 1 else ""} at {config.project.endpoint}')
        for function_name in functions:
            version = manifests[function_name]['version']
            console.print(f'{PREFIX} start deploying function {function_name}:{version}')
            processing_step = register_processing_step(entrypoint, function_name, version, manifests[function_name])

            if processing_step.deployment_state != DeploymentStates.undefined and processing_step.deployment_state != DeploymentStates.not_deployed:
                console.print(f'{PREFIX} Processing step for function {function_name}:{version} is already deployed. Skipping deployment.')
                continue
            if processing_step._entity.properties.code_hash is not None:
                console.print(f'{PREFIX} Processing step for function {function_name}:{version} is already registered with an code artifact. Skipping deployment.')
                continue
            else:
                # Push image to registry
                if not container_client.tag_base_image_as_function(base_image, info, function_name, version):
                    exit(1)
                digest = container_client.push_function_image(info, function_name, version)
                if not digest:
                    console.print(f'{ERROR_PREFIX} Failed to push function image for {function_name}:{version}')
                    exit(1)
                deployment = config.get_function_deployment(function_name)
                processing_step.self_link.navigate().assign_code_hash_action.execute(
                    AssignCodeHashParameters(CodeHash=digest))
                processing_step.self_link.navigate().configure_deployment_action.execute(
                    ConfigureDeploymentParameters(
                        ResourcePreset=deployment.resource_preset,
                        Entrypoint=config.project.entrypoint,
                        Scaling=ScalingConfiguration(
                            MaxReplicas=deployment.max_replicas,
                            Behaviour=ScalingBehaviours.balanced
                        ),
                    )
                )

    except Exception as e:
        err_console.print(f'{ERROR_PREFIX} Error: {e}')
        exit(1)
