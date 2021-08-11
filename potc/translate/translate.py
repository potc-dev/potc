import os
from itertools import chain
from typing import Mapping, Any, Tuple

from yapf.yapflib.yapf_api import FormatCode

from .addons import Addons
from .builtins import builtins_
from .plugins import plugins_
from .rules import UnprocessableError, rules_chain


class TranslationFailed(Exception):
    def __init__(self, obj):
        Exception.__init__(self, f'Translating failed for {repr(obj)}.')
        self.__obj = obj

    @property
    def obj(self):
        return self.__obj


def translate_object(obj, extend_rules=None) -> Tuple[str, Addons, str]:
    ext_ = rules_chain(*(extend_rules or []))
    final_ = rules_chain(ext_, plugins_, builtins_)

    addon = Addons(rule=final_)
    try:
        _code, _trace_name = final_(obj, addon)
        return _code.strip(), addon, _trace_name
    except UnprocessableError:
        raise TranslationFailed


def _translate_vars(vars_: Mapping[str, Any], extend_rules=None):
    codes, addons = [], []
    for key, value in sorted(vars_.items()):
        _code, _addon, _ = translate_object(value, extend_rules)
        codes.append((key, _code))
        addons.append(_addon)

    _imports = sorted(set(chain(*map(lambda x: x.imports, addons))), key=lambda x: x.key)
    return _imports, codes


def translate_vars(vars_: Mapping[str, Any], extend_rules=None) -> str:
    actual_vars = dict(vars_)
    actual_vars.update(dict(__all__=sorted(vars_.keys())))
    _import_lines, _assignments = _translate_vars(actual_vars, extend_rules)
    _assignment_lines = [f'{key} = {code}' for key, code in _assignments]

    _code = os.linesep.join(list(map(str, chain(_import_lines, _assignment_lines))))
    _code, _ = FormatCode(_code)
    return _code
