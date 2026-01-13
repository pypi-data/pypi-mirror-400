from yta_editor_nodes.timeline import TimelineNode
from abc import ABC, abstractmethod
from typing import Union


class _ParallelNodeAbstract(TimelineNode, ABC):
    """
    The abstract class of the parallel node.
    """

    def __init__(
        self,
        # TODO: Put the correct class
        # TODO: Maybe I need the 'node' in the TimelineNode class
        # TODO: Maybe I need a shortcut to 'is_gpu_available'...
        nodes: list[TimelineNode],
        name: str,
        start: Union[int, float, 'Fraction'] = 0.0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        self.nodes: list[TimelineNode] = nodes
        """
        The list of nodes that will be executed in parallel
        to obtain the outputs that will be combined.
        """

        super().__init__(
            name = name,
            start = start,
            end = end
        )

    def _process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the input and obtain a result as the output.
        """
        return self._combine_outputs(
            [
                node.process(
                    input = input,
                    **kwargs
                )
                for node in self.nodes
            ]
        )
    
    @abstractmethod
    def _combine_outputs(
        self,
        outputs: list[Union['np.ndarray', 'moderngl.Texture']]
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Combine the different `outputs` into a single one.
        """
        # TODO: This must be according to the type
        pass