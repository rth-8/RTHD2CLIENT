from bungie_api import ItemSubType, DamageType, AmmoType, CharacterClass, CharacterStats
import local_images

################################################################################
class ItemData:
    def __init__(self) -> None:
        self.hash = 0
        self.instanceId = 0
        self.power = 0
        self.tier = 0
        self.state = 0
        self.icon = ""
        self.seasonOverlayIcon = ""
        self.name = ""
        self.tierAndType = ""


################################################################################
class WeaponData(ItemData):
    def __init__(self) -> None:
        super().__init__()
        self.ammoType: AmmoType = AmmoType.NoType
        self.damageType: DamageType = DamageType.NoType


################################################################################
class ArmorData(ItemData):
    def __init__(self) -> None:
        super().__init__()
        self.class_type = CharacterClass.Unknown
        self.subtype = ItemSubType.NoType
        self.archetype = ""
        self.stat_health  = 0
        self.stat_melee   = 0
        self.stat_grenade = 0
        self.stat_super   = 0
        self.stat_class   = 0
        self.stat_weapons = 0
        self.pattern = "000000"

    def total(self):
        return (self.stat_health +
                self.stat_melee +
                self.stat_grenade +
                self.stat_super +
                self.stat_class +
                self.stat_weapons)

    def get_str1(self):
        return (f"{str(self.hash):15}"
              + f"{str(self.instanceId):25}"
              + f"{self.archetype:15}"
              + f"T{str(self.tier):5}"
              + f"{str(self.stat_health):5}"
              + f"{str(self.stat_melee):5}"
              + f"{str(self.stat_grenade):5}"
              + f"{str(self.stat_super):5}"
              + f"{str(self.stat_class):5}"
              + f"{str(self.stat_weapons):5}"
              + f"{self.pattern:10}"
            #   + f"{self.name}"
              )


################################################################################

def get_armor_html(item, hc, mc, gc, sc, cc, wc):
    class_img = ""
    match item.class_type:
        case CharacterClass.Titan:  class_img = local_images.class_titan_icon_raw_data
        case CharacterClass.Hunter: class_img = local_images.class_hunter_icon_raw_data
        case CharacterClass.Warlock:class_img = local_images.class_warlock_icon_raw_data
    return (
f"""
<html>
<table width="100%" border="0">
<tr><td><h1>{item.name}</h1></td><td style="text-align: right"><img src="data:image/png;base64,{class_img}" width="64" height="64"/?</td></tr>
</table>
({item.instanceId})
<h2>{item.power}</h2>
<h3>{item.archetype}</h3>
<h3>Tier: {'*' * item.tier} ({item.tier})</h3>
<table width="100%" border="1">
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Health]}"  width="16" height="16"/></td><td width="5%">{item.stat_health }</td><td style="color: {hc};">{'█' * item.stat_health }</td></tr>
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Melee]}"   width="16" height="16"/></td><td width="5%">{item.stat_melee  }</td><td style="color: {mc};">{'█' * item.stat_melee  }</td></tr>
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Grenade]}" width="16" height="16"/></td><td width="5%">{item.stat_grenade}</td><td style="color: {gc};">{'█' * item.stat_grenade}</td></tr>
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Super]}"   width="16" height="16"/></td><td width="5%">{item.stat_super  }</td><td style="color: {sc};">{'█' * item.stat_super  }</td></tr>
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Class]}"   width="16" height="16"/></td><td width="5%">{item.stat_class  }</td><td style="color: {cc};">{'█' * item.stat_class  }</td></tr>
<tr><td width="5%"><img src="{local_images.stat_icons_b64_black[CharacterStats.Weapons]}" width="16" height="16"/></td><td width="5%">{item.stat_weapons}</td><td style="color: {wc};">{'█' * item.stat_weapons}&nbsp;</td></tr>
</table>
<h3>Total {item.total()}</h3>
</html>
""")
