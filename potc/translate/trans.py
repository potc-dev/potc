import os
import re
from abc import ABCMeta
from itertools import chain
from typing import Tuple, Mapping, Any, Type, Union

from isort import code as sort_code_imports
from yapf.yapflib.yapf_api import FormatCode

from .base import make_both_rules
from ..fixture import Addons, UnprocessableError
from ..fixture.imports import ImportStatement
from ..rules import installed_loader, system_all, default_all, native_all


class TranslationFailed(Exception):
    """
    Overview:
        Exception when translation is failed.
    """

    def __init__(self, obj):
        """
        Overview:
            Constructor of :class:`TranslationFailed`.

        Arguments:
            - obj: Object which is failed to be translated.

        """
        Exception.__init__(self, f'Translating failed for {repr(obj)}.')
        self.__obj = obj

    @property
    def obj(self):
        """
        Overview:
            The object which is failed to be translated.
        """
        return self.__obj


class ObjectTranslation:
    """
    Overview:
        Result of object translation.
    """

    def __init__(self, code: str, addon: Addons, trace: str):
        """
        Overview:
            Constructor of :class:`ObjectTranslation`.

        Arguments:
            - code (:obj:`str`): String translated code.
            - addon (:obj:`Addons`): Addon object for this translation.
            - trace (:obj:`str`): Rule name for the translated object.
        """
        self.__code = code
        self.__addon = addon
        self.__trace = trace

    @property
    def code(self) -> str:
        """
        Overview:
            String translated code.
        """
        return self.__code

    @property
    def addon(self) -> Addons:
        """
        Overview:
            Addon object for this translation.
        """
        return self.__addon

    @property
    def trace(self) -> str:
        """
        Overview:
            Rule name for the translated object.
        """
        return self.__trace

    @property
    def imports(self) -> Tuple[ImportStatement, ...]:
        """
        Overview:
            Import statements of this translation.
        """
        return self.addon.import_items

    def __str__(self):
        """
        Overview:
            Just get the string code, such as for the :func:`print` function.
        """
        return self.__code

    def __iter__(self):
        """
        Overview:
            Iterate this object.

        Examples::
            >>> ot = ObjectTranslation(cc, aa, tt)
            >>> c, a, t = ot
            >>> assert c is cc
            >>> assert a is aa
            >>> assert t is tt
        """
        yield self.__code
        yield self.__addon
        yield self.__trace


class VarsTranslation:
    """
    Overview:
        Result of vars translation.
    """

    def __init__(self, code: str, addons: Mapping[str, Addons]):
        """
        Overview:
            Constructor of :class:`VarsTranslation`.

        Arguments:
            - code (:obj:`str`): String translated code.
            - addons (:obj:`Mapping[str, Addons]`): Addon objects for the sub translations.
        """
        self.__code = code
        self.__addons = addons

    @property
    def code(self) -> str:
        """
        Overview:
            String translated code.
        """
        return self.__code

    @property
    def addons(self) -> Mapping[str, Addons]:
        """
        Overview:
            Addon objects for the sub translations.
        """
        return self.__addons

    def __str__(self) -> str:
        """
        Overview:
            Just get the string code, such as for the :func:`print` function.
        """
        return self.__code

    def __iter__(self):
        """
        Overview:
            Iterate this object.

        Examples::
            >>> ot = VarsTranslation(cc, aa)
            >>> c, a = ot
            >>> assert c is cc
            >>> assert a is aa
        """
        yield self.__code
        yield self.__addons


_VARS_KEY_PATTERN = re.compile(r'^[_a-zA-Z][_0-9a-zA-Z]*$')


class _AbstractTranslator(metaclass=ABCMeta):
    def __init__(self, rules):
        """
        Overview:
            Constructor of :class:`_AbstractTranslator`.

        Arguments:
            - rules: Rules for translator.
        """
        self.__rule, self.__plain_rule = make_both_rules(rules)

    def transobj(self, obj) -> ObjectTranslation:
        """
        Overview:
            Do translation to the given object ``obj``.

        Arguments:
            - obj: Object to be translated.

        Returns:
            - result (:obj:`ObjectTranslation`): Result of object translation.
        """
        addon = Addons(self.__plain_rule)
        try:
            _code, _trace_name = self.__rule(obj, addon)
            return ObjectTranslation(_code.strip(), addon, _trace_name)
        except UnprocessableError:
            raise TranslationFailed(obj)

    def __transvars(self, vars_: Mapping[str, Any]):
        codes, addons = [], []
        for key, value in sorted(vars_.items()):
            _result = self.transobj(value)
            _code, _addon = _result.code, _result.addon
            codes.append((key, _code))
            addons.append((key, _addon))

        _imports = sorted(set(chain(*map(lambda x: x[1].import_items, addons))), key=lambda x: x.key)
        return _imports, codes, addons

    def transvars(self, vars_: Mapping[str, Any], reformat=None, isort: bool = True) -> VarsTranslation:
        r"""
        Overview:
            Do translation to the given variables ``vars_``, and create a runnable code.

        Arguments:
            - vars\_ (:obj:`Mapping[str, Any]`): Variables to be translated.
            - reformat: Reformatter for the final source code, default is ``None`` which means \
                do not reformat the code.
            - isort (:obj:`bool`): Sort the import statements, default is ``True``.

        Returns:
            - result (:obj:`VarsTranslation`): Result of vars translation.
        """
        actual_vars = dict(vars_)
        for key in actual_vars.keys():
            if not _VARS_KEY_PATTERN.fullmatch(key):
                raise NameError(f'Invalid variable name - {repr(key)}.')

        actual_vars.update(dict(__all__=sorted(vars_.keys())))
        _import_lines, _assignments, _addons = self.__transvars(actual_vars)

        _assignment_lines = [f'{key} = {code}' for key, code in _assignments]
        _code = os.linesep.join(list(map(str, chain(_import_lines, _assignment_lines))))

        if isort:
            _code = sort_code_imports(_code)
        if reformat is not None:
            if callable(reformat):
                _code = reformat(_code)
            else:
                _code, _ = FormatCode(_code, style_config=reformat)
        return VarsTranslation(_code, dict(_addons))


class BaseTranslator(_AbstractTranslator):
    """
    Overview:
        Base translator for the common translation cases.

        This class is based on :class:`_AbstractTranslator`, contains only \
        system-leveled and default object-leveled translation rules.
    """

    def __init__(self, extend_rules=None):
        """
        Overview:
            Constructor of :class:`BaseTranslator`.

        Arguments:
            - extend_rules: Rules for base translator.
        """
        _AbstractTranslator.__init__(self, (system_all, extend_rules or [], default_all))


class BlankTranslator(BaseTranslator):
    """
    Overview:
        Blank translator for the common translation cases.

        This class is based on :class:`BaseTranslator`, contains all the native rules \
        in this project. May be the best choice for DIY and testings.

    .. note::

        The rules from the plugins will be not be here, \
        and will certainly not be applied when translation is processed.
    """

    def __init__(self, extend_rules=None):
        """
        Overview:
            Constructor of :class:`BlankTranslator`.

        Arguments:
            - extend_rules: Rules for base translator.
        """
        BaseTranslator.__init__(self, [(extend_rules or []), native_all])


class Translator(BlankTranslator):
    """
    Overview:
        Common translator for the common translation cases.

        This class is based on :class:`BlankTranslator`, contains all the \
        rules from the installed plugins. It is the best choice for being used directly.
    """

    def __init__(self, extend_rules=None):
        """
        Overview:
            Constructor of :class:`Translator`.

        Arguments:
            - extend_rules: Rules for base translator.
        """
        BlankTranslator.__init__(self, [(extend_rules or []), installed_loader()])


def autotrans(trans: Union[BaseTranslator, Type[BaseTranslator], list, tuple]) -> BaseTranslator:
    """
    Overview:
        Turn the given object ``trans`` to a :class:`BaseTranslator` instance.

    Arguments:
        - trans (:obj:`Union[BaseTranslator, Type[BaseTranslator], list, tuple]`): \
            Any object to be transformed to :class:`BaseTranslator` instance.

    Returns:
        - translator (:obj:`BaseTranslator`): Translator instance which can be directly used.

    """
    if isinstance(trans, BaseTranslator):
        return trans
    elif isinstance(trans, type) and issubclass(trans, BaseTranslator):
        return trans()
    else:
        return Translator(trans)
