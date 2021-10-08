from .trans import autotrans, ObjectTranslation, VarsTranslation


def transobj(obj, trans=None) -> ObjectTranslation:
    """
    Overview:
        Process-oriented version of :meth:`potc.translate.trans.BaseTranslator.transobj`.

    Arguments:
        - obj: Object to be translated.
        - trans: Translator to be used, default is ``None`` which means use \
            an instance of :class:'potc.translate.trans.Translator'.

    Returns:
        - result (:obj:`ObjectTranslation`): Result of object translation.

    Examples::
        >>> import math
        >>> t = transobj([1, '2', 3.4, ..., None, math.e])
        >>> t
        <potc.translate.trans.ObjectTranslation object at 0x7f08a9520f10>
        >>> t.code
        "[1, '2', 3.4, ..., None, math.e]"
        >>> t.imports
        (<_SelfDirectImport 'import math'>,)
    """
    return autotrans(trans).transobj(obj)


def transvars(vars_, trans=None, reformat=None, isort: bool = True) -> VarsTranslation:
    """
    Overview:
        Process-oriented version of :meth:`potc.translate.trans.BaseTranslator.transvars`.

    Arguments:
        - vars\_ (:obj:`Mapping[str, Any]`): Variables to be translated.
        - trans: Translator to be used, default is ``None`` which means use \
            an instance of :class:'potc.translate.trans.Translator'.
        - reformat: Reformatter for the final source code, default is ``None`` which means \
            do not reformat the code.
        - isort (:obj:`bool`): Sort the import statements, default is ``True``.

    Returns:
        - result (:obj:`VarsTranslation`): Result of vars translation.

    Examples::
        >>> import math
        >>> t = transvars({
        ...     'a': [1, '2', 3.4, ..., None, math.e],
        ...     'b': dict(a='ds', b=(), c={3, 4, 5}),
        ... })
        >>> t
        <potc.translate.trans.VarsTranslation object at 0x7f08a95cd5b0>
        >>> print(t.code)
        import math
        __all__ = ['a', 'b']
        a = [1, '2', 3.4, ..., None, math.e]
        b = {'a': 'ds', 'b': (), 'c': {3, 4, 5}}
    """
    return autotrans(trans).transvars(vars_, reformat, isort)
