"""
Module for the effects and nodes that are made by
putting different nodes together.
"""
from yta_editor_nodes.processor import _ProcessorGPUAndCPU
from yta_editor_nodes.utils import instantiate_cpu_and_gpu_processors
from typing import Union
from abc import abstractmethod


class _NodeComplex(_ProcessorGPUAndCPU):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some complex node that will be
    done by CPU or GPU (at least one of the options)*

    A complex node, which is a node made by other nodes,
    that is capable of processing inputs and obtain a
    single output by using the GPU or the CPU.

    This type of node is for complex modifications.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        node_complex_cpu, node_complex_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__init__(
            processor_cpu = node_complex_cpu,
            processor_gpu = node_complex_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        node_complex_cpu, node_complex_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__reinit__(
            processor_cpu = node_complex_cpu,
            # TODO: Maybe we need to reset the GPU
            processor_gpu = node_complex_gpu,
            do_use_gpu = do_use_gpu
        )

    @abstractmethod
    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU procesors and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        pass

    def process(
        self,
        # TODO: What about the type (?)
        input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            input = input,
            **kwargs
        )

"""
Specific implementations below this class.
"""

class DisplayOverAtNodeComplex(_NodeComplex):
    """
    The overlay input is positioned with the given position,
    rotation and size, and then put as an overlay of the
    also given base input.

    Information:
    - The scene size is `(1920, 1080)`, so provide the
    `position` parameter according to it, where it is
    representing the center of the texture.
    - The `rotation` is in degrees, where `rotation=90`
    means rotating 90 degrees to the right.
    - The `size` parameter must be provided according to
    the previously mentioned scene size `(1920, 1080)`.

    TODO: This has no inheritance, is special and we need
    to be able to identify it as a valid one.
    """

    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU procesors and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        return instantiate_cpu_and_gpu_processors(
            class_name = 'DisplayOverAtNodeComplex',
            cpu_module_path = None,
            cpu_kwargs = None,
            gpu_module_path = 'yta_editor_nodes_gpu.complex',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
            }
        )

    def process(
        self,
        # TODO: What about the type (?)
        base_input: Union['np.ndarray', 'moderngl.Texture'],
        overlay_input: Union['np.ndarray', 'moderngl.Texture'],
        position: tuple[int, int] = (1920 / 2, 1080 / 2),
        size: tuple[int, int] = (1920 / 2, 1080 / 2),
        rotation: int = 0
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            position = position,
            size = size,
            rotation = rotation
        )