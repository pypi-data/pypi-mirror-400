import importlib
import pkgutil
from types import ModuleType


def load_submodules(package: ModuleType) -> None:
    """
    Dynamically imports all submodules of a given package.

    This function walks through all submodules within the specified package
    and imports them, ensuring they are registered in `sys.modules`.
    This is useful for scenarios where modules need to be loaded
    for their side effects (e.g., registering classes or functions)
    or to make them discoverable via introspection.

    Args:
        package: The package module object whose submodules are to be loaded.
                 This should be the result of an `import` statement (e.g., `import my_package`).
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + "."
    ):
        importlib.import_module(module_name)
