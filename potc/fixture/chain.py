from functools import reduce
from itertools import product
from operator import __or__
from typing import Union, Callable, List, Tuple, Optional

from hbutils.algorithm import topoids
from hbutils.reflection import dynamic_call

from .common import is_rule, rule_name, unprocessable, UnprocessableError


def build_chain(c: Union[List, Tuple, Callable],
                id_gen: Optional[Callable] = None) -> List[Callable]:
    """
    Overview:
        Build chain of the rules.
        Bases on orders which depends by tuples and lists.

    Arguments:
        - c (:obj:`Union[List, Tuple, Callable]`): Rule structure object, can be a list, \
            tuple or rule, or the nested structure of them.
        - id_gen (:obj:`Optional[Callable]`): Id generator of the rules, default is ``None`` \
            which means ``id`` function.

    Returns:
        - chain (:obj:`List[Callable]`): List of the rules in order.

    Example:
        >>> build_chain(r1)                        # [r1]
        >>> build_chain([(r1, r2), (r3, r2)])      # [r1, r3, r2] or [r3, r1, r2]
        >>> build_chain((r1, [r2, (r3, r4)], r5))  # [r1, r2, r3, r4, r5] or [r1, r3, r2, r4, r5] or [r1, r3, r4, r2, r5]
    """
    id_gen = id_gen or id
    rules = {}
    edges = set()

    def _rule_walk(ci: Union[List, Tuple, Callable]):
        if is_rule(ci):
            rules[id_gen(ci)] = ci
            return {id_gen(ci)}, {id_gen(ci)}, {id_gen(ci)}
        elif isinstance(ci, tuple):
            children = list(filter(lambda x: x[0], map(_rule_walk, ci)))
            if not children:
                return set(), set(), set()

            for (_, _, _lasts), (_, _firsts, _) in zip(children[:-1], children[1:]):
                for _last, _first in product(_lasts, _firsts):
                    edges.add((_last, _first))

            _all_ids = reduce(__or__, map(lambda x: x[0], children))
            _, _first_ids, _ = children[0]
            _, _, _last_ids = children[-1]
            return _all_ids, _first_ids, _last_ids
        elif isinstance(ci, list):
            children = list(filter(lambda x: x[0], map(_rule_walk, ci)))
            if not children:
                return set(), set(), set()

            _all_ids = reduce(__or__, map(lambda x: x[0], children))
            _first_ids = reduce(__or__, map(lambda x: x[1], children))
            _last_ids = reduce(__or__, map(lambda x: x[2], children))
            return _all_ids, _first_ids, _last_ids
        else:
            raise TypeError(f'Unknown element type in rule chain, '
                            f'list, tuple or decorated rule expected '
                            f'but {repr(type(ci).__name__)} found.')

    _rule_walk(c)

    all_ids = set(rules.keys())
    count = len(all_ids)
    _name_to_id = dict(map(lambda x: (rule_name(x), id_gen(x)), rules.values()))
    _names = sorted(set(map(lambda x: rule_name(x), rules.values())))

    if len(_names) < count:
        _duplicated_names = tuple(sorted(set(
            map(lambda x: x[0], filter(lambda x: x[0] == x[1], zip(_names[:-1], _names[1:])))
        )))
        raise NameError(f'Duplicate rule names in the chain - {repr(_duplicated_names)}.')

    _name_to_index = {name: nid for nid, name in enumerate(_names)}
    _id_to_index = {_name_to_id[name]: _name_to_index[name] for name in _names}
    _index_to_id = {_name_to_index[name]: _name_to_id[name] for name in _names}
    new_edges = set(map(lambda x: (_id_to_index[x[0]], _id_to_index[x[1]]), edges))

    try:
        order = topoids(count, new_edges)
    except ArithmeticError as err:
        _, conflict_indices = err.args
        _index_to_name = {nid: name for nid, name in enumerate(_names)}
        conflicted_names = tuple(sorted(map(lambda x: _index_to_name[x], conflict_indices)))
        raise ArithmeticError(
            f'Conflicted order with in {repr(conflicted_names)}.',
            tuple(map(lambda x: (x, rules[_index_to_id[_name_to_index[x]]]), conflicted_names)),
        )
    return [rules[_index_to_id[oid]] for oid in order]


def rules_combine(*rules):
    """
    Overview:
        Combined the ordered rule list to be a executable rule-like function (but not a rule object actually).

    Arguments:
        - rules: List of the rules (may be the result of function ``build_chain``.

    Returns:
        - func: Combined rule function.
    """
    for r in rules:
        if not is_rule(r):
            raise TypeError(f"Not a rule - {repr(r)}.")
    names = sorted(map(rule_name, rules))
    if len(set(names)) < len(names):
        duplicate_names = sorted(set(
            map(lambda p: p[0], filter(lambda p: p[0] == p[1], zip(names[:-1], names[1:])))
        ))
        raise KeyError(f'Duplicate names found in rule chain - {", ".join(map(repr, duplicate_names))}.')

    def _new_rule(v, addon):
        with addon.transaction():
            for _rule_item in map(dynamic_call, rules):
                try:
                    with addon.transaction():
                        _result = _rule_item(v, addon)
                except UnprocessableError:
                    continue
                else:
                    return str(_result), rule_name(_rule_item)

            unprocessable()

    return _new_rule
