from bungie_api import CharacterClass, ItemType, AmmoType

BASE_URL = "https://www.bungie.net"

class WeaponData:
    def __init__(self) -> None:
        self.icon = ""
        self.name = ""
        self.tierAndType = ""
        self.ammoType: AmmoType = AmmoType.NoType


class CharacterData:
    def __init__(self) -> None:
        self.className = "n/a"
        self.emblemIcon = None
        self.emblemSmall = None
        self.emblemIconTransparent = None
        self.emblemLarge = None
        self.equipedWeapons: WeaponData = []


    def process_info_json(self, d):
        self.emblemIcon = d["Response"]["character"]["data"]["emblemPath"]
        self.emblemSmall = d["Response"]["character"]["data"]["emblemBackgroundPath"]
        self.className = CharacterClass(d["Response"]["character"]["data"]["classType"]).name


    def _add_weapon(self, d):
        w = WeaponData()
        w.icon = d["Response"]["displayProperties"]["icon"]
        w.name = d["Response"]["displayProperties"]["name"]
        w.tierAndType = d["Response"]["itemTypeAndTierDisplayName"]
        if d["Response"]["itemType"] == ItemType.Weapon.value:
            w.ammoType = d["Response"]["equippingBlock"]["ammoType"]
        # Note: equiped items have game order, so first weapon in json data is weapon in first (primary) slot
        self.equipedWeapons.append(w)


    def process_item_json(self, d, idx):
        type = d["Response"]["itemType"]

        if type == ItemType.Weapon.value:
            self._add_weapon(d)

        elif type == ItemType.Emblem.value:
            self.emblemIconTransparent = d["Response"]["secondaryOverlay"]
            self.emblemLarge = d["Response"]["secondarySpecial"]
