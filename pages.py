from user_data import UserData
from character_data import CharacterData

BASE_URL = "https://www.bungie.net"


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
        character1_emblem = f"{BASE_URL}{charactersDataList[0].emblemPicturePath}"
        character2_class = f"{charactersDataList[1].className}"
        character2_emblem = f"{BASE_URL}{charactersDataList[1].emblemPicturePath}"
        character3_class = f"{charactersDataList[2].className}"
        character3_emblem = f"{BASE_URL}{charactersDataList[2].emblemPicturePath}"
        styles = load_styles()
        page = content.format(**locals())
    print(f"Page:\n{page}")
    return page


def get_page_character(characterData: CharacterData):
    print("Create character page...")
    page = "<head></head><body><h1>:(</h1></body>"
    with open("html/character.html", mode="r") as file:
        content = file.read()
        emblem_color_r = 74
        emblem_color_g = 61
        emblem_color_b = 21
        character_icon = f"{BASE_URL}{characterData.emblemIconPath}"
        character_class_name = f"{characterData.className}"
        styles = load_styles()
        page = content.format(**locals())
    print(f"Page:\n{page}")
    return page
