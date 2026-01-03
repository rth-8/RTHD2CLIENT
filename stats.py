# Standalone script for analysis of instanced items stats
# Some functions used by application for finding duplicates

import os
import json
import pandas as pd
from bungie_api import CharacterStats, ItemSubType


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


def print_item(list, max, max_stat):
    print(f"{str(list[0]):15}"
        + f"{list[1]:25}"
        + f"{list[2]:15}"
        + f"{str(list[3]):5}"
        + f"{str(list[4]):5}"
        + f"{str(list[5]):5}"
        + f"{str(list[6]):5}"
        + f"{str(list[7]):5}"
        + f"{str(list[8]):5}"
        + f"{str(list[9]):5}"
        + f"{str(list[10]):10}"
        + f"max: {str(max)} ({str(max_stat)})")


def files_for_armor_type(type):
    dir = ""
    match type:
        case ItemSubType.ArmorHelmet:    dir = "./cache/helmets"
        case ItemSubType.ArmorGauntlets: dir = "./cache/gauntlets"
        case ItemSubType.ArmorChest:     dir = "./cache/chests"
        case ItemSubType.ArmorLegs:      dir = "./cache/legs"
        case ItemSubType.ArmorClassItem: dir = "./cache/class_items"
        case _: raise Exception("Unexpected armor type!")
    # dir = "./cache/titan_exotic_class_items/"
    files = list(filter(lambda item: item.startswith("user_profile_inv_instance_") and item.endswith(".json"), os.listdir(dir)))
    return dir, files


def extract_instances(dir, files):
    lol = []
    for file_name in files:
        path_name = f"{dir}/{file_name}"
        with open(path_name, 'r') as file:
            # load data
            data = json.load(file)
            # extract data
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
            # create pattern
            ptrn = []
            ptrn.append('1' if stat_health >  0 else '0')
            ptrn.append('1' if stat_melee >   0 else '0')
            ptrn.append('1' if stat_grenade > 0 else '0')
            ptrn.append('1' if stat_super >   0 else '0')
            ptrn.append('1' if stat_class >   0 else '0')
            ptrn.append('1' if stat_weapons > 0 else '0')
            pattern = "".join(ptrn)
            # make row
            row = []
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
            row.append(pattern)
            print_item(row, max, max_stat)
            lol.append(row)
    return lol


def find_duplicates(lol, use_archetype=True):
    size = len(lol)
    dupes = []
    for i in range(0, size-1, 1):
        for j in range(i, size, 1):
            if lol[i][1] == lol[j][1]:
                # skip comparison of same instances
                continue
            # Comparison:
            # 1. item (hash) (idx 0)
            # 2. archetype (idx 2)
            # 3. pattern (idx 10)
            item1 = None
            item2 = None
            if use_archetype:
                if lol[i][0]  == lol[j][0] and lol[i][2]  == lol[j][2] and lol[i][10] == lol[j][10]:
                    item1 = lol[i]
                    item2 = lol[j]
            else:
                if lol[i][0]  == lol[j][0] and lol[i][10] == lol[j][10]:
                    item1 = lol[i]
                    item2 = lol[j]
            if item1 and item2:
                print("-----------------------------------------")
                print_item(item1, 0, "")
                print_item(item2, 0, "")
                # print DIM query
                dupe = f"id:{item1[1]} or id:{item2[1]}"
                print(dupe)
                dupes.append(dupe)
    return dupes


#################################################################################################################################

if __name__ == '__main__':

    dir, files = files_for_armor_type(ItemSubType.ArmorHelmet)
    # dir, files = files_for_armor_type(ItemSubType.ArmorClassItem)
    if len(files) == 0:
        print("No instanced items found!")
        exit(0)


    list_of_lists = extract_instances(dir, files)


    duplicates = find_duplicates(list_of_lists)
    # duplicates = find_duplicates(list_of_lists, False)
    print(f"Found {len(duplicates)} duplicates")


    with open("duplicates.log", 'w') as file:
        for dupe in duplicates:
            file.write(dupe)
            file.write('\n')


    df = pd.DataFrame(list_of_lists, 
        columns=["hash", "id", "archetype", "tier", "health", "melee", "grenade", "super", "class", "weapons", "pattern"])
    # print(df)

    # print(df.loc[ df["melee"] == 25])
    # print(df.loc[ df["archetype"] == "Paragon"])
    # print(df.loc[ df["tier"] == 5])
    # print(df.loc[(df["tier"] == 5) & (df["archetype"] == "Paragon")])
    print(df.loc[ (df["archetype"] == "Specialist") & df["pattern"] == "010011"])

