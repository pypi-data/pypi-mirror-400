#!/usr/bin/env python3
# coding: utf-8

import importlib
import os
import pkgutil


def submodules(root_module):
    """
    Load all submodules of `root_module`.
    And map these submodules names to submodules.
    :param root_module: is a module.
    :return: a dict whose keys are name of submodules and values are submodules loaded.
    Or `{}` if no submodule loaded.
    Or None if `root_module` is not the directory structure.
    """
    mod_path = root_module.__file__

    fn = os.path.basename(mod_path)
    pathname = os.path.dirname(mod_path)
    if fn not in ("__init__.py", "__init__.pyc"):
        return None

    rst = {}
    for _, name, _ in pkgutil.iter_modules([pathname]):
        full_name = root_module.__name__ + "." + name
        mod = importlib.import_module(full_name)
        rst[name] = mod

    return rst


def submodule_tree(root_module):
    """
    Load all submodules of `root_module` recursively. And put them in a **submodule
    dict**. Every key of this dict is a submodule's name, and every value in this dict
    has a 'module' part which is the submodule the key named and a 'children' part which
    is the submodule dict of the 'module' part. If the 'module' part has no submodule,
    the 'children' part will be assigned to `{}`. If the 'module' part is not the
    directory structure, the 'children' part will be assigned to None.
    :param root_module: is a module.
    :return: the submodule dict of `root_module`.
    Or None if `root_module` is not the directory structure.
    """
    """Example:
    {'submod1': {'module': <module> submod1,
     'children': submodule_tree(<module> submod1),
    },
    }
    """
    rst = submodules(root_module)
    if rst is None:
        return None

    for name, mod in rst.items():
        children = submodule_tree(mod)
        rst[name] = {"module": mod, "children": children}

    return rst


def submodule_leaf_tree(root_module):
    """
    Load all submodules of `root_module` recursively. And put them in a **submodule-leaf
    dict**. Every key of this dict is a submodules' name, and every value is a
    submodule-leaf dict of the submodule the key named, or the submodule itself if
    the submodule is not the directory structure.
    If no submodule loaded, submodule-leaf dict will be `{}`.
    :param root_module: is a module.
    :return: the submodule-leaf dict of `root_module`.
    Or None if `root_module` is not the directory structure.
    Example:
    {'submod1': submodule_leaf_tree( <module> submod1) or <module> submod1 }
    """
    rst = submodules(root_module)
    if rst is None:
        return None

    for name, mod in rst.items():
        children = submodule_leaf_tree(mod)
        if children is None:
            rst[name] = mod
        else:
            rst[name] = children

    return rst
