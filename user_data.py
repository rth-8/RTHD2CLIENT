class UserData:
    def __init__(self) -> None:
        self.displayName = "n/a"
        self.displayNameCode = "n/a"
        self.membershipType = None
        self.membershipId = None
        self.profilePicturePath = None

    def parse_user_info(self, json_data):
        self.displayName = json_data["Response"]["destinyMemberships"][0]["bungieGlobalDisplayName"]
        self.displayNameCode = json_data["Response"]["destinyMemberships"][0]["bungieGlobalDisplayNameCode"]
        self.membershipType = json_data["Response"]["destinyMemberships"][0]["membershipType"]
        self.membershipId = json_data["Response"]["destinyMemberships"][0]["membershipId"]
        self.profilePicturePath = json_data["Response"]["bungieNetUser"]["profilePicturePath"]
