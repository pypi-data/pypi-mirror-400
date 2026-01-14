"""
Metadata for byod_NewOEMDevice_PBTransition_v3_Prod table
"""

# Description of the table
DESCRIPTION = """
byod_NewOEMDevice_PBTransition_v3_Prod table contains user retention metrics for Edge Windows new users.
It tracks the transition of users from a previous browser to a new one (likely Edge, codenamed Anaheim),
allowing for analysis based on cohorts, engagement windows, and geographic regions.
"""

# Sample data showing the table structure
# Note: This is a plausible sample based on the query's column usage.
SAMPLE = \
"""
Sample data for byod_NewOEMDevice_PBTransition_v3_Prod:

ReportDate,CohortWindow,EngagementWindow,EngagementSource,DayOfWeek,CountryCode,deviceIsDMA,CountAnaheim_Initial,BrowsingDevices_Initial
2024-05-15 00:00:00,R07,14,WXaaSIEDualAdjusted,Wed,US,0,500,8000
2024-05-15 00:00:00,R07,14,WXaaSIEDualAdjusted,Wed,DE,1,120,1500
2024-05-22 00:00:00,R07,14,WXaaSIEDualAdjusted,Wed,JP,0,300,4500
"""

# Description of filterable columns and mappings (for template use)
# ----------------------------------------------------------------
# Defines filters that can be used to customize the SQL templates.
FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for data analysis (inclusive).",
    },
    "end_date": {
        "description": "End date for data analysis (exclusive).",
    },
    "cohort_window": {
        "description": "The retention cohort to analyze (e.g., retention after N days).",
        "mapping": {
            "R01": "1-Day Retention",
            "R07": "7-Day Retention",
            "R14": "14-Day Retention",
            "R30": "30-Day Retention"
        },
        "default": "R07"
    },
    "day_of_week": {
        "description": "Filter data for a specific day of the week to ensure comparable trends.",
        "mapping": {
            "Mon": "Monday",
            "Tue": "Tuesday",
            "Wed": "Wednesday",
            "Thu": "Thursday",
            "Fri": "Friday",
            "Sat": "Saturday",
            "Sun": "Sunday"
        },
        "default": "Wed"
    },
    "include_dma_region": {
        "description": "Specify whether to include or exclude countries under the EU's Digital Markets Act (DMA).",
        "values": ["true", "false"],
        "default": "false" # The original query excluded DMA regions.
    },
    "sort_order": {
        "description": "The sort order for the final retention metric.",
        "mapping": {
            "ASC": "Ascending (worst performers first)",
            "DESC": "Descending (best performers first)"
        },
        "default": "ASC"
    },
    "country_filter": {
        "description": "Filter data by specific country/region. If not specified, includes all countries.",
        "mapping": {
            "ALL": "All countries/regions (no filter)",
            "CN": "China",
            "US": "United States", 
            "JP": "Japan",
            "DE": "Germany",
            "GB": "United Kingdom",
            "IN": "India",
            "BR": "Brazil",
            "CA": "Canada",
            "AU": "Australia",
            "FR": "France"
        },
    }
}


# Helper functions for processing filter placeholders
# ----------------------------------------------------------------

def get_dma_filter_sql(params):
    """
    Generates the SQL snippet for the {dma_filter_clause} placeholder.
    """
    include_dma_region_flag = params.get('include_dma_region', 'false')
    dma_countries = "('AT', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GF', 'GP', 'GR', 'HR', 'HU', 'IE', 'IS', 'IT', 'LI', 'LT', 'LU', 'LV', 'MT', 'MQ', 'NL', 'NO', 'PL', 'PT', 'RE', 'RO', 'SE', 'SI', 'SK', 'YT')"
    
    if str(include_dma_region_flag).lower() == 'false':
        # This logic exactly matches the original query to EXCLUDE DMA regions
        country_clause = f"IF(CountryCode IS NULL OR CountryCode = '', 'Unknown', IF(CountryCode IN {dma_countries}, 'True', 'False')) IN ('False')"
        device_clause = "IF(deviceIsDMA == 1, 'true', 'false') IN ('false')"
        return f"AND ({country_clause})\n       AND ({device_clause})"
    else:
        # If we want to include DMA regions, we simply don't add any filter.
        # Returning an empty string means the placeholder will be replaced with nothing.
        return ""

def get_country_filter_sql(params):
    """
    Generates the SQL snippet for the {country_filter_clause} placeholder.
    
    Logic:
    - When country_filter is "ALL" or None or empty: do not add any filter
    - If there is a country filter: add a filter for the specified country
    """
    country_filter = params.get('country_filter')
    if not country_filter or country_filter.upper() == "ALL":
        # no country filter specified, return empty string
        return ""
    else:
        # when a specific country is provided, add the filter
        return f"AND (CountryCode = '{country_filter}')"


# SQL Templates with placeholders for customizable filters
# ----------------------------------------------------------------
# The templating engine will replace placeholders like {filter_name} with user-provided values.
# The special placeholder {dma_filter_clause} requires logic to build the correct SQL snippet.
SQL_TEMPLATES = [
    {
        "name": "calculate_Edge_Windows_New_User_retention",
        "description": "Calculates the daily retention rate for Edge Windows New Users based on specified cohort, day of week, and region.",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["cohort_window", "day_of_week", "include_dma_region", "sort_order", "country_filter"],
        "template": """
SELECT toStartOfDay(toDateTime(ReportDate + INTERVAL 1 DAY)) AS `__timestamp`,
       SUM(CountAnaheim_Initial) * 100.000 / SUM(BrowsingDevices_Initial) AS `Retention`
FROM `titan_byod_prod`.`byod_NewOEMDevice_PBTransition_v3_Prod`
WHERE ReportDate + INTERVAL 1 DAY >= toDateTime('{start_date} 00:00:00')
  AND ReportDate + INTERVAL 1 DAY < toDateTime('{end_date} 00:00:00')
  AND (CohortWindow = '{cohort_window}')
  AND (EngagementWindow = 14)
  AND (EngagementSource = 'WXaaSIEDualAdjusted')
  AND (DayOfWeek IN ('{day_of_week}'))
  {dma_filter_clause}
  {country_filter_clause}
GROUP BY toStartOfDay(toDateTime(ReportDate + INTERVAL 1 DAY))
ORDER BY `Retention` {sort_order}
LIMIT 50000;
""",
        "template_params": {
            "dma_filter_clause": get_dma_filter_sql,
            "country_filter_clause": get_country_filter_sql
        }
    }
]