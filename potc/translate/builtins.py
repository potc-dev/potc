import math
import types

from .addons import Addons, AddonProxy
from .supports import raw_object, typed_object, function, _dump_obj, raw_type
from ..utils import dynamic_call


@dynamic_call
def builtin_int(v: int, addon: Addons):
    addon.is_type(v, int)
    return repr(v)


@dynamic_call
def builtin_float(v: float, addon: Addons):
    addon.is_type(v, float)
    with addon.transaction():
        if math.isinf(v):
            return ('+' if v > 0 else '-') + addon.obj(math).attr('inf').str()
        elif math.isnan(v):
            return addon.obj(math).attr('nan')
        else:
            if math.isclose(v, math.e):
                return addon.obj(math).attr('e')
            elif math.isclose(v, math.pi):
                return addon.obj(math).attr('pi')
            elif math.isclose(v, math.tau):
                return addon.obj(math).attr('tau')
            else:
                return repr(v)


@dynamic_call
def builtin_str(v: str, addon: Addons):
    addon.is_type(v, str)
    return repr(v)


@dynamic_call
def builtin_none(v: None, addon: Addons):
    if v is not None:
        addon.unprocessable()
    return repr(v)


@dynamic_call
def builtin_list(v: list, addon: Addons):
    addon.is_type(v, list)
    with addon.transaction():
        if type(v) == list:
            return f'[{", ".join(map(addon.rule, v))}]'
        else:
            return addon.obj(type(v)).call(list(v))


@dynamic_call
def builtin_tuple(v: tuple, addon: Addons):
    addon.is_type(v, tuple)
    with addon.transaction():
        if type(v) == tuple:
            return f'({", ".join(map(addon.rule, v))}{", " if len(v) == 1 else ""})'
        else:
            return addon.obj(type(v)).call(tuple(v))


@dynamic_call
def builtin_set(v: set, addon: Addons):
    addon.is_type(v, set)
    with addon.transaction():
        if type(v) == set:
            if len(v) > 0:
                return f'{{{", ".join(map(addon.rule, v))}}}'
            else:
                return 'set()'
        else:
            return addon.obj(type(v)).call(set(v))


@dynamic_call
def builtin_dict(v: dict, addon: Addons):
    addon.is_type(v, dict)
    with addon.transaction():
        if type(v) == dict:
            return f'{{{", ".join(map(lambda e: f"{addon.rule(e[0])}: {addon.rule(e[1])}", v.items()))}}}'
        else:
            return addon.obj(type(v)).call(dict(v))


@dynamic_call
def builtin_bytes(v: bytes, addon: Addons):
    addon.is_type(v, bytes)
    return repr(v)


@dynamic_call
def builtin_bytearray(v: bytearray, addon: Addons):
    addon.is_type(v, bytearray)
    with addon.transaction():
        return addon.obj(bytearray).call(bytes(v))


@dynamic_call
def builtin_func(v, addon: Addons):
    addon.is_type(v, types.FunctionType)
    with addon.transaction():
        return addon.obj(function).call(v.__name__, _dump_obj(v))


_TYPE_NAMES = {getattr(types, name): name for name in filter(lambda x: x.endswith('Type'), dir(types))}


@dynamic_call
def builtin_type(v: type, addon: Addons):
    addon.is_type(v, type)
    with addon.transaction():
        try:
            if v in _TYPE_NAMES.keys():
                return addon.obj(types).attr(_TYPE_NAMES[v])
            else:
                return addon.obj(v)
        except (ImportError, TypeError):
            _full_name = ((v.__module__ + '.') if hasattr(v, '__module__') else '') + v.__name__
            return addon.obj(raw_type).call(_full_name, _dump_obj(v))


@dynamic_call
def builtin_module(v, addon: Addons):
    addon.is_type(v, types.ModuleType)
    with addon.transaction():
        return addon.obj(v)


@dynamic_call
def builtin_object(v, addon: Addons):
    with addon.transaction():
        try:
            _i = addon.obj(type(v))
        except (ImportError, TypeError):
            return addon.obj(raw_object).call(_dump_obj(v))
        else:
            return addon.obj(typed_object).call(type(v), _dump_obj(v))


@dynamic_call
def sys_addon_proxy(v: AddonProxy, addon: Addons):
    addon.is_type(v, AddonProxy)
    with addon.transaction():
        return v.str()


builtins_ = [
    sys_addon_proxy,
    builtin_int,
    builtin_float,
    builtin_str,
    builtin_none,
    builtin_list,
    builtin_tuple,
    builtin_set,
    builtin_dict,
    builtin_bytes,
    builtin_bytearray,
    builtin_func,
    builtin_type,
    builtin_module,
    builtin_object,
]
