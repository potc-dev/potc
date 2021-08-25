from functools import partial

from ..fixture import Addons, rule
from ..supports import raw_object, typed_object
from ..supports.bin import dump_obj


@rule()
def default_object(v, addon: Addons):
    try:
        _i = addon.obj(type(v))
    except (ImportError, TypeError):
        _call = partial(addon.obj(raw_object))
    else:
        _call = partial(addon.obj(typed_object), type(v))

    return _call(dump_obj(v))


default_all = [
    (
        default_object,
    ),
]
