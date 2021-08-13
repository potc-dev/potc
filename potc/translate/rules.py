import re
from functools import wraps
from itertools import chain

from ..utils import dynamic_call


class UnprocessableError(Exception):
    pass


def unprocessable():
    raise UnprocessableError()


_NAME_PATTERN = re.compile('^[a-zA-Z0-9_]+$')
_TRACED_RULE_TAG = '__traced_rule__'
_RULE_NAME_TAG = '__rule_name__'


def _rule_trace(rule):
    if getattr(rule, _TRACED_RULE_TAG, False):
        return rule

    @wraps(rule)
    def _new_rule(*args, **kwargs):
        return rule(*args, **kwargs), _get_rule_name(rule)

    setattr(_new_rule, _TRACED_RULE_TAG, True)
    setattr(_new_rule, _RULE_NAME_TAG, _get_rule_name(rule))
    return _new_rule


_PRESERVED_NAMES = {'globals', "<chain>"}


def rule_rename(name: str):
    if not _NAME_PATTERN.fullmatch(name):
        raise NameError(f'Rule name should match {repr(_NAME_PATTERN.pattern)}, but {repr(name)} found.')
    if name in _PRESERVED_NAMES:
        raise NameError(f'Rule name {repr(name)} is preserved, please change another name.')

    def _decorator(rule):
        @wraps(rule)
        def _new_rule(*args, **kwargs):
            return rule(*args, **kwargs)

        setattr(_new_rule, _RULE_NAME_TAG, name)
        return _new_rule

    return _decorator


def _get_rule_name(rule):
    return getattr(rule, _RULE_NAME_TAG, None) or rule.__name__


_INCLUDED_RULE_NAMES_TAG = '__included_rule_names__'


def rules_chain(*rules):
    rules = [_rule_trace(r) for r in rules]
    names = sorted(chain(
        filter(lambda x: x != '<chain>', map(_get_rule_name, rules)),
        *map(lambda t: getattr(t, _INCLUDED_RULE_NAMES_TAG, []),
             filter(lambda x: _get_rule_name(x) == '<chain>', rules)),
    ))
    duplicate_names = sorted(set(map(lambda p: p[0], filter(lambda p: p[0] == p[1], zip(names[:-1], names[1:])))))
    if duplicate_names:
        raise KeyError(f'Duplicate names found in rule chain - {", ".join(map(repr, duplicate_names))}.')

    @dynamic_call
    def _new_rule(v, addon):
        for _rule_item in map(dynamic_call, rules):
            try:
                with addon.transaction():
                    _result, _name = _rule_item(v, addon)
            except UnprocessableError:
                continue
            else:
                return str(_result), _name

        unprocessable()

    setattr(_new_rule, _TRACED_RULE_TAG, True)
    setattr(_new_rule, _RULE_NAME_TAG, '<chain>')
    setattr(_new_rule, _INCLUDED_RULE_NAMES_TAG, names)
    return _new_rule
