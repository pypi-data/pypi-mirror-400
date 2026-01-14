from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Tuple

from docker.models.images import Image

from pinexq.cli.docker_tools.client import ContainerClient
from pinexq.cli.utils.console import console, err_console
from pinexq.cli.utils.const import PINEXQ_PREFIX as PREFIX, PINEXQ_ERROR_PREFIX as ERROR_PREFIX


def generate_manifest_signature(container_client: ContainerClient, base_image: Image, function_name: str,
                                entrypoint: str) -> dict:
    return container_client.run_manifest(base_image, function_name, entrypoint=entrypoint)


@dataclass
class BuildOptions:
    dockerfile: str
    context_dir: str
    secrets: list[str]
    tag: str
    entrypoint: str


def generate_manifests(container_client: ContainerClient, functions: list[str], build_options: BuildOptions) -> Tuple[dict, list]:
    # Generate manifests
    # We are building the image for the current execution context to generate manifests
    # This will build for the local architecture to make sure the manifest generation can be executed locally
    base_image = container_client.pre_build_image(build_options.context_dir, build_options.dockerfile,
                                                  build_options.tag,
                                                  secrets=build_options.secrets)
    if not base_image:
        console.print(f'{ERROR_PREFIX} Failed to build base image.')
        exit(1)
    container_functions = container_client.run_function_list(base_image, entrypoint=build_options.entrypoint)
    if not container_functions:
        err_console.print(f'{ERROR_PREFIX} Failed to list functions in procon.')
    console.print(f'{PREFIX} Found following functions in container: {container_functions}')
    if len(functions) == 0:
        functions = container_functions
    else:
        console.print(f'{PREFIX} Functions specified in command line: {functions}')
        functions = [f for f in container_functions if f in functions]
    manifests = {}
    for function_name in functions:
        signature = generate_manifest_signature(container_client, base_image, function_name, build_options.entrypoint)
        manifests[function_name] = signature
        os.makedirs('.manifests', exist_ok=True)
        manifest_path = Path('.manifests') / f"{signature['function_name']}.json"
        with open(manifest_path, 'w') as f:
            json.dump(signature, f, indent=2)
    return manifests, functions
