# Standalone script for analysis of instanced items stats

import os
import json
import pandas as pd
from bungie_api import CharacterStats


def map_archetype(stat: CharacterStats):
    match stat:
        case CharacterStats.Health: return "Bulwark"
        case CharacterStats.Melee: return "Brawler"
        case CharacterStats.Grenade: return "Grenadier"
        case CharacterStats.Super: return "Paragon"
        case CharacterStats.Class: return "Specialist"
        case CharacterStats.Weapons: return "Gunner"
        case _: return "???"


def get_stat_and_max(data, stat: CharacterStats, max, max_stat: CharacterStats):
    value = int(data["Response"]["stats"]["data"]["stats"][str(stat.value)]["value"])
    new_max = value if value > max else max
    new_stat = stat if value > max else max_stat
    return value, new_max, new_stat


dir = "./cache/"
files = list(filter(lambda item: item.startswith("user_profile_inv_instance_") and item.endswith(".json"), os.listdir(dir)))

for file_name in files:
    path_name = f"{dir}{file_name}"
    with open(path_name, 'r') as file:
        data = json.load(file)
        hash = data["Response"]["item"]["data"]["itemHash"]
        max = 0
        max_stat = None
        stat_health,  max, max_stat = get_stat_and_max(data, CharacterStats.Health,  max, max_stat)
        stat_melee,   max, max_stat = get_stat_and_max(data, CharacterStats.Melee,   max, max_stat)
        stat_grenade, max, max_stat = get_stat_and_max(data, CharacterStats.Grenade, max, max_stat)
        stat_super,   max, max_stat = get_stat_and_max(data, CharacterStats.Super,   max, max_stat)
        stat_class,   max, max_stat = get_stat_and_max(data, CharacterStats.Class,   max, max_stat)
        stat_weapons, max, max_stat = get_stat_and_max(data, CharacterStats.Weapons, max, max_stat)
        archetype = map_archetype(max_stat)
        print(f"{str(hash):15}"
            + f"{archetype:15}"
            + f"{str(stat_health):5}"
            + f"{str(stat_melee):5}"
            + f"{str(stat_grenade):5}"
            + f"{str(stat_super):5}"
            + f"{str(stat_class):5}"
            + f"{str(stat_weapons):5}"
            + f"max: {str(max)} ({str(max_stat)})")
