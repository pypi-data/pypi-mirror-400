"""
Titan Table Metadata Dictionary Definition File
"""

# Import table metadata
from pm_studio_mcp.utils.titan.tables.edgemacecsretentionv1 import (
    SAMPLE as EDGE_MAC_ECS_RETENTION_SAMPLE,
    DESCRIPTION as EDGE_MAC_ECS_RETENTION_DESC,
    FILTER_COLUMNS as EDGE_MAC_ECS_RETENTION_FILTER_COLUMNS,
    SQL_TEMPLATES as EDGE_MAC_ECS_RETENTION_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.KPI_DailyUser import (
    SAMPLE as KPI_DAILY_USER_SAMPLE,
    DESCRIPTION as KPI_DAILY_USER_DESC,
    FILTER_COLUMNS as KPI_DAILY_USER_FILTER_COLUMNS,
    SQL_TEMPLATES as KPI_DAILY_USER_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.KPI_BrowserMinutes_All import (
    SAMPLE as KPI_BROWSER_MINUTES_ALL_SAMPLE,
    DESCRIPTION as KPI_BROWSER_MINUTES_ALL_DESC,
    FILTER_COLUMNS as KPI_BROWSER_MINUTES_ALL_FILTER_COLUMNS,
    SQL_TEMPLATES as KPI_BROWSER_MINUTES_ALL_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.byod_NewOEMDevice_PBTransition_v3_Prod import (
    SAMPLE as BYOD_NEW_OEM_DEVICE_SAMPLE,
    DESCRIPTION as BYOD_NEW_OEM_DEVICE_DESC,
    FILTER_COLUMNS as BYOD_NEW_OEM_DEVICE_FILTER_COLUMNS,
    SQL_TEMPLATES as BYOD_NEW_OEM_DEVICE_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.KPI_DeviceFlow import (
    SAMPLE as KPI_DEVICE_FLOW_SAMPLE,
    DESCRIPTION as KPI_DEVICE_FLOW_DESC,
    FILTER_COLUMNS as KPI_DEVICE_FLOW_FILTER_COLUMNS,
    SQL_TEMPLATES as KPI_DEVICE_FLOW_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.EdgeMobileUserOverviewV3 import (
    SAMPLE as EDGE_MOBILE_OVERVIEW_SAMPLE,
    DESCRIPTION as EDGE_MOBILE_OVERVIEW_DESC,
    FILTER_COLUMNS as EDGE_MOBILE_OVERVIEW_FILTER_COLUMNS,
    SQL_TEMPLATES as EDGE_MOBILE_OVERVIEW_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.Device_Aggregate_Analytics import (
    SAMPLE as CN_BROWSER_COMPETITOR_SAMPLE,
    DESCRIPTION as CN_BROWSER_COMPETITOR_DESC,
    FILTER_COLUMNS as CN_BROWSER_COMPETITOR_FILTER_COLUMNS,
    SQL_TEMPLATES as CN_BROWSER_COMPETITOR_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.CopilotTelemetryDaily import (
    SAMPLE as COPILOT_MAC_SAMPLE,
    DESCRIPTION as COPILOT_MAC_DESC,
    FILTER_COLUMNS as COPILOT_MAC_FILTER_COLUMNS,
    SQL_TEMPLATES as COPILOT_MAC_SQL_TEMPLATES
)
from pm_studio_mcp.utils.titan.tables.edgemobileretentionoverview import (
    SAMPLE as EDGE_MOBILE_RETENTION_SAMPLE,
    DESCRIPTION as EDGE_MOBILE_RETENTION_DESC,
    FILTER_COLUMNS as EDGE_MOBILE_RETENTION_FILTER_COLUMNS,
    SQL_TEMPLATES as EDGE_MOBILE_RETENTION_SQL_TEMPLATES
)
# Define table metadata dictionary
# Each table entry contains:
# - sample: Sample data showing the table structure
# - description: Detailed description of the table's purpose and contents
# - filter_columns: Available filters and their configurations
# - sql_templates: Pre-defined SQL query templates with:
#   * name: Unique identifier for the template
#   * description: Brief explanation of the query purpose
#   * template: SQL query with placeholders
#   * required_filters: List of filters that must be provided
#   * optional_filters: List of filters that are optional
#   * template_params: Dynamic parameter processing functions for complex filters
TABLE_METADATA = {
    # Edge Mac retention data table
    # Contains user retention metrics for Edge browser on Mac
    "EdgeMacECSRetentionV1": {
        "sample": EDGE_MAC_ECS_RETENTION_SAMPLE,
        "description": EDGE_MAC_ECS_RETENTION_DESC,
        "filter_columns": EDGE_MAC_ECS_RETENTION_FILTER_COLUMNS,
        "sql_templates": EDGE_MAC_ECS_RETENTION_SQL_TEMPLATES
    },
    # Daily active user metrics table
    # Contains user activity data across different platforms and regions
    "KPI_DailyUser": {
        "sample": KPI_DAILY_USER_SAMPLE,
        "description": KPI_DAILY_USER_DESC,
        "filter_columns": KPI_DAILY_USER_FILTER_COLUMNS,
        "sql_templates": KPI_DAILY_USER_SQL_TEMPLATES
    },
    # Browser usage minutes table
    # Contains detailed browser usage metrics with various filtering options
    "KPI_BrowserMinutes_All": {
        "sample": KPI_BROWSER_MINUTES_ALL_SAMPLE,
        "description": KPI_BROWSER_MINUTES_ALL_DESC,
        "filter_columns": KPI_BROWSER_MINUTES_ALL_FILTER_COLUMNS,
        "sql_templates": KPI_BROWSER_MINUTES_ALL_SQL_TEMPLATES
    },
    # Edge Windows New User Retention
    # Contains data for Edge Windows new user retention analysis
    "byod_NewOEMDevice_PBTransition_v3_Prod": {
        "sample": BYOD_NEW_OEM_DEVICE_SAMPLE,
        "description": BYOD_NEW_OEM_DEVICE_DESC,
        "filter_columns": BYOD_NEW_OEM_DEVICE_FILTER_COLUMNS,
        "sql_templates": BYOD_NEW_OEM_DEVICE_SQL_TEMPLATES
    },
    # Edge Windows Existing User Retention
    # Contains data for Edge Windows existing user retention analysis
    "KPI_DeviceFlow": {
        "sample": KPI_DEVICE_FLOW_SAMPLE,
        "description": KPI_DEVICE_FLOW_DESC,
        "filter_columns": KPI_DEVICE_FLOW_FILTER_COLUMNS,
        "sql_templates": KPI_DEVICE_FLOW_SQL_TEMPLATES
    },
    # Edge mobile user overview table
    # Contains mobile user metrics with activity data for Edge mobile apps
    "EdgeMobileUserOverviewV3": {
        "sample": EDGE_MOBILE_OVERVIEW_SAMPLE,
        "description": EDGE_MOBILE_OVERVIEW_DESC,
        "filter_columns": EDGE_MOBILE_OVERVIEW_FILTER_COLUMNS,
        "sql_templates": EDGE_MOBILE_OVERVIEW_SQL_TEMPLATES
    },
    # China AI browser competitor analysis table
    # Contains data for analyzing browser competition in China market including AI browsers
    "Device_Aggregate_Analytics": {
        "sample": CN_BROWSER_COMPETITOR_SAMPLE,
        "description": CN_BROWSER_COMPETITOR_DESC,
        "filter_columns": CN_BROWSER_COMPETITOR_FILTER_COLUMNS,
        "sql_templates": CN_BROWSER_COMPETITOR_SQL_TEMPLATES
    },
     # Copilot Telemetry Daily table
    # Contains daily active user metrics for Copilot Mac app
    "CopilotTelemetryDaily": {
        "sample": COPILOT_MAC_SAMPLE,
        "description": COPILOT_MAC_DESC,
        "filter_columns": COPILOT_MAC_FILTER_COLUMNS,
        "sql_templates": COPILOT_MAC_SQL_TEMPLATES
    },
    # Edge Mobile retention data table
    # Contains user retention metrics for Edge browser on Android and iOS
    "EdgeMobileRetentionOverview": {
        "sample": EDGE_MOBILE_RETENTION_SAMPLE,
        "description": EDGE_MOBILE_RETENTION_DESC,
        "filter_columns": EDGE_MOBILE_RETENTION_FILTER_COLUMNS,
        "sql_templates": EDGE_MOBILE_RETENTION_SQL_TEMPLATES
    }
}

# Define template metadata dictionary for quick template lookup
# This dictionary is populated with:
# - Full template names as keys
# - Individual keywords from template names as additional keys
# - Table names broken into keywords as additional keys
# Each key points to the complete template information including:
# - table: The source table name
# - template_info: The complete template definition
# - table_description: Description of the source table
# - filter_columns: Available filters for the template
TEMPLATE_METADATA = {}

# Populate template metadata
for table_name, table_info in TABLE_METADATA.items():
    if "sql_templates" in table_info:
        # Create a reference template_info using the first template
        # This allows table name keywords to point to a valid template entry
        first_template = table_info["sql_templates"][0] if table_info["sql_templates"] else None
        if first_template:
            table_template_info = {
                "table": table_name,
                "template_info": first_template,
                "table_description": table_info["description"],
                "filter_columns": table_info.get("filter_columns", {})
            }
            
            # Index the table name - first normalize it
            table_name_lower = table_name.lower()
            
            # Add table name directly
            if table_name_lower not in TEMPLATE_METADATA:
                TEMPLATE_METADATA[table_name_lower] = table_template_info
                
            # Split table name by camelCase pattern (e.g. EdgeMobileUserOverviewV3 -> edge mobile user overview v3)
            import re
            # Split by capital letters, numbers, and underscores
            table_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|[0-9]|_|$)|[0-9]+', table_name)
            for part in table_parts:
                part_lower = part.lower()
                if part_lower and part_lower not in TEMPLATE_METADATA:
                    TEMPLATE_METADATA[part_lower] = table_template_info
            
        # Process each template normally
        for template in table_info["sql_templates"]:
            if "name" in template:
                template_name = template["name"].lower()
                template_info = {
                    "table": table_name,
                    "template_info": template,
                    "table_description": table_info["description"],
                    "filter_columns": table_info.get("filter_columns", {})
                }
                # Store the main template entry
                TEMPLATE_METADATA[template_name] = template_info
                  
                # Add keywords for fuzzy matching, but only store references
                # First split by spaces, then by underscores for more granular matching
                for part in template_name.split():
                    if part not in TEMPLATE_METADATA:
                        TEMPLATE_METADATA[part] = template_info
                    
                    # Handle underscore-separated keywords
                    for keyword in part.split('_'):
                        if keyword and keyword not in TEMPLATE_METADATA:
                            TEMPLATE_METADATA[keyword] = template_info
