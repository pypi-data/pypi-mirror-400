from yta_validation.parameter import ParameterValidator
from yta_programming.singleton import SingletonABCMeta
from abc import abstractmethod
from typing import Union


class _ProcessorGPUAndCPU(metaclass = SingletonABCMeta):
    """
    *Abstract class*

    *For internal use only*

    Abstract class to share the common behaviour of
    being able to handle a process with a GPU and/or
    a CPU processor, chosen by the user.
    """

    @property
    def is_gpu_available(
        self
    ) -> bool:
        """
        Boolean flag to indicate if the GPU is available
        or not, that means that the processor that uses
        GPU is set.
        """
        return self._processor_gpu is not None
    
    @property
    def is_cpu_available(
        self
    ) -> bool:
        """
        Boolean flag to indicate if the CPU is available
        or not, that means that the processor that uses
        CPU is set.
        """
        return self._processor_cpu is not None
    
    @property
    def _processor(
        self
    ) -> Union['_ProcessorCPU', '_ProcessorGPU']:
        """
        *For internal use only*
        
        Get the processor that must be applied to process
        the inputs according to the internal flag that
        indicates if we want to use GPU or CPU and also
        depending on the availability of these classes.
        """
        return (
            (
                # Prefer GPU if available
                self._processor_gpu or
                self._processor_cpu
            ) if self._do_use_gpu else (
                # Prefer CPU if available
                self._processor_cpu or
                self._processor_gpu
            )
        )
    
    def __init__(
        self,
        processor_cpu: Union['_ProcessorGPU', None] = None,
        processor_gpu: Union['_ProcessorCPU', None] = None,
        do_use_gpu: bool = True,
    ):
        """
        The `processor_cpu` and
        `processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        ParameterValidator.validate_mandatory_bool('do_use_gpu', do_use_gpu)

        if (
            processor_cpu is None and
            processor_gpu is None
        ):
            raise Exception('No node processor provided. At least one node processor is needed.')

        self._processor_cpu: Union['_ProcessorCPU', None] = processor_cpu
        """
        The transition processor that is able to do the
        processing by using the CPU. If it is None we cannot
        process it with CPU.
        """
        self._processor_gpu: Union['_ProcessorGPU', None] = processor_gpu
        """
        The transition processor that is able to do the
        processing by using the GPU. If it is None we cannot
        process it with GPU.
        """
        self._do_use_gpu: bool = do_use_gpu
        """
        Internal flag to indicate if we should use GPU,
        if True, or CPU if False.
        """

    def __reinit__(
        self,
        processor_cpu: Union['_ProcessorGPU', None] = None,
        processor_gpu: Union['_ProcessorCPU', None] = None,
        do_use_gpu: bool = True,
    ):
        if (
            processor_cpu is None and
            processor_gpu is None
        ):
            raise Exception('No node processor provided. At least one node processor is needed.')
        
        self._processor_cpu: Union['_ProcessorCPU', None] = processor_cpu
        self._processor_gpu: Union['_ProcessorGPU', None] = processor_gpu
        self._do_use_gpu: bool = do_use_gpu

    def use_gpu(
        self
    ) -> '_ProcessorGPUAndCPU':
        """
        Set the internal flag to use GPU if available.
        """
        self._do_use_gpu = True

        return self

    def use_cpu(
        self
    ) -> '_ProcessorGPUAndCPU':
        """
        Set the internal flag to use CPU if available.
        """
        self._do_use_gpu = False

        return self

    @abstractmethod
    def process(
        self,
        input: Union['moderngl.Texture', 'np.ndarray']
    ) -> Union['moderngl.Texture', 'np.ndarray']:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        pass