from typing import Tuple, List

import click
from hbutils.reflection import quick_import_object

from .base import CONTEXT_SETTINGS, _is_rule_block
from .utils import validator, err_validator, multiple_validator, rules_struct
from ...translate import transobj


@err_validator((ImportError,))
@multiple_validator
@validator
def validate_rules(value: str):
    rule, _, _ = quick_import_object(value, _is_rule_block)
    return rule


@err_validator((ImportError,))
@validator
def validate_input(value: str):
    return quick_import_object(value)


def _trans_cli(cli: click.Group):
    @cli.command('trans', help='Translate existing python object to visible code.',
                 context_settings=CONTEXT_SETTINGS)
    @click.option('-r', '--rules', 'rules', type=click.UNPROCESSED, callback=validate_rules, multiple=True,
                  default=[], help='External rules definition.')
    @click.option('-I', '--information', is_flag=True, default=False,
                  help='Show detailed information of imported object.')
    @click.argument('input_', type=click.UNPROCESSED, callback=validate_input)
    def _trans(input_: Tuple[object, str, str], rules: List[object], information: bool):
        _obj, _module, _name = input_
        _type = type(_obj)
        _result = transobj(_obj, trans=rules)

        if information:
            click.secho(click.style('Object Information:', fg='blue'))
            if _module:
                click.secho(f'Module : {_module}')
            click.secho(f'Name : {_name}')
            click.secho(f'Type : {_type.__qualname__}')
            if rules:
                click.secho('External Rules :')
                click.secho(transobj(rules, trans=rules_struct).code)
            click.secho()

            import_list = sorted(set(_result.imports), key=lambda x: x.key)
            if import_list:
                click.secho(click.style('Import Statements:', fg='cyan'))
                for imp in import_list:
                    click.secho(str(imp))
                click.secho()

            click.secho(click.style('Expression:', fg='green'))
            click.secho(_result)
            click.secho()
        else:
            click.secho(_result)

    return cli
