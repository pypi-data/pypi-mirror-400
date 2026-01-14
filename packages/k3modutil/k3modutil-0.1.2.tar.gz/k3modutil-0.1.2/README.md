# k3modutil

[![Action-CI](https://github.com/pykit3/k3modutil/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3modutil/actions/workflows/python-package.yml)
[![Build Status](https://travis-ci.com/pykit3/k3modutil.svg?branch=master)](https://travis-ci.com/pykit3/k3modutil)
[![Documentation Status](https://readthedocs.org/projects/k3modutil/badge/?version=stable)](https://k3modutil.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3modutil)](https://pypi.org/project/k3modutil)

Submodule Utilities.

k3modutil is a component of [pykit3] project: a python3 toolkit set.


Submodule Utilities.




# Install

```
pip install k3modutil
```

# Synopsis

```python

import k3modutil
import pykit

k3modutil.submodules(pykit)
# {
#    'modutil': <module> pykit.modutil,
#    ... ...
# }

k3modutil.submodule_tree(pykit)
# {
#    'modutil': {'module': <module> pykit.modutil,
#                'children': {
#                            'modutil': {
#                                    'module': <module> pykit.modutil.modutil,
#                                    'children': None,
#                                    },
#                            'test': {
#                                    'module': <module> pykit.modutil.test,
#                                    'children': {
#                                        'test_modutil': {
#                                            'module': <module> pykit.modutil.test.test_modutil,
#                                            'children': None,
#                                        },
#                                    },
#                            }
#                },
#               }
#    ... ...
# }

k3modutil.submodule_leaf_tree(pykit)
# {
#    'modutil': {
#                'modutil': <module> pykit.modutil.modutil,
#                'test': {'test_modutil': <module> pykit.modutil.test.test_modutil},
#                }
#    ... ...
# }

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3