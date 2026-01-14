"""
Metadata for EdgeMobileRetentionOverview table
"""


# Description of the table
DESCRIPTION = \
"""
EdgeMobileRetentionOverview represents the retention data for Edge Mobile (Android and iOS).
The table contains information about user retention across different time periods, regions, and channels.
Retention metrics are calculated based on rolling window ranges, where 0 represents the base cohort and 1 represents retained users.
"""

# Sample data showing the table structure
SAMPLE = \
"""
Sample data for EdgeMobileRetentionOverview:

date                    osCategory   channel_ingressed_name   customer_type   a15Region       isDefaultBrowser   rolling_window_range   cnt
2025-05-01 00:00:00     android      Stable                   consumer        United States   1                  0                      1000
2025-05-01 00:00:00     android      Stable                   consumer        United States   1                  1                      800
2025-05-01 00:00:00     ios          Stable                   consumer        Greater China   0                  0                      500
2025-05-01 00:00:00     ios          Stable                   consumer        Greater China   0                  1                      350
"""


FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for data analysis",
    },
    "end_date": {
        "description": "End date for data analysis",
    },    
    "osCategory": {
        "description": "Operating system category",
        "values": ["android", "ios"]
    },   
    "channel": {
        "description": "Edge distribution channel (Note: This is NOT for install sources like 'Organic' - use install_channel_l1 for that)",
        "mapping": {
            "Stable": "Stable",
            "Beta": "Beta",
            "Dev": "Dev",
            "Canary": "Canary"
        },
        
    },
    "customer_type": {
        "description": "Type of customer",
        "values": ["consumer", "commercial"]
    },
    "region": {
        "description": "Geographic region identifiers",
        "values": [
            "ANZ", "APAC", "CEE", "Canada", "Empty", 
            "France", "Germany", "Greater China", "India", 
            "Japan", "Korea", "Latam", "MEA", "Others", 
            "UK", "United States", "Unknown", "Western Europe"
        ]
    },
    "isDefaultBrowser": {
        "description": "Whether Edge is set as the default browser",
        "mapping": {
            "0": "Not default browser",
            "1": "Default browser",
        }
    },   
    "rolling_window_range": {
        "description": "Day range for retention calculation",
        "values": {
            "0": "Base cohort",
            "1": "Retained users"
        }
    },
    "isNewUser": {
        "description": "Whether the user is new to Edge",
        "mapping": {
            "0": "Existing user",
            "1": "New user"
        }
    },    
    "install_channel_l1": {
        "description": "Installation channel identifier",
        "mapping": {
            "Organic": "Organic installs",
            "Upsell": "Upsell from other products",
            "PaidAds": "Paid advertising",
            "Unknown": "Unknown",
            "Others": "Other channels",
            "OEM": "OEM installations"
        }     
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
# Example: WHERE `date` >= '{start_date} 00:00:00.000000'
#
# The system will:
#   1. Check that all required filters are provided by the user
#   2. For optional filters, use default values from FILTER_COLUMNS if available
#   3. Replace all placeholders with their corresponding values
#
SQL_TEMPLATES = [
    {
        "name": "edge_mobile_d1_retention_by_date",
        "description": "Calculate Day 1 retention rate for Edge Mobile over time",
        "required_filters": ["start_date", "end_date"],        "optional_filters": ["osCategory", "channel", "customer_type", "region", "isDefaultBrowser", "isNewUser", "install_channel_l1"],
        "template": """
SELECT 
    toStartOfDay(toDateTime(`date`)) AS `__timestamp`,
    IF(SUM(IF(rolling_window_range=1, cnt, 0))==0, null, SUM(IF(rolling_window_range=1, cnt, 0))/SUM(IF(rolling_window_range=0, cnt, 0))) AS `d1retention`,
    SUM(IF(rolling_window_range=0, cnt, 0)) AS `cohort_size`
FROM `edge_prod`.`EdgeMobileRetentionOverview`
WHERE `date` >= '{start_date} 00:00:00.000000'
  AND `date` < '{end_date} 00:00:00.000000'
  AND rolling_window_range IN (0, 1)
  {os_category_filter}
  {channel_filter}
  {customer_type_filter}
  {region_filter}
  {default_browser_filter}
  {is_new_user_filter}
  {install_channel_filter}
GROUP BY toStartOfDay(toDateTime(`date`))
ORDER BY `__timestamp` DESC
LIMIT 1000;
""",        "template_params": {            "os_category_filter": lambda params: f"AND (osCategory = '{params.get('osCategory').lower()}')" if params.get("osCategory") else "AND (osCategory in ('android', 'ios'))",
            "channel_filter": lambda params: f"AND (channel_ingressed_name = '{params.get('channel')}')" if params.get("channel") and not is_install_channel(params.get("channel")) else "AND (channel_ingressed_name in ('Beta', 'Canary', 'Dev', 'Stable'))",
            "customer_type_filter": lambda params: f"AND (customer_type in {tuple(params.get('customer_type'))})" if isinstance(params.get('customer_type'), list) else (
                f"AND (customer_type = '{params.get('customer_type')}')" if params.get("customer_type") else 
                "AND (customer_type in ('consumer', 'commercial'))"
            ),
            "region_filter": lambda params: f"AND (a15Region = '{params.get('region')}')" if params.get("region") else "AND (a15Region in ('ANZ', 'APAC', 'CEE', 'Canada', 'Empty', 'France', 'Germany', 'Greater China', 'India', 'Japan', 'Korea', 'Latam', 'MEA', 'Others', 'UK', 'United States', 'Unknown', 'Western Europe'))",
            "default_browser_filter": lambda params: f"AND (isDefaultBrowser = {params.get('isDefaultBrowser')})" if params.get("isDefaultBrowser") is not None else "AND (isDefaultBrowser in (0, 1))",
            "is_new_user_filter": lambda params: f"AND (isNewUser = {1 if params.get('isNewUser') in [1, '1', True, 'True', 'true'] else 0})" if params.get("isNewUser") is not None else "AND (isNewUser in (0, 1))",
            "install_channel_filter": lambda params: f"AND (install_channel_l1 = '{params.get('install_channel_l1')}')" if params.get("install_channel_l1") else "AND (install_channel_l1 in ('Organic', 'Upsell', 'Unknown', 'PaidAds', 'Abnormal', 'OEM', 'Others'))"
        }
    },
    {
    "name": "edge_mobile_retention_by_os",
        "description": "Compare retention rates between Android and iOS",
        "required_filters": ["start_date", "end_date"],        "optional_filters": ["channel", "customer_type", "region", "isDefaultBrowser", "isNewUser", "install_channel_l1"],
        "template": """
SELECT 
    osCategory,
    IF(SUM(IF(rolling_window_range=1, cnt, 0))==0, null, SUM(IF(rolling_window_range=1, cnt, 0))/SUM(IF(rolling_window_range=0, cnt, 0))) AS `d1retention`,
    SUM(IF(rolling_window_range=0, cnt, 0)) AS `cohort_size`
FROM EdgeMobileRetentionOverview
WHERE `date` >= '{start_date} 00:00:00.000000'
  AND `date` < '{end_date} 00:00:00.000000'
  AND rolling_window_range IN (0, 1)
  {channel_filter}
  {customer_type_filter}
  {region_filter}
  {default_browser_filter}
  {is_new_user_filter}
  {install_channel_filter}
GROUP BY osCategory
ORDER BY `d1retention` DESC
LIMIT 1000;
""",        "template_params": {
            "channel_filter": lambda params: f"AND (channel_ingressed_name = '{params.get('channel')}')" if params.get("channel") and not is_install_channel(params.get("channel")) else "AND (channel_ingressed_name in ('Beta', 'Canary', 'Dev', 'Stable'))",
            "customer_type_filter": lambda params: f"AND (customer_type in {tuple(params.get('customer_type'))})" if isinstance(params.get('customer_type'), list) else (
                f"AND (customer_type = '{params.get('customer_type')}')" if params.get("customer_type") else 
                "AND (customer_type in ('consumer', 'commercial'))"
            ),
            "region_filter": lambda params: f"AND (a15Region = '{params.get('region')}')" if params.get("region") else "AND (a15Region in ('ANZ', 'APAC', 'CEE', 'Canada', 'Empty', 'France', 'Germany', 'Greater China', 'India', 'Japan', 'Korea', 'Latam', 'MEA', 'Others', 'UK', 'United States', 'Unknown', 'Western Europe'))",
            "default_browser_filter": lambda params: f"AND (isDefaultBrowser = {params.get('isDefaultBrowser')})" if params.get("isDefaultBrowser") is not None else "AND (isDefaultBrowser in (0, 1))",
            "is_new_user_filter": lambda params: f"AND (isNewUser = {1 if params.get('isNewUser') in [1, '1', True, 'True', 'true'] else 0})" if params.get("isNewUser") is not None else "AND (isNewUser in (0, 1))",
            "install_channel_filter": lambda params: f"AND (install_channel_l1 = '{params.get('install_channel_l1')}')" if params.get("install_channel_l1") else "AND (install_channel_l1 in ('Organic', 'Upsell', 'Unknown', 'PaidAds', 'Abnormal', 'OEM', 'Others'))"
        }
    }
]


