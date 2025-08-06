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

