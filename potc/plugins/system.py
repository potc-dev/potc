from ..rules import Addons, AddonProxy, rule


@rule()
def system_addon_proxy(v: AddonProxy, addon: Addons):
    addon.is_type(v, AddonProxy)
    with addon.transaction():
        return str(v)


system_all = [
    system_addon_proxy,
]
