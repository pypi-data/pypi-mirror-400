import inspect
import random
import re
from types import ModuleType
from typing import Any, Callable, List, Optional, Pattern

from lambdawaker.reflection.load import load_submodules


def select_random_function_from_module(module: ModuleType, name_pattern: Optional[str] = None) -> Callable[..., Any]:
    """
    Selects a random function from the given module.

    Args:
        module: The module object to search within.
        name_pattern: An optional regular expression pattern to filter functions by their names.

    Returns:
        A randomly selected function object from the module that matches the `name_pattern` if provided.

    Raises:
        ValueError: If no functions are found in the module, or no functions match the `name_pattern`.
    """
    functions = [obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]

    if name_pattern is not None:
        pattern = re.compile(name_pattern)
        functions = [func for func in functions if pattern.search(func.__name__)]

    if not functions:
        raise ValueError(f"No functions found in module {module.__name__}")

    return random.choice(functions)


def select_random_function_from_module_and_submodules(
        module: ModuleType, name_pattern: Optional[str] = None
) -> Callable[..., Any]:
    """
    Selects a random function from the given module or any of its submodules.
    This function first loads all submodules of the given module.

    Args:
        module: The module object to search within, including its submodules.
        name_pattern: An optional regular expression pattern to filter functions by their names.

    Returns:
        A randomly selected function object from the module or its submodules that matches the `name_pattern` if provided.

    Raises:
        ValueError: If no functions are found in the module or its submodules, or no functions match the `name_pattern`.
    """
    load_submodules(module)
    return _select_random_function_from_module_and_submodules(module, name_pattern)


cache = {}


def query_all_functions_from_module(module: ModuleType, pattern: Optional[Pattern[str]], ignore_cache=False) -> List[Callable[..., Any]]:
    """
    Recursively queries all functions from a module and its submodules that match a given pattern.

    Args:
        module: The module object to query.
        pattern: An optional compiled regular expression pattern to filter function names.
        ignore_cache: If True, the function will not use the cache and will query the module again.

    Returns:
        A list of function objects that match the pattern.
    """
    if module in cache and not ignore_cache:
        return cache[module]

    all_functions: List[Callable[..., Any]] = []

    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and (pattern is None or pattern.search(name)):
            all_functions.append(obj)

    for name, obj in inspect.getmembers(module):
        if inspect.ismodule(obj) and obj.__name__.startswith(module.__name__ + '.'):
            all_functions.extend(query_all_functions_from_module(obj, pattern))

    cache[module] = all_functions
    return all_functions


def _select_random_function_from_module_and_submodules(module: ModuleType, name_pattern: Optional[str] = None) -> Callable[..., Any]:
    """
        Given a module, selects a random function from that module or any of its submodules.

        Args:
            module: A Python module object
            name_pattern: Optional regexp pattern to filter functions by name

        Returns:
            A randomly selected function from the module or its submodules

        Raises:
            ValueError: If no functions are found in the module or its submodules
        """
    pattern = None
    if name_pattern is not None:
        pattern = re.compile(name_pattern)

    all_functions = query_all_functions_from_module(module, pattern)

    if not all_functions:
        raise ValueError(f"No functions found in module {module.__name__} or its submodules")

    return random.choice(all_functions)
