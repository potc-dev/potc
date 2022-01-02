import warnings
from itertools import chain
from string import Template
from typing import List, Tuple, Union, Iterable

import click
from hbutils.reflection import quick_import_object, iter_import_objects

from .base import CONTEXT_SETTINGS, _is_rule_block
from .utils import validator, err_validator, multiple_validator
from ...translate import transvars


@err_validator((ImportError,))
@multiple_validator
@validator
def validate_rules(value: str):
    rule, _, _ = quick_import_object(value, _is_rule_block)
    return rule


@err_validator((ImportError, ValueError,))
@multiple_validator
@validator
def validate_value(value: str):
    try:
        name, target = value.split('=', maxsplit=1)
    except ValueError:
        name, target = '$name', value

    result = []
    np = Template(name)
    for _object, _, _full_name in iter_import_objects(target):
        _name = _full_name[::-1].split('.', maxsplit=1)[0][::-1]
        result.append((np.safe_substitute(dict(name=_name)), _object))

    return result


def _is_reformatter(item):
    return isinstance(item, (dict, str)) or callable(item)


@validator
def validate_reformat(value: str):
    try:
        _object, _, _ = quick_import_object(value, _is_reformatter)
    except ImportError:
        return value
    else:
        return _object


def _export_cli(cli: click.Group):
    @cli.command('export', help='Export existing python items to runnable source code.',
                 context_settings=CONTEXT_SETTINGS)
    @click.option('-r', '--rules', 'rules', type=click.UNPROCESSED, callback=validate_rules, multiple=True,
                  default=[], help='External rules definition.')
    @click.option('-v', '--value', 'items', type=click.UNPROCESSED, callback=validate_value, multiple=True,
                  help='Value to be exported, such as \'mypackage.subpack.var1\'.')
    @click.option('-f', '--reformat', 'reformat', type=click.UNPROCESSED, callback=validate_reformat, show_default=True,
                  default='google', help='Code reformatter afterwards.')
    @click.option('-F', '--no-reformat', 'no_reformat', is_flag=True, default=False,
                  help='No reformat to the exported code, -f option will be ignored.')
    def _export(items: List[Iterable[Tuple[str, object]]], rules: List[object],
                reformat: Union[str, object], no_reformat: bool):
        items = list(chain(*items))
        dvars = {}
        for name, obj in items:
            if name in dvars.keys():
                warnings.warn(UserWarning(f'Duplicate name {repr(name)} with value {repr(obj)} '
                                          f'found in -v option, and it will be ignored.'))
            else:
                dvars[name] = obj

        reformat = None if no_reformat else reformat
        _result = transvars(dvars, trans=rules, reformat=reformat)
        click.secho(_result)

    return cli
