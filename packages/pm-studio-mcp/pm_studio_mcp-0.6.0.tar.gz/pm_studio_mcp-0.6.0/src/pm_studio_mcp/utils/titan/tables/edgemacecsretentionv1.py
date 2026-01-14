"""
Metadata for EdgeMacECSRetentionV1 table
"""

# Description of the table
DESCRIPTION = \
"""
EdgeMacECSRetentionV1 represents the retention data for Edge Mac.
The table contains information about user retention across different time periods, regions, and channels.
Retention rate can be calculated as: retainedUser / activeUser
"""

# Sample data showing the table structure
SAMPLE = \
"""
Sample data for EdgeMacECSRetentionV1:

date_str	datetime	metrics_date_str	metrics_datetime	a14Region	accountType	dataConsent	app_build_number	channel_ingressed_name	ext_location_country	ext_os_ver	isNewUser	offset	activeUser	retainedUser
2025-04-20	2025-04-20T00:00:00	2025-04-06	2025-04-06T00:00:00	Middle East & Africa	All	0	135.0.3179.54	stable	TR	15.1.0	0	14	5	4
2025-04-20	2025-04-20T00:00:00	2025-04-06	2025-04-06T00:00:00	Middle East & Africa	All	0	135.0.3179.54	stable	TR	15.1.0	1	14	3	1
"""


FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for data analysis",
    },
    "end_date": {
        "description": "End date for data analysis",
    },
    "account_type": {
        "description": "Type of user account",
        "mapping": {
            "All": "All account types",
            "MSA": "Microsoft account",
            "AAD": "Azure Active Directory"
        },
        "default": "All"
    },
    "channel": {
        "description": "Distribution channel identifier",
        "mapping": {
            "stable": "Stable",
            "beta": "Beta",
            "dev": "Dev",
            "canary": "Canary"
        },
        "default": "stable"
    },
    "region": {
        "description": "Geographic region identifiers",
        "values": ["Greater China", "United States", "Latam", "APAC", "MEA", "Japan", "India", "UK", "Korea", "Canada", "ANZ", "Unknown", ""]
        
    },
    "isNewUser": {
        "description": "Type of user based on experience",
        "mapping": {
            "0": "Existing user",
            "1": "New user",
        },
    },
    "offset": {
        "description": "Number of days for retention calculation",
        "values": {
            "1": "Day 1 retention",
            "7": "Day 7 retention",
            "14": "Day 14 retention",
            "28": "Day 28 retention"
        },
        "default": "1"
    }
}

# SQL Templates with placeholders for customizable filters
# ----------------------------------------------------------------
# Each template includes:
#   - name: A unique identifier for the template
#   - description: Brief explanation of the query purpose
#   - template: The SQL query with placeholders in the format {filter_name}
#   - required_filters: List of filters that must be provided by the user (will cause error if missing)
#   - optional_filters: List of filters that are optional and will use defaults if available
#
# Placeholder format: {filter_name}
# Example: WHERE `metrics_datetime` >= toDateTime('{start_date} 00:00:00')
#
# The system will:
#   1. Check that all required filters are provided by the user
#   2. For optional filters, use default values from FILTER_COLUMNS if available
#   3. Replace all placeholders with their corresponding values
#
SQL_TEMPLATES = [
    {
        "name": "edge_mac_user_retention_by_date",
        "description": "Calculate user retention rate over time for a specific retention window",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["channel", "offset", "isNewUser"],
        "template": """
SELECT 
    toStartOfDay(toDateTime(`metrics_datetime`)) AS `cohort_date`,
    SUM(retainedUser)/SUM(activeUser) AS `retention_rate`,
    SUM(activeUser) AS `cohort_size`
FROM EdgeMacECSRetentionV1
WHERE `metrics_datetime` >= toDateTime('{start_date} 00:00:00')
  AND `metrics_datetime` < toDateTime('{end_date} 00:00:00')
  AND channel_ingressed_name = '{channel}'
  {is_new_user_filter}
  AND offset = '{offset}'
GROUP BY toStartOfDay(toDateTime(`metrics_datetime`))
ORDER BY `cohort_date` DESC
LIMIT 1000;
""",
        "template_params": {
            "is_new_user_filter": lambda params: "AND (isNewUser in (1))" if params.get("isNewUser") else ""
        }
    },
    {
        "name": "edge_macuser_retention_group_by_region",
        "description": "Compare retention rates for new users across different regions",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["channel", "offset", "isNewUser"],
        "template": """
SELECT 
    a14Region AS `region`,
    SUM(retainedUser)/SUM(activeUser) AS `retention_rate`,
    SUM(activeUser) AS `cohort_size`
FROM EdgeMacECSRetentionV1
WHERE `metrics_datetime` >= toDateTime('{start_date} 00:00:00')
  AND `metrics_datetime` < toDateTime('{end_date} 00:00:00')
  AND channel_ingressed_name = '{channel}'
  AND offset = '{offset}'
  {is_new_user_filter}
GROUP BY a14Region
HAVING `cohort_size` >= 100
ORDER BY `retention_rate` DESC
LIMIT 1000;
""",
        "template_params": {
            "is_new_user_filter": lambda params: "AND (isNewUser in (1))" if params.get("isNewUser") else ""
        }
    }
]
