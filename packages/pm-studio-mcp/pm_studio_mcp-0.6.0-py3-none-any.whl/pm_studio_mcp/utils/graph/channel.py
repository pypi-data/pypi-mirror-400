import requests
import markdown
from .auth import AuthUtils
from .channel_config import TEAM_NAME_TO_ID, CHANNEL_NAME_TO_ID
from .user import UserUtils

def normalize_name(name: str) -> str:
    """Normalize a name by stripping extra spaces and converting to lowercase."""
    return name.strip().lower()

class ChannelUtils:
    """Utilities for accessing Microsoft Teams channels and posting messages via MS Graph API"""

    @staticmethod
    def append_signature(html: str) -> str:
        """Add PM Studio signature to the message"""
        signature = "</br></br><p style=\"color: grey;\"> Sent via <a href='https://aka.ms/pmstudio'>PM Studio</a></p>"
        return html + signature

    @staticmethod
    def send_message_to_channel_by_id(team_id: str, channel_id: str, message: str, mentions: list = None):
        """
        Send a message to a Teams channel.

        Args:
            team_id (str): The ID of the team
            channel_id (str): The ID of the channel
            message (str): The message content (supports HTML and @mentions)
            mentions (list, optional): List of user objects to mention in the message.
                Each mention should be a dict with 'id', 'displayName', and 'userPrincipalName'

        Returns:
            dict: Response status and details
        """
        print(f"Sending message to channel...(by id)")
        print ("Mentions is ", mentions, flush=True)


        access_token = AuthUtils().login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        endpoint = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"

        payload = {
            "body": {
                "contentType": "html",
                "content": ChannelUtils.append_signature(message)
            }
        }

        # Add mentions if provided
        if mentions:
            payload["mentions"] = []
            for i, mention in enumerate(mentions):
                # Use display name by default, but prefer original mention text if available
                mention_text = mention.get('displayName', mention.get('userPrincipalName', 'Unknown'))
                
                payload["mentions"].append({
                    "id": i,
                    "mentionText": mention_text,
                    "mentioned": {
                        "user": {
                            "id": mention.get('id'),
                            "displayName": mention.get('displayName'),
                            "userPrincipalName": mention.get('userPrincipalName')
                        }
                    }
                })
            print(f"Mentions included: {payload['mentions']}", flush=True)  

        try:
            response = requests.post(url=endpoint, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")

            if response.status_code == 201:
                print("Message sent successfully to channel.")
                return {
                    "status": "success",
                    "message": "Message sent successfully to channel.",
                    "message_id": response.json().get("id")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Error sending message to channel: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error sending message to channel: {str(e)}"
            }

    @staticmethod
    def send_message_to_channel_by_name(team_name: str, channel_name: str, message: str, mentions: list = None):
        """
        Send a message to a Teams channel by team and channel names using static configuration.

        Args:
            team_name (str): Name of the team (must match configuration)
            channel_name (str): Name of the channel (must match configuration)
            message (str): The message content (supports Markdown)
            mentions (list, optional): List of user objects to mention in the message.
                Each mention should be a dict with 'id', 'displayName', and 'userPrincipalName'

        Returns:
            dict: Response status and details
        """
        # Normalize team and channel names
        normalized_team_name = normalize_name(team_name)
        normalized_channel_name = normalize_name(channel_name)

        print(f"Sending message to channel '{normalized_channel_name}' in team '{normalized_team_name}'...", flush=True)

        message_html = markdown.markdown(message)

        team_id = get_team_id(normalized_team_name)
        if not team_id:
            available_teams = get_available_teams()
            return {
                "status": "error",
                "message": f"Team '{normalized_team_name}' not found in configuration. Available teams: {', '.join(available_teams)}"
            }

        channel_id = get_channel_id(normalized_team_name, normalized_channel_name)
        if not channel_id:
            available_channels = get_available_channels(normalized_team_name)
            return {
                "status": "error",
                "message": f"Channel '{normalized_channel_name}' not found in team '{normalized_team_name}'. Available channels: {', '.join(available_channels)}"
            }

        print(f"Found team ID: {team_id}, channel ID: {channel_id}", flush=True)

        return ChannelUtils.send_message_to_channel_by_id(team_id, channel_id, message_html, mentions)

    @staticmethod
    def send_message_to_channel_by_url(channel_info: dict, message: str, mentions: list = None):
        """
        Send a message to a Teams channel using a channel URL.

        Args:
            channel_info (dict): Dictionary containing 'channel_url'.
            message (str): The message content (supports HTML and @mentions).
            mentions (list, optional): List of user objects to mention in the message.

        Returns:
            dict: Response status and details.
        """
        if 'channel_url' not in channel_info:
            return {
                "status": "error",
                "message": "Missing 'channel_url' in channel_info."
            }

        try:
            channel_url = channel_info['channel_url']

            # Extract Channel ID
            channel_id_start = channel_url.find('/channel/') + len('/channel/')
            channel_id_end = channel_url.find('/Channel')
            channel_id = channel_url[channel_id_start:channel_id_end]

            # Extract Team ID
            team_id_start = channel_url.find('groupId=') + len('groupId=')
            team_id_end = channel_url.find('&tenantId')
            team_id = channel_url[team_id_start:team_id_end]

            if not channel_id or not team_id:
                return {
                    "status": "error",
                    "message": "Failed to parse team ID or channel ID from the URL."
                }

            # Send the message
            return ChannelUtils.send_message_to_channel_by_id(team_id, channel_id, message, mentions)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing channel URL: {str(e)}"
            }

    @staticmethod
    def send_message_to_channel(channel_info: dict, message: str):
        """
        Determine the type of channel input (URL, ID, or name) and send the message accordingly.

        Args:
            channel_info (dict): Dictionary containing one of the following:
                - 'team_name' and 'channel_name'
                - 'team_id' and 'channel_id'
                - 'channel_url'
            message (str): The message content (supports HTML and @mentions)

        Returns:
            dict: Response status and details
        """
        print(f"[DEBUG] Original message received: {message}", flush=True)
        
        # Extract mentions from the message
        mentions = ChannelUtils.extract_mentions_from_message(message)
        
        # Process the message to create proper mention HTML if mentions are found
        processed_message = message
        if mentions:
            # Create mention HTML tags with display names
            processed_message = ChannelUtils.create_mention_html(message, mentions)
            print(f"[DEBUG] Processed message with mentions: {processed_message}", flush=True)
        
        if 'channel_url' in channel_info:
            # Use channel URL to send the message
            return ChannelUtils.send_message_to_channel_by_url(channel_info, processed_message, mentions)

        elif 'team_id' in channel_info and 'channel_id' in channel_info:
            # Use team ID and channel ID to send the message
            return ChannelUtils.send_message_to_channel_by_id(
                channel_info['team_id'],
                channel_info['channel_id'],
                processed_message,
                mentions
            )

        elif 'team_name' in channel_info and 'channel_name' in channel_info:
            # Use team and channel names to send the message
            return ChannelUtils.send_message_to_channel_by_name(
                channel_info['team_name'],
                channel_info['channel_name'],
                processed_message,
                mentions
            )

        else:
            return {
                "status": "error",
                "message": "Invalid channel_info provided. Must include 'channel_url', or 'team_id' and 'channel_id', or 'team_name' and 'channel_name'."
            }

    @staticmethod
    def create_mention_html(message: str, mentions: list):
        """
        Create HTML with proper mention tags for Teams.
        
        Args:
            message (str): Original message text
            mentions (list): List of user information dicts
            
        Returns:
            str: HTML formatted message with mention tags
        """
        import re
        html_message = message
        
        for i, mention in enumerate(mentions):
            display_name = mention.get('displayName', mention.get('userPrincipalName', 'Unknown'))
            
            # Create the mention tag with proper format including the display name
            # This format is required by Teams API: <at id="0">Display Name</at>
            mention_tag = f'<at id="{i}">{display_name}</at>'
            
            # Use the original mention text from the message if available
            if 'originalMentionText' in mention and mention['originalMentionText']:
                original_text = mention['originalMentionText']
                mention_pattern = rf'@{re.escape(original_text)}'
                
                print(f"[DEBUG] Replacing mention with original text: '@{original_text}' -> '{mention_tag}'", flush=True)
                
                # Replace the exact mention pattern with the mention tag
                if re.search(mention_pattern, html_message):
                    html_message = re.sub(mention_pattern, mention_tag, html_message)
                    continue
            
            # Fallback to previous behavior if no originalMentionText or it wasn't found
            # Get just the first name for better matching
            first_name = display_name.split()[0] if display_name and ' ' in display_name else display_name
            
            # Try to find mentions in various formats
            mention_patterns = [
                rf'@{re.escape(first_name)}\b',
                rf'@{re.escape(display_name)}\b',
                rf'@{re.escape(mention.get("userPrincipalName", ""))}\b'
            ]
            
            # For single-word names, also try matching without word boundary
            if first_name == display_name:
                mention_patterns.append(rf'@{re.escape(first_name)}')
            
            # Try to match each pattern with regex
            found_match = False
            for pattern in mention_patterns:
                if re.search(pattern, html_message):
                    html_message = re.sub(pattern, mention_tag, html_message)
                    found_match = True
                    break
            
            # If no specific mention was found but we need to include the mention
            if not found_match and '@' in html_message:
                # Look for any unmatched @mentions 
                unmatched_mentions = re.findall(r'@\w+', html_message)
                if unmatched_mentions:
                    # Replace the first unmatched mention with our mention tag
                    html_message = html_message.replace(unmatched_mentions[0], mention_tag, 1)
                    found_match = True
                
                # If still no match found, manually append the mention to the end of the message
                if not found_match:
                    html_message += f" {mention_tag}"
        
        print(f"[DEBUG] Final HTML message with mentions: {html_message}", flush=True)
        return html_message

    @staticmethod
    def send_message_with_mentions(team_name: str, channel_name: str, message: str, mention_users: list = None):
        """
        Send a message to a Teams channel with mentions, automatically resolving user information.
        
        Args:
            team_name (str): Name of the team
            channel_name (str): Name of the channel
            message (str): The message content (supports Markdown and @mentions)
            mention_users (list, optional): List of user emails or display names to mention
            
        Returns:
            dict: Response status and details
        """
        mentions = []
        
        if mention_users:
            for user_identifier in mention_users:
                users = UserUtils.get_users_by_name(user_identifier)
                print(f"[DEBUG] Users found: {users}")
                
                if users and len(users) == 1:
                    user = users[0]
                    user_info = {
                        'id': user.get('id'),
                        'displayName': user.get('displayName'),
                        'userPrincipalName': user.get('userPrincipalName'),
                        'originalMentionText': user_identifier  # Store the original user identifier
                    }
                    mentions.append(user_info)
                else:
                    print(f"Warning: Could not find user information for '{user_identifier}'")
        
        # Convert message to HTML and process mentions
        message_html = markdown.markdown(message)
        if mentions:
            message_html = ChannelUtils.create_mention_html(message_html, mentions)
        
        return ChannelUtils.send_message_to_channel_by_name(team_name, channel_name, message_html, mentions)

    @staticmethod
    def extract_mentions_from_message(message: str):
        """
        Extract @mentions from a message and resolve user information.
        
        Args:
            message (str): The message content that may contain @mentions
            
        Returns:
            list: List of user information dicts for mentioned users with original mention text
        """
        import re
        
        print(f"[DEBUG] Starting mention extraction from message: '{message}'", flush=True)
        
        # Find all @mentions in the message (both email and display name patterns)
        # Updated pattern to properly capture mentions by stopping at word boundaries or specific punctuation
        mention_pattern = r'@([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z0-9._-]+)(?=\s|$|[^\w.-])'
        print(f"[DEBUG] Using mention pattern: {mention_pattern}", flush=True)
        
        mentions_found = re.findall(mention_pattern, message)
        print(f"[DEBUG] Raw mentions found by regex: {mentions_found}", flush=True)
        print(f"[DEBUG] Number of raw mentions found: {len(mentions_found)}", flush=True)
        
        mentions = []
        for i, mention_text in enumerate(mentions_found):
            print(f"[DEBUG] Processing mention {i+1}/{len(mentions_found)}: '{mention_text}'", flush=True)
            
            original_mention_text = mention_text
            mention_text = mention_text.strip()
            print(f"[DEBUG] After stripping: '{mention_text}'", flush=True)
            
            if mention_text:  # Skip empty matches
                print(f"[DEBUG] Attempting to get user info for: '{mention_text}'", flush=True)
                users = UserUtils.get_users_by_name(mention_text)
                print(f"[DEBUG] Users found: {users}")

                if users and len(users) == 1:
                    user = users[0]
                    user_info = {
                        'id': user.get('id'),
                        'displayName': user.get('displayName'),
                        'userPrincipalName': user.get('userPrincipalName'),
                        'originalMentionText': original_mention_text  # Store the original mention text
                    }
                    print(f"[DEBUG] Successfully found user info: {user_info}", flush=True)
                    mentions.append(user_info)
                else:
                    print(f"[DEBUG] Warning: Could not find user information for '@{mention_text}'", flush=True)
            else:
                print(f"[DEBUG] Skipping empty mention text after stripping", flush=True)
        
        print(f"[DEBUG] Final mentions list: {mentions}", flush=True)
        print(f"[DEBUG] Total mentions resolved: {len(mentions)}", flush=True)
        
        return mentions

# Ensure helper functions are defined
from .channel_config import TEAM_NAME_TO_ID, CHANNEL_NAME_TO_ID

def get_team_id(team_name: str) -> str:
    normalized_team_name = normalize_name(team_name)
    for name, team_id in TEAM_NAME_TO_ID.items():
        if normalize_name(name) == normalized_team_name:
            return team_id
    return None

def get_channel_id(team_name: str, channel_name: str) -> str:
    normalized_team_name = normalize_name(team_name)
    normalized_channel_name = normalize_name(channel_name)

    if normalized_team_name in CHANNEL_NAME_TO_ID:
        for name, channel_id in CHANNEL_NAME_TO_ID[normalized_team_name].items():
            if normalize_name(name) == normalized_channel_name:
                return channel_id
    return None

def get_available_teams() -> list:
    return [name for name in TEAM_NAME_TO_ID.keys()]

def get_available_channels(team_name: str) -> list:
    normalized_team_name = normalize_name(team_name)
    if normalized_team_name in CHANNEL_NAME_TO_ID:
        return [name for name in CHANNEL_NAME_TO_ID[normalized_team_name].keys()]
    return []
