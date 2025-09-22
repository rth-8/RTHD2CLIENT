from user_data import UserData
from character_data import CharacterData
from bungie_api import CharacterStas, ItemState, ItemSubType, DamageType, AmmoType
import base64


BASE_URL = "https://www.bungie.net"

stat_icons = {
    CharacterStas.Health: "html/stat_health.png",
    CharacterStas.Melee: "html/stat_melee.png",
    CharacterStas.Grenade: "html/stat_grenade.png",
    CharacterStas.Super: "html/stat_super.png",
    CharacterStas.Class: "html/stat_class.png",
    CharacterStas.Weapons: "html/stat_weapons.png",
}

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

stat_icons_raw_data = {}
ammo_type_icons_raw_data = {}
damage_type_icons_raw_data = {}


def load_local_image(path: str) -> str:
    with open(path, "rb") as file:
        print(f"Loading local image: {path}")
        raw = file.read()
        data = base64.b64encode(raw).decode("utf-8")
        return data


def load_local_images():
    for key in stat_icons.keys():
        stat_icons_raw_data[key] = load_local_image(stat_icons[key])
    for key in ammo_type_icons.keys():
        ammo_type_icons_raw_data[key] = load_local_image(ammo_type_icons[key])
    for key in damage_type_icons.keys():
        damage_type_icons_raw_data[key] = load_local_image(damage_type_icons[key])


refresh_button_icon_raw_data = load_local_image("html/refresh.png")
back_button_icon_raw_data = load_local_image("html/back.png")


def load_file(path):
    content = ""
    with open(path, mode="r") as file:
        content = file.read()
    return content


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
        styles = load_file("html/styles.css")
        page = content.format(**locals())
    # print(f"Page:\n{page}")
    return page


def _getWeapon(characterData: CharacterData, idx):
    icon = f"{BASE_URL}{characterData.equipedWeapons[idx].icon}"
    season_overlay = f"{BASE_URL}{characterData.equipedWeapons[idx].seasonOverlayIcon}"
    name = characterData.equipedWeapons[idx].name
    type = characterData.equipedWeapons[idx].tierAndType
    ammo_type = "data:image/png;base64," + ammo_type_icons_raw_data[AmmoType(characterData.equipedWeapons[idx].ammoType)]
    damage_type = "data:image/png;base64," + damage_type_icons_raw_data[DamageType(characterData.equipedWeapons[idx].damageType)]
    if characterData.equipedWeapons[idx].state & ItemState.Masterwork.value:
        border_style = "item_masterworked"
    else:
        border_style = "item_normal"
    return icon, season_overlay, name, type, ammo_type, damage_type, border_style


def _getArmorPiece(characterData: CharacterData, subtype: ItemSubType.ArmorHelmet):
    icon = f"{BASE_URL}{characterData.equipedArmor[subtype].icon}"
    season_overlay = f"{BASE_URL}{characterData.equipedArmor[subtype].seasonOverlayIcon}"
    name = characterData.equipedArmor[subtype].name
    type = characterData.equipedArmor[subtype].tierAndType
    if characterData.equipedArmor[subtype].state & ItemState.Masterwork.value:
        border_style = "item_masterworked"
    else:
        border_style = "item_normal"
    return icon, season_overlay, name, type, border_style


def get_page_character(characterData: CharacterData):
    print("Create character page...")
    page = "<head></head><body><h1>:(</h1></body>"
    with open("html/character.html", mode="r") as file:
        content = file.read()
        # General:
        character_idx = f"{characterData.idx}"
        refresh_button_image = "data:image/png;base64," + refresh_button_icon_raw_data
        back_button_image = "data:image/png;base64," + back_button_icon_raw_data
        # Title:
        character_details_emblem = f"{BASE_URL}{characterData.emblemLarge}"
        character_details_icon = f"{BASE_URL}{characterData.emblemIconTransparent}"
        character_class_name = f"{characterData.className}"
        # Stats:
        character_subclass_icon = f"{BASE_URL}{characterData.subclassIcon}"
        character_stat_power = characterData.stats[CharacterStas.Power]
        stat_health_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Health]
        stat_melee_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Melee]
        stat_grenade_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Grenade]
        stat_super_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Super]
        stat_class_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Class]
        stat_weapons_icon = "data:image/png;base64," + stat_icons_raw_data[CharacterStas.Weapons]
        character_stat_health = characterData.stats[CharacterStas.Health]
        character_stat_melee = characterData.stats[CharacterStas.Melee]
        character_stat_grenade = characterData.stats[CharacterStas.Grenade]
        character_stat_super = characterData.stats[CharacterStas.Super]
        character_stat_class = characterData.stats[CharacterStas.Class]
        character_stat_weapons = characterData.stats[CharacterStas.Weapons]
        # Weapons:
        weapon1_icon, weapon1_season_overlay, weapon1_name, weapon1_type, weapon1_ammo_type, weapon1_damage_type, weapon1_border_style = \
            _getWeapon(characterData, 0)
        weapon2_icon, weapon2_season_overlay, weapon2_name, weapon2_type, weapon2_ammo_type, weapon2_damage_type, weapon2_border_style = \
            _getWeapon(characterData, 1)
        weapon3_icon, weapon3_season_overlay, weapon3_name, weapon3_type, weapon3_ammo_type, weapon3_damage_type, weapon3_border_style = \
            _getWeapon(characterData, 2)
        # Armor:
        helmet_icon, helmet_season_overlay, helmet_name, helmet_type, helmet_border_style = \
            _getArmorPiece(characterData, ItemSubType.ArmorHelmet)
        gauntlets_icon, gauntlets_season_overlay, gauntlets_name, gauntlets_type, gauntlets_border_style = \
            _getArmorPiece(characterData, ItemSubType.ArmorGauntlets)
        chest_icon, chest_season_overlay, chest_name, chest_type, chest_border_style = \
            _getArmorPiece(characterData, ItemSubType.ArmorChest)
        legs_icon, legs_season_overlay, legs_name, legs_type, legs_border_style = \
            _getArmorPiece(characterData, ItemSubType.ArmorLegs)
        classitem_icon, classitem_season_overlay, classitem_name, classitem_type, classitem_border_style = \
            _getArmorPiece(characterData, ItemSubType.ArmorClassItem)
        # Style:
        styles = load_file("html/styles.css")
        functions = load_file("html/functions.js")
        page = content.format(**locals())
    # print(f"Page:\n{page}")
    return page
