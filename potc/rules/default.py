
from ..fixture import Addons, rule
from ..supports import raw_object
from ..supports.bin import dump_obj


@rule()
def default_object(v, addon: Addons):
    return addon.obj(raw_object)(addon.raw(dump_obj(v)))


default_all = [
    (
        default_object,
    ),
]
