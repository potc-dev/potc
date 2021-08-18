from functools import wraps

from ..fixture import rules_combine, build_chain
from ..rules import builtin_all, installed_all, system_all


def raw_make_rule(rules=None):
    return rules_combine(*build_chain(rules or []))


def make_rule(extern=None):
    _rule_args = (system_all, [(extern or []), installed_all, builtin_all])
    return raw_make_rule(_rule_args)


def make_both_rules(extern=None):
    _rule = make_rule(extern)

    @wraps(_rule)
    def _plain_rule(*args, **kwargs):
        _value, _ = _rule(*args, **kwargs)
        return _value

    return _rule, _plain_rule


def make_plain_rule(extern=None):
    _, _plain_rule = make_both_rules(extern)
    return _plain_rule
