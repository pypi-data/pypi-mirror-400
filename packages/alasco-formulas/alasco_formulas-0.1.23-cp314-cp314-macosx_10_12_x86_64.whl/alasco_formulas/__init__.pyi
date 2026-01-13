from typing import Literal, Protocol, Self

class Node(Protocol):
    """A node in the formula evaluation tree.

    Attributes:
        name: Display name for the node
        formula: Formula string to evaluate (e.g., "=10+5" or "=@ref1")
        value: The evaluated result as a string (empty before evaluation)
        is_hidden: Whether the node is hidden
        children: List of child nodes
    """

    name: str
    formula: str
    value: str
    is_hidden: bool
    children: list[Self]

def evaluate(formula: str) -> str:
    """Evaluates a single formula string.

    Args:
        formula: Formula string to evaluate (e.g., "=10+5" or "=@ref1")

    Returns:
        The evaluated result as a string, or an error indication.
    """
    ...

def evaluate_boolean(formula: str) -> str:
    """Evaluates a boolean expression formula string.

    Args:
        formula: Boolean expression string to evaluate (e.g., "1 == 1" or "5 > 3")

    Returns:
        The evaluated result as a string ("true" or "false"), or an error indication.
    """
    ...

def evaluate_tree[T: Node](root: T) -> T:
    """Evaluates a tree of nodes with formulas.

    This function evaluates all formulas in the tree, handling references
    between nodes (e.g., "=@ref1" references another node's value).

    Args:
        root: A Node object representing the root of the tree to evaluate

    Returns:
        The same tree structure with all 'value' fields populated with evaluation results

    Raises:
        TypeError: If the input does not match the Node protocol or attribute types are incorrect
        AttributeError: If required attributes are missing or cannot be accessed
        ValueError: If the input cannot be processed
    """
    ...

def get_tokens(
    formula: str,
) -> list[
    tuple[
        str,
        Literal[
            "number",
            "operator",
            "nodereference",
            "function",
            "aggregation",
            "conditional",
            "parenthesis",
            "unexpected",
        ],
    ]
]:
    """Parses a formula string into tokens with preserved number formats.

    This function parses a formula and returns a list of tokens, where each token
    contains the original string value and its type. Numbers preserve their original
    decimal separator (comma or point) for locale-based formatting.

    Args:
        formula: Formula string to tokenize (e.g., "=3,14 + 2.5")

    Returns:
        A list of tuples, where each tuple contains (value, token_type)

    Raises:
        ValueError: If the input cannot be parsed or is invalid
    """
    ...

def replace_reference[T: Node](root: T, old_ref: str, new_ref: str) -> T:
    """Replaces all occurrences of a reference with a new reference in a node tree.

    This function recursively traverses the node tree and replaces all references
    to the old reference (e.g., "@oldRef" or "@{old reference}") with the new reference
    (e.g., "@newRef" or "@{new reference}") in all formula strings. The function preserves
    extra properties on nodes that are not part of the standard Node interface.

    Args:
        root: A Node object representing the root of the tree
        old_ref: The reference to replace (e.g., "oldRef" or "old reference")
        new_ref: The new reference to use (e.g., "newRef" or "new reference")

    Returns:
        The same tree structure with all references updated

    Raises:
        TypeError: If the input does not match the Node protocol or attribute types are incorrect
        AttributeError: If required attributes are missing or cannot be accessed
        ValueError: If the input cannot be processed
    """
    ...
