from importlib.metadata import version

__version__ = version("k3modutil")

from .modutil import (
    submodules,
    submodule_tree,
    submodule_leaf_tree,
)

__all__ = [
    "submodules",
    "submodule_tree",
    "submodule_leaf_tree",
]
