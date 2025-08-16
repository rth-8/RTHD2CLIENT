from PIL import Image
import requests
from io import BytesIO
from bungie_api import AmmoType

BASE_URL = "https://www.bungie.net"

class CharacterData:
    def __init__(self) -> None:
        self.className = "n/a"
        self.emblemIconPath = None
        self.emblemPicturePath = None
        self.emblemHash = None
        self.emblemColor_R = 0
        self.emblemColor_G = 0
        self.emblemColor_B = 0
        self.weapon1: WeaponData = None
        self.weapon2: WeaponData = None
        self.weapon3: WeaponData = None

    def set_bg_color(self):
        response = requests.get(f"{BASE_URL}{self.emblemIconPath}")
        img = Image.open(BytesIO(response.content))
        img = img.quantize(colors=4, kmeans=4).convert('RGB')
        n_dom_colors = 4
        dom_colors = sorted(img.getcolors(2 ** 24), reverse=True)[:n_dom_colors]
        self.emblemColor_R = dom_colors[0][1][0]
        self.emblemColor_G = dom_colors[0][1][1]
        self.emblemColor_B = dom_colors[0][1][2]


class WeaponData:
    def __init__(self) -> None:
        self.icon = ""
        self.name = ""
        self.tierAndType = ""
        self.ammoType: AmmoType = AmmoType.NoType
