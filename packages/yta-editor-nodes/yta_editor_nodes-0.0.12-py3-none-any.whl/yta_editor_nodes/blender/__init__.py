"""
The blenders, capable of mixing different inputs into
a single one by using different parameters and 
techniques.

All the classes here will have an instance of the
specific CPU and/or GPU class that is able to run the
code by using either CPU or GPU. The user can choose
between GPU and CPU and that option will be considered
(only if available).
"""
from yta_editor_nodes.processor import _ProcessorGPUAndCPU
from yta_editor_nodes.utils import instantiate_cpu_and_gpu_processors
from typing import Union
from abc import abstractmethod


class _Blender(_ProcessorGPUAndCPU):
    """
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some blenders that will use
    CPU or GPU (at least one of the options)*

    Class that is capable of mixing 2 different
    inputs by using the GPU or the CPU.
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
        blender_cpu, blender_gpu = self._instantiate_cpu_and_gpu_blenders(
            output_size = output_size,
            **kwargs
        )

        super().__init__(
            processor_cpu = blender_cpu,
            processor_gpu = blender_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        blender_cpu, blender_gpu = self._instantiate_cpu_and_gpu_blenders(
            output_size = output_size,
            **kwargs
        )

        super().__reinit__(
            processor_cpu = blender_cpu,
            # TODO: Maybe we need to reset the GPU
            processor_gpu = blender_gpu,
            do_use_gpu = do_use_gpu
        )

    @abstractmethod
    def _instantiate_cpu_and_gpu_blenders(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        **kwargs
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU blenders and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        pass

    def process(
        self,
        base_input: Union['np.ndarray', 'moderngl.Texture'],
        overlay_input: Union['np.ndarray', 'moderngl.Texture'],
        mix_weight: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            **kwargs
        )
    
    def blend_multiple_inputs(
        self,
        inputs: list[Union['np.ndarray', 'moderngl.Texture']],
        mix_weights: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            **kwargs
        )
    
"""
Specific implementations below this class.
"""
    
class MixBlender(_Blender):
    """
    A blender that uses a float value to mix the
    result with the original input as much as that
    value determines.
    """

    def _instantiate_cpu_and_gpu_blenders(
        self,
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU blenders and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        return instantiate_cpu_and_gpu_processors(
            class_name = 'MixBlender',
            cpu_module_path = 'yta_editor_nodes_cpu.blender',
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.blender',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
            }
        )

    def blend(
        self,
        base_input: Union['np.ndarray', 'moderngl.Texture'],
        overlay_input: Union['np.ndarray', 'moderngl.Texture'],
        mix_weight: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            **kwargs
        )

class AlphaBlender(_Blender):
    """
    The most common blender used in video edition.

    This blender will use the alpha channel of the 
    overlay input, multiplied by the `blend_strength`
    parameter provided, to use it as the mixer factor
    between the base and the overlay inputs.
    """

    def _instantiate_cpu_and_gpu_blenders(
        self,
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU blenders and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        return instantiate_cpu_and_gpu_processors(
            class_name = 'AlphaBlender',
            cpu_module_path = 'yta_editor_nodes_cpu.blender',
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.blender',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
            }
        )

    def blend(
        self,
        base_input: Union['np.ndarray', 'moderngl.Texture'],
        overlay_input: Union['np.ndarray', 'moderngl.Texture'],
        mix_weight: float = 1.0,
        blend_strength: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            blend_strength = blend_strength,
            **kwargs
        )
    
    # TODO: This method has to be reviewed in the general
    # class to be able to receive array parameters and
    # send them to the individual process as single parameter
    def blend_multiple_inputs(
        self,
        inputs: list[Union['np.ndarray', 'moderngl.Texture']],
        mix_weights: Union[list[float], float] = 1.0,
        blend_strengths: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            blend_strength = blend_strengths,
            **kwargs
        )
    
class AddBlender(_Blender):
    """
    The most common blender used in video edition.

    This blender will increase the brightness by
    combining the colors of the base and the overlay
    inputs, using the overlay as much as the 
    `strength` parameter is indicating.
    """

    def _instantiate_cpu_and_gpu_blenders(
        self,
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        *For internal use only*

        Instantiate the CPU and GPU blenders and return 
        them in that order.

        This method has been created to be used in both the
        '__init__' and the '__reinit__' methods.

        This method must be implemented by each class.
        """
        return instantiate_cpu_and_gpu_processors(
            class_name = 'AddBlender',
            cpu_module_path = 'yta_editor_nodes_cpu.blender',
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.blender',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
            }
        )

    def blend(
        self,
        base_input: Union['np.ndarray', 'moderngl.Texture'],
        overlay_input: Union['np.ndarray', 'moderngl.Texture'],
        mix_weight: float = 1.0,
        strength: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            strength = strength,
            **kwargs
        )
    
    # TODO: This method has to be reviewed in the general
    # class to be able to receive array parameters and
    # send them to the individual process as single parameter
    def blend_multiple_inputs(
        self,
        inputs: list[Union['np.ndarray', 'moderngl.Texture']],
        mix_weights: Union[list[float], float] = 1.0,
        strengths: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            strengths = strengths,
            **kwargs
        )


__all__ = [
    'MixBlender',
    'AlphaBlender',
    'AddBlender'
]

"""
Note for the developer:

I leave this old way to instantiate dynamically
but less refactored, just in case. Please, remove
in the next commits if the new version is already
working.

TODO: Old way to import dynamically
blender_cpu = None
if is_cpu_available():
    from yta_editor_nodes_cpu.blender import AddBlenderCPU

    blender_cpu = AddBlenderCPU()

blender_gpu = None
if is_gpu_available():
    from yta_editor_nodes_gpu.blender import AddBlenderGPU

    blender_gpu = AddBlenderGPU(
        opengl_context = None,
        # TODO: Do not hardcode please...
        output_size = (1920, 1080),
    )
"""