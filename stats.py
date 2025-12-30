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


def get_stat(data, stat: CharacterStats, max, max_stat: CharacterStats, reduce):
    value = int(data["Response"]["stats"]["data"]["stats"][str(stat.value)]["value"])
    new_max = value if value > max else max
    new_stat = stat if value > max else max_stat
    new_reduce = value if value > 0 and value < 10 else reduce
    return value, new_max, new_stat, new_reduce


dir = "./cache/"
files = list(filter(lambda item: item.startswith("user_profile_inv_instance_") and item.endswith(".json"), os.listdir(dir)))

list_of_lists = []

for file_name in files:
    path_name = f"{dir}{file_name}"
    with open(path_name, 'r') as file:
        data = json.load(file)
        row = []
        tier = int(data["Response"]["instance"]["data"]["gearTier"])
        # Ignore tier-less items from before Armor 3.0
        if tier == 0:
            continue
        hash = data["Response"]["item"]["data"]["itemHash"]
        instance_id = data["Response"]["item"]["data"]["itemInstanceId"]
        max = 0
        max_stat = None
        reduce = 0
        stat_health,  max, max_stat, reduce = get_stat(data, CharacterStats.Health,  max, max_stat, reduce)
        stat_melee,   max, max_stat, reduce = get_stat(data, CharacterStats.Melee,   max, max_stat, reduce)
        stat_grenade, max, max_stat, reduce = get_stat(data, CharacterStats.Grenade, max, max_stat, reduce)
        stat_super,   max, max_stat, reduce = get_stat(data, CharacterStats.Super,   max, max_stat, reduce)
        stat_class,   max, max_stat, reduce = get_stat(data, CharacterStats.Class,   max, max_stat, reduce)
        stat_weapons, max, max_stat, reduce = get_stat(data, CharacterStats.Weapons, max, max_stat, reduce)
        # reduce stats to base level before any upgrade
        stat_health -= reduce
        stat_melee -= reduce
        stat_grenade -= reduce
        stat_super -= reduce
        stat_class -= reduce
        stat_weapons -= reduce
        archetype = map_archetype(max_stat)
        print(f"{str(hash):15}"
            + f"{instance_id:25}"
            + f"{archetype:15}"
            + f"{str(tier):5}"
            + f"{str(stat_health):5}"
            + f"{str(stat_melee):5}"
            + f"{str(stat_grenade):5}"
            + f"{str(stat_super):5}"
            + f"{str(stat_class):5}"
            + f"{str(stat_weapons):5}"
            + f"max: {str(max)} ({str(max_stat)})")
        row.append(hash)
        row.append(instance_id)
        row.append(archetype)
        row.append(tier)
        row.append(stat_health)
        row.append(stat_melee)
        row.append(stat_grenade)
        row.append(stat_super)
        row.append(stat_class)
        row.append(stat_weapons)
        list_of_lists.append(row)

df = pd.DataFrame(list_of_lists, columns=["hash", "id", "archetype", "tier", "health", "melee", "grenade", "super", "class", "weapons"])
# print(df)

# print(df.loc[ df["melee"] == 25])
# print(df.loc[ df["archetype"] == "Paragon"])
# print(df.loc[ df["tier"] == 5])
print(df.loc[(df["tier"] == 5) & (df["archetype"] == "Paragon")])
