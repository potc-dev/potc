from functools import wraps
from typing import Union, Tuple

import click
from hbutils.reflection import dynamic_call

from ...fixture.addons import Addons
from ...fixture.common import is_rule, rule, rule_name
from ...rules import builtin_all


def validator(func):
    func = dynamic_call(func)

    @wraps(func)
    def _new_func(ctx, param, value):
        return func(ctx=ctx, param=param, value=value)

    return _new_func


def multiple_validator(func):
    func = validator(func)

    @wraps(func)
    def _new_func(ctx, param, value):
        return [func(ctx, param, item) for item in value]

    return _new_func


_EXPECTED_TREE_ERRORS = (
    ValueError, TypeError, ImportError, AttributeError, ModuleNotFoundError,
    FileNotFoundError, IsADirectoryError, PermissionError, FileExistsError,
)

_EXCEPTION_WRAPPED = '__exception_wrapped__'


def err_validator(types: Union[type, Tuple[type, ...]]):
    def _decorator(func):
        func = validator(func)

        @wraps(func)
        def _new_func(ctx, param, value):
            try:
                return func(ctx, param, value)
            except click.BadParameter as err:
                raise err
            except types as err:
                _messages = [item for item in err.args if isinstance(item, str)]
                _final_message = _messages[0] if _messages else str(_messages)
                raise click.BadParameter(_final_message)

        return _new_func

    return _decorator


def _cli_builder(base_cli, *wrappers):
    _cli = None or base_cli
    for wrapper in wrappers:
        _cli = wrapper(_cli)
    return _cli


def _is_rule_rules(v):
    if is_rule(v):
        return True
    elif isinstance(v, (list, tuple)):
        return all(map(_is_rule_rules, v))
    else:
        return False


@rule()
def rules_rule(v, addon: Addons):
    if is_rule(v):
        return f'<{rule_name(v)}>'
    else:
        addon.unprocessable()


@rule(type_=list)
def rules_list(v, addon: Addons):
    if _is_rule_rules(v):
        return '[' + ', '.join(map(addon.rule, v)) + ']'
    else:
        addon.unprocessable()


@rule(type_=tuple)
def rule_tuple(v, addon: Addons):
    if _is_rule_rules(v):
        return '(' + ' --> '.join(map(addon.rule, v)) + ')'
    else:
        addon.unprocessable()


rules_struct = [
    (
        (rules_rule, rule_tuple, rules_list),
        builtin_all
    )
]
