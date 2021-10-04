import re
from collections import namedtuple
from functools import wraps
from typing import Callable, Type, Union, Tuple, Optional

from hbutils.reflection import dynamic_call


class UnprocessableError(Exception):
    """
    Overview:
        Signal exception which means the rules before cannot process this data.
    """
    pass


def unprocessable():
    """
    Overview:
        Raise an ``UnprocessableError``.
    """
    raise UnprocessableError()


RuleInfo = namedtuple('RuleInfo', ['name', 'origin'])

_RULE_TAG = '__rule__'
_NAME_PATTERN = re.compile('^[a-zA-Z0-9_]+$')


def rule(alias: Optional[str] = None, type_: Union[Type, Tuple[Type, ...], None] = None):
    """
    Overview:
        Make a common function to a rule function.

    Arguments:
        - alias (:obj:`Optional[str]`): Alias name of this rule, default is ``None`` which means \
            just use the name of the wrapped function.
        - type\\_ (:obj:`Union[Type, Tuple[Type, ...], None]`): Type of the data, can be a type \
            or a tuple of types, default is ``None`` which means no type limit.

    Returns:
        - decorator: A function decorator of the raw rule function.

    Examples:
        There are some example from builtin part.

        - builtin_int (A very easy case)

        >>> @rule(type_=int)
        >>> def builtin_int(v: int):
        >>>     return repr(v)

        - builtin_float (A little complex case)

        >>> @rule(type_=float)
        >>> def builtin_float(v: float, addon: Addons):
        >>>     if math.isinf(v):
        >>>         return ('+' if v > 0 else '-') + str(addon.obj(math).inf)
        >>>     elif math.isnan(v):
        >>>         return addon.obj(math).nan
        >>>     else:
        >>>         if math.isclose(v, math.e):
        >>>             return addon.obj(math).e
        >>>         elif math.isclose(v, math.pi):
        >>>             return addon.obj(math).pi
        >>>         elif math.isclose(v, math.tau):
        >>>             return addon.obj(math).tau
        >>>         else:
        >>>             return repr(v)

    """

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
    """
    Overview:
        Check if a function is a potc rule.

    Arguments:
        - func (:obj:`Callable`): Function object.

    Returns:
        - is_rule (:obj:`bool`): Is a rule or not.

    Examples:
        >>> is_rule(builtin_int)            # True
        >>> is_rule(lambda x, addon: None)  # False
    """
    return isinstance(getattr(func, _RULE_TAG, None), RuleInfo)


def rule_name(rule_: Callable) -> str:
    """
    Overview:
        Name of the rule.

    Arguments:
        - rule\\_ (:obj:`Callable`): Rule object.

    Returns:
        - name (:obj:`str`): Name of the rule.

    Examples:
        >>> rule_name(builtin_int)  # 'builtin_int'
    """
    return getattr(rule_, _RULE_TAG).name


def rule_origin(rule_: Callable) -> Callable:
    """
    Overview:
        Original function of the rule.

    Arguments:
        - rule\\_ (:obj:`Callable`): Rule object.

    Returns:
        - func (:obj:`str`): Original function.
    """
    return getattr(rule_, _RULE_TAG).origin
