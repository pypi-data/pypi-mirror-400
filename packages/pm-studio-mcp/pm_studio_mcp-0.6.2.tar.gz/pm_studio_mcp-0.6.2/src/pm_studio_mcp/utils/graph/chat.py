import requests
import markdown
import base64
import re
from .auth import AuthUtils
from .user import UserUtils

class ChatUtils:
    """Utilities for accessing Microsoft Teams chat data via MS Graph API"""

    @staticmethod
    def append_signature(html: str) -> str:
        signature = "<br><br><p style=\"color: grey;\"> Sent via <a href='https://aka.ms/pmstudio'>PM Studio</a></p>"
        return html + signature

    @staticmethod
    def get_chat_members(chat_id: str):
        access_token = AuthUtils().login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        members_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/members"
        resp = requests.get(members_url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("value", [])
        else:
            print(f"Error retrieving chat members: {resp.text}")
            return None

    @staticmethod
    def get_group_chat_id_by_name(topic: str):
        print("Retrieving group chat ID...")
        access_token = AuthUtils().login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {"$top": 50}
        chats_url = "https://graph.microsoft.com/v1.0/me/chats"

        while chats_url:
            chats_response = requests.get(chats_url, headers=headers, params=params)
            if chats_response.status_code != 200:
                print(f"Error retrieving chats: {chats_response.text}")
                return False

            for chat in chats_response.json().get("value", []):
                if chat.get("topic") and topic in chat.get("topic", ""):
                    print(chat.get("id"))
                    return chat.get("id")

            chats_url = chats_response.json().get("@odata.nextLink")
            params = None

        print(f"Chat with topic '{topic}' not found.")
        return None

    @staticmethod
    def match_member(mention_lower: str, member: dict) -> bool:
        user = member.get("user", {})
        email = member.get("email", "") or user.get("email", "")
        display = member.get("displayName", "") or user.get("displayName", "")
        alias = email.split("@")[0] if email else ""

        email = email.lower()
        display = display.lower()
        alias = alias.lower()
        display_no_space = display.replace(" ", "").lower()

        return (
            mention_lower == email or
            mention_lower == display or
            mention_lower == alias or
            alias.startswith(mention_lower) or
            mention_lower in display or
            mention_lower == display_no_space
        )

    @staticmethod
    def prepare_message_with_mentions(message: str, chat_id: str):
        mention_pattern = r'@([\w.\-]+)'
        mentions_found = re.findall(mention_pattern, message)

        if not mentions_found:
            return {
                "body": {
                    "contentType": "html",
                    "content": ChatUtils.append_signature(message.replace('\n', '<br>'))
                }
            }

        members = ChatUtils.get_chat_members(chat_id)
        if members is None:
            return {
                "body": {
                    "contentType": "html",
                    "content": ChatUtils.append_signature(message.replace('\n', '<br>'))
                }
            }

        html_content = message
        mentions_array = []

        for mention_text in mentions_found:
            mention_lower = mention_text.lower()
            matched_member = None

            for member in members:
                if ChatUtils.match_member(mention_lower, member):
                    matched_member = member
                    break

            if matched_member:
                user_obj = matched_member.get("user", {})
                user_id = user_obj.get("id") or matched_member.get("userId")
                display_name = matched_member.get("displayName") or user_obj.get("displayName") or mention_text

                if not user_id:
                    continue

                mention_id = len(mentions_array)
                mentions_array.append({
                    "id": mention_id,
                    "mentionText": f"@{display_name}",
                    "mentioned": {
                        "@odata.type": "#microsoft.graph.chatMessageMentionedIdentitySet",
                        "user": {
                            "id": user_id,
                            "displayName": display_name
                        }
                    }
                })

                html_content = ChatUtils._replace_first_mention(html_content, mention_text, display_name, mention_id)
            else:
                continue

        html_content = html_content.replace('\n', '<br>')
        html_content = ChatUtils.append_signature(html_content)

        return {
            "body": {
                "contentType": "html",
                "content": html_content
            },
            "mentions": mentions_array
        }

    @staticmethod
    def _replace_first_mention(text: str, mention_text: str, display_name: str, mention_id: int) -> str:
        pattern = f'@{re.escape(mention_text)}'
        replacement = f'<at id="{mention_id}">@{display_name}</at>'
        match = re.search(pattern, text)
        if not match:
            return text
        start, end = match.span()
        return text[:start] + replacement + text[end:]

    @staticmethod
    def send_chat_with_id(chat_id: str, message: str, image_path: str = None):
        print("Sending message to chat...")
        print("imgpath = ", image_path, flush=True)

        if image_path:  # image_path is not empty 
            # Read image as binary and convert to base64 string
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare temporaryId reference
            temporary_id = "1"

            # Format message with image
            image_html = f'<div>{message}</div><img src="../hostedContents/{temporary_id}/$value" height="297" width="297">'
            message = f"<br/>{image_html}<br/>"


        access_token = AuthUtils().login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        if chat_id == "self":
            print("Sending note to myself...")
            endpoint = "https://graph.microsoft.com/v1.0/me/chats/48:notes/messages"
            # If sending to self, we don't need mentions or hosted contents
            payload = {
                        "body": {
                            "contentType": "html",
                            "content": ChatUtils.append_signature(message)
                        }
            }

        else:
            print(f"Sending note to group chat: {chat_id}")
            endpoint = f"https://graph.microsoft.com/v1.0/me/chats/{chat_id}/messages"
            payload = ChatUtils.prepare_message_with_mentions(message, chat_id)


        if image_path: 
            # Read image as binary and convert to base64 string
            payload["hostedContents"] = [
                {
                    "@microsoft.graph.temporaryId": temporary_id,
                    "contentBytes": image_base64,
                    "contentType": "image/png"  # Ensure the content type is specified
                }
            ]


        try:
            response = requests.post(url=endpoint, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")

            if response is None:
                return {
                    "status": "error",
                    "message": "No response received from the API."
                }

            if response.status_code == 201:
                print("Note sent successfully.")
                return {
                    "status": "success",
                    "message": "Note sent successfully."
                }
            else:
                return {
                    "status": "error",
                    "message": f"Error sending note: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error sending note: {str(e)}"
            }

    @staticmethod
    def send_message_to_chat(chat_type: str, chat_name: str, message: str, user_index: int = None , image_path: str = None):
        print("Sending note in Microsoft Teams...")
        messageHTML = markdown.markdown(message)
       
        if chat_type == "myself":
            return ChatUtils.send_chat_with_id("self", messageHTML,image_path)
        elif chat_type == "group":
            chat_id = ChatUtils.get_group_chat_id_by_name(chat_name)
            if chat_id is None:
                return {"status": "error", "message": f"Chat with topic '{chat_name}' not found."}
            return ChatUtils.send_chat_with_id(chat_id, messageHTML, image_path)
        elif chat_type == "person":
            # First try to find an existing one-on-one chat by email or name
            #email_name = chat_name
            #chat_id = ChatUtils.get_existing_one_on_one_chat_id(email_name)
            #if chat_id is not None:
            #    return ChatUtils.send_chat_with_id(chat_id, messageHTML)

            # Not finding in existing chat, search for matching users
            print(f"Searching for users with name '{chat_name}'...", flush=True)
            # Search for users by name
            users = UserUtils.get_users_by_name(chat_name) 
            #print(f"chat.py: users = UserUtils.get_users_by_name(chat_name) = {users}", flush=True) 
            if not users:
                return {
                    "status": "error",
                    "message": f"No users found matching the name '{chat_name}'."
                }
            elif len(users) == 1:
                # If there's only one match, use it automatically
                print(f"Found one user. Sending message directly...", flush=True)
                print(f"Found one user: {users[0]['id']} {users[0]['displayName']} ({users[0]['userPrincipalName']})", flush=True)
                email = users[0].get("userPrincipalName") or users[0].get("mail")
                user_id = users[0].get("id")
                chat_id = ChatUtils.create_one_on_one_chat_id(user_id)
                if chat_id is None:
                    return {
                        "status": "error",
                        "message": f"Could not create chat with user '{email}'."
                    }
                else:
                    return ChatUtils.send_chat_with_id(chat_id, messageHTML,image_path)
            else:
                if user_index is not None and 0 <= user_index < len(users):
                    selected_user = users[user_index-1]  # Adjust for 1-based index
                    print(f"Selected user: {selected_user['displayName']} ({selected_user['userPrincipalName']})", flush=True)
                    email = selected_user.get("userPrincipalName") or selected_user.get("mail")
                    user_id = selected_user.get("id")
                    chat_id = ChatUtils.create_one_on_one_chat_id(user_id)
                    if chat_id is None:
                        return {
                            "status": "error",
                            "message": f"Could not create chat with user '{email}'."
                        }
                    else:
                        return ChatUtils.send_chat_with_id(chat_id, messageHTML,image_path)
                else:
                    for i, user in enumerate(users):
                        print(f"{i+1}. {user['displayName']} ({user['userPrincipalName']}) {user['jobTitle']}", flush=True)
                    return {
                        "status": "multiple_matches",
                        "message": f"Multiple users found matching the name '{chat_name}'. Please select one.",
                        "users": users
                    }
        else:
            return {
                "status": "error",
                "message": "Invalid type. Please use 'myself', 'group', or 'person'."
            }

    @staticmethod
    def create_one_on_one_chat_id(user_id: str):
        access_token = AuthUtils.login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        print(f"Creating 1:1 chat with user '{user_id}'...", flush=True)
        current_user_id = UserUtils.get_current_user().get("id")
        if not current_user_id:
            print("Failed to get current user ID", flush=True)
            return None

        # if the user ID is the same as the current user, then return "self"
        if current_user_id == user_id:
            return "self"

        payload = {
            "chatType": "oneOnOne",
            "members": [
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{current_user_id}"
                },
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{user_id}"
                }
            ]
        }
        
        create_chat_url = "https://graph.microsoft.com/v1.0/chats"
        create_resp = requests.post(create_chat_url, headers=headers, json=payload)
        if create_resp.status_code in (201, 200):
            print(f"1:1 chat created successfully with user '{user_id}'.", flush=True)
            return create_resp.json().get("id")
        else:
            print(f"Error creating 1:1 chat: {create_resp.text}", flush=True)
            return None

    @staticmethod
    def get_existing_one_on_one_chat_id(email_name: str):
        access_token = AuthUtils().login()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # List top 1:1 chats and look for a chat with the user
        print(f"Searching for 1:1 chat with user '{email_name}'...", flush=True)
        chats_url = "https://graph.microsoft.com/v1.0/me/chats?$filter=chatType eq 'oneOnOne'"
        search_count = 0  # Initialize counter, adding to limit processing to 20 members for performance
        # Allow max_search_count to be set as a class variable or default to 20
        max_search_count = 20

        while chats_url and search_count <= max_search_count:
            response = requests.get(chats_url, headers=headers)
            if response.status_code != 200:
                print(f"Error retrieving 1:1 chats (HTTP {response.status_code}): {response.text}", flush=True)
                return None
            for chat in response.json().get("value", []):
                members = ChatUtils.get_chat_members(chat["id"])
                if members:
                    for member in members:
                        search_count += 1
                        if search_count > max_search_count:
                            print(f"More than {max_search_count} members processed, stopping further processing.", flush=True)
                            break
                        # Check both 'email' and 'userPrincipalName'                        
                        # Get member values safely, ensuring they're never None
                        member_email = member.get("email", "") or ""
                        member_upn = member.get("userPrincipalName", "") or ""
                        member_display = member.get("displayName", "") or ""
                        print(f"Checking member: {member_display} ({member_email}, {member_upn})", flush=True)
                        if (
                            member_email.lower() == email_name.lower() or
                            member_upn.lower() == email_name.lower() or
                            member_display.lower() == email_name.lower()
                        ):
                            return chat["id"]                            
            chats_url = response.json().get("@odata.nextLink")

        print(f"No 1:1 chat found with user '{email_name}' after checking {search_count} members.", flush=True)
        return None