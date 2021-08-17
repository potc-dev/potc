import re
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import Optional, Tuple


class ImportStatement(metaclass=ABCMeta):
    @property
    @abstractmethod
    def target(self):
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def key(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _is_valid(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _str(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def _check_valid(self):
        if not self._is_valid():
            raise ValueError(f'Invalid import statement - {repr(self._str())}.')

    @contextmanager
    def _with_check(self):
        _state = self.__getstate__()

        try:
            yield
            self._check_valid()
        except Exception as err:
            self.__setstate__(_state)
            raise err

    @abstractmethod
    def __getstate__(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __setstate__(self, state):
        raise NotImplementedError  # pragma: no cover

    def __str__(self):
        self._check_valid()
        return self._str()

    def __repr__(self):
        return f'<{type(self).__name__} {repr(self._str())}>'


_SEGMENT_PATTERN = re.compile('[a-zA-Z0-9_]+')
_LINK_PATTERN = re.compile('[a-zA-Z0-9_]+(\\.[a-zA-Z0-9_]+)*')


class FromImport(ImportStatement):
    def __init__(self, _from: str, _import: Optional[str] = None, _as: Optional[str] = None):
        self.__from = _from
        self.__import = _import
        self.__as = _as

    def import_(self, obj_name: str) -> 'FromImport':
        with self._with_check():
            self.__import = obj_name
            return self

    def as_(self, alias_name: Optional[str]) -> 'FromImport':
        with self._with_check():
            self.__as = alias_name
            return self

    def _is_valid(self):
        if self.__from and self.__import:
            return (not self.__from or _LINK_PATTERN.fullmatch(self.__from)) and \
                   (not self.__import or _SEGMENT_PATTERN.fullmatch(self.__import)) and \
                   (not self.__as or _SEGMENT_PATTERN.fullmatch(self.__as))
        else:
            return False

    def _str(self):
        if not self.__as:
            return f'from {self.__from} import {self.__import}'
        else:
            return f'from {self.__from} import {self.__import} as {self.__as}'

    @property
    def target(self):
        self._check_valid()
        if self.__as:
            return self.__as
        else:
            return self.__import

    @property
    def key(self):
        self._check_valid()
        return f'{self.__from}.{self.__import}', 1, self.target

    def __hash__(self):
        return hash((self.__from, self.__import, self.__as))

    def __eq__(self, other):
        if other is self:
            return True
        elif type(other) == type(self):
            return (self.__from, self.__import, self.__as) == (other.__from, other.__import, other.__as)
        else:
            return False

    def __setstate__(self, state):
        self.__from, self.__import, self.__as = state

    def __getstate__(self):
        return self.__from, self.__import, self.__as


class DirectImport(ImportStatement):
    def __init__(self, _import: str, _as: Optional[str] = None):
        self.__import = _import
        self.__as = _as

    def as_(self, alias_name: Optional[str]) -> 'DirectImport':
        with self._with_check():
            self.__as = alias_name
            return self

    def _is_valid(self):
        if self.__import:
            return (not self.__import or _LINK_PATTERN.fullmatch(self.__import)) and \
                   (not self.__as or _SEGMENT_PATTERN.fullmatch(self.__as))
        else:
            return False

    def _str(self):
        if not self.__as:
            return f'import {self.__import}'
        else:
            return f'import {self.__import} as {self.__as}'

    @property
    def target(self):
        self._check_valid()
        if self.__as:
            return self.__as
        else:
            return self.__import.split('.')[-1]

    @property
    def key(self):
        self._check_valid()
        return f'{self.__import}', 0, self.target

    def __hash__(self):
        return hash((self.__import, self.__as))

    def __eq__(self, other):
        if other is self:
            return True
        elif type(other) == type(self):
            return (self.__import, self.__as) == (other.__import, other.__as)
        else:
            return False

    def __setstate__(self, state):
        self.__import, self.__as = state

    def __getstate__(self):
        return self.__import, self.__as


class _SelfFormImport(FromImport):
    def __init__(self, _from: str, _import: Optional[str] = None, _as: Optional[str] = None, _this=None):
        FromImport.__init__(self, _from, _import, _as)
        self.__this = _this

    def import_(self, obj_name: str) -> '_SelfFormImport':
        _return = FromImport.import_(self, obj_name)
        self.__this.append(self)
        return self

    def as_(self, alias_name: Optional[str]) -> '_SelfFormImport':
        _return = FromImport.as_(self, alias_name)
        self.__this.append(self)
        return self

    def __getstate__(self):
        return FromImport.__getstate__(self), self.__this

    def __setstate__(self, state):
        _parent_state, self.__this = state
        FromImport.__setstate__(self, _parent_state)


class _SelfDirectImport(DirectImport):
    def __init__(self, _import: str, _as: Optional[str] = None, _this=None):
        DirectImport.__init__(self, _import, _as)
        self._check_valid()
        self.__this = _this
        self.__this.append(self)

    def as_(self, alias_name: Optional[str]) -> '_SelfDirectImport':
        _return = DirectImport.as_(self, alias_name)
        self.__this.append(self)
        return self

    def __getstate__(self):
        return DirectImport.__getstate__(self), self.__this

    def __setstate__(self, state):
        _parent_state, self.__this = state
        DirectImport.__setstate__(self, _parent_state)


class ImportPool:
    def __init__(self, *imports: ImportStatement):
        self.__imports = list(imports)
        self.__ids = {id(item): item.target for item in self.__imports}
        _this = self

    def append(self, import_: ImportStatement):
        if id(import_) not in self.__ids.keys():
            self.__imports.append(import_)
            self.__ids[id(import_)] = import_.target

    def import_(self, _import: str):
        return _SelfDirectImport(_import, _this=self)

    def from_(self, _from: str) -> _SelfFormImport:
        return _SelfFormImport(_from, _this=self)

    @property
    def imports(self) -> Tuple['ImportStatement', ...]:
        return tuple(self.__imports)

    def __getstate__(self):
        return self.__imports, self.__ids

    def __setstate__(self, state):
        self.__imports, self.__ids = state
