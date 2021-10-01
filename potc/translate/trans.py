import os
import re
from abc import ABCMeta
from itertools import chain
from typing import Tuple, Mapping, Any

from isort import code as sort_code_imports
from yapf.yapflib.yapf_api import FormatCode

from .base import make_both_rules
from ..fixture import Addons, UnprocessableError
from ..fixture.imports import ImportStatement
from ..rules import installed_loader, system_all, default_all, native_all


class TranslationFailed(Exception):
    def __init__(self, obj):
        Exception.__init__(self, f'Translating failed for {repr(obj)}.')
        self.__obj = obj

    @property
    def obj(self):
        return self.__obj


class ObjectTranslation:
    def __init__(self, code, addon, trace):
        self.__code = code
        self.__addon = addon
        self.__trace = trace

    @property
    def code(self) -> str:
        return self.__code

    @property
    def addon(self) -> Addons:
        return self.__addon

    @property
    def trace(self) -> str:
        return self.__trace

    @property
    def imports(self) -> Tuple[ImportStatement, ...]:
        return self.addon.import_items

    def __str__(self):
        return self.__code

    def __iter__(self):
        yield self.__code
        yield self.__addon
        yield self.__trace


class VarsTranslation:
    def __init__(self, code: str, addons: Mapping[str, Addons]):
        self.__code = code
        self.__addons = addons

    @property
    def code(self) -> str:
        return self.__code

    @property
    def addons(self) -> Mapping[str, Addons]:
        return self.__addons

    def __str__(self) -> str:
        return self.__code

    def __iter__(self):
        yield self.__code
        yield self.__addons


_VARS_KEY_PATTERN = re.compile(r'^[_a-zA-Z][_0-9a-zA-Z]*$')


class _AbstractTranslator(metaclass=ABCMeta):
    def __init__(self, rules):
        self.__rule, self.__plain_rule = make_both_rules(rules)

    def transobj(self, obj) -> ObjectTranslation:
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

    def transvars(self, vars_: Mapping[str, Any], reformat=None, isort: bool = True):
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
    def __init__(self, extend_rules=None):
        _AbstractTranslator.__init__(self, (system_all, extend_rules or [], default_all))


class BlankTranslator(BaseTranslator):
    def __init__(self, extend_rules=None):
        BaseTranslator.__init__(self, [(extend_rules or []), native_all])


class Translator(BlankTranslator):
    def __init__(self, extend_rules=None):
        BlankTranslator.__init__(self, [(extend_rules or []), installed_loader()])


def autotrans(trans):
    if isinstance(trans, BaseTranslator):
        return trans
    elif isinstance(trans, type) and issubclass(trans, BaseTranslator):
        return trans()
    else:
        return Translator(trans)
