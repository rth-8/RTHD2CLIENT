from user_data import UserData
from character_data import CharacterData
from bungie_api import ItemState, DamageType, AmmoType
import base64


BASE_URL = "https://www.bungie.net"

ammo_type_icons = {
    AmmoType.Normal: "html/ammo_primary.png",
    AmmoType.Special: "html/ammo_special.png",
    AmmoType.Heavy: "html/ammo_heavy.png",
}

damage_type_icons = {
    DamageType.Kinetic: "html/damage_type_kinetic.png",
    DamageType.Arc: "html/damage_type_arc.png",
    DamageType.Solar: "html/damage_type_solar.png",
    DamageType.Void: "html/damage_type_void.png",
    DamageType.Stasis: "html/damage_type_stasis.png",
    DamageType.Strand: "html/damage_type_strand.png",
}

ammo_type_icons_raw_data = {}
damage_type_icons_raw_data = {}


def load_local_image(path):
    with open(path, "rb") as file:
        print(f"Loading local image: {path}")
        raw = file.read()
        data = base64.b64encode(raw).decode("utf-8")
        return data


def load_local_images():
    for key in ammo_type_icons.keys():
        ammo_type_icons_raw_data[key] = load_local_image(ammo_type_icons[key])
    for key in damage_type_icons.keys():
        damage_type_icons_raw_data[key] = load_local_image(damage_type_icons[key])


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
        # General:
        character_idx = f"{characterData.idx}"
        # Title:
        character_details_emblem = f"{BASE_URL}{characterData.emblemLarge}"
        character_details_icon = f"{BASE_URL}{characterData.emblemIconTransparent}"
        character_class_name = f"{characterData.className}"
        # Weapons:
        weapon1_icon = f"{BASE_URL}{characterData.equipedWeapons[0].icon}"
        weapon2_icon = f"{BASE_URL}{characterData.equipedWeapons[1].icon}"
        weapon3_icon = f"{BASE_URL}{characterData.equipedWeapons[2].icon}"
        weapon1_season_overlay = f"{BASE_URL}{characterData.equipedWeapons[0].seasonOverlayIcon}"
        weapon2_season_overlay = f"{BASE_URL}{characterData.equipedWeapons[1].seasonOverlayIcon}"
        weapon3_season_overlay = f"{BASE_URL}{characterData.equipedWeapons[2].seasonOverlayIcon}"
        weapon1_name = characterData.equipedWeapons[0].name
        weapon2_name = characterData.equipedWeapons[1].name
        weapon3_name = characterData.equipedWeapons[2].name
        weapon1_type = characterData.equipedWeapons[0].tierAndType
        weapon2_type = characterData.equipedWeapons[1].tierAndType
        weapon3_type = characterData.equipedWeapons[2].tierAndType
        weapon1_ammo_type = "data:image/png;base64," + ammo_type_icons_raw_data[AmmoType(characterData.equipedWeapons[0].ammoType)]
        weapon2_ammo_type = "data:image/png;base64," + ammo_type_icons_raw_data[AmmoType(characterData.equipedWeapons[1].ammoType)]
        weapon3_ammo_type = "data:image/png;base64," + ammo_type_icons_raw_data[AmmoType(characterData.equipedWeapons[2].ammoType)]
        weapon1_damage_type = "data:image/png;base64," + damage_type_icons_raw_data[DamageType(characterData.equipedWeapons[0].damageType)]
        weapon2_damage_type = "data:image/png;base64," + damage_type_icons_raw_data[DamageType(characterData.equipedWeapons[1].damageType)]
        weapon3_damage_type = "data:image/png;base64," + damage_type_icons_raw_data[DamageType(characterData.equipedWeapons[2].damageType)]
        if characterData.equipedWeapons[0].state & ItemState.Masterwork.value:
            weapon1_border_style = "item_masterworked"
        else:
            weapon1_border_style = "item_normal"
        if characterData.equipedWeapons[1].state & ItemState.Masterwork.value:
            weapon2_border_style = "item_masterworked"
        else:
            weapon2_border_style = "item_normal"
        if characterData.equipedWeapons[2].state & ItemState.Masterwork.value:
            weapon3_border_style = "item_masterworked"
        else:
            weapon3_border_style = "item_normal"
        # Style:
        styles = load_styles()
        page = content.format(**locals())
    # print(f"Page:\n{page}")
    return page
