from yta_validation import PythonValidator
from typing import Union

import importlib


def is_gpu_available(
) -> bool:
    """
    Check if the GPU module is installed or not.
    """
    return PythonValidator.is_dependency_installed('yta_editor_nodes_gpu')

def is_cpu_available(
) -> bool:
    """
    Check if the CPU module is installed or not.
    """
    return PythonValidator.is_dependency_installed('yta_editor_nodes_cpu')


def instantiate_cpu_and_gpu_processors(
    class_name: str,
    cpu_module_path: Union[str, None] = 'yta_editor_nodes_cpu.blender',
    cpu_kwargs: Union[dict, None] = None,
    gpu_module_path: Union[str, None] = 'yta_editor_nodes_gpu.blender',
    gpu_kwargs: Union[dict, None] = None
) -> tuple[Union[any, None], Union[any, None]]:
    """
    Obtain instances of the classes with the given
    `class_name` (with CPU or GPU suffix) from the
    given modules, using the also given `cpu_kwargs`
    and `gpu_kwargs`.

    If `cpu_module_path` or `gpu_module_path` is
    None, the class will not be imported. Useful 
    when you only have one service available (GPU
    or CPU only).

    Example:
        ```
        cpu, gpu = instantiate_cpu_and_gpu_processors(
            class_name = 'MixBlender',
            module_path_cpu = 'yta_editor_nodes_cpu.blender',
            module_path_gpu = 'yta_editor_nodes_gpu.blender',
            cpu_kwargs = {},
            gpu_kwargs = {}
        )
        ```

    This example will try to instantiate the
    `MixBlenderCPU` and `MixBlenderGPU` classes from
    those modules.
    """
    processor_cpu = None
    do_has_cpu_dependency_installed = is_cpu_available()
    processor_gpu = None
    do_has_gpu_dependency_installed = is_gpu_available()

    if (
        not do_has_cpu_dependency_installed and
        not do_has_gpu_dependency_installed
    ):
        raise Exception('No CPU nor GPU dependency was found. Install the CPU dependency with the "pip install yta_editor_nodes[yta_editor_nodes_cpu]" command, or the GPU dependency with "pip install yta_editor_nodes[yta_editor_nodes_gpu]".')

    if (
        cpu_module_path is not None and
        do_has_cpu_dependency_installed
    ):
        try:
            # print(f'Importing {cpu_module_path} {class_name}CPU')
            cpu_module = importlib.import_module(cpu_module_path)
            processor_cpu = getattr(cpu_module, f'{class_name}CPU')(**(cpu_kwargs or {}))
        except (ImportError, AttributeError):
            pass

    if (
        gpu_module_path is not None and
        do_has_gpu_dependency_installed
    ):
        try:
            # print(f'Importing {gpu_module_path} {class_name}GPU')
            gpu_module = importlib.import_module(gpu_module_path)
            processor_gpu = getattr(gpu_module, f'{class_name}GPU')(**(gpu_kwargs or {}))
        except (ImportError, AttributeError):
            pass

    if (
        processor_cpu is None and
        processor_gpu is None
    ):
        raise Exception(f'No CPU nor GPU module found for the "{class_name}" class.')

    return (
        processor_cpu,
        processor_gpu
    )
