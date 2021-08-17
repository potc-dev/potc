from ..rules import builtin_all, installed_all, system_all
from ..fixture import rules_combine, build_chain


def raw_make_rule(rules=None):
    return rules_combine(*build_chain(rules or []))


def make_rule(extern=None):
    _rule_args = (system_all, [(extern or []), installed_all, builtin_all])
    return raw_make_rule(_rule_args)
