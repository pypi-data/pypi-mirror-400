"""
Our awesome editor module in which we have
all the classes that interact with it and
make it possible.

This is the nodes module, in which we have
all the classes that make the concept work.
"""
from yta_editor_nodes.timeline.utils import is_edition_node
from yta_editor_nodes.timeline.abstract import TimelineNode
from yta_editor_nodes.timeline.serial import SerialNode
from yta_editor_nodes.timeline.parallel import ParallelNode
from typing import Union


# TODO: This below is to test the timeline and graphs
class TimelineGraph:
    """
    Basic way to handle the timeline as a graph
    of nodes, that includes a starting (root) 
    node that will begin the process.
    """

    def __init__(
        self,
        root_node: TimelineNode
    ):
        self.root_node: TimelineNode = root_node
        """
        The root node in which everything starts.
        """

    # TODO: Maybe rename to 'process' (?)
    def render(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        t: float
    ):
        """
        Render the provided `input` at the given `t` time
        moment. The `input` must be the frame that belongs
        to that time moment.
        """
        return self.root_node.process(
            input = input,
            t = t
        )
    
class TimelineOfNodes:
    """
    Class to handle the timeline of a video, made with
    nodes that can be interconnected.
    """

    def __init__(
        self
    ):
        self._nodes: list['TimelineNode'] = []
        """
        The different nodes we have.
        """
        self._min_t: float = 0
        """
        The `start` time moment of the node that starts the
        first. Use this value to avoid unnecessary comparisons
        when trying to apply effects.

        We don't need to spend time checking if the user asks
        for s=1.0 but our nodes are applied in the time range
        [3.5, 8.5].
        """
        self._max_t: float = -1
        """
        The `end` time moment of the node that ends the
        last. Use this value to avoid unnecessary comparisons
        when trying to apply effects.

        We don't need to spend time checking if the user asks
        for s=1.0 but our nodes are applied in the time range
        [3.5, 8.5].
        """

    def add_node(
        self,
        node: 'TimelineNode'
    ) -> 'TimelineOfNodes':
        """
        Add a node to the timeline. The node must be a SerialNode,
        ParallelNode, etc, not a ProcessorNode.
        """
        if not is_edition_node(node):
            raise Exception('The "node" provided is not a valid edition node (is not a SerialNode nor a ParallelNode).')
        
        # TODO: We should check that is not repeated and
        # more things, but by now just this
        self._nodes.append(node)

        # Update 'min_t' and 'max_t' if necessary
        if node.start < self._min_t:
            self._min_t = node.start
        if node.end > self._max_t:
            self._max_t = node.end

        return self
    
    # TODO: Implement 'remove_node'? If we do, we have to 
    # maybe reset '_min_t' and '_max_t'

    def _get_active_nodes_at(
        self,
        t: float
    ) -> list['TimelineNode']:
        """
        Get a list with the nodes that are active (must be
        processed) in the `t` time moment provided.
        """
        return (
            _get_active_nodes_at(
                nodes = self._nodes,
                t = t
            )
            if self._min_t <= t <= self._max_t else
            []
        )
    
    def process(
        self,
        input: Union['np.ndarray', 'moderngl.Texture'],
        t: float
    ):
        """
        Process the provided `input` for the given `t` time
        moment.
        """
        nodes = self._get_active_nodes_at(t)

        for node in nodes:
            #print(f'A {type(node).__name__} ({type(node.node).__name__}) must process the input at t={str(t)}')
            print(f'A {type(node).__name__} ({node.name}) must process the input at t={str(t)}')
            # TODO: We need to handle the orders carefully, and also
            # the nodes that have input connections have to receive
            # the input from the other node
            input = node.process(
                input = input,
                t = t
            )

        return input
    
__all__ = [
    'TimelineGraph',
    'TimelineOfNodes',
    'SerialNode',
    'ParallelNode'
]
    

# TODO: Maybe I should have utils for this below
def _get_active_nodes_at(
    nodes: list['TimelineNode'],
    t: float
) -> list['TimelineNode']:
    """
    Get the nodes from the given `nodes` list that are
    active at the `t` time moment provided, that means
    that hey must be processed.
    """
    return [
        node
        for node in nodes
        # TODO: node.end can be None right now
        if node.start <= t <= node.end
    ]

def _get_nodes_without_input_connections(
    nodes: list['TimelineNode']
) -> list['TimelineNode']:
    """
    Get the nodes from the given `nodes` list that don't
    have input connections (they are root nodes).
    """
    return [
        node
        for node in nodes
        if not node.has_input_connections
    ]

"""
Note for the developer:

A guide to the different types of nodes we will have
when imitating DaVinci Resolve.

TimelineNode (abstracto)
├── ProcessorNode (procesa un solo flujo)
│   ├── EffectNode (filtros, LUTs, shaders…)
│   └── TransitionNode (mezcla entre dos entradas)
│
├── CompositeNode (combina múltiples flujos)
│   ├── SerialNode (uno tras otro)
│   ├── ParallelNode (ramas simultáneas)
│   └── LayerNode (capas con blending o máscaras)
│
└── GroupNode (contiene una mini subred de nodos)

"""
