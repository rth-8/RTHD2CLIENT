import base64

from bungie_api import CharacterStats, AmmoType, DamageType

stat_icons = {
    CharacterStats.Health: "html/stat_health.png",
    CharacterStats.Melee: "html/stat_melee.png",
    CharacterStats.Grenade: "html/stat_grenade.png",
    CharacterStats.Super: "html/stat_super.png",
    CharacterStats.Class: "html/stat_class.png",
    CharacterStats.Weapons: "html/stat_weapons.png",
}

stat_icons_black = {
    CharacterStats.Health: "html/stat_health_black.png",
    CharacterStats.Melee: "html/stat_melee_black.png",
    CharacterStats.Grenade: "html/stat_grenade_black.png",
    CharacterStats.Super: "html/stat_super_black.png",
    CharacterStats.Class: "html/stat_class_black.png",
    CharacterStats.Weapons: "html/stat_weapons_black.png",
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

def load_local_image(path: str) -> str:
    with open(path, "rb") as file:
        print(f"Loading local image: {path}")
        raw = file.read()
        data = base64.b64encode(raw).decode("utf-8")
        return data

def load_local_images():
    global class_titan_icon_raw_data
    global class_hunter_icon_raw_data
    global class_warlock_icon_raw_data
    global stat_icons_b64_white
    global stat_icons_b64_black
    global ammo_type_icons_raw_data
    global damage_type_icons_raw_data
    global refresh_button_icon_raw_data
    global back_button_icon_raw_data
    global shaped_overlay_icon_raw_data
    # Classes
    class_titan_icon_raw_data = load_local_image("html/class_titan.png")
    class_hunter_icon_raw_data = load_local_image("html/class_hunter.png")
    class_warlock_icon_raw_data = load_local_image("html/class_warlock.png")
    # Stats
    for key in stat_icons.keys():
        raw = load_local_image(stat_icons[key])
        stat_icons_b64_white[key] = "data:image/png;base64," + raw
        raw = load_local_image(stat_icons_black[key])
        stat_icons_b64_black[key] = "data:image/png;base64," + raw
    # Ammo types
    for key in ammo_type_icons.keys():
        ammo_type_icons_raw_data[key] = load_local_image(ammo_type_icons[key])
    # Damage types
    for key in damage_type_icons.keys():
        damage_type_icons_raw_data[key] = load_local_image(damage_type_icons[key])
    # General
    refresh_button_icon_raw_data = load_local_image("html/refresh.png")
    back_button_icon_raw_data = load_local_image("html/back.png")
    shaped_overlay_icon_raw_data = load_local_image("html/shaped_overlay.png")

# Images:

class_titan_icon_raw_data = None
class_hunter_icon_raw_data = None
class_warlock_icon_raw_data = None

stat_icons_b64_white = {}
stat_icons_b64_black = {}

ammo_type_icons_raw_data = {}
damage_type_icons_raw_data = {}

refresh_button_icon_raw_data = None
back_button_icon_raw_data = None

shaped_overlay_icon_raw_data = None
