import copy
import io
from contextlib import contextmanager

from ..translate import translate_object

_TEST_OBJ = '_TEST_OBJ'


@contextmanager
def obj_translate_assert(obj, extend_rules=None):
    _code, _addon, _name = translate_object(obj, extend_rules)

    vs = {}
    exec('', vs)
    original_vs = copy.deepcopy(vs)

    with io.StringIO() as _source_file:
        for _import in sorted(set(_addon.imports), key=lambda x: x.key):
            print(_import, file=_source_file)

        print(f'{_TEST_OBJ} = {_code}', file=_source_file)

        _source_code = _source_file.getvalue()

    exec(_source_code, vs)
    _changes = {key: value for key, value in vs.items() if
                key not in original_vs.keys() or original_vs[key] is not vs[key]}

    _obj = _changes[_TEST_OBJ]

    yield _obj, _name
