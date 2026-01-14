import requests
from .auth import AuthUtils

class UserUtils:
    """Utilities for accessing users data via MS Graph API"""

    @staticmethod
    def get_current_user():
        """
        Get information about the currently authenticated user.
        
        Returns:
            dict: User information or None if error.
        """
        access_token = AuthUtils.getAzureCLIToken()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        user_url = "https://graph.microsoft.com/v1.0/me"
        
        response = requests.get(user_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error retrieving user info: {response.text}")
            return None

    @staticmethod
    def get_current_user_alias():
        """
        Get the alias of the currently authenticated user.
        
        Returns:
            str: User alias or None if error.
        """
        user_info = UserUtils.get_current_user()
        if user_info:
            alias = user_info.get("userPrincipalName", None).split('@')[0] if user_info.get("userPrincipalName") else None
            if alias:
                return alias
        return None


    @staticmethod
    def get_users_by_name(name: str):
        """
        This method uses Edge-specific authentication, which may only be available on Windows systems.
        Search for users by display name.
        
        Args:
            name (str): The name to search for (can be partial match).
        
        Returns:
            list: List of users matching the name or empty list if none found.
        """
        access_token = AuthUtils.getAzureCLIToken()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Use $filter with startswith or contains for flexible name matching
        # Option 1: Exact match
        # filter_query = f"displayName eq '{name}'"
        # Option 2: Starts with (recommended for name searches)
        # filter_query = f"startswith(displayName,'{name}')"
        # Option 3: Contains (broader search)
        # filter_query = f"contains(displayName,'{name}')"

        # if "@" in name, consider it an email or UPN
        if "@" in name:
            # Option 1: Exact match for email or UPN
            filter_query = f"(userPrincipalName eq '{name}') or (mail eq '{name}')"
        else:
            # Option 2: Starts with (recommended for name searches)
            filter_query = f"startswith(displayName,'{name}') or startswith(userPrincipalName,'{name}') or startswith(mail,'{name}')"

        user_url = f"https://graph.microsoft.com/v1.0/users?$filter={filter_query}"
        #print(f"Searching for user with filter: {user_url}", flush=True)

        print(f"Searching for user with URL: {user_url}", flush=True)
        
        response = requests.get(user_url, headers=headers)
        
        if response.status_code == 200:
            # Limit the number of results to avoid overwhelming output
            limit = 50
            users = response.json().get("value", [])[:limit]
            if not users:
                print(f"No users found matching '{name}'", flush=True)
                return []
            else:
                print(f"Found {len(users)} user(s) matching '{name}'", flush=True)
                #print(users, flush=True)
                print("Users found:", flush=True)
                internal_users = []
                for user in users:
                    print(f" - {user['displayName']} ({user.get('mail', 'No email provided')})", flush=True)
                    mail = user.get('mail', 'No email provided')
                    userPrincipalName = user.get('userPrincipalName', 'No UPN provided')
                    if (mail and mail.lower().endswith('microsoft.com')): 
                        internal_users.append(user)
                print(f"Internal users (microsoft.com): {len(internal_users)}", flush=True)
                return internal_users
        else:
            error_message = response.text[:200] + ('...' if len(response.text) > 200 else '')
            print(f"Error searching for user: {error_message}", flush=True)
            #print(f"Error searching for user: {response.text}", flush=True)
            return []