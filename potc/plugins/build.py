from .builtin import builtin_all
from .installed import installed_all
from .system import system_all
from ..rules import rules_combine, build_chain


def rule_build(extern=None):
    _rule_args = (system_all, [(extern or []), installed_all, builtin_all])
    return rules_combine(*build_chain(_rule_args))
