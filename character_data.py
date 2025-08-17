from PIL import Image
import requests
from io import BytesIO
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
        self.emblemIconPath = None
        self.emblemPicturePath = None
        self.emblemHash = None
        self.emblemColor_R = 0
        self.emblemColor_G = 0
        self.emblemColor_B = 0
        self.equipedWeapons: WeaponData = []


    def _set_bg_color(self):
        response = requests.get(f"{BASE_URL}{self.emblemIconPath}")
        img = Image.open(BytesIO(response.content))
        img = img.quantize(colors=4, kmeans=4).convert('RGB')
        n_dom_colors = 4
        dom_colors = sorted(img.getcolors(2 ** 24), reverse=True)[:n_dom_colors]
        self.emblemColor_R = dom_colors[0][1][0]
        self.emblemColor_G = dom_colors[0][1][1]
        self.emblemColor_B = dom_colors[0][1][2]


    def process_info_json(self, d):
        self.emblemIconPath = d["Response"]["character"]["data"]["emblemPath"]
        self.emblemPicturePath = d["Response"]["character"]["data"]["emblemBackgroundPath"]
        self.emblemHash = d["Response"]["character"]["data"]["emblemHash"]
        self.className = CharacterClass(d["Response"]["character"]["data"]["classType"]).name
        self._set_bg_color()


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
