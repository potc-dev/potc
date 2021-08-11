import importlib
import types


def try_import_info(obj, alias=None):
    try:
        _simple = _raw_import_info(obj)
        _sentence = (*_simple, *(('as', alias) if alias else ()))
        _actual = _validate_import_info(*_sentence)
    except (TypeError, ImportError, AttributeError, ModuleNotFoundError):
        raise TypeError(f'Unable to import {repr(obj)}, error occurred when trying to trace.')

    if _actual is obj:
        return _sentence
    else:
        raise TypeError(f'Unable to import {repr(obj)}, validate fail.')


def _raw_import_info(obj):
    if not hasattr(obj, '__module__') and isinstance(obj, types.ModuleType):
        return 'import', obj.__name__
    elif hasattr(obj, '__module__') and hasattr(obj, '__name__'):
        if isinstance(obj, types.ModuleType):
            return 'import', f'{obj.__module__}.{obj.__name__}'
        else:
            return 'from', obj.__module__, 'import', obj.__name__
    else:
        raise TypeError(f'Unable to import {repr(obj)}.')


def _validate_import_info(*args):
    if args[0] == 'from':
        module = importlib.import_module(args[1])
        return getattr(module, args[3])
    elif args[0] == 'import':
        return importlib.import_module(args[1])
