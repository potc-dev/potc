from ..fixture import Addons, rule
from ..supports import raw_object
from ..supports.bin import dump_obj


@rule()
def default_object(v, addon: Addons):
    return addon.obj(raw_object)(addon.raw(dump_obj(v), func=repr))


#: Overview:
#:      Default object type.
#:      Used as the default implement, when all the rules are disabled, \
#:      this rule and system rules will still work to make sure the basic property.
#:
#: Items:
#:      - Default expression of :class:`object`
default_all = [
    (
        default_object,
    ),
]
