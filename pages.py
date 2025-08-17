from user_data import UserData
from character_data import CharacterData

BASE_URL = "https://www.bungie.net"

ammo_type_icons = [
    "n/a",
    "https://www.bungie.net/common/destiny2_content/icons/99f3733354862047493d8550e46a45ec.png",
    "https://www.bungie.net/common/destiny2_content/icons/d920203c4fd4571ae7f39eb5249eaecb.png",
    "https://www.bungie.net/common/destiny2_content/icons/78ef0e2b281de7b60c48920223e0f9b1.png",
]

def load_styles():
    styles = ""
    with open("html/styles.css", mode="r") as file:
        styles = file.read()
    return styles


def get_page_user_info(userData: UserData, charactersDataList):
    print("Create info page...")
    page = "<head></head><body><h1>:(</h1></body>"
    with open("html/profile.html", mode="r") as file:
        content = file.read()
        profile_icon = f"{BASE_URL}/{userData.profilePicturePath}"
        display_name = f"{userData.displayName}"
        display_name_code = f"{userData.displayNameCode}"
        character1_class = f"{charactersDataList[0].className}"
        character1_emblem = f"{BASE_URL}{charactersDataList[0].emblemSmall}"
        character2_class = f"{charactersDataList[1].className}"
        character2_emblem = f"{BASE_URL}{charactersDataList[1].emblemSmall}"
        character3_class = f"{charactersDataList[2].className}"
        character3_emblem = f"{BASE_URL}{charactersDataList[2].emblemSmall}"
        styles = load_styles()
        page = content.format(**locals())
    # print(f"Page:\n{page}")
    return page


def get_page_character(characterData: CharacterData):
    print("Create character page...")
    page = "<head></head><body><h1>:(</h1></body>"
    with open("html/character.html", mode="r") as file:
        content = file.read()
        # Title:
        charcter_details_emblem = f"{BASE_URL}{characterData.emblemLarge}"
        character_details_icon = f"{BASE_URL}{characterData.emblemIconTransparent}"
        character_class_name = f"{characterData.className}"
        # Weapons:
        weapon1_icon = f"{BASE_URL}{characterData.equipedWeapons[0].icon}"
        weapon2_icon = f"{BASE_URL}{characterData.equipedWeapons[1].icon}"
        weapon3_icon = f"{BASE_URL}{characterData.equipedWeapons[2].icon}"
        weapon1_name = characterData.equipedWeapons[0].name
        weapon2_name = characterData.equipedWeapons[1].name
        weapon3_name = characterData.equipedWeapons[2].name
        weapon1_type = characterData.equipedWeapons[0].tierAndType
        weapon2_type = characterData.equipedWeapons[1].tierAndType
        weapon3_type = characterData.equipedWeapons[2].tierAndType
        weapon1_ammo_type = ammo_type_icons[characterData.equipedWeapons[0].ammoType]
        weapon2_ammo_type = ammo_type_icons[characterData.equipedWeapons[1].ammoType]
        weapon3_ammo_type = ammo_type_icons[characterData.equipedWeapons[2].ammoType]
        # Style:
        styles = load_styles()
        page = content.format(**locals())
    # print(f"Page:\n{page}")
    return page
