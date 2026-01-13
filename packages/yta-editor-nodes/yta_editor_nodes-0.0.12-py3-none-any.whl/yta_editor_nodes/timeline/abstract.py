from yta_validation.parameter import ParameterValidator
from abc import ABC, abstractmethod
from typing import Union


class TimelineNode(ABC):
    """
    *Abstract class*

    *This class has to be inherited by any class that
    is able to handle some input to obtain an output
    as a result*

    The abstract class of a TimelineNode, which is the entity
    that is able to process some input to return an
    output that can be sent to the next node, and able
    to connect (by storing the references) to the 
    other nodes.
    """

    @property
    def has_input_connections(
        self
    ) -> bool:
        """
        Flag that indicates if the node has, at least, other
        node connected as an input.

        TODO: Can it be connected to more than one (?)
        """
        return len(self.input_nodes) > 0
    
    @property
    def has_output_connections(
        self
    ) -> bool:
        """
        Flag that indicates if the node has, at least, other
        node connected as an output.

        TODO: Can it be connected to more than one (?)
        """
        return len(self.output_nodes) > 0

    def __init__(
        self,
        name: str,
        start: Union[int, float, 'Fraction'] = 0.0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        if (
            end is not None and
            end < start
        ):
            raise Exception('The "end" parameter provided must be greater or equal to the "start" parameter.')

        self.name: str = name
        """
        Just a simple name for the node.
        """
        self.start: float = start
        """
        The 't' time moment in which the TimelineNode must start
        being applied (including it).
        """
        self.end: Union[float, None] = end
        """
        The 't' time moment in which the TimelineNode must stop
        being applied (excluding it).

        TODO: The 'end' we receive here could be
        greater than the actual end of the media
        in which the TimedNode will be applied,
        but it seems to be working correctly as
        we will never receive a 't' from that
        media that is out of its own bounds...
        """
        self.input_nodes: list['TimelineNode'] = []
        """
        The nodes that are connected to this one as an
        input. The amount of elements could change
        according to the type of node.
        """
        self.output_nodes: list['TimelineNode'] = []
        """
        The nodes that are connected to this one as an
        output. The amount of elements could change
        according to the type of node.
        """
        self._cached_output: Union['np.ndarray', 'moderngl.Texture', None] = None
        """
        The output, but cached, so when it is generated
        it is stored here.
        """

    def _get_t(
        self,
        t: Union[int, float, 'Fraction']
    ) -> float:
        """
        Obtain the 't' time moment relative to the
        effect duration.

        Imagine `start=3` and `end=5`, and we receive 
        a `t=4`. It is inside the range, so we have
        to apply the effect, but as the effect
        lasts from second 3 to second 5 (`duration=2`),
        the `t=4` is actually a `t=1` for the effect
        because it is the time elapsed since the
        effect started being applied, that was on the 
        second 3.

        The formula:
        - `t - self.start`
        """
        return t - self.start
    
    def is_within_time(
        self,
        t: float
    ) -> bool:
        """
        Flag to indicate if the 't' time moment provided
        is in the range of this TimedNode instance, 
        which means between the 'start' and the 'end'.

        The formula:
        - `start <= t < end`
        """
        return (
            self.start <= t < self.end
            if self.end is not None else
            self.start <= t
        )

    def connect_to(
        self,
        node: 'TimelineNode'
    ) -> 'TimelineNode':
        """
        Connect the `node` provided to this one as an
        output, and also this one as an input of the
        `node`.

        TODO: The connection has to be done with another
        SerialNode, ParallelNode, etc.
        """
        # TODO: Don't connect if the time intervals don't
        # overlap (A.end > B.start is not possible)
        # the 'node' is output, so the 'self.end' cannot
        # be smaller than 'node.start'
        # TODO: Interesting as 'utils'
        def do_overlap_in_time(
            # TODO: Maybe pass the nodes instead (?)
            a_start: float,
            # TODO: What about 'None' (?)
            a_end: float,
            b_start: float,
            # TODO: What about 'None' (?)
            b_end: float
        ):
            """
            Check if the A period of time (defined by `a_start` and
            `a_end`) overlaps the B period of time (defined by `b_start`
            and `b_end`).

            Examples:
            - `A: s=1 e=2  B: s=2 e=3` They do not overlap
            - `A: s=1 e=2.2  B: s=2 e=3` They overlap in [2.0, 2.2)
            - `A: s=2 e=3  B: s=1 e=2` They do not overlap
            - `A: s=2 e=3  B: s=1 e=2.2` THey overlap in [2.0, 2.2)
            """
            # TODO: I'm faking this here to avoid the error
            a_end = (
                999
                if a_end is None else
                a_end
            )

            b_end = (
                999
                if b_end is None else
                b_end
            )

            return not (
                a_end <= b_start or
                b_end <= a_start
            )
        
        if not do_overlap_in_time(
            a_start = self.start,
            a_end = self.end,
            b_start = node.start,
            b_end = node.end
        ):
            raise Exception(f'This node (start="{str(self.start)}" end="{str(self.end)}") and the provided as `node` (start="{str(node.start)}" end="{str(node.end)}") do not overlap in time so they cannot be connected.')

        self.output_nodes.append(node)
        node.input_nodes.append(self)

        return self

    def clear_cache(
        self
    ) -> 'TimelineNode':
        """
        Clear the cache of this node, but also for
        the nodes that are outputs of this one, as
        the results would change.
        """
        self._cached_output = None

        for output_node in self.output_nodes:
            output_node.clear_cache()

        return self

    def process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        t: float = 0.0,
        # TODO: Maybe we need 'fps' and 'number_of_frames'
        # to calculate progressions or similar...
        **kwargs
    ) -> Union['moderngl.Texture', 'np.ndarray']:
        """
        Process the provided `input` if the given 't'
        time moment is in the range of this node instance,
        or return the original `input` if not.
        """
        result = input

        # TODO: With simple nodes we don't need the 't' and
        # this is failing if we don't put the **kwargs in
        # our CPU or GPU processors
        if self.is_within_time(t):
            # This will be ignored if no needed as we use **kwargs
            kwargs['t'] = self._get_t(t)
            result = self._process(
                input = input,
                **kwargs
            )

        return result

    @abstractmethod
    def _process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        **kwargs
    ) -> Union['np.ndarray', 'moderngl.Texture']:
        """
        Process the input and obtain a result as the output.
        """
        pass