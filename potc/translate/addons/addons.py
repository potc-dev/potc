import copy
from contextlib import contextmanager
from functools import lru_cache
from itertools import chain
from typing import Tuple

from .imports import ImportPool, ImportStatement, FromImport, DirectImport, from_import_str, direct_import_str
from ...utils import try_import_info


@lru_cache()
def _get_unprocessable():
    from ..rules import unprocessable
    return unprocessable


def unprocessable():
    return _get_unprocessable()()


class Addons:
    def __init__(self, rule=None):
        self.__imports = ImportPool()
        self.__rule = rule

    def import_(self, _import: str) -> DirectImport:
        return self.__imports.import_(_import)

    def from_(self, _from: str) -> FromImport:
        return self.__imports.from_(_from)

    def quick_import(self, obj, alias=None):
        _import_str = ' '.join(try_import_info(obj, alias=alias))
        try:
            _import = from_import_str(self, _import_str)
        except ValueError:
            _import = direct_import_str(self, _import_str)

        if alias:
            _import = _import.as_(alias)
        return _import

    def rule(self, v):
        with self.transaction():
            _result, _trace = self.__rule(v, self)
            return _result

    def func_call(self, func, *args, falias=None, **kwargs):
        with self.transaction():
            _import = self.quick_import(func, alias=falias)
            _pitems = chain(
                map(lambda x: self.rule(x), args),
                map(lambda p: f"{p[0]}={self.rule(p[1])}", kwargs.items())
            )
            return f'{_import.target}({", ".join(_pitems)})'

    def obj_attr(self, obj, attr, oalias=None):
        with self.transaction():
            _import = self.quick_import(obj, alias=oalias)
            return f'{_import.target}.{attr}'

    @property
    def imports(self) -> Tuple[ImportStatement, ...]:
        return self.__imports.imports

    def assert_(self, value):
        if not value:
            self.unprocessable()

    def is_type(self, v, type_: type):
        self.assert_(isinstance(v, type_))

    # noinspection PyMethodMayBeStatic
    def unprocessable(self):
        unprocessable()

    @contextmanager
    def transaction(self):
        _state = copy.deepcopy(self.__getstate__())
        try:
            yield self
        except Exception as err:
            self.__setstate__(_state)
            raise err

    def __getstate__(self):
        return self.__imports, self.__rule

    def __setstate__(self, state):
        self.__imports, self.__rule = state
