"""
Evaluation discovery mechanism.

This module provides functionality for discovering classes that inherit from Evaluation.
"""

import importlib.util
import inspect
import os


def find_evaluation_subclasses(directory: str, base_class_name="Evaluation"):
    """
    Dynamically import Python files under 'directory' and find classes that
    inherit from a class named 'Evaluation'. Returns a list of non-abstract
    class objects.
    """
    subclasses = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                filepath = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(filepath))[0]

                spec = importlib.util.spec_from_file_location(
                    module_name, filepath
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                    except Exception as e:
                        print(f"Skipping {filepath} due to import error: {e}")
                        continue

                    # Inspect for subclasses
                    for name, obj in inspect.getmembers(
                        module, inspect.isclass
                    ):
                        if any(
                            base.__name__ == base_class_name
                            for base in obj.__mro__[1:]
                        ) and not inspect.isabstract(obj):
                            subclasses.append(obj)

    return subclasses
