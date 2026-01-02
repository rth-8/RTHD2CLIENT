# This is standalone script for analysis of inventory (vault) items.

import os
import json

TYPE = 0
STYP = 1
TIER = 2
NAME = 3


def print_table(items):
    for h, v in items.items():
        type_name = ""
        subtype_name = ""
        match v[TYPE]:
            case 2: type_name = "Armor"
            case 3: type_name = "Weapon"
            case _: type_name = "???"
        if v[TYPE] == 2:
            match v[STYP]:
                case 26: subtype_name = "Helmet"
                case 27: subtype_name = "Gauntlets"
                case 28: subtype_name = "Chest"
                case 29: subtype_name = "Legs"
                case 30: subtype_name = "ClassItem"
                case _: subtype_name = "???"
        else:
            subtype_name = "---"
        print(f"{str(h):15}{type_name:15}{subtype_name:15}{v[TIER]:15}{v[NAME]}")


def print_list(lst):
    print("~~~~~~~~~~~~~~~~~~~~")
    for elem in lst:
        print(f"{elem[0]},    # {elem[1]}")


def get_legendary_armor_subtype(items, subtype):
    lst = [(h, v[NAME]) for (h, v) in items.items() if v[TYPE] == 2 and v[STYP] == subtype and v[TIER] == "Legendary"]
    # print(lst)
    # print(len(lst))
    print_list(lst)
    return lst


dir = "./cache/"
files = list(filter(lambda item: item.startswith("user_profile_inv_") and item.endswith(".json"), os.listdir(dir)))
# print(files)

items = {}
for file_name in files:
    path_name = f"{dir}{file_name}"
    # print(f"LOAD: {file_name}")
    # print(f"LOAD: {path_name}")
    with open(path_name, 'r') as file:
        data = json.load(file)
        hash = data["Response"]["hash"]
        type = int(data["Response"]["itemType"])
        subtype = int(data["Response"]["itemSubType"])
        tier = data["Response"]["inventory"]["tierTypeName"]
        items[hash] = (
            type,
            subtype,
            tier,
            data["Response"]["displayProperties"]["name"],
        )


print_table(items)


helmets = get_legendary_armor_subtype(items, 26)

gauntlets = get_legendary_armor_subtype(items, 27)

chests = get_legendary_armor_subtype(items, 28)

legs = get_legendary_armor_subtype(items, 29)

class_items = get_legendary_armor_subtype(items, 30)
