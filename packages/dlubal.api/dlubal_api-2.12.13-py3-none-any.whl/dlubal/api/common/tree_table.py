from dlubal.api.common.packing import get_internal_value, set_internal_value, get_internal_value_type
from dlubal.api.common.common_pb2 import Value


def _set_internal_tree_value(wrapped_value: Value, value: int | float | str | bool | None):
    wrapped_value_type = get_internal_value_type(wrapped_value)

    if not wrapped_value_type:
        set_internal_value(wrapped_value, value)
    else:
        value_type = type(value)

        # This is necessary to allow entering numbers greater than maximal allowed integer
        if value_type is int and wrapped_value_type is float:
            value = float(value)

        set_internal_value(wrapped_value, value)


def _get_child_container(tree):
    if hasattr(tree, 'rows'):
        return tree.rows
    elif hasattr(tree, 'children'):
        return tree.children
    else:
        return None

def _get_subtree_item(subtree, path: list[str]):
    """
    Recursively retrieve an item from a subtree based on the specified path.

    Args:
        subtree: The starting subtree object which may have children.
        path (list[str]): A list of keys representing the path to the desired item.

    Returns:
        The subtree item at the specified path if found, otherwise None.
    """
    if not path:
        return subtree

    container = _get_child_container(subtree)
    if container is None:
        return None

    for child in container:
        if hasattr(child, 'key') and child.key == path[0]:
            return _get_subtree_item(child, path[1:])
    return None

def _iter_over_all_rows(tree, key, values=[], path=[], return_paths: bool = False):
    """
    Recursively walk the tree structure and collect values for the given key.

    Args:
        tree: The current tree node that may expose rows or children.
        key: The key to search for and collect values from.
        values (list): Mutable accumulator used to collect the found values.
        path (list[str]): Path accumulated so far, used to report full key paths.
        return_paths (bool): When True, return (path, value) tuples instead of raw values.

    Returns:
        list: All collected values (or path/value tuples) for the requested key.
    """
    current_path = path + [tree.key]

    if tree.key == key:
        value = get_internal_value(tree.value)
        if return_paths:
            values.append((current_path, value))
        else:
            values.append(value)
        return values

    if hasattr(tree, 'rows'):
        for row in tree.rows:
            values = _iter_over_all_rows(row, key, values, current_path, return_paths=return_paths)
        return values
    elif hasattr(tree, 'children'):
        for child in tree.children:
            values = _iter_over_all_rows(child, key, values, current_path, return_paths=return_paths)
        return values
    else:
        raise AssertionError('Unknown tree structure')

def _iter_over_all_rows_set(tree, key, values=[]):
    """
    Recursively walk the tree structure and set values for every occurrence of the given key.

    Args:
        tree: The current tree node that may expose rows or children.
        key: The key whose values will be overwritten.
        values (list): Mutable queue of values to assign to subsequent matches.

    Returns:
        list: Remaining values that were not consumed by matching nodes.
    """

    if tree.key == key:
        _set_internal_tree_value(tree.value, values.pop(0))
        return values
    elif hasattr(tree, 'rows'):
        for row in tree.rows:
            values = _iter_over_all_rows_set(row, key, values)
        return values
    elif hasattr(tree, 'children'):
        for child in tree.children:
            values = _iter_over_all_rows_set(child, key, values)
        return values
    else:
        raise AssertionError('Unknown tree structure')


def _get_tree_value_occurrence(tree, key, occurrence: int, found_occurrences: int = 0):
    """
    Recursively traverse the tree to find the value of the requested occurrence of the key.

    Args:
        tree: The root tree object which contains rows or children.
        key: The key to search for throughout the tree.
        occurrence (int): Zero-based occurrence index to retrieve.
        found_occurrences (int): How many occurrences of the key have already been seen.

    Returns:
        tuple[Any | None, int]: The value of the requested occurrence (if found) and
        the updated count of processed occurrences.
    """

    current_occurrences = found_occurrences
    if tree.key == key:
        if occurrence == found_occurrences:
            return get_internal_value(tree.value), current_occurrences
        else:
            current_occurrences = current_occurrences + 1

    container = _get_child_container(tree)
    if container is None:
        return None, current_occurrences

    for row in container:
        value, current_occurrences = _get_tree_value_occurrence(row, key, occurrence, current_occurrences)
        if value is not None:
            return value, current_occurrences

    return None, current_occurrences

def _set_tree_value_occurrence(tree, key, value: int | float | str | bool, occurrence: int, found_occurrences: int = 0):
    """
    Recursively traverse the tree and replace the value of the requested occurrence of the key.

    Args:
        tree: The root tree object which contains rows or children.
        key: The key to search for throughout the tree.
        value: Value to assign to the matching occurrence.
        occurrence (int): Zero-based occurrence index to update.
        found_occurrences (int): How many occurrences of the key have already been seen.

    Returns:
        tuple[bool, int]: Flag that indicates whether the target occurrence was updated and
        the updated count of processed occurrences.
    """

    current_occurrences = found_occurrences
    if tree.key == key:
        if occurrence == found_occurrences:
            _set_internal_tree_value(tree.value, value)
            return True, current_occurrences
        else:
            current_occurrences = current_occurrences + 1

    container = _get_child_container(tree)
    if container is None:
        return False, current_occurrences

    for row in container:
        result, current_occurrences = _set_tree_value_occurrence(row, key, value, occurrence, current_occurrences)
        if result:
            return True, current_occurrences

    return False, current_occurrences


def _get_key_occurrence_value(tree, key: str, occurrence: int = 0):
    """
    Return the value for the specified occurrence of a key at the root level.

    Args:
        tree: The tree table message containing top-level rows.
        key (str): Target key to inspect.
        occurrence (int): Zero-based occurrence index to retrieve.

    Returns:
        Any | None: Value of the requested occurrence if it exists, otherwise None.
    """
    if occurrence < 0:
        return None

    found_occurrences = 0
    # Get only specified value with the given key
    for row in tree.rows:
        value, found_occurrences = _get_tree_value_occurrence(row, key, occurrence, found_occurrences)
        if value is not None:
            return value

    return None


def _set_key_occurrence_value(tree, key: str, value: int | float | str | bool, occurrence: int = 0):
    """
    Set the value of a specific occurrence of a key within the top-level rows.

    Args:
        tree: The tree table message containing top-level rows.
        key (str): Target key to update.
        value (int | float | str | bool): Value to assign to the requested occurrence.
        occurrence (int): Zero-based occurrence index to update.

    Returns:
        bool: True if the requested occurrence was found and updated, otherwise False.
    """

    found_occurrences = 0

    # Set new value
    for row in tree.rows:
        result, found_occurrences = _set_tree_value_occurrence(row, key, value, occurrence, found_occurrences)
        if result:
            return True

    return False


def get_values_by_key(tree, key: str, path: list[str] = [], occurrence: int | None = None, return_paths: bool = False) -> list | int | float | str | bool | None:
    """
    Retrieve values of a key from the tree, optionally narrowing the search to a subtree and/or to a specific occurrence.

    Args:
        tree: The root tree object which contains rows.
        key (str): The key to search for in the tree rows.
        path (list[str]): Optional path identifying the subtree to inspect.
        occurrence (int | None): If provided, return only this occurrence. Occurrence counting starts from 1.
        return_paths (bool): When True, include the path next to each returned value.

    Returns:
        list | Any | None: When `occurrence` is None, returns a list of values (or path/value tuples) for every match.
        Otherwise returns the single value for the requested occurrence, or None if it cannot be found.
    """

    if path:
        tree = get_tree_item(tree, path)
        if not tree:
            return None

    if occurrence is None:
        # Get all values with the given key
        values = []
        for row in tree.rows:
            values = _iter_over_all_rows(row, key, values, path=path, return_paths=return_paths)
        return values
    else:
        if occurrence < 1:
            raise Exception("Occurrence has to be greater than 0")

        occurrence = occurrence - 1
        return _get_key_occurrence_value(tree, key, occurrence)


def set_values_by_key(tree, key: str, values: list, path: list[str] = [], occurrence: int | None = None):
    """
    Set values for the specified key across the entire tree, optionally limited to a subtree or a single occurrence.

    Args:
        tree: The root tree object which contains rows.
        key (str): The key to update in the tree rows.
        values (list): The list of values to assign (consumed sequentially for each matching occurrence).
        path (list[str]): Optional path identifying the subtree whose occurrences should be updated.
        occurrence (int | None): When provided, only this occurrence (relative to the full tree or subtree) is updated. Occurrence counting starts from 1.

    Returns:
        None
    """

    if not values:
        return

    if path:
        tree = get_tree_item(tree, path)
        if not tree:
            return None

    if occurrence is None:
        # Set new values
        for row in tree.rows:
           values = _iter_over_all_rows_set(row, key, values)
    else:
        if occurrence < 1:
            raise Exception("Occurrence has to be greater than 0")

        occurrence = occurrence - 1
        _set_key_occurrence_value(tree, key, values[0], occurrence)


def get_tree_item(tree, path: list[str]):
    """
    Retrieve an item from a tree table protobuf message based on the specified path.

    Args:
        tree: The root tree object which contains rows.
        path (list[str]): A list of keys representing the path to the desired item.

    Returns:
        The tree item at the specified path if found, otherwise None.
    """
    if not path:
        return tree

    container = _get_child_container(tree)
    if container is None:
        return None

    for row in container:
        if hasattr(row, 'key') and row.key == path[0]:
            return _get_subtree_item(row, path[1:])
    return None


def get_value_by_path(tree, path: list[str]) -> int | float | str | bool | None:
    """
    Retrieve the value from a tree table protobuf message at the specified path.

    Args:
        tree: The root tree object which contains rows.
        path (list[str]): A list of keys representing the path to the desired value.

    Returns:
        The value at the specified path if found, otherwise None.
    """
    row = get_tree_item(tree, path)
    if not row:
        return None
    return get_internal_value(row.value)


def set_value_by_path(tree, path: list[str], value: int | float | str | bool | None):
    """
    Set a value in a tree table protobuf message at the specified path.
    Creates intermediate rows if they do not exist.

    Args:
        tree: The root tree object which contains rows or children.
        path (list[str]): A list of keys representing the path to the desired item.
        value (int | float | str | bool | None): The value to set at the specified path.

    Returns:
        None
    """
    if not path:
        return

    current = tree
    for key in path[:-1]:
        # Determine container: rows or children
        container = _get_child_container(current)
        if container is None:
            return

        # Find child with key
        child = None
        for row in container:
            if row.key == key:
                child = row
                break

        # If not found, create new row
        if child is None:
            child = container.add()
            child.key = key

        current = child

    # Handle last key
    last_key = path[-1]
    container = _get_child_container(current)
    if container is None:
        return

    # Find or create last row
    last_row = None
    for row in container:
        if row.key == last_key:
            last_row = row
            break

    if last_row is None:
        last_row = container.add()
        last_row.key = last_key

    # Set the value
    _set_internal_tree_value(last_row.value, value)
