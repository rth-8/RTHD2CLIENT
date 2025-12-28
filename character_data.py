from bungie_api import CharacterClass, CharacterStas, ItemState, ItemType, ItemSubType, DamageType, AmmoType

BASE_URL = "https://www.bungie.net"


################################################################################
class ItemData:
    def __init__(self) -> None:
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


################################################################################
class CharacterData:
    def __init__(self, idx) -> None:
        self.idx = idx
        self.className = "n/a"
        self.emblemIcon = None
        self.emblemSmall = None
        self.emblemIconTransparent = None
        self.emblemLarge = None
        self.subclassType: DamageType = DamageType.NoType
        self.subclassIcon = None
        self.stats = {}
        self.equipedWeapons: WeaponData = []
        self.equipedArmor = {}


    def clear(self):
        self.equipedWeapons.clear()
        self.equipedArmor.clear()


    def process_info_json(self, d):
        self.emblemIcon = d["Response"]["character"]["data"]["emblemPath"]
        self.emblemSmall = d["Response"]["character"]["data"]["emblemBackgroundPath"]
        self.className = CharacterClass(d["Response"]["character"]["data"]["classType"]).name
        stats = d["Response"]["character"]["data"]["stats"]
        self.stats[CharacterStas.Power] = stats[f"{CharacterStas.Power.value}"]
        self.stats[CharacterStas.Health] = stats[f"{CharacterStas.Health.value}"]
        self.stats[CharacterStas.Melee] = stats[f"{CharacterStas.Melee.value}"]
        self.stats[CharacterStas.Grenade] = stats[f"{CharacterStas.Grenade.value}"]
        self.stats[CharacterStas.Super] = stats[f"{CharacterStas.Super.value}"]
        self.stats[CharacterStas.Class] = stats[f"{CharacterStas.Class.value}"]
        self.stats[CharacterStas.Weapons] = stats[f"{CharacterStas.Weapons.value}"]


    def _add_weapon(self, d, state):
        w = WeaponData()
        w.state = state
        w.icon = d["Response"]["displayProperties"]["icon"]
        w.seasonOverlayIcon = d["Response"]["iconWatermark"]
        w.name = d["Response"]["displayProperties"]["name"]
        w.tierAndType = d["Response"]["itemTypeAndTierDisplayName"]
        if d["Response"]["itemType"] == ItemType.Weapon.value:
            w.ammoType = d["Response"]["equippingBlock"]["ammoType"]
            w.damageType = d["Response"]["defaultDamageType"]
        # print weapon info:
        print(f"Weapon: {w.name} ({w.state}), ammo type {w.ammoType}, dmg type {w.damageType}")
        if w.state & ItemState.Locked.value:
            print(" - locked")
        if w.state & ItemState.Masterwork.value:
            print(" - masterworked")
        if w.state & ItemState.Crafted.value:
            print(" - crafted")
        # Note: equiped items have game order, so first weapon in json data is weapon in first (primary) slot
        self.equipedWeapons.append(w)


    def _add_armor(self, d, state):
        sub_type = ItemSubType(d["Response"]["itemSubType"])
        a = ArmorData()
        a.state = state
        a.icon = d["Response"]["displayProperties"]["icon"]
        a.seasonOverlayIcon = d["Response"]["iconWatermark"]
        a.name = d["Response"]["displayProperties"]["name"]
        a.tierAndType = d["Response"]["itemTypeAndTierDisplayName"]
        self.equipedArmor[sub_type] = a


    def process_item_json(self, d, state):
        type = d["Response"]["itemType"]
        if type == ItemType.Subclass.value:
            # NOTE: Character Subclass is retrieved as equiped item (part of equiped items list)
            self.subclassType = DamageType(d["Response"]["talentGrid"]["hudDamageType"])
            self.subclassIcon = d["Response"]["displayProperties"]["icon"]
            # TODO: Subclass icon is now loaded from bungie site, 
            # but in future it might be loaded from local image (see pages.py, e.g. ammo type icons).
            # For this purpose subclassType is also stored.
        elif type == ItemType.Weapon.value:
            self._add_weapon(d, state)
        elif type == ItemType.Armor.value:
            self._add_armor(d, state)
        elif type == ItemType.Emblem.value:
            self.emblemIconTransparent = d["Response"]["secondaryOverlay"]
            self.emblemLarge = d["Response"]["secondarySpecial"]

