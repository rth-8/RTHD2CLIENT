from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

import sys
import os
import json
import pyperclip

import constants
from my_secrets import MySecrets
from my_oauth import MyOAuth
from bungie_api import ComponentCharacter, ComponentItem, ItemSubType, ItemState, CharacterStats
from user_data import UserData
from character_data import CharacterData
import pages
from stats import files_for_armor_type, extract_instances, find_duplicates, save_duplicates_to_file
from item_data import get_armor_html
import local_images


API_ROOT = "https://www.bungie.net/Platform"

USER_MEMBERSHIP_INFO = "User/GetMembershipsForCurrentUser/"
USER_PROFILE = "{}/Destiny2/{}/Profile/{}/?components=100"
USER_PROFILE_INV = "{}/Destiny2/{}/Profile/{}/?components=102"

CACHE_USER_MEMBERSHIP_INFO = "cache/membership_info.json"
CACHE_USER_PROFILE = "cache/user_profile.json"
CACHE_USER_PROFILE_INV = "cache/user_profile_inv.json"
CACHE_USER_CHARACTER_INFO = "cache/character_{}_info.json"


################################################################################
class MyMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("mainwindow.ui", self)

        self.actionExit.triggered.connect(self.close)
        self.actionInventoryRefresh.triggered.connect(self._refresh_inventory)
        self.actionGet_general_info.triggered.connect(self._get_general_info_about_vault_items)

        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(self._url_changed)
        self.webview.page().certificateError.connect(self._on_cert_error)
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.frm_mid.setLayout(layout)

        self.btn_find.clicked.connect(self._slot_find_btn)
        self.lst_result.currentTextChanged.connect(self._slot_list_select)
        self.btn_lock_item1.clicked.connect(self._slot_btn_lock_item1)
        self.btn_lock_item2.clicked.connect(self._slot_btn_lock_item2)
        self.btn_clear_all.clicked.connect(self._slot_btn_clear_all)
        self.btn_save_to_file.clicked.connect(self._slot_btn_save_to_file)
        self.btn_dim_query_copy.clicked.connect(self._slot_btn_dim_query_copy)

        self.btn_find2.clicked.connect(self._slot_btn_find2)
        self.lst_result2.currentTextChanged.connect(self._slot_list2_select)

        self.secrets = MySecrets()
        self.oauth = MyOAuth(self.secrets)
        self.userData = UserData()
        self.charactersDataList = []

        self.inv_instances = []
        self.inv_duplicates = []
        self.selected_idx1 = -1
        self.selected_idx2 = -1

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
            # Refresh character page
            chidx = int(resp_url.split('=')[1])
            print(f"Refresh character {chidx}...")
            self._delete_cached_character(chidx)
            self._get_character_info(chidx, self.userData.characterHashes[chidx])
            d = self._load_from_cache(CACHE_USER_CHARACTER_INFO.format(chidx))
            if d:
                self.charactersDataList[chidx].clear()
                self.charactersDataList[chidx].process_info_json(d)
                self._get_character_equipment(d, self.charactersDataList[chidx], chidx)
            self.webview.setHtml(pages.get_page_character(self.charactersDataList[chidx]))
        elif resp_url.startswith("about:blank?profile"):
            # Show profile page
            print("Switch to profile page...")
            self.webview.setHtml(pages.get_page_user_info(self.userData, self.charactersDataList))
        elif resp_url.startswith("about:blank?character"):
            # Show character page
            print("Switch to character page...")
            print(f"NEW PAGE: {resp_url}")
            parts = resp_url.split("=")
            chidx = int(parts[1]) - 1
            if chidx >= 0 and chidx < len(self.charactersDataList):
                self.webview.setHtml(pages.get_page_character(self.charactersDataList[chidx]))
        elif resp_url.startswith("http"):
            # Show http page
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
            download = True     # file not exists yet -> download
        else:
            fstat = os.stat(cache_file)
            if fstat.st_size == 0:
                download = True     # file exists, but its empty -> download
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
        return download


    def _load_from_cache(self, cache_file):
        json_data = None
        print(f"Load from {cache_file}...")
        with open(cache_file, "r") as file:
            json_data = json.load(file)
        return json_data


    def _get_inventory(self):
        print("Get user profile inventory...")
        url = USER_PROFILE_INV.format(API_ROOT, self.userData.membershipType, self.userData.membershipId)
        self._download_and_save(url, CACHE_USER_PROFILE_INV)


    def _refresh_inventory(self):
        if os.path.exists(CACHE_USER_PROFILE_INV):
            print(f"Delete inventory...")
            os.remove(CACHE_USER_PROFILE_INV)
        self._get_inventory()
        print("Done.")


    def _get_general_info_about_vault_items(self):
        d = self._load_from_cache(CACHE_USER_PROFILE_INV)
        if d:
            inv = d["Response"]["profileInventory"]["data"]["items"]
            # NOTE: Currently only interested in uniquely instanced items (weapons and armor pieces) with quantity 1
            # TODO: What about consumables and other non-instanced items ?
            inv = list(filter(lambda item: "itemInstanceId" in item and "quantity" in item and int(item["quantity"]) == 1, inv))
            print("Get profile inventory items...")
            print("Count: ", len(inv))
            for item in inv:
                itemHash = item["itemHash"]
                url = f"{API_ROOT}/Destiny2/Manifest/DestinyInventoryItemDefinition/{itemHash}/"
                # NOTE: From the nature of inventory data (itemHash vs itemInstanceId), 
                # there will be multiple instances for single itemHash. However there will not be duplicated
                # queries to endpoint, because _download_and_save checks, if data were already downloaded 
                # (i.e. corresponding file is in cache).
                self._download_and_save(url, f"cache/user_profile_inv_{itemHash}.json")
        print("Done.")


    def _get_instanced_items_info(self, filter, type_name):
        print(f"Downloading instances for '{type_name}'")
        # print(f"FILTER: {filter}")
        # first try to create subfolder
        folder = f"cache/{type_name}"
        dirtocreate = os.getcwd() + "/" + folder
        try:
            os.stat(dirtocreate)
        except:
            os.mkdir(dirtocreate)
        # proceed with downloading instanced items info
        d = self._load_from_cache(CACHE_USER_PROFILE_INV)
        if d:
            inv = d["Response"]["profileInventory"]["data"]["items"]
            for item in inv:
                itemHash = item["itemHash"]
                if itemHash in filter:
                    itemInstanceId = item["itemInstanceId"]
                    url = (f"{API_ROOT}/Destiny2/{self.userData.membershipType}/Profile/{self.userData.membershipId}/"
                            + f"Item/{itemInstanceId}/?components="
                            + str(ComponentItem.ItemInstances.value) + ","
                            + str(ComponentItem.ItemPerks.value) + ","
                            + str(ComponentItem.ItemStats.value) + ","
                            + str(ComponentItem.ItemCommonData.value))
                    self._download_and_save(url, f"cache/{type_name}/user_profile_inv_instance_{itemInstanceId}.json")


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
            self._get_inventory()

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

        # TEST QUERIES:
        # print("----- TEST -----")
        # self._download(f"{API_ROOT}/Destiny2/{self.userData.membershipType}/Profile/{self.userData.membershipId}/Item/6917530156741587405/?components=300,301,302,303,304,305,306,307,308")
        # self._download(f"{API_ROOT}/Destiny2/Manifest/DestinyInventoryItemDefinition/95722356/")
        # print("----- TEST -----")


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
                character_data.process_item_json(dd, item["state"])


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


    def _get_all_instance_ids(self):
        l = []
        d = self._load_from_cache(CACHE_USER_PROFILE_INV)
        if d:
            inv = d["Response"]["profileInventory"]["data"]["items"]
            inv = list(filter(lambda item: "itemInstanceId" in item and "quantity" in item and int(item["quantity"]) == 1, inv))
            for item in inv:
                l.append(item["itemInstanceId"])
        return l


    def _delete_cached_instance(self, fpath):
        if os.path.exists(fpath):
            print(f"Delete: {fpath}")
            os.remove(fpath)
            return True
        return False


    def _remove_nonexisting_instances(self, files):
        iids = self._get_all_instance_ids()
        for f in files:
            iid = f[26:-5]  # extract instance id from file name
            if iid not in iids:
                print(f"Remove: {f}")
                # remove file, which instance id is not in inventory anymore
                if self._delete_cached_instance(f"./cache/helmets/{f}"):
                    continue
                if self._delete_cached_instance(f"./cache/gauntlets/{f}"):
                    continue
                if self._delete_cached_instance(f"./cache/chests/{f}"):
                    continue
                if self._delete_cached_instance(f"./cache/legs/{f}"):
                    continue
                if self._delete_cached_instance(f"./cache/class_items/{f}"):
                    continue


    def _clear_all_duplicates_tab(self):
        self.lst_result.clear()
        self.inv_instances.clear()
        self.inv_duplicates.clear()
        self.selected_idx1 = -1
        self.selected_idx2 = -1
        self.txt_dim_query.clear()
        self.btn_lock_item1.setText("???")
        self.btn_lock_item2.setText("???")
        self.txt_item1.clear()
        self.txt_item2.clear()


    def _clear_all_finder_tab(self):
        self.lst_result2.clear()
        self.inv_instances.clear()
        self.txt_item3.clear()


    def _slot_btn_clear_all(self):
        self._clear_all_duplicates_tab()


    def _slot_find_btn(self):
        # get picked armor type
        at = ItemSubType(self.cmb_armor_type.currentIndex() + ItemSubType.ArmorHelmet.value)
        print(f"FIND: duplicates: {at}")
        # check armor type and prepare downloading info
        download_filter = None
        download_name = None
        match at:
            case ItemSubType.ArmorHelmet:    download_filter = constants.helmets_legendary.keys()    ; download_name = "helmets"
            case ItemSubType.ArmorGauntlets: download_filter = constants.gauntlets_legendary.keys()  ; download_name = "gauntlets"
            case ItemSubType.ArmorChest:     download_filter = constants.chests_legendary.keys()     ; download_name = "chests"
            case ItemSubType.ArmorLegs:      download_filter = constants.legs_legendary.keys()       ; download_name = "legs"
            case ItemSubType.ArmorClassItem:
                download_filter = list(constants.class_items_legendary.keys()) + list(constants.class_items_exotic.keys())
                download_name = "class_items"
            case _: raise Exception("Unexpected armor type!")
        # clear current data
        self._clear_all_duplicates_tab()
        self._clear_all_finder_tab()
        # download instances
        self._get_instanced_items_info(download_filter, download_name)
        # process downloaded instances
        # get all instance files from sub-dir for given armor type
        dir, files = files_for_armor_type(at)
        if len(files) == 0:
            print("No instanced items found!")
            return
        # try delete any instance file, which id is not in current inventory json
        self._remove_nonexisting_instances(files)
        # get all files from sub-dir again, this time without deleted files
        dir, files = files_for_armor_type(at)
        if len(files) == 0:
            print("No instanced items found!")
            return
        self.inv_instances = extract_instances(dir, files)
        self.inv_duplicates = find_duplicates(self.inv_instances, self.chb_set.isChecked(), self.chb_archetype.isChecked())
        self.statusbar.showMessage(f"Found {len(self.inv_duplicates)} duplicates")
        for dupe in self.inv_duplicates:
            self.lst_result.addItem(f"id:{self.inv_instances[dupe[0]].instanceId} or id:{self.inv_instances[dupe[1]].instanceId}")
        print("Done.")


    def _toggle_lock_btn_text(self, btn, item):
        if item.state & ItemState.Locked.value:
            btn.setText("Unlock")
        else:
            btn.setText("Lock")


    def _map_colors(self, val1, val2):
        col1 = "black"
        col2 = "black"
        if val1 > val2:
            col1 = "green"
            col2 = "red"
        elif val1 < val2:
            col1 = "red"
            col2 = "green"
        else:
            col1 = "blue"
            col2 = "blue"
        return col1, col2


    def _slot_list_select(self, text):
        idx = self.lst_result.currentRow()
        i = self.inv_duplicates[idx][0]
        j = self.inv_duplicates[idx][1]
        # print(f"List index {idx}: {i} - {j}")
        self.txt_dim_query.setText(text)
        self.txt_item1.clear()
        self.txt_item2.clear()
        self.selected_idx1 = -1
        self.selected_idx2 = -1
        # Show stats
        # NOTE: max is 42: ##########################################
        hc1, hc2 = self._map_colors(self.inv_instances[i].stat_health , self.inv_instances[j].stat_health )
        mc1, mc2 = self._map_colors(self.inv_instances[i].stat_melee  , self.inv_instances[j].stat_melee  )
        gc1, gc2 = self._map_colors(self.inv_instances[i].stat_grenade, self.inv_instances[j].stat_grenade)
        sc1, sc2 = self._map_colors(self.inv_instances[i].stat_super  , self.inv_instances[j].stat_super  )
        cc1, cc2 = self._map_colors(self.inv_instances[i].stat_class  , self.inv_instances[j].stat_class  )
        wc1, wc2 = self._map_colors(self.inv_instances[i].stat_weapons, self.inv_instances[j].stat_weapons)
        # 1
        self.selected_idx1 = i
        self._toggle_lock_btn_text(self.btn_lock_item1, self.inv_instances[i])
        self.txt_item1.append(get_armor_html(self.inv_instances[i], hc1, mc1, gc1, sc1, cc1, wc1))
        # 2
        self.selected_idx2 = j
        self._toggle_lock_btn_text(self.btn_lock_item2, self.inv_instances[j])
        self.txt_item2.append(get_armor_html(self.inv_instances[j], hc2, mc2, gc2, sc2, cc2, wc2))


    def _toggle_instance_lock_state(self, idx, btn):
        if idx > -1:
            iid = self.inv_instances[idx].instanceId
            print(f"Instance: {iid}")
            state = self.inv_instances[idx].state & ItemState.Locked.value
            print(f"Locked: {state}")
            # Prepare DestinyItemStateRequest struct for SetLockState POST request
            # NOTE: for whatever reason, SetLockState requires membership type and loged-in charcter id (wtf???)
            data = {
                "state": not state,
                "itemId": iid,
                "characterId": "2305843009315334455",
                "membershipType": self.userData.membershipType
            }
            url = f"{API_ROOT}/Destiny2/Actions/Items/SetLockState/"
            # NOTE: json argument must NOT be already made json structure, but just dictionary.
            # This is because 'post' does serialization by itself, so if already made json is provided, 
            # double serialization happens and that corrupts the final json structure.
            r = self.oauth.session.post(url, headers={"X-API-Key": self.secrets.api_key, "Content-Type": "application/json"}, json=data)
            print(f"Response status: {r.status_code}")
            # print(r.request.body)
            # print(r.request.headers)
            # print(r.json())
            if r.status_code == 200:
                # toggle state
                self.inv_instances[idx].state = self.inv_instances[idx].state ^ ItemState.Locked.value
                self._toggle_lock_btn_text(btn, self.inv_instances[idx])
                dir = ""
                match self.inv_instances[idx].subtype:
                    case ItemSubType.ArmorHelmet:    dir = "helmets"
                    case ItemSubType.ArmorGauntlets: dir = "gauntlets"
                    case ItemSubType.ArmorChest:     dir = "chests"
                    case ItemSubType.ArmorLegs:      dir = "legs"
                    case ItemSubType.ArmorClassItem: dir = "class_items"
                    case _: raise Exception("Unexpected armor type!")
                fpath = f"./cache/{dir}/user_profile_inv_instance_{self.inv_instances[idx].instanceId}.json"
                json_data = None
                with open(fpath, "r") as file:
                    json_data = json.load(file)
                if json_data:
                    json_data["Response"]["item"]["data"]["state"] = self.inv_instances[idx].state
                    with open(fpath, "w") as file:
                        json.dump(json_data, file)


    def _slot_btn_lock_item1(self):
        print("Toggle lock state for item 1...")
        if self.selected_idx1 > -1:
            self._toggle_instance_lock_state(self.selected_idx1, self.btn_lock_item1)
        print("Done.")


    def _slot_btn_lock_item2(self):
        print("Toggle lock state for item 2...")
        if self.selected_idx2 > -1:
            self._toggle_instance_lock_state(self.selected_idx2, self.btn_lock_item2)
        print("Done.")


    def _slot_btn_save_to_file(self):
        if len(self.inv_duplicates) > 0:
            r = QFileDialog.getSaveFileName(self, "Save", ".", "*.txt")
            if len(r[0]) > 0:
                save_duplicates_to_file(self.inv_instances, self.inv_duplicates, r[0])


    def _slot_btn_dim_query_copy(self):
        # copy DIM query to clipboard
        pyperclip.copy(self.txt_dim_query.text())


    def _slot_btn_find2(self):
        # clear current data
        self._clear_all_duplicates_tab()
        self._clear_all_finder_tab()
        # get picked armor type
        aidx = self.cmb_armor_type2.currentIndex()
        print(f"FIND: pattern: {aidx}")
        if aidx == 0:
            # get files from all subfolders
            dir, files = files_for_armor_type(ItemSubType.ArmorHelmet)
            if len(files) > 0:
                self.inv_instances += extract_instances(dir, files)
            dir, files = files_for_armor_type(ItemSubType.ArmorGauntlets)
            if len(files) > 0:
                self.inv_instances += extract_instances(dir, files)
            dir, files = files_for_armor_type(ItemSubType.ArmorChest)
            if len(files) > 0:
                self.inv_instances += extract_instances(dir, files)
            dir, files = files_for_armor_type(ItemSubType.ArmorLegs)
            if len(files) > 0:
                self.inv_instances += extract_instances(dir, files)
            dir, files = files_for_armor_type(ItemSubType.ArmorClassItem)
            if len(files) > 0:
                self.inv_instances += extract_instances(dir, files)
            if len(files) == 0:
                print("No instanced items found!")
                return
        else:
            # get files from selected subfolder only
            at = ItemSubType(aidx - 1 + ItemSubType.ArmorHelmet.value)
            dir, files = files_for_armor_type(at)
            if len(files) == 0:
                print("No instanced items found!")
                return
            self.inv_instances = extract_instances(dir, files)
        # create pattern
        ptrn = []
        ptrn.append('1' if self.chb_health.isChecked()  else '0')
        ptrn.append('1' if self.chb_melee.isChecked()   else '0')
        ptrn.append('1' if self.chb_grenade.isChecked() else '0')
        ptrn.append('1' if self.chb_super.isChecked()   else '0')
        ptrn.append('1' if self.chb_class.isChecked()   else '0')
        ptrn.append('1' if self.chb_weapons.isChecked() else '0')
        pattern = "".join(ptrn)
        # finds instances matching pattern
        for item in self.inv_instances:
            if item.pattern == pattern:
                self.lst_result2.addItem(f"id:{item.instanceId}")
        print("Done.")


    def _slot_list2_select(self, text):
        for item in self.inv_instances:
            if item.instanceId == text.split(":")[1]:
                self.txt_item3.clear()
                self.txt_item3.append(get_armor_html(item, "black", "black", "black", "black", "black", "black"))


################################################################################
class MyUI:
    def __init__(self) -> None:
        print("Opening main window...")
        app = QApplication(sys.argv)
        window = MyMainWindow()
        window.show()
        app.exec()
        print("Main window closed.")

