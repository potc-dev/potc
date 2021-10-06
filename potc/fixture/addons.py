import copy
from contextlib import contextmanager
from functools import lru_cache
from itertools import chain
from typing import Tuple, Optional

from .imports import ImportPool, ImportStatement, FromImport, DirectImport, try_import_info


@lru_cache()
def _get_unprocessable():
    from .common import unprocessable
    return unprocessable


def unprocessable():
    return _get_unprocessable()()


class AddonProxy:
    """
    Overview:
        Proxy of addon expression.
    """

    def __init__(self, base, rule):
        """
        Overview:
            Constructor of ``AddonProxy``

        Arguments:
            - base: Base unit of the proxy.
            - rule: Translation rule.
        """
        self.__base = base
        self.__rule = rule

    def __getattr__(self, item: str):
        """
        Overview:
            Generate attribute-getting expression, \
            like ``base.xxx``.

        Arguments:
            - item (:obj:`str`): Attribute name.

        Returns:
            - proxy: New generated proxy.
        """
        return AddonProxy(f'{self.__base}.{item}', self.__rule)

    def __getitem__(self, item):
        """
        Overview:
            Generate item-getting expression, \
            like ``base[233]``, ``base[::-1]`` or ``base[1, 2, 3]``.

        Arguments:
            - item (:obj:`str`): Item value, can be simple value, slice or tuple.

        Returns:
            - proxy: New generated proxy.
        """
        if isinstance(item, slice):
            _items = [item.start, item.stop, *((item.step,) if item.step is not None else ())]
            _item_str = ':'.join(map(lambda x: '' if x is None else self.__rule(x), _items))
        elif isinstance(item, tuple) and len(item) > 0:
            _item_str = ', '.join(map(self.__rule, item))
            _item_str = _item_str + (', ' if len(item) == 1 else '')
        else:
            _item_str = self.__rule(item)
        return AddonProxy(f'{self.__base}[{_item_str}]', self.__rule)

    def __call__(self, *args, **kwargs):
        """
        Overview:
            Generate item call expression, \
            like ``base(1, 2, x=1, y=2)``.

        Arguments:
            - args: Positional arguments.
            - kwargs: Key-word arguments.

        Returns:
            - proxy: New generated proxy.
        """
        _items = chain(
            map(lambda x: self.__rule(x), args),
            map(lambda p: f"{p[0]}={self.__rule(p[1])}", kwargs.items())
        )
        return AddonProxy(
            f'{self.__base}({", ".join(_items)})',
            self.__rule,
        )

    def __str__(self) -> str:
        """
        Overview:
            String format of expression.

        Returns:
            - return (:obj:`str`): String formatted expression.
        """
        return self.__base


class Addons:
    """
    Overview:
        Addon object used in rules.
    """

    def __init__(self, rule=None):
        """
        Overview:
            Constructor of ``Addons``.

        Arguments:
            - rule: Translation rule, default is ``None`` which means no translation rule, \
                auto translation will also be disabled when ``None`` is used.
        """
        self.__imports = ImportPool()
        self.__rule = rule

    def import_(self, _import: str) -> DirectImport:
        return self.__imports.import_(_import)

    def from_(self, _from: str) -> FromImport:
        return self.__imports.from_(_from)

    def obj(self, obj, alias: Optional[str] = None) -> AddonProxy:
        """
        Overview:
            Generate an object proxy.
            Object proxy means a object which need to be automatically imported, \
            such as ``json``, an import statement ``import json`` will be generated.
            If the object cannot be imported, it will raise exception.

        Arguments:
            - obj: Target object.
            - alias (:obj:`Optional[str]`): Alias name of the imported object, \
                default is ``None`` which means do not alias.

        Returns:
            - proxy (:obj:`AddonProxy`): Expression proxy object.
        """
        with self.transaction():
            segments = try_import_info(obj, alias=alias)
            _import = self
            for sign, content in zip(segments[::2], segments[1::2]):
                if sign == 'from':
                    _import = _import.from_(content)
                elif sign == 'import':
                    _import = _import.import_(content)
                else:
                    _import = _import.as_(content)

            if alias:
                _import = _import.as_(alias)
            return AddonProxy(str(_import.target), self.rule)

    def val(self, obj) -> AddonProxy:
        """
        Overview:
            Generate a value proxy.
            Differs from ``obj`` method, this method will not do automatic import, \
            it will just generate the string expression with the rule translator.

        Arguments:
            - obj: Value object.

        Returns:
            - proxy (:obj:`AddonProxy`): Expression proxy object.
        """
        with self.transaction():
            return AddonProxy(self.rule(obj), self.rule)

    # noinspection PyMethodMayBeStatic
    def raw(self, val, *, func=None) -> AddonProxy:
        """
        Overview:
            Generate raw proxy.

        Arguments:
            - val: Raw object.
            - func: Translation function, default is ``None`` which means just \
                turn it to string by builtin function ``str``.

        Returns:
            - proxy (:obj:`AddonProxy`): Raw proxy object.
        """
        return AddonProxy((func or str)(val), self.rule)

    def rule(self, v) -> str:
        """
        Overview:
            Express the value with the rule translator.

        Arguments:
            - v: Value object.

        Returns:
            - str (:obj:`str`): String formatted expression.
        """
        with self.transaction():
            return str(self.__rule(v, self))

    @property
    def import_items(self) -> Tuple[ImportStatement, ...]:
        """
        Overview:
            Import statements.

        Returns:
            - statements (:obj:`Tuple[ImportStatement, ...]`): Tuple of import statements.
        """
        return self.__imports.imports

    # noinspection PyMethodMayBeStatic
    def unprocessable(self):
        """
        Overview:
            Raise an exception ``UnprocessableError``.
            Announce that the current rule cannot express this value.
        """
        unprocessable()

    @contextmanager
    def transaction(self):
        """
        Overview:
            Open up an atomic transaction context.
            If exception is thrown in this context, all the update in this \
            addon object will be undone.

        Example:
            >>> with addon.transaction():
            >>>     addon.rule(1)
            >>>     addon.val([1, 2])
            >>>     addon.obj(json)
            >>>     raise RuntimeError  # the changes above will be undone
        """
        _state = copy.deepcopy(self.__getstate__())
        try:
            yield self
        except Exception as err:
            self.__setstate__(_state)
            raise err

    def __getstate__(self):
        """
        Overview:
            Get state value of this object.

        Returns:
            - state: State value.
        """
        return self.__imports, self.__rule

    def __setstate__(self, state):
        """
        Overview:
            Set state value of this object.

        Arguments:
            - state: State value.
        """
        self.__imports, self.__rule = state
