import sys
import msal
from msal import PublicClientApplication
# Ensure the environment are set, use constant values as default if not

class AuthUtils:
    # Class variables for script mode and token storage
    
    app = None  # MSAL PublicClientApplication instance
    scopes = ["https://graph.microsoft.com/.default"]

    @staticmethod
    def login():
        """
        Authenticate with MSAL and return the access token.

        Returns:
            str: The access token
        """

        try:
            print("Authenticating...")

            # In interactive mode, we try to get the token silently first
            print("Running in interactive mode, trying to get token silently",flush=True)
            if AuthUtils.app is None:
                print("initializing AuthUtils.app, getting configs", flush=True)
                from pm_studio_mcp.config import config
                client_id = config.GRAPH_CLIENT_ID
                tenant_id = config.MICROSOFT_TENANT_ID
                authority = f"https://login.microsoftonline.com/{tenant_id}"

                AuthUtils.app = PublicClientApplication(
                    client_id=client_id,
                    authority=authority,
                    enable_broker_on_mac=True if sys.platform == "darwin" else False, #needed for broker-based flow
                    enable_broker_on_windows=True if sys.platform == "win32" else False, #needed for broker-based flow
                )

            accounts = AuthUtils.app.get_accounts()
            print(f"Found {len(accounts)} cached accounts.", flush=True)
            if accounts:
                print ("Found cached account: ", flush=True)
                for account in accounts:
                    print(f"  {account['username']}")
                
                result = AuthUtils.app.acquire_token_silent(
                    AuthUtils.scopes, 
                    account=accounts[0],
                    force_refresh=True # Get new token even if the cached one is not expired
                )
                                                            
                if result:
                    return result['access_token']

            # If no cached token, do interactive authentication
            result = AuthUtils.app.acquire_token_interactive(
                AuthUtils.scopes,
                parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE #needed for broker-based flow
                # port=0,  # Specify the port if needed
            )

            if "access_token" not in result:
                print(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                sys.exit(1)

            print("Authentication successful!",flush=True)
            return result["access_token"]

        except Exception as e:
            print(f"Authentication error: {str(e)}")
            sys.exit(1)

    @staticmethod
    def getEdgeToken():
        """
        [Windows Only] 
        Get the access token for Microsoft Edge.

        Returns:
            str: The access token

        Token Permissions:
            # email
            # Files.ReadWrite
            # Files.ReadWrite.All
            # Notes.Create
            # Notes.ReadWrite
            # Notes.ReadWrite.All
            # openid
            # People.Read
            # profile
            # User.Read
            # User.ReadBasic.All
        """

        edgeApp = PublicClientApplication(
            client_id="ecd6b820-32c2-49b6-98a6-444530e5a77a",  # Microsoft Edge client ID
            authority="https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47",
            enable_broker_on_mac=True if sys.platform == "darwin" else False,  # needed for broker-based flow
            enable_broker_on_windows=True if sys.platform == "win32" else False  # needed for broker-based flow
        )

        result = edgeApp.acquire_token_interactive(
            scopes=["https://graph.microsoft.com/.default"],
            parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE #broker-based flow
        )

        return result["access_token"]
    

    @staticmethod
    def getAzureCLIToken():
        """
        Get the access token for Azure CLI, which can authenticate in both platform and has user permissions

        Returns:
            str: The access token

        Token Permissions:
        # Application.ReadWrite.All
        # AppRoleAssignment.ReadWrite.All
        # AuditLog.Read.All
        # DelegatedPermissionGrant.ReadWrite.All
        # Directory.AccessAsUser.All
        # email
        # Group.ReadWrite.All
        # openid
        # profile
        # User.Read.All 
        # User.ReadWrite.All
        """

        edgeApp = PublicClientApplication(
            client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",  # Microsoft Azure CLI client id
            authority="https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47",
            enable_broker_on_mac=True if sys.platform == "darwin" else False,  # needed for broker-based flow
            enable_broker_on_windows=True if sys.platform == "win32" else False  # needed for broker-based flow
        )

        result = edgeApp.acquire_token_interactive(
            scopes=["https://graph.microsoft.com/.default"],
            parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE #broker-based flow
        )

        return result["access_token"]
    
    @staticmethod
    def getTitanToken():
        """
        Get the access token for Microsoft Titan, which can authenticate in both platform and has user permissions

        Returns:
            str: The access token

        """
        
        from pm_studio_mcp.config import config
        print("Getting Titan access token...", flush=True)
        titanApp = PublicClientApplication(
            client_id=config.TITAN_CLIENT_ID,  # Microsoft Azure CLI client id
            authority=f"https://login.microsoftonline.com/{config.MICROSOFT_TENANT_ID}",
        )

        result = titanApp.acquire_token_interactive(
            scopes=["api://dcca0492-ea09-452c-bf98-3750d4331d33/signin"],
        )

        return result["access_token"]