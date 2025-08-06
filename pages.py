from user_data import UserData
from character_data import CharacterData

BASE_URL = "https://www.bungie.net"

def get_page_user_info(userData: UserData, characterData: CharacterData):
    print("Create info page...")
    print(f"Icon: {BASE_URL}/{userData.profilePicturePath}")

    return f"""
        <head>
        </head>
        <body>
            <img src="{BASE_URL}/{userData.profilePicturePath}">
            <h1>{userData.displayName}#{userData.displayNameCode}</h1>
            <table>
                <tr>
                    <td>{characterData[0].className}</td><td><img src="{BASE_URL}/{characterData[0].emblemPicturePath}"></td>
                </tr>
            </table>
        </body>
    """
