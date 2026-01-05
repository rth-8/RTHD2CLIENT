from bungie_api import ItemSubType, DamageType, AmmoType

################################################################################
class ItemData:
    def __init__(self) -> None:
        self.hash = 0
        self.instanceId = 0
        self.power = 0
        self.tier = 0
        self.state = 0
        self.icon = ""
        self.seasonOverlayIcon = ""
        self.name = ""
        self.tierAndType = ""


################################################################################
class WeaponData(ItemData):
    def __init__(self) -> None:
        super().__init__()
        self.ammoType: AmmoType = AmmoType.NoType
        self.damageType: DamageType = DamageType.NoType


################################################################################
class ArmorData(ItemData):
    def __init__(self) -> None:
        super().__init__()
        self.subtype = ItemSubType.NoType
        self.archetype = ""
        self.stat_health  = 0
        self.stat_melee   = 0
        self.stat_grenade = 0
        self.stat_super   = 0
        self.stat_class   = 0
        self.stat_weapons = 0
        self.pattern = "000000"

    def total(self):
        return (self.stat_health +
                self.stat_melee +
                self.stat_grenade +
                self.stat_super +
                self.stat_class +
                self.stat_weapons)

    def get_str1(self):
        return (f"{str(self.hash):15}"
              + f"{str(self.instanceId):25}"
              + f"{self.archetype:15}"
              + f"T{str(self.tier):5}"
              + f"{str(self.stat_health):5}"
              + f"{str(self.stat_melee):5}"
              + f"{str(self.stat_grenade):5}"
              + f"{str(self.stat_super):5}"
              + f"{str(self.stat_class):5}"
              + f"{str(self.stat_weapons):5}"
              + f"{self.pattern:10}"
            #   + f"{self.name}"
              )
