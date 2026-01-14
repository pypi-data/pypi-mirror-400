import os
from typing import Optional
"""
Constants used in the PM Studio MCP server.
"""

# =====================
# Greeting message template
# =====================
GREETING_TEMPLATE = "hello, {name}! How can I help you today? I can help you to do competitor analysis, user feedback summary, write docs and more!"

# =====================
# Configuration constants (placeholders, please update with real values as needed)
# Warning: Do not hardcode sensitive information in production code, you should consider adding environment variables in .env file.
# =====================

# Microsoft tenant ID for authentication
MICROSOFT_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"  # Microsoft tenant ID

# Titan API configuration
TITAN_CLIENT_ID = "dcca0492-ea09-452c-bf98-3750d4331d33"  # Titan API client ID
TITAN_ENDPOINT = "https://titanapi.westus2.cloudapp.azure.com/v2/query"  # Titan API endpoint
TITAN_SCOPE = "api://dcca0492-ea09-452c-bf98-3750d4331d33/signin"  # Titan API scope

# =====================
# Graph API Team Configuration
# =====================
# Microsoft Graph Client IDs mapped to team aliases
GRAPH_TEAM_MAPPING = {
    # Edge Consumer Team
    "268dc89a-e0a3-4a5d-8547-9c15f482b2c1": [
        
        "gajie", 
        "juanliu",
        "mile",
        "yancheng",
        "sezho",
        "lyatin",
        "dingxiao"
    ],
    # Edge Mobile Team  
    "de37a421-e719-42d3-a5cb-4fcd10068413": [
        "emilywu",
        "hongjunqiu",
        "yingzhuang", 
        "wenyuansu",
    ],
    # SA Bill Team
    "cc21085d-446f-4e83-9d3b-b21ce9830b65": [
        "tajie",
        "xiaoxch",
        "liyayong",
        "v-keepliu",
        "yongweizhang",
        "eviema",
        "angliu",
        "emmaxu",
        "zhangjingwei",
        "yugon",
        "chenxitan"
    ], 
    # core Team
    "b3427785-fc2b-49a2-9a41-99143ed5703d": [
        "yche",
        "chfen",
        "zhangjingwei",
        "siyangliu",
        "yazhouzhou",
        "lmike",
        "shengjieshi",
        "v-xiaomengli",
        "jinghuama"
    ]
}

# Reddit API configuration
# Reddit API client ID
REDDIT_CLIENT_ID = ""
# Reddit API client secret
REDDIT_CLIENT_SECRET = ""

# Data.ai API configuration
# Data.ai API key
DATA_AI_API_KEY = ""

# Unwrap API configuration
# Unwrap API access token
UNWRAP_ACCESS_TOKEN = ""  

# Path of your working directory, this is used to store output files
WORKING_PATH = ""

# GitHub Copilot token, should be set as an environment variable for security
GITHUB_TOKEN = ""  

def get_user_graph_id() -> str:
    """
    Auto-detect Graph Client ID by mapping user alias to team configuration.
    
    Returns:
        str: Graph Client ID for the user's team, or empty string if not found
    """
    # Use UserUtils to get current user alias and map to team
    try:
        from pm_studio_mcp.utils.graph.user import UserUtils
        
        user_alias = UserUtils.get_current_user_alias()
        if user_alias:
            user_alias = user_alias.strip().lower()
            print(f"Retrieved user alias: '{user_alias}'", flush=True)
            
            # Look up client ID from team mapping
            for graph_client_id, aliases in GRAPH_TEAM_MAPPING.items():
                if user_alias in aliases:
                    print(f"Found Graph Client ID: {graph_client_id[:8]}...", flush=True)
                    return graph_client_id
            
            print(f"User alias '{user_alias}' not found in team mapping", flush=True)
            
    except Exception as e:
        print(f"UserUtils failed: {e}", flush=True)
    
    print("No Graph Client ID found", flush=True)
    return ""

class Config:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._initialize_config()

    def _initialize_config(self):

        # Greeting message configuration
        self.GREETING_TEMPLATE = os.environ.get('GREETING_TEMPLATE', GREETING_TEMPLATE)

        # Working directory configuration
        self.WORKING_PATH = os.environ.get('WORKING_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../temp'))
        os.makedirs(self.WORKING_PATH, exist_ok=True)

        # Reddit API configuration
        self.REDDIT_CLIENT_ID = self._get_config_value('REDDIT_CLIENT_ID', REDDIT_CLIENT_ID)
        self.REDDIT_CLIENT_SECRET = self._get_config_value('REDDIT_CLIENT_SECRET', REDDIT_CLIENT_SECRET)

        # Data.ai API configuration
        self.DATA_AI_API_KEY = self._get_config_value('DATA_AI_API_KEY', DATA_AI_API_KEY)

        # Microsoft Graph API configuration
        self.GRAPH_CLIENT_ID = self._get_config_value('GRAPH_CLIENT_ID', get_user_graph_id()) 

        # Microsoft authentication configuration
        self.MICROSOFT_TENANT_ID = self._get_config_value('MICROSOFT_TENANT_ID', MICROSOFT_TENANT_ID)

        # Unwrap API configuration
        self.UNWRAP_ACCESS_TOKEN = self._get_config_value('UNWRAP_ACCESS_TOKEN', UNWRAP_ACCESS_TOKEN) 

        # Titan API configuration
        self.TITAN_CLIENT_ID = self._get_config_value('TITAN_CLIENT_ID', TITAN_CLIENT_ID)
        self.TITAN_ENDPOINT = self._get_config_value('TITAN_ENDPOINT',  TITAN_ENDPOINT)
        self.TITAN_SCOPE = self._get_config_value('TITAN_SCOPE', TITAN_SCOPE)

        # Google Ads API configuration
        self.GOOGLE_ADS_DEVELOPER_TOKEN = self._get_config_value('GOOGLE_ADS_DEVELOPER_TOKEN', '')
        self.GOOGLE_ADS_LOGIN_CUSTOMER_ID = self._get_config_value('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
        self.GOOGLE_ADS_CLIENT_SECRET_JSON = self._get_config_value('GOOGLE_ADS_CLIENT_SECRET_JSON', '')
        self.GOOGLE_ADS_CREDENTIALS_JSON = self._get_config_value('GOOGLE_ADS_CREDENTIALS_JSON', '')

        # GitHub Copilot configuration
        # Note: GitHub Copilot token should be set as an environment variable for security
        self.GITHUB_TOKEN = self._get_config_value('GITHUB_TOKEN', GITHUB_TOKEN)

    def _get_config_value(self, env_var: str, default_value: str) -> str:
        value = os.environ.get(env_var)
        if value:
            print(f"Using {env_var} from environment")
            return value
        print(f"Using default value for {env_var}")
        return default_value

# Create global config instance
config = Config()