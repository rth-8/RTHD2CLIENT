from bungie_api import CharacterClass, ItemState, ItemType, AmmoType

BASE_URL = "https://www.bungie.net"


################################################################################
class WeaponData:
    def __init__(self) -> None:
        self.state = 0
        self.icon = ""
        self.seasonOverlayIcon = ""
        self.name = ""
        self.tierAndType = ""
        self.ammoType: AmmoType = AmmoType.NoType


################################################################################
class CharacterData:
    def __init__(self, idx) -> None:
        self.idx = idx
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


    def _add_weapon(self, d, state):
        w = WeaponData()
        w.state = state
        w.icon = d["Response"]["displayProperties"]["icon"]
        w.seasonOverlayIcon = d["Response"]["iconWatermark"]
        w.name = d["Response"]["displayProperties"]["name"]
        w.tierAndType = d["Response"]["itemTypeAndTierDisplayName"]
        if d["Response"]["itemType"] == ItemType.Weapon.value:
            w.ammoType = d["Response"]["equippingBlock"]["ammoType"]
        # print weapon info:
        print(f"Weapon: {w.name} ({w.state})")
        if w.state & ItemState.Locked.value:
            print(" - locked")
        if w.state & ItemState.Masterwork.value:
            print(" - masterworked")
        if w.state & ItemState.Crafted.value:
            print(" - crafted")
        # Note: equiped items have game order, so first weapon in json data is weapon in first (primary) slot
        self.equipedWeapons.append(w)


    def process_item_json(self, d, state):
        type = d["Response"]["itemType"]
        if type == ItemType.Weapon.value:
            self._add_weapon(d, state)
        elif type == ItemType.Emblem.value:
            self.emblemIconTransparent = d["Response"]["secondaryOverlay"]
            self.emblemLarge = d["Response"]["secondarySpecial"]

