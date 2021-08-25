import re

from potc.fixture import rule, Addons
from potc.rules import builtin_dict

_KEY_PATTERN = re.compile('^[_a-zA-Z][_0-9a-zA-Z]*$')


@rule(type_=dict)
def pretty_dict(v: dict, addon: Addons):
    for key in v.keys():
        if not (isinstance(key, str) and _KEY_PATTERN.fullmatch(key)):
            addon.unprocessable()

    return addon.obj(type(v))(**{key: value for key, value in v.items()})


__rules__ = [
    # pretty_dict will be executed before builtin_dict
    (pretty_dict, builtin_dict,),
]
