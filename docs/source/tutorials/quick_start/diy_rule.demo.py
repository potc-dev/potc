import re

import numpy as np

from potc import transvars
from potc.fixture import rule, Addons
from potc.rules import builtin_dict


@rule(type_=np.ndarray)
def ndarray_(v, addon: Addons):
    with addon.transaction():
        return addon.obj(np, 'np').array(v.tolist())


_VAR_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


@rule(type_=dict)
def my_dict(v: dict, addon: Addons):
    if all([_VAR_NAME.fullmatch(key) for key in v.keys()]):
        return addon.val(type(v))(**v)
    else:
        addon.unprocessable()  # give up rule replacing


if __name__ == '__main__':
    _code = transvars({
        'np_objects': {
            'a': np.array([[1, 2, ], [3, 4]]),
            'b': {
                'c': np.array([1, 2, 3]),
                'd': np.zeros((2, 3)),
                't': 233,
            },
            'e': {
                '0': np.array([1, 2]),
                'p': 2j,
            }
        },
        'np_module': np,
    }, [
        ndarray_,  # rule for np.ndarray
        (my_dict, builtin_dict,),  # rule for dict, before `builtin_dict`
    ], reformat='pep8')  # auto reformat the code
    print(_code)
