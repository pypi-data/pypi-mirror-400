from yta_editor_nodes.timeline import TimelineNode
from typing import Union


class SerialNode(TimelineNode):
    """
    A node that is executed from a specific input and
    generates a single output that is sent to the next
    node.
    """

    def __init__(
        self,
        # TODO: Put the correct class
        # TODO: Maybe I need the 'node' in the TimelineNode class
        # TODO: Maybe I need a shortcut to 'is_gpu_available'...
        node: 'NodeProcessor',
        name: str,
        start: Union[int, float, 'Fraction'] = 0.0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        self.node: TimelineNode = node
        """
        The node to execute and to obtain the output from.
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
        return self.node.process(
            input = input,
            **kwargs
        )