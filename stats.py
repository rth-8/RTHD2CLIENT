# Standalone script for analysis of instanced items stats
# Some functions used by application for finding duplicates

import os
import json
from bungie_api import CharacterStats, ItemSubType
from item_data import ArmorData
import constants


def map_archetype(stat: CharacterStats):
    match stat:
        case CharacterStats.Health: return "Bulwark"
        case CharacterStats.Melee: return "Brawler"
        case CharacterStats.Grenade: return "Grenadier"
        case CharacterStats.Super: return "Paragon"
        case CharacterStats.Class: return "Specialist"
        case CharacterStats.Weapons: return "Gunner"
        case _: return "???"


def map_armor_piece(hash):
    stype = ItemSubType.NoType
    name = "???"
    if hash in constants.helmets:
        stype = ItemSubType.ArmorHelmet
        name = constants.helmets.get(hash)
    elif hash in constants.gauntlets:
        stype = ItemSubType.ArmorGauntlets
        name = constants.gauntlets.get(hash)
    elif hash in constants.chests:
        stype = ItemSubType.ArmorChest
        name = constants.chests.get(hash)
    elif hash in constants.legs:
        stype = ItemSubType.ArmorLegs
        name = constants.legs.get(hash)
    elif hash in constants.class_items:
        stype = ItemSubType.ArmorClassItem
        name = constants.class_items.get(hash)
    # else:
    #     raise Exception("Unexpected armor type!")
    return stype, name


def get_stat(data, stat: CharacterStats, max, max_stat: CharacterStats):
    value = int(data["Response"]["stats"]["data"]["stats"][str(stat.value)]["value"])
    new_max = value if value > max else max
    new_stat = stat if value > max else max_stat
    return value, new_max, new_stat


def print_item(item, max, max_stat):
    print(item.get_str1(), f"max: {str(max)} ({str(max_stat)})")


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
    instances = []
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
            # make armor item
            item = ArmorData()
            item.hash = data["Response"]["item"]["data"]["itemHash"]
            item.subtype, item.name = map_armor_piece(item.hash)
            item.instanceId = data["Response"]["item"]["data"]["itemInstanceId"]
            item.power = data["Response"]["instance"]["data"]["primaryStat"]["value"]
            item.tier = tier
            item.state = data["Response"]["item"]["data"]["state"]
            # extract stats and find max
            max = 0
            max_stat = None
            item.stat_health,  max, max_stat = get_stat(data, CharacterStats.Health,  max, max_stat)
            item.stat_melee,   max, max_stat = get_stat(data, CharacterStats.Melee,   max, max_stat)
            item.stat_grenade, max, max_stat = get_stat(data, CharacterStats.Grenade, max, max_stat)
            item.stat_super,   max, max_stat = get_stat(data, CharacterStats.Super,   max, max_stat)
            item.stat_class,   max, max_stat = get_stat(data, CharacterStats.Class,   max, max_stat)
            item.stat_weapons, max, max_stat = get_stat(data, CharacterStats.Weapons, max, max_stat)
            item.archetype = map_archetype(max_stat)
            # create pattern
            ptrn = []
            ptrn.append('1' if item.stat_health >  10 else '0')
            ptrn.append('1' if item.stat_melee >   10 else '0')
            ptrn.append('1' if item.stat_grenade > 10 else '0')
            ptrn.append('1' if item.stat_super >   10 else '0')
            ptrn.append('1' if item.stat_class >   10 else '0')
            ptrn.append('1' if item.stat_weapons > 10 else '0')
            item.pattern = "".join(ptrn)
            # finalize
            print_item(item, max, max_stat)
            instances.append(item)
    return instances


def find_duplicates(instances, use_armor_set=True, use_archetype=True):
    size = len(instances)
    dupes = []
    for i in range(0, size-1, 1):
        for j in range(i, size, 1):
            if instances[i].instanceId == instances[j].instanceId:
                # skip comparison of same instances
                continue
            # Comparison:
            # 1. item (hash)
            # 2. archetype
            # 3. pattern
            idx1 = None
            idx2 = None
            if use_armor_set and use_archetype:
                if instances[i].hash == instances[j].hash and \
                   instances[i].archetype == instances[j].archetype and \
                   instances[i].pattern == instances[j].pattern:
                    idx1 = i
                    idx2 = j
            elif use_armor_set and not use_archetype:
                if instances[i].hash == instances[j].hash and \
                   instances[i].pattern == instances[j].pattern:
                    idx1 = i
                    idx2 = j
            elif not use_armor_set and use_archetype:
                if instances[i].archetype == instances[j].archetype and \
                   instances[i].pattern == instances[j].pattern:
                    idx1 = i
                    idx2 = j
            else: # pattern only
                if instances[i].pattern == instances[j].pattern:
                    idx1 = i
                    idx2 = j
            # Found?
            if idx1 and idx2:
                print("-----------------------------------------")
                print_item(instances[i], 0, "")
                print_item(instances[j], 0, "")
                # print DIM query
                print(f"id:{instances[i].instanceId} or id:{instances[j].instanceId}")
                dupes.append((i,j))
    return dupes


def save_duplicates_to_file(instances, duplicates, fileName):
    with open(fileName, 'w') as file:
        for dupe in duplicates:
            file.write(f"id:{instances[dupe[0]].instanceId} or id:{instances[dupe[1]].instanceId}")
            file.write('\n')


#################################################################################################################################

if __name__ == '__main__':
    dir, files = files_for_armor_type(ItemSubType.ArmorHelmet)
    # dir, files = files_for_armor_type(ItemSubType.ArmorClassItem)
    if len(files) == 0:
        print("No instanced items found!")
        exit(0)

    # list of instanced items
    instances = extract_instances(dir, files)

    duplicates = find_duplicates(instances)
    # duplicates = find_duplicates(list_of_lists, False)
    print(f"Found {len(duplicates)} duplicates")
    print(duplicates)

    save_duplicates_to_file(instances, duplicates, "duplicates.log")
