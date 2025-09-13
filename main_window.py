from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

import sys
import os
import json

from my_secrets import MySecrets
from my_oauth import MyOAuth
from bungie_api import ComponentCharacter
from user_data import UserData
from character_data import CharacterData
import pages


API_ROOT = "https://www.bungie.net/Platform"

USER_MEMBERSHIP_INFO = "User/GetMembershipsForCurrentUser/"
USER_PROFILE = "{}/Destiny2/{}/Profile/{}/?components=100"

CACHE_USER_MEMBERSHIP_INFO = "cache/membership_info.json"
CACHE_USER_PROFILE = "cache/user_profile.json"
CACHE_USER_CHARACTER_INFO = "cache/character_{}_info.json"


################################################################################
class MyMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("mainwindow.ui", self)
        self.setWindowTitle("RTH D2 client")

        self.actionExit.triggered.connect(self.close)

        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(self._url_changed)
        self.webview.page().certificateError.connect(self._on_cert_error)
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.frm_mid.setLayout(layout)

        self.secrets = MySecrets()
        self.oauth = MyOAuth(self.secrets)
        self.userData = UserData()
        self.charactersDataList = []

        if not self.oauth.session.authorized:
            link = self.oauth.start_oauth()
            self.webview.load(QUrl(link))
        else:
            print("Session already authorized.")
            try:
                self._get_user_info()
            except:
                print("Something went wrong?!")
                link = self.oauth.start_oauth()
                self.webview.load(QUrl(link))
                self._get_user_info()
        
        self.webview.setHtml(pages.get_page_user_info(self.userData, self.charactersDataList))


    def _url_changed(self, url: QUrl):
        print("URL changed...")
        # print(url)
        resp_url = str(url.url())
        if resp_url.startswith("about:blank?refresh"):
            chidx = int(resp_url.split('=')[1])
            print(f"Refresh character {chidx}...")
            self._delete_cached_character(chidx)
            self._get_character_info(chidx, self.userData.characterHashes[chidx])
            d = self._load_from_cache(CACHE_USER_CHARACTER_INFO.format(chidx))
            if d:
                self.charactersDataList[chidx].process_info_json(d)
                self._get_character_equipment(d, self.charactersDataList[chidx], chidx)
            self.webview.setHtml(pages.get_page_character(self.charactersDataList[chidx]))
        elif resp_url.startswith("about:blank?profile"):
            print("Switch to profile page...")
            self.webview.setHtml(pages.get_page_user_info(self.userData, self.charactersDataList))
        elif resp_url.startswith("about:blank?character"):
            print("Switch to character page...")
            print(f"NEW PAGE: {resp_url}")
            parts = resp_url.split("=")
            chidx = int(parts[1]) - 1
            if chidx >= 0 and chidx < len(self.charactersDataList):
                self.webview.setHtml(pages.get_page_character(self.charactersDataList[chidx]))
        elif resp_url.startswith("http"):
            print(f"NEW URL: {resp_url}")
            self.edit_url.setText(resp_url)
            self.oauth.get_and_store_token(resp_url)
    

    def _on_cert_error(self, e):
        print(f"cert error: {e.description()}")
        print(f"type: {e.type()}")
        print(f"overridable: {e.isOverridable()}")
        print(f"url: {e.url()}")
        for c in e.certificateChain():
            print(c.toText())
        e.acceptCertificate()


    def _download(self, endpoint_url):
        print(f"Download from {endpoint_url}...")
        r = self.oauth.session.get(url=endpoint_url, headers={"X-API-Key": self.secrets.api_key})
        print(f"Response status: {r.status_code}")
        print(r.text)
        return r.json()


    def _download_and_save(self, endpoint_url, cache_file):
        download = False
        if not os.path.exists(cache_file):
            download = True
        else:
            fstat = os.stat(cache_file)
            if fstat.st_size == 0:
                download = True
        if download:
            print(f"Download from {endpoint_url}...")
            r = self.oauth.session.get(url=endpoint_url, headers={"X-API-Key": self.secrets.api_key})
            print(f"Response status: {r.status_code}")
            # print(r.text)
            json_data = r.json()
            if r.status_code == 200 and json_data["ErrorStatus"] == "Success":
                with open(cache_file, "w") as file:
                    print(f"Saving {cache_file}...")
                    json.dump(json_data, file)


    def _load_from_cache(self, cache_file):
        json_data = None
        print(f"Load from {cache_file}...")
        with open(cache_file, "r") as file:
            json_data = json.load(file)
        return json_data


    def _get_user_info(self):
        # get membership info
        print("Get user membership info...")
        url = f"{API_ROOT}/{USER_MEMBERSHIP_INFO}"
        self._download_and_save(url, CACHE_USER_MEMBERSHIP_INFO)

        # get user profile
        d = self._load_from_cache(CACHE_USER_MEMBERSHIP_INFO)
        if d:
            self.userData.parse_user_info(d)
            print("Get user profile...")
            url = USER_PROFILE.format(API_ROOT, self.userData.membershipType, self.userData.membershipId)
            self._download_and_save(url, CACHE_USER_PROFILE)

        # get character infos
        d = self._load_from_cache(CACHE_USER_PROFILE)
        if d:
            characterIds = d["Response"]["profile"]["data"]["characterIds"]
            chidx = 0
            for chid in characterIds:
                self._get_character_info(chidx, chid)
                self.userData.characterHashes[chidx] = chid
                chidx = chidx + 1

        # go through character infos, create new character data and get equiped weapons
        print("CHARACTERS:")
        for chidx in self.userData.characterHashes.keys():
            print(f"Character {chidx}: {self.userData.characterHashes[chidx]}")
            d = self._load_from_cache(CACHE_USER_CHARACTER_INFO.format(chidx))
            if d:
                ch = CharacterData(chidx)
                # get general character data: emblems and class name (Titan|Hunter|Warlock)
                ch.process_info_json(d)
                self._get_character_equipment(d, ch, chidx)
                self.charactersDataList.append(ch)
        
        # test
        # url = f"{API_ROOT}/Destiny2/Manifest/DestinySocketTypeDefinition/2218962841/"
        # url = (f"{API_ROOT}/Destiny2/{self.userData.membershipType}/Profile/{self.userData.membershipId}/Item/6917530097621948459/"
        #     + "?components=300,307")
        # self._download(url)


    def _get_character_info(self, chidx, chid):
        print(f"Get character #{chidx}: {chid} ...")
        url = (f"{API_ROOT}/Destiny2/{self.userData.membershipType}/Profile/{self.userData.membershipId}/Character/{chid}/?components="
                + str(ComponentCharacter.Characters.value) + "," 
                + str(ComponentCharacter.CharacterEquipment.value) + "," 
                + str(ComponentCharacter.CharacterInventories.value))
        self._download_and_save(url, CACHE_USER_CHARACTER_INFO.format(chidx))


    def _get_character_equipment(self, json_data, character_data, chidx):
        print("Get equiped items...")
        items = json_data["Response"]["equipment"]["data"]["items"]
        for item in items:
            itemHash = item["itemHash"]
            entityType = "DestinyInventoryItemDefinition"
            url = f"{API_ROOT}/Destiny2/Manifest/{entityType}/{itemHash}/"
            self._download_and_save(url, f"cache/character_{chidx}_equipment_{itemHash}.json")
            dd = self._load_from_cache(f"cache/character_{chidx}_equipment_{itemHash}.json")
            if dd:
                character_data.process_item_json(dd)


    def _delete_cached_character(self, chidx):
        print(f"Delete character #{chidx} ...")
        info_file = CACHE_USER_CHARACTER_INFO.format(chidx)
        if os.path.exists(info_file):
            print(f"Delete info {info_file}")
            os.remove(info_file)
            item_files = os.listdir("./cache")
            for f in item_files:
                pat = f"character_{chidx}"
                if pat in f:
                    to_del = f"./cache/{f}"
                    if os.path.exists(to_del):
                        print(f"Delete item {to_del}")
                        os.remove(to_del)


################################################################################
class MyUI:
    def __init__(self) -> None:
        print("Opening main window...")
        app = QApplication(sys.argv)
        window = MyMainWindow()
        window.show()
        app.exec()
        print("Main window closed.")

