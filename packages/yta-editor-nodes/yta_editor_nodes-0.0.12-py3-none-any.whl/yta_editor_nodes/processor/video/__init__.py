"""
Nodes that modify inputs to obtain outputs but
depending on a 't' time moment to adjust it to the
time of the video in which the input (a frame of a
video) is being edited. A movement effect is not 
edited the same when we are at the begining of the
video effect than when we are at the end.
"""
from yta_editor_nodes.utils import instantiate_cpu_and_gpu_processors
from yta_editor_nodes.processor import _NodeProcessor
from typing import Union
from abc import ABC


class _VideoNodeProcessor(_NodeProcessor, ABC):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some effect that will be done by
    CPU or GPU (at least one of the options)*

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU, but for 
    video frames, including a `t` time moment parameter
    when processing.
    """

    def process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        t: float,
        **kwargs
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            input = input,
            t = t,
            **kwargs
        )
    
"""
Specific implementations below this class.
"""
    
class BreathingFrameVideoNodeProcessor(_VideoNodeProcessor):
    """
    The frame but as if it was breathing.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        zoom: float = 0.05,
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        super().__init__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            zoom = zoom
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        # TODO: 'output_size' was not before
        output_size: Union[tuple[int, int], None] = None,
        zoom: Union[float, None] = None,
    ):
        super().__reinit__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            zoom = zoom
        )

    def _instantiate_cpu_and_gpu_processors(
        self,
        output_size: tuple[int, int] = (1920, 1080),
        zoom: float = 0.05
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
            class_name = 'BreathingFrameVideoNodeProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor.video',
            cpu_kwargs = {},
            gpu_module_path = 'yta_editor_nodes_gpu.processor.video',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
                'zoom': zoom
            }
        )

class WavingFramesVideoNodeProcessor(_VideoNodeProcessor):
    """
    A video frame that is moving like a wave.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        output_size: tuple[int, int] = (1920, 1080),
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
        do_use_transparent_pixels: bool = False
    ):
        """
        The `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU to process the input.
        """
        super().__init__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            amplitude = amplitude,
            frequency = frequency,
            speed = speed,
            do_use_transparent_pixels = do_use_transparent_pixels
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        # TODO: 'output_size' was not before
        output_size: Union[tuple[int, int], None] = None,
        amplitude: Union[float, None] = None,
        frequency: Union[float, None] = None,
        speed: Union[float, None] = None,
        do_use_transparent_pixels: Union[bool, None] = None
    ):
        super().__reinit__(
            do_use_gpu = do_use_gpu,
            output_size = output_size,
            amplitude = amplitude,
            frequency = frequency,
            speed = speed,
            do_use_transparent_pixels = do_use_transparent_pixels
        )

    def _instantiate_cpu_and_gpu_processors(
        self,
        # TODO: Should this be 'None' or these values (?)
        output_size: tuple[int, int] = (1920, 1080),
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
        do_use_transparent_pixels: bool = False
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
            class_name = 'WavingFramesVideoNodeProcessor',
            cpu_module_path = 'yta_editor_nodes_cpu.processor.video',
            cpu_kwargs = {
                'amplitude': amplitude,
                'frequency': frequency,
                'speed': speed,
                'do_use_transparent_pixels': do_use_transparent_pixels
            },
            gpu_module_path = 'yta_editor_nodes_gpu.processor.video',
            gpu_kwargs = {
                'opengl_context': None,
                'output_size': output_size,
                'amplitude': amplitude,
                'frequency': frequency,
                'speed': speed,
                'do_use_transparent_pixels': do_use_transparent_pixels
            }
        )