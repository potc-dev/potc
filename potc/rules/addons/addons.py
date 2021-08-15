import copy
from contextlib import contextmanager
from functools import lru_cache
from itertools import chain
from typing import Tuple

from .imports import ImportPool, ImportStatement, FromImport, DirectImport
from ...utils import try_import_info


@lru_cache()
def _get_unprocessable():
    from ..utils import unprocessable
    return unprocessable


def unprocessable():
    return _get_unprocessable()()


class AddonProxy:
    def __init__(self, base, rule):
        self.__base = base
        self.__rule = rule

    def __getattr__(self, item: str):
        return AddonProxy(f'{self.__base}.{item}', self.__rule)

    def __getitem__(self, item):
        if isinstance(item, slice):
            _temp_rule = lambda x: '' if x is None else self.__rule(x)
            _item_str = f'{_temp_rule(item.start)}:{_temp_rule(item.stop)}:{_temp_rule(item.step)}'
        else:
            _item_str = self.__rule(item)
        return AddonProxy(f'{self.__base}[{_item_str}]', self.__rule)

    def __call__(self, *args, **kwargs):
        _items = chain(
            map(lambda x: self.__rule(x), args),
            map(lambda p: f"{p[0]}={self.__rule(p[1])}", kwargs.items())
        )
        return AddonProxy(
            f'{self.__base}({", ".join(_items)})',
            self.__rule,
        )

    def __str__(self) -> str:
        return self.__base


class Addons:
    def __init__(self, rule=None):
        self.__imports = ImportPool()
        self.__rule = rule

    def __import(self, _import: str) -> DirectImport:
        return self.__imports.import_(_import)

    def __from(self, _from: str) -> FromImport:
        return self.__imports.from_(_from)

    def obj(self, obj, alias=None) -> AddonProxy:
        with self.transaction():
            segments = try_import_info(obj, alias=alias)
            if alias is None and segments[:2] == ('from', 'builtins'):
                return self.val(obj)

            _import = self
            for sign, content in zip(segments[::2], segments[1::2]):
                if sign == 'from':
                    _import = _import.__from(content)
                elif sign == 'import':
                    _import = (_import.__import if _import is self else _import.import_)(content)
                else:
                    _import = _import.as_(content)

            if alias:
                _import = _import.as_(alias)
            return AddonProxy(str(_import.target), self.rule)

    def val(self, obj) -> AddonProxy:
        with self.transaction():
            return AddonProxy(self.rule(obj), self.rule)

    def rule(self, v):
        with self.transaction():
            _result, _trace = self.__rule(v, self)
            return str(_result)

    @property
    def import_items(self) -> Tuple[ImportStatement, ...]:
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
