import re
from collections import namedtuple
from functools import wraps
from typing import Callable, Type, Union, Tuple

from ..utils import dynamic_call


class UnprocessableError(Exception):
    pass


def unprocessable():
    raise UnprocessableError()


RuleInfo = namedtuple('RuleInfo', ['name', 'origin'])

_RULE_TAG = '__rule__'
_NAME_PATTERN = re.compile('^[a-zA-Z0-9_]+$')


def rule(alias=None, type_: Union[Type, Tuple[Type, ...], None] = None):
    def _decorator(func: Callable):
        if is_rule(func):
            _name = alias or rule_name(func)
            return rule(_name, type_)(rule_origin(func))
        else:
            _name = alias or func.__name__
            _actual_func = dynamic_call(func)
            if not _NAME_PATTERN.fullmatch(_name):
                raise NameError(f'Invalid rule name, '
                                f'{repr(_NAME_PATTERN.pattern)} expected but {repr(_name)} found.')

            @wraps(func)
            def _new_func(v, addon):
                if type_ is not None and not isinstance(v, type_):
                    unprocessable()
                with addon.transaction():
                    return _actual_func(v, addon)

            setattr(_new_func, _RULE_TAG, RuleInfo(_name, func))
            return _new_func

    return _decorator


def is_rule(func: Callable) -> bool:
    return isinstance(getattr(func, _RULE_TAG, None), RuleInfo)


def rule_name(func: Callable) -> str:
    return getattr(func, _RULE_TAG).name


def rule_origin(func: Callable) -> Callable:
    return getattr(func, _RULE_TAG).origin
