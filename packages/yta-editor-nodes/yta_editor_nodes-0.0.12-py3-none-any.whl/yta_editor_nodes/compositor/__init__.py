"""
This module cocntains the nodes that are capable of
building the scene by positioning the inputs in
different positions.
"""
from yta_editor_nodes.abstract import _ProcessorGPUAndCPU
from yta_editor_nodes.utils import instantiate_cpu_and_gpu_processors
from typing import Union
from abc import abstractmethod


class _NodeCompositor(_ProcessorGPUAndCPU):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some node that will be positioning
    inputs, done by CPU or GPU (at least one of the
    options)*

    A node specifically designed to build a scene by
    positioning inputs in different positions and 
    obtaining a single output by using GPU or CPU.
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
        node_compositor_cpu, node_compositor_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__init__(
            processor_cpu = node_compositor_cpu,
            processor_gpu = node_compositor_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        node_compositor_cpu, node_compositor_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__reinit__(
            processor_cpu = node_compositor_cpu,
            # TODO: Maybe we need to reset the GPU
            processor_gpu = node_compositor_gpu,
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

class DisplacementWithRotationNodeCompositor(_NodeCompositor):
    """
    The frame, but moving and rotating over other frame.
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
            class_name = 'DisplacementWithRotationNodeCompositor',
            cpu_module_path = None,
            cpu_kwargs = None,
            gpu_module_path = 'yta_editor_nodes_gpu.compositor',
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
        position: tuple[int, int] = (1920 / 2 * 1.5, 1080 / 2 * 1.5),
        size: tuple[int, int] = (1920 / 2 * 1.5, 1080 / 2 * 1.5),
        rotation: int = 45,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            # TODO: Do I really need this 'output_size' (?)
            output_size = (1920, 1080),
            position = position,
            size = size,
            rotation = rotation,
            **kwargs
        )