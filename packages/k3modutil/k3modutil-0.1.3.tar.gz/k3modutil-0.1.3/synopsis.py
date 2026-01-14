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
