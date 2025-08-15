from enum import Enum

# https://destinydevs.github.io/BungieNetPlatform/docs/schemas/Destiny-DestinyComponentType

class ComponentCharacter(Enum):
    # This will get you summary info about each of the characters in the profile.
    Characters=200
    # This will get you information about any non-equipped items on the character or character(s) in question, 
    # if you're allowed to see it. You have to either be authenticated as that user, or that user must allow anonymous 
    # viewing of their non-equipped items in Bungie.Net settings to actually get results.
    CharacterInventories=201
    # This will get you information about the progression (faction, experience, etc... "levels") relevant to each character, 
    # if you are the currently authenticated user or the user has elected to allow anonymous viewing of its progression info.
    CharacterProgressions=202
    # This will get you just enough information to be able to render the character in 3D if you have written a 3D rendering 
    # library for Destiny Characters, or "borrowed" ours. It's okay, I won't tell anyone if you're using it. 
    # I'm no snitch. (actually, we don't care if you use it - go to town)
    CharacterRenderData=203
    # This will return info about activities that a user can see and gating on it, if you are the currently authenticated user 
    # or the user has elected to allow anonymous viewing of its progression info. Note that the data returned by this can be 
    # unfortunately problematic and relatively unreliable in some cases. We'll eventually work on making it more consistently 
    # reliable.
    CharacterActivities=204
    # This will return info about the equipped items on the character(s). Everyone can see this.
    CharacterEquipment=205


class ComponentItem(Enum):
    # This will return basic info about instanced items - whether they can be equipped, their tracked status, and some info 
    # commonly needed in many places (current damage type, primary stat value, etc)
    ItemInstances=300
    # Items can have Objectives (DestinyObjectiveDefinition) bound to them. If they do, this will return info for items 
    # that have such bound objectives.
    ItemObjectives=301
    # Items can have perks (DestinyPerkDefinition). If they do, this will return info for what perks are active on items.
    ItemPerks=302
    # If you just want to render the weapon, this is just enough info to do that rendering.
    ItemRenderData=303
    # Items can have stats, like rate of fire. Asking for this component will return requested item's stats if they have stats.
    ItemStats=304
    # Items can have sockets, where plugs can be inserted. Asking for this component will return all info relevant 
    # to the sockets on items that have them.
    ItemSockets=305
    # Items can have talent grids, though that matters a lot less frequently than it used to. Asking for this component 
    # will return all relevant info about activated Nodes and Steps on this talent grid, like the good ol' days.
    ItemTalentGrids=306
    # Items that aren't instanced still have important information you need to know: how much of it you have, 
    # the itemHash so you can look up their DestinyInventoryItemDefinition, whether they're locked, etc... 
    # Both instanced and non-instanced items will have these properties. You will get this automatically with Inventory components - 
    # you only need to pass this when calling GetItem on a specific item.
    ItemCommonData=307
    # Items that are "Plugs" can be inserted into sockets. This returns statuses about those plugs and why they can/can't be inserted. 
    # I hear you giggling, there's nothing funny about inserting plugs. Get your head out of the gutter and pay attention!
    ItemPlugStates=308


class CharacterClass(Enum):
    Titan=0	 
    Hunter=1
    Warlock=2
    Unknown=3


class ItemType(Enum):
    NoType=0
    Currency=1
    Armor=2
    Weapon=3
    Message=7
    Engram=8
    Consumable=9
    ExchangeMaterial=10
    MissionReward=11
    QuestStep=12
    QuestStepComplete=13
    Emblem=14
    Quest=15
    Subclass=16
    ClanBanner=17
    Aura=18
    Mod=19


class ItemSubType(Enum):
    NoType=0
    Crucible=1
    Vanguard=2
    Exotic=5
    AutoRifle=6     #
    Shotgun=7
    Machinegun=8
    HandCannon=	9
    RocketLauncher=10   #
    FusionRifle=11
    SniperRifle=12      #
    PulseRifle=13
    ScoutRifle=14   #
    Crm=16
    Sidearm=17  #
    Sword=18
    Mask=19
    Shader=20
    # empiric:
    LinearFusionRifle=22
    GrenadeLauncher=23
    SubmachineGun=24


class DamageType(Enum):
    NoType=0
    Kinetic=1
    Arc=2
    Solar=3
    Void=4
    Raid=5      # ???
    Stasis=6
    Strand=7


# Note: values set empiricaly
class AmmoType(Enum):
    Normal=1
    Special=2
    Heavy=3

