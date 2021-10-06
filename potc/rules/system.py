from ..fixture import Addons, AddonProxy, rule


@rule(type_=AddonProxy)
def system_addon_proxy(v: AddonProxy, addon: Addons):
    with addon.transaction():
        return str(v)


#: Overview:
#:      Rules for potc system.
#:
#: Items:
#:      - :class:`potc.fixture.addons.AddonProxy`.
system_all = [
    system_addon_proxy,
]
