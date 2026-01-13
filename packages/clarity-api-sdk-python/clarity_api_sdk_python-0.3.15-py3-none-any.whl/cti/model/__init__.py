"""Pydantic models for CTI objects."""

import inspect
import pkgutil
from importlib import import_module

__all__ = []

# Iterate over all modules in the current package
for loader, name, is_pkg in pkgutil.iter_modules(__path__):
    if not is_pkg:
        # Import the module
        module = import_module(f".{name}", __package__)
        # Find all public classes in the module
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            # Check if the class is defined in this module (not imported)
            # and if it's a public class (doesn't start with an underscore)
            if class_obj.__module__ == module.__name__ and not class_name.startswith(
                "_"
            ):
                # Add the class to globals() to make it importable from the package
                globals()[class_name] = class_obj
                # Add the class name to __all__
                if class_name not in __all__:
                    __all__.append(class_name)  # type: ignore

# Sort __all__ for consistency
__all__.sort()  # type: ignore
