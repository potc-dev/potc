import os
from itertools import chain
from typing import Mapping, Any, Tuple

from isort import code as sort_code_imports
from yapf.yapflib.yapf_api import FormatCode

from .make import make_both_rules
from ..fixture import UnprocessableError, Addons


class TranslationFailed(Exception):
    def __init__(self, obj):
        Exception.__init__(self, f'Translating failed for {repr(obj)}.')
        self.__obj = obj

    @property
    def obj(self):
        return self.__obj


def translate_object(obj, extern=None) -> Tuple[str, Addons, str]:
    _rule, _plain_rule = make_both_rules(extern)
    addon = Addons(rule=_plain_rule)
    try:
        _code, _trace_name = _rule(obj, addon)
        return _code.strip(), addon, _trace_name
    except UnprocessableError:
        raise TranslationFailed


def _translate_vars(vars_: Mapping[str, Any], extend_rules=None):
    codes, addons = [], []
    for key, value in sorted(vars_.items()):
        _code, _addon, _ = translate_object(value, extend_rules)
        codes.append((key, _code))
        addons.append(_addon)

    _imports = sorted(set(chain(*map(lambda x: x.import_items, addons))), key=lambda x: x.key)
    return _imports, codes


def translate_vars(vars_: Mapping[str, Any], extend_rules=None, reformat=None, isort: bool = True) -> str:
    actual_vars = dict(vars_)
    actual_vars.update(dict(__all__=sorted(vars_.keys())))
    _import_lines, _assignments = _translate_vars(actual_vars, extend_rules)
    _assignment_lines = [f'{key} = {code}' for key, code in _assignments]

    _code = os.linesep.join(list(map(str, chain(_import_lines, _assignment_lines))))

    if isort:
        _code = sort_code_imports(_code)
    if reformat is not None:
        if hasattr(reformat, '__call__'):
            _code = reformat(_code)
        else:
            _code, _ = FormatCode(_code, style_config=reformat)
    return _code
