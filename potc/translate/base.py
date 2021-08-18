from functools import wraps

from ..fixture import rules_combine, build_chain


def make_rule(rules=None):
    return rules_combine(*build_chain(rules or []))


def make_both_rules(rules=None):
    _rule = make_rule(rules)

    @wraps(_rule)
    def _plain_rule(*args, **kwargs):
        _value, _ = _rule(*args, **kwargs)
        return _value

    return _rule, _plain_rule
