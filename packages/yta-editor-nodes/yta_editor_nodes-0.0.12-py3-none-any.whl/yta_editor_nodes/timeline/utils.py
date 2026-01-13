from yta_validation import PythonValidator
from typing import Union


VALID_EDITION_NODES = ['SerialNode', 'ParallelNode']
"""
The list of valid edition nodes as strings, to
compare easy to validate.
"""

def is_edition_node(
    node: Union['SerialNode', 'ParallelNode']
) -> bool:
    """
    Check if the provided `node` is an edition node, which
    has to be a SerialNode or a ParallelNode (by now).

    TODO: Update this in the future.
    """
    return PythonValidator.is_instance_of(node, VALID_EDITION_NODES)

def validate_is_edition_node(
    node: Union['SerialNode', 'ParallelNode']
) -> None:
    """
    Check if the provided `node` is an edition node, which
    has to be a `SerialNode` or a `ParallelNode` (by now), or
    raise an exception if not.
    """
    if not is_edition_node(node):
        raise Exception('The `node` provided is not an edition node.')