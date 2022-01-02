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
    original_vs = copy.copy(vs)
    exec(source, vs)

    return {
        key: value for key, value in vs.items() if
        key not in original_vs.keys() or original_vs[key] is not vs[key]
    }


_TEST_OBJ = '_TEST_OBJ'


@contextmanager
def transobj_assert(obj: object, trans=None):
    """
    Overview:
        Assertion-based test for :func:`potc.translate.quick.transobj` function.

        This function is managed by ``contextmanager``, so you can use it with a ``with`` block.

    Arguments:
        - obj (:obj:`object`): Object to be translated
        - trans: Translator to be used. See :func:`potc.translate.quick.transobj`.

    Examples::
        >>> with transobj_assert([1, -2, 3.2, '1234']) as obj, name:
        ...     assert obj == [1, -2, 3.2, '1234']
        ...     assert name == 'builtin_list'

    .. note::

        When this function is called, the translated object code will be dumped into \
        a python file and then import from it, so please **make sure the code you created \
        can be supported by standard python grammar**.
    """
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
    r"""
    Overview:
        Assertion-based test for :func:`potc.translate.quick.transvars` function.

        This function is managed by ``contextmanager``, so you can use it with a ``with`` block.

    Arguments:
        - vars\_ (:obj:`Mapping[str, Any]`): The items to be translated, should be a mapping contains \
            all the values and their names.
        - trans: Translator to be used. See :func:`potc.translate.quick.transvars`.
        - reformat: Reformatter to be used. See :func:`potc.translate.quick.transvars`.
        - isort (:obj:`bool`): Sort the import statements. See :func:`potc.translate.quick.transvars`.

    Examples::
        >>> with transvars_assert({
        ...     'a': 233,
        ...     'b': [1, 2, 3, {'x': 1}],
        ... }) as (v, code):
        ...     assert v == {  # v is the mapping of the values
        ...         'a': 233,
        ...         'b': [1, 2, 3, {'x': 1}],
        ...     }
        ...     assert 'import' not in code  # code is the dumped source code

    .. note::

        When this function is called, the translated object code will be dumped into \
        a python file and then import from it, so please **make sure the code you created \
        can be supported by standard python grammar**.
    """
    _code, _addons = _transvars_func()(vars_, trans, reformat, isort)
    _changes = run_script(_code)

    assert '__all__' in _changes.keys(), f"No {repr('__all__')} variable found."
    _vars = {key: _changes[key] for key in _changes['__all__']}
    yield _vars, _code
