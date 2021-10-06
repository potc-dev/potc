from .builtin import builtin_all, builtin_reflect, builtin_collection, builtin_basic, builtin_ellipsis, \
    builtin_slice, builtin_range, builtin_bytes, builtin_float, builtin_module, \
    builtin_tuple, builtin_func, builtin_type, builtin_dict, builtin_int, builtin_list, builtin_none, builtin_set, \
    builtin_str, builtin_items, builtin_complex, builtin_object
from .typing import typing_wrapper, typing_all, typing_typevar, typing_callable, typing_items

native_all = [
    typing_all,
    builtin_all,
]
