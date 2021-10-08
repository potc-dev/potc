import importlib
import re
import types
import uuid
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import Optional, Tuple


def try_import_info(obj, alias: Optional[str] = None) -> Tuple[str, ...]:
    """
    Overview:
        Try to get an import statement from given object.

    Arguments:
        - obj (:obj:`object`): Given object.
        - alias (:obj:`Optional[str]`): Alias name for import statement, \
            default is ``None`` which means do not alias.

    Returns:
        - import (:obj:`Tuple[str, ...]`): Import statement tuple.

    Example:
        >>> import dill
        >>> try_import_info(dill)  # ('import', 'dill')
        >>>
        >>> from potc import transvars
        >>> try_import_info(transvars)  # ('from', 'potc', 'import', 'transvars')
    """
    try:
        _simple = _raw_import_info(obj)
        _segments = _simple[1].split('.')
        if _simple[0] == 'import':
            combiner = lambda i: '.'.join([*_segments[:i], _segments[-1]])
            rg = range(0, len(_segments))
        else:
            combiner = lambda i: '.'.join(_segments[:i])
            rg = range(1, len(_segments) + 1)

        _simpler = lambda i: (_simple[0], combiner(i), *_simple[2:])
        for index in rg:
            _sp = _simpler(index)
            try:
                if _validate_import_info(*_sp) is obj:
                    return (*_sp, *(('as', alias) if alias else ()))
            except (TypeError, ImportError, AttributeError, ModuleNotFoundError):
                continue
        raise TypeError(f'Unable to import {repr(obj)}, validate fail.')
    except (TypeError, ImportError, AttributeError, ModuleNotFoundError):
        raise TypeError(f'Unable to import {repr(obj)}, error occurred when trying to trace.')


def _raw_import_info(obj):
    if isinstance(obj, types.ModuleType):
        _segments = obj.__name__.split('.')
        if len(_segments) > 1:
            return 'from', '.'.join(_segments[:-1]), 'import', _segments[-1]
        else:
            return 'import', obj.__name__
    elif hasattr(obj, '__module__') and hasattr(obj, '__name__'):
        return 'from', obj.__module__, 'import', obj.__name__
    else:
        raise TypeError(f'Unable to import {repr(obj)}.')


def _validate_import_info(*args):
    if args[0] == 'from':
        module = importlib.import_module(args[1])
        return getattr(module, args[3])
    elif args[0] == 'import':
        return importlib.import_module(args[1])


class ImportStatement(metaclass=ABCMeta):
    def __init__(self):
        """
        Overview:
            Constructor of :class:`ImportStatement`.
        """
        self.__uuid = uuid.uuid4()

    @property
    def uuid(self):
        """
        Overview:
            UUID of the import statement, will be unique when generated.
        """
        return self.__uuid

    @property
    @abstractmethod
    def target(self):
        """
        Overview:
            Import target.

            - ``from aa import bb``  --> bb.
            - ``from aa import bb as cc``  --> cc.
            - ``import aa``  --> aa.
            - ``import aa.bb``  --> bb.

            Just seen target as the actual sign name of the imported object.
        """
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def key(self):
        """
        Overview:
            Key value of the import statement.
            Used for sorting.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _is_valid(self) -> bool:
        """
        Overview:
            Whether this import statement is valid.

        Return:
            - valid (:obj:`bool`): Is valid or not.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _str(self) -> str:
        """
        Overview:
            String format of this import statement.

        Returns:
            - str (:obj:`str`): String format.
        """
        raise NotImplementedError  # pragma: no cover

    def _check_valid(self):
        """
        Overview:
            Check if this statement is valid.
            if not valid, raise ``ValueError``.
        """
        if not self._is_valid():
            raise ValueError(f'Invalid import statement - {repr(self._str())}.')

    @contextmanager
    def _with_check(self):
        """
        Overview:
            Open a context, do some update and make sure the final statement is valid.
            If not, this statement will be rolled back, and all the updates will be ignored.
        """
        _state = self.__getstate__()

        try:
            yield
            self._check_valid()
        except Exception as err:
            self.__setstate__(_state)
            raise err

    @abstractmethod
    def __getstate__(self):
        """
        Overview:
            Get value state of statement.

        Returns:
            - state: Value state.
        """
        return self.__uuid

    @abstractmethod
    def __setstate__(self, state):
        """
        Overview:
            Set value state of statement.
        """
        self.__uuid = state

    def __str__(self) -> str:
        """
        Overview:
            Get string format, will check its validity before return.

        Returns:
            - str (:obj:`str`): String format.
        """
        self._check_valid()
        return self._str()

    def __repr__(self) -> str:
        """
        Overview:
            Get representation format.

        Returns:
            - repr (:obj:`str`): Representation format.
        """
        return f'<{type(self).__name__} {repr(self._str())}>'


_SEGMENT_PATTERN = re.compile('[a-zA-Z0-9_]+')
_LINK_PATTERN = re.compile('[a-zA-Z0-9_]+(\\.[a-zA-Z0-9_]+)*')


class FromImport(ImportStatement):
    """
    Overview:
        ``from xxx import yyy as zzz`` formatted import statement.
    """

    def __init__(self, _from: str, _import: Optional[str] = None, _as: Optional[str] = None):
        """
        Overview:
            Constructor of ``FromImport``.

        Arguments:
            - \_from (:obj:`str`): From source.
            - \_import (:obj:`Optional[str]`): Import item, default is ``None``.
            - \_as (:obj:`Optional[str]`): Alias name, default is ``None`` which means no alias.
        """
        ImportStatement.__init__(self)
        self.__from = _from
        self.__import = _import
        self.__as = _as

    def import_(self, obj_name: str) -> 'FromImport':
        """
        Overview:
            Import from source.

        Arguments:
            - obj_name (:obj:`str`): Import object name.

        Returns:
            - self: Self object.
        """
        with self._with_check():
            self.__import = obj_name
            return self

    def as_(self, alias_name: Optional[str]) -> 'FromImport':
        """
        Overview:
            Alias imported item.

        Arguments:
            - alias_name (:obj:`Optional[str]`): Alias name.

        Returns:
            - self: Self object.
        """
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
        self.__from, self.__import, self.__as, _state = state
        ImportStatement.__setstate__(self, _state)

    def __getstate__(self):
        return self.__from, self.__import, self.__as, ImportStatement.__getstate__(self)


class DirectImport(ImportStatement):
    """
    Overview:
        ``import xxx as yyy`` formatted import statement.
    """

    def __init__(self, _import: str, _as: Optional[str] = None):
        """
        Overview:
            Constructor of ``DirectImport``.

        Arguments:
            - \_import (:obj:`Optional[str]`): Import item, default is ``None``.
            - \_as (:obj:`Optional[str]`): Alias name, default is ``None`` which means no alias.
        """
        ImportStatement.__init__(self)
        self.__import = _import
        self.__as = _as

    def as_(self, alias_name: Optional[str]) -> 'DirectImport':
        """
        Overview:
            Alias imported item.

        Arguments:
            - alias_name (:obj:`Optional[str]`): Alias name.

        Returns:
            - self: Self object.
        """
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
        self.__import, self.__as, _state = state
        ImportStatement.__setstate__(self, _state)

    def __getstate__(self):
        return self.__import, self.__as, ImportStatement.__getstate__(self)


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
    """
    Overview:
        Pool of import statements.
    """

    def __init__(self, *imports: ImportStatement):
        """
        Overview:
            Constructor of ``ImportPool``.

        Arguments:
            - imports: Import statements.
        """
        self.__imports = list(imports)
        self.__ids = {item.uuid: item.target for item in self.__imports}
        _this = self

    def append(self, import_: ImportStatement):
        """
        Overview:
            Append new statement.

        Arguments:
            - import\_: Import statement.
        """
        if import_.uuid not in self.__ids.keys():
            self.__imports.append(import_)
            self.__ids[import_.uuid] = import_.target

    def import_(self, _import: str) -> _SelfDirectImport:
        """
        Overview:
            Start a direct import statement.

        Arguments:
            - \_import (:obj:`str`): Import item.

        Returns:
            - statement (:obj:`DirectImport`): Direct import statement.
        """
        return _SelfDirectImport(_import, _this=self)

    def from_(self, _from: str) -> _SelfFormImport:
        """
        Overview:
            Start a from import statement.

        Arguments:
            - from (:obj:`str`): Import source.

        Returns:
            - statement (:obj:`FromImport`): From import statement.
        """
        return _SelfFormImport(_from, _this=self)

    @property
    def imports(self) -> Tuple['ImportStatement', ...]:
        """
        Overview:
            Get tuple of current import statements.

        Returns:
            - imports (:obj:`Tuple['ImportStatement', ...]`): Import statements.
        """
        return tuple(self.__imports)

    def __getstate__(self):
        """
        Overview:
            Get value state of import pool.

        Returns:
            - state: Value state.
        """
        return self.__imports, self.__ids

    def __setstate__(self, state):
        """
        Overview:
            Set value state of import pool.
        """
        self.__imports, self.__ids = state
