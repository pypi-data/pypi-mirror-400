"""
The nodes that are able to make simple processing.
"""
from yta_editor_nodes.utils import instantiate_cpu_and_gpu_processors
from yta_editor_nodes.abstract import _ProcessorGPUAndCPU
from typing import Union
from abc import abstractmethod, ABC


class _NodeProcessor(_ProcessorGPUAndCPU, ABC):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some effect that will be done by
    CPU or GPU (at least one of the options)*

    A simple processor node that is capable of
    processing inputs and obtain a single output by
    using the GPU or the CPU.

    This type of node is for the effects and 
    transitions.
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
        node_processor_cpu, node_processor_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__init__(
            processor_cpu = node_processor_cpu,
            processor_gpu = node_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        node_processor_cpu, node_processor_gpu = self._instantiate_cpu_and_gpu_processors(
            output_size = output_size,
            **kwargs
        )

        super().__reinit__(
            processor_cpu = node_processor_cpu,
            processor_gpu = node_processor_gpu,
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
    
# Specific implementations below
class SelectionMaskNodeProcessor(_NodeProcessor):
    """
    Class to use a mask selection (from which we will
    determine if the pixel must be applied or not) to
    apply the processed input over the original one.

    If the selection mask is completely full, the
    result will be the processed input.
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
            class_name = 'SelectionMaskProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor',
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.processor',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
            }
        )

    def process(
        self,
        # TODO: What about the type (?)
        original_input: Union['np.ndarray', 'moderngl.Texture'],
        processed_input: Union['np.ndarray', 'moderngl.Texture'],
        selection_mask_input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            original_input = original_input,
            processed_input = processed_input,
            selection_mask_input = selection_mask_input,
            **kwargs
        )
    
# TODO: Just for testing, at least by now
class ColorContrastNodeProcessor(_NodeProcessor):
    """
    Node processor to test the color contrast
    change.

    TODO: Improve this, its just temporary
    """
    
    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: float = 1.5
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        super().__init__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: Union[float, None] = None
    ):
        super().__reinit__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        # TODO: Should this be 'None' or these values (?)
        factor: float = 1.5
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
            class_name = 'ColorContrastNodeProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor',
            cpu_kwargs = {
                'factor': factor
            },
            gpu_module_path = 'yta_editor_nodes_gpu.processor',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
                'factor': factor,
            }
        )
    
class BrightnessNodeProcessor(_NodeProcessor):
    """
    Node processor to modify the brightness of
    the input.
    """
    
    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: float = 2.0
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        super().__init__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: Union[float, None] = None
    ):
        super().__reinit__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        # TODO: Should this be 'None' or these values (?)
        factor: float = 2.0
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
            class_name = 'BrightnessNodeProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor',
            cpu_kwargs = {
                'factor': factor
            },
            gpu_module_path = 'yta_editor_nodes_gpu.processor',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
                'factor': factor,
            }
        )

class BlackAndWhiteNodeProcessor(_NodeProcessor):
    """
    Node processor to apply the black and white
    effect.

    TODO: Improve this, its just temporary
    """
    
    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: float = 1.5
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        super().__init__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        factor: Union[float, None] = None
    ):
        super().__reinit__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            factor = factor
        )

    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        # TODO: Should this be 'None' or these values (?)
        factor: float = 1.5
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
            class_name = 'BlackAndWhiteNodeProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor',
            # TODO: Why is the 'factor' only in GPU (?)
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.processor',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
                'factor': factor,
            }
        )
