# This is standalone script for analysis of inventory (vault) items.

import os
import json

TYPE = 0
STYP = 1
TIER = 2
NAME = 3
CLSS = 4


def print_table(items):
    print(f"{"Item Hash":15}{"Type":15}{"Subtype":15}{"Tier":15}{"Class":15}{"Name"}")
    print("-----------------------------------------------------------------------------------------------")
    for h, v in items.items():
        type_name = ""
        subtype_name = ""
        class_name = ""
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
        match v[CLSS]:
            case 0: class_name = "Titan"
            case 1: class_name = "Hunter"
            case 2: class_name = "Warlock"
            case _: class_name = "???"
        print(f"{str(h):15}{type_name:15}{subtype_name:15}{v[TIER]:15}{class_name:15}{v[NAME]}")
    print("-----------------------------------------------------------------------------------------------")


def print_list(lst):
    print("~~~~~~~~~~~~~~~~~~~~")
    for elem in lst:
        print(f"{elem[0]}, {elem[1]}, {elem[2]}")


def get_armor_subtype(items, subtype, tier="Legendary"):
    lst = [(h, v[CLSS], v[NAME]) for (h, v) in items.items() if v[TYPE] == 2 and v[STYP] == subtype and v[TIER] == tier]
    print_list(lst)
    return lst


def generate_dict(file, lst, subtype_name, tier="Legendary"):
    file.write(f"{subtype_name}_{tier} = {{\n")
    for elem in lst:
        file.write(f"{elem[0]:15} : ({elem[1]}, \"{elem[2]}\"),\n")
    file.write("}\n\n")


def generate_constants(items):
    with open("constants.py", 'w') as file:
        print("\nLegendary Armor Pieces:")
        print("----- HELMETS -----")
        helmets = get_armor_subtype(items, 26, "Legendary")
        print("----- GAUNTLETS -----")
        gauntlets = get_armor_subtype(items, 27, "Legendary")
        print("----- CHESTS -----")
        chests = get_armor_subtype(items, 28, "Legendary")
        print("----- LEGS -----")
        legs = get_armor_subtype(items, 29, "Legendary")
        print("----- CLASS ITEMS -----")
        class_items = get_armor_subtype(items, 30, "Legendary")

        # Generate constants
        generate_dict(file, helmets, "helmets", "legendary")
        generate_dict(file, gauntlets, "gauntlets", "legendary")
        generate_dict(file, chests, "chests", "legendary")
        generate_dict(file, legs, "legs", "legendary")
        generate_dict(file, class_items, "class_items", "legendary")

        print("\nExotic Armor Pieces:")
        print("----- HELMETS -----")
        helmets = get_armor_subtype(items, 26, "Exotic")
        print("----- GAUNTLETS -----")
        gauntlets = get_armor_subtype(items, 27, "Exotic")
        print("----- CHESTS -----")
        chests = get_armor_subtype(items, 28, "Exotic")
        print("----- LEGS -----")
        legs = get_armor_subtype(items, 29, "Exotic")
        print("----- CLASS ITEMS -----")
        class_items = get_armor_subtype(items, 30, "Exotic")

        # Generate constants
        generate_dict(file, helmets, "helmets", "exotic")
        generate_dict(file, gauntlets, "gauntlets", "exotic")
        generate_dict(file, chests, "chests", "exotic")
        generate_dict(file, legs, "legs", "exotic")
        generate_dict(file, class_items, "class_items", "exotic")


#################################################################################################################################

if __name__ == '__main__':
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
            items[hash] = (
                int(data["Response"]["itemType"]),
                int(data["Response"]["itemSubType"]),
                data["Response"]["inventory"]["tierTypeName"],
                data["Response"]["displayProperties"]["name"],
                data["Response"]["classType"],
            )

    print_table(items)
    generate_constants(items)
