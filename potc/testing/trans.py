import copy
import io
from contextlib import contextmanager
from functools import lru_cache
from typing import Mapping, Any


@lru_cache()
def _transobj_func():
    from ..translate import transobj
    return transobj


@lru_cache()
def _transvars_func():
    from ..translate import transvars
    return transvars


def run_script(source: str) -> Mapping[str, Any]:
    vs = {key: value for key, value in globals().items() if key.startswith('__') and key.endswith('__')}
    exec('', vs)
    original_vs = copy.deepcopy(vs)
    exec(source, vs)

    return {
        key: value for key, value in vs.items() if
        key not in original_vs.keys() or original_vs[key] is not vs[key]
    }


_TEST_OBJ = '_TEST_OBJ'


@contextmanager
def transobj_assert(obj, trans=None):
    _code, _addon, _name = _transobj_func()(obj, trans)

    with io.StringIO() as _source_file:
        for _import in sorted(set(_addon.import_items), key=lambda x: x.key):
            print(_import, file=_source_file)

        print(f'{_TEST_OBJ} = {_code}', file=_source_file)
        _source_code = _source_file.getvalue()

    _changes = run_script(_source_code)
    _obj = _changes[_TEST_OBJ]

    yield _obj, _name


@contextmanager
def transvars_assert(vars_: Mapping[str, Any], trans=None, reformat=None, isort: bool = True):
    _code, _addons = _transvars_func()(vars_, trans, reformat, isort)
    _changes = run_script(_code)

    assert '__all__' in _changes.keys(), f"No {repr('__all__')} variable found."
    _vars = {key: _changes[key] for key in _changes['__all__']}
    yield _vars, _code
