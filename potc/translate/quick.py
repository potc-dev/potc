from .trans import autotrans, ObjectTranslation, VarsTranslation


def transobj(obj, trans=None) -> ObjectTranslation:
    return autotrans(trans).transobj(obj)


def transvars(vars_, trans=None, reformat=None, isort: bool = True) -> VarsTranslation:
    return autotrans(trans).transvars(vars_, reformat, isort)
