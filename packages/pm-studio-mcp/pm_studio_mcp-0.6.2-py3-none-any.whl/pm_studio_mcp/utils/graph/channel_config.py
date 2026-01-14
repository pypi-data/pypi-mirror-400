"""
Teams Channel Configuration

This file contains the mapping of team names to team IDs and channel names to channel IDs.
To use the automated channel messaging feature, you need to configure your teams and channels here.

HOW TO GET TEAM ID AND CHANNEL ID:
1. Open the Teams channel you want to send messages to
2. Click on the channel name dropdown (next to the channel name)
3. Select "Get link to channel"
4. From the generated URL, extract:
   - Channel ID: The part after "/channel/" and before "/Channel" (highlighted in RED in the URL)
   - Team ID: The part after "groupId=" and before "&tenantId" (highlighted in YELLOW in the URL)

Example URL structure:
https://teams.microsoft.com/l/channel/[CHANNEL_ID]/Channel%20name?groupId=[TEAM_ID]&tenantId=...

SETUP INSTRUCTIONS:
1. Copy your team names and their corresponding team IDs to TEAM_NAME_TO_ID below
2. Copy your channel names and their corresponding channel IDs to CHANNEL_NAME_TO_ID below
3. Once configured, you can use team names and channel names to send messages automatically

Note: Make sure you have proper permissions to send messages to the configured channels.
"""

# Team name to Team ID mapping
# Add your teams here: "Team Display Name": "team-id-from-url"
TEAM_NAME_TO_ID = {
    "Channel testing": "a7fd77b3-9dfd-47c6-8a6d-cbf5b3a21c06",
    "Edge Mobile": "d8af2c70-2329-4b03-981b-ddce723e20f1",
    "Edge Mac": "14283b26-826a-4d14-8ece-28bcd57266ff",
    "Edge Mobile Commercial": "8b485a81-945e-4788-96c9-0896096dee0e",
}

# Channel name to Channel ID mapping (grouped by team)
# Add your channels here organized by team:
# "Team Name": {
#     "Channel Display Name": "channel-id-from-url",
# }
CHANNEL_NAME_TO_ID = {
    "Channel testing": {
        "Channel testing 01": "19%3AUdgklVIviZyFUEe0lpBmrNWyNd4jeFqCJ7c0xkbqXE41%40thread.tacv2",
    },
    "Edge Mobile": {
        "General": "19%3Addabcae4e0ff459ab4ab1295dde56889%40thread.skype",
    },
    "Edge Mac": {
        "User Feedback": "19%3Af2da5e1f3d3a413fa915c2cd656cc7ab%40thread.tacv2",
    },
    "Edge Mobile Commercial": {
        "General": "19%3A1I5lyPiPRF7QXM_SDTa-Cu1jdfAhe5nG-TohumzfVps1%40thread.tacv2",
        "Testing": "19%3A86c8fca6cefe49be95c93ec6df47bef0%40thread.tacv2",
    },

}

def normalize_name(name: str) -> str:
    """Normalize a name by stripping extra spaces and converting to lowercase."""
    return name.strip().lower()

# Normalize CHANNEL_NAME_TO_ID keys for consistent access
CHANNEL_NAME_TO_ID = {
    normalize_name(team): {
        normalize_name(channel): channel_id
        for channel, channel_id in channels.items()
    }
    for team, channels in CHANNEL_NAME_TO_ID.items()
}

# Normalize channel name lookups
def get_channel_id(team_name: str, channel_name: str) -> str:
    normalized_team_name = normalize_name(team_name)
    normalized_channel_name = normalize_name(channel_name)
    if normalized_team_name in CHANNEL_NAME_TO_ID:
        for name, channel_id in CHANNEL_NAME_TO_ID[normalized_team_name].items():
            if normalize_name(name) == normalized_channel_name:
                return channel_id
    return None

# Normalize available channels retrieval
def get_available_channels(team_name: str) -> list:
    normalized_team_name = normalize_name(team_name)
    if normalized_team_name in CHANNEL_NAME_TO_ID:
        return list(CHANNEL_NAME_TO_ID[normalized_team_name].keys())
    return []








