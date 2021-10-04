import importlib
import types
from typing import Optional, Tuple


def try_import_info(obj, alias: Optional[str] = None) -> Tuple[str, ...]:
    """
    Overview:
        Try to get an import statement from given object.

    Arguments:
        - obj (:obj:`object`): Given object.
        - alias (:obj:`Optional[str]`): Alias name for import statement, \
            default is ``None`` which means do not alias.

    Returns:
        - import (:obj:`Tuple[str, ...]`): Import statement tuple.

    Example:
        >>> import dill
        >>> try_import_info(dill)  # ('import', 'dill')
        >>>
        >>> from potc import translate_vars
        >>> try_import_info(translate_vars)  # ('from', 'potc', 'import', 'translate_vars')
    """
    try:
        _simple = _raw_import_info(obj)
        _segments = _simple[1].split('.')
        if _simple[0] == 'import':
            combiner = lambda i: '.'.join([*_segments[:i], _segments[-1]])
            rg = range(0, len(_segments))
        else:
            combiner = lambda i: '.'.join(_segments[:i])
            rg = range(1, len(_segments) + 1)

        _simpler = lambda i: (_simple[0], combiner(i), *_simple[2:])
        for index in rg:
            _sp = _simpler(index)
            try:
                if _validate_import_info(*_sp) is obj:
                    return (*_sp, *(('as', alias) if alias else ()))
            except (TypeError, ImportError, AttributeError, ModuleNotFoundError):
                continue
        raise TypeError(f'Unable to import {repr(obj)}, validate fail.')
    except (TypeError, ImportError, AttributeError, ModuleNotFoundError):
        raise TypeError(f'Unable to import {repr(obj)}, error occurred when trying to trace.')


def _raw_import_info(obj):
    if isinstance(obj, types.ModuleType):
        _segments = obj.__name__.split('.')
        if len(_segments) > 1:
            return 'from', '.'.join(_segments[:-1]), 'import', _segments[-1]
        else:
            return 'import', obj.__name__
    elif hasattr(obj, '__module__') and hasattr(obj, '__name__'):
        return 'from', obj.__module__, 'import', obj.__name__
    else:
        raise TypeError(f'Unable to import {repr(obj)}.')


def _validate_import_info(*args):
    if args[0] == 'from':
        module = importlib.import_module(args[1])
        return getattr(module, args[3])
    elif args[0] == 'import':
        return importlib.import_module(args[1])
