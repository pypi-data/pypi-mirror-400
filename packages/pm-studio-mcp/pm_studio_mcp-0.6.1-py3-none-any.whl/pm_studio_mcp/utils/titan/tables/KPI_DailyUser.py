"""
Metadata for KPI_DailyUser table
"""

# Description of the table
DESCRIPTION = """
KPI_DailyUser table contains daily active user metrics for Edge browser across different platforms, 
operating systems, regions, and channels. 
"""

# Sample data showing the table structure
SAMPLE = \
"""
Sample data for KPI_DailyUser:

DateId,DataType,RollingWindow,tenant_type,osCategoryId,deviceClassId,osArchId,osRelease,browser_build_number,channel_latest_id,ext_location_country,a14RegionId,language,isInSANMarket,installSource,acquisitionSource,previousPBId,isAnaheimMVU,isAllDBWIN,isPromoterOrDetractor,segmentId,isEdu,customerSegmentId,mngd_ecs,edu_ecs,customer_type_ecs,Cnt,upscaledCnt,isNewOEMDevice,CustomerType,didConsent
2023-05-15 00:00:00,ActiveUser,1,All,3,0,0,Mint 21.1,1.0.0.0,4,CO,9,en-US,0,0,Unknown,0,-1,-1,-1,0,-1,,,,,1,0,-1,Unknown,-1
2023-05-15 00:00:00,ActiveUser,1,All,5,0,0,Unknown,1.0.0.0,2,ZA,10,en-GB,0,0,Unknown,0,-1,-1,-1,0,-1,,,,,3,0,-1,Unknown,-1
2023-05-15 00:00:00,ActiveUser,1,All,5,0,0,Unknown,1.0.0.0,2,UA,3,ru,0,0,Unknown,0,-1,-1,-1,0,-1,,,,,1,0,-1,Unknown,-1
"""

# Description of filterable columns and mappings (for template use)
# ----------------------------------------------------------------
# The filter columns definition provides metadata for template-based queries.
# Each filter can include:
#   - description: Brief explanation of the filter
#   - mapping: For categorical variables, provides mapping from codes to display values
#   - default: Used when a filter is not explicitly provided
#
# Required vs Optional filters:
#   - Filters listed in a template's "required_filters" must be provided by the user
#   - Other filters in the template are optional and will use defaults if not provided
#
FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for data analysis",
    },
    "end_date": {
        "description": "End date for data analysis",
    },
    "os_category": {
        "description": "Operating system categories",
        "mapping": {
            "1": "Android",
            "2": "iOS",
            "3": "Linux",
            "4": "Mac",
            "5": "Other",
            "6": "WCOS",
            "7": "Windows 10+",
            "8": "Windows Downlevel",
            "9": "Unknown"
        },
        "default": "Mac"
    },
    "channel": {
        "description": "Distribution channel identifier",
        "mapping": {
            "1": "Canary",
            "2": "Dev",
            "3": "Beta",
            "4": "Stable",
            "5": "Unknown"
        },
        "default": "Stable"
    },
    "region": {
        "description": "Geographic region identifiers",
        "mapping": {
            "1": "Asia Pacific",
            "2": "Canada",
            "3": "Central and Eastern Europe",
            "4": "France",
            "5": "Germany",
            "6": "Greater China",
            "7": "India",
            "8": "Japan",
            "9": "Latin (Central & South) America",
            "10": "Middle East & Africa",
            "11": "United Kingdom",
            "12": "United States of America",
            "13": "Western Europe",
            "0": "Unknown"
        },
        "special_cases": {
            "Korea": "a14RegionId == 1 AND ext_location_country == 'KR'",
            "ANZ": "(ext_location_country == 'NZ' AND a14RegionId == 1) OR a14RegionId == 19"
        },
    },
    "data_type": {
        "description": "Classification of data measurement",
        "values": ["ActiveUser", "Mobile"],
        "default": "ActiveUser"
    },
    "rolling_window": {
        "description": "Time aggregation window for measurements",
        "values": {
            "1": "daily data",
            "7": "weekly data",
            "30": "monthly data"
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
# Example: WHERE `DateId` >= toDateTime('{start_date} 00:00:00')
#
# The system will:
#   1. Check that all required filters are provided by the user
#   2. For optional filters, use default values from FILTER_COLUMNS if available
#   3. Replace all placeholders with their corresponding values
#
SQL_TEMPLATES = [
    {
        "name": "edge_mac_upscaled_DAU_by_region",
        "description": "Retrieve daily active users filtered by a14 region",
        "required_filters": ["start_date", "end_date", "region"],
        "optional_filters": ["os_category", "channel"],
        "template": """
SELECT CASE
           WHEN (a14RegionId == 1
                 AND ext_location_country == 'KR') THEN 'Korea'
           WHEN ((ext_location_country == 'NZ'
                  AND a14RegionId == 1)
                 OR a14RegionId == 19) THEN 'ANZ'
           WHEN a14RegionId == 1 THEN 'Asia Pacific'
           WHEN a14RegionId == 2 THEN 'Canada'
           WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
           WHEN a14RegionId == 4 THEN 'France'
           WHEN a14RegionId == 5 THEN 'Germany'
           WHEN a14RegionId == 6 THEN 'Greater China'
           WHEN a14RegionId == 7 THEN 'India'
           WHEN a14RegionId == 8 THEN 'Japan'
           WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
           WHEN a14RegionId == 10 THEN 'Middle East & Africa'
           WHEN a14RegionId == 11 THEN 'United Kingdom'
           WHEN a14RegionId == 12 THEN 'United States of America'
           WHEN a14RegionId == 13 THEN 'Western Europe'
           WHEN a14RegionId == 0 THEN 'Unknown'
           ELSE 'Other'
       END AS `region`,
       toStartOfDay(toDateTime(`DateId`)) AS `__timestamp`,
       SUM(upscaledCnt) AS `SUM(upscaledCnt)`
FROM KPI_DailyUser GLOBAL
JOIN
  (SELECT CASE
              WHEN (a14RegionId == 1
                    AND ext_location_country == 'KR') THEN 'Korea'
              WHEN ((ext_location_country == 'NZ'
                     AND a14RegionId == 1)
                    OR a14RegionId == 19) THEN 'ANZ'
              WHEN a14RegionId == 1 THEN 'Asia Pacific'
              WHEN a14RegionId == 2 THEN 'Canada'
              WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
              WHEN a14RegionId == 4 THEN 'France'
              WHEN a14RegionId == 5 THEN 'Germany'
              WHEN a14RegionId == 6 THEN 'Greater China'
              WHEN a14RegionId == 7 THEN 'India'
              WHEN a14RegionId == 8 THEN 'Japan'
              WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
              WHEN a14RegionId == 10 THEN 'Middle East & Africa'
              WHEN a14RegionId == 11 THEN 'United Kingdom'
              WHEN a14RegionId == 12 THEN 'United States of America'
              WHEN a14RegionId == 13 THEN 'Western Europe'
              WHEN a14RegionId == 0 THEN 'Unknown'
              ELSE 'Other'
          END AS `region__`,
          SUM(upscaledCnt) AS `mme_inner__`
   FROM KPI_DailyUser
   WHERE (((DataType IN ('ActiveUser',
                         'Mobile')
            AND RollingWindow = '1'))
          AND ((DataType = 'Mobile'
                OR tenant_type ='All(Desktop+Mobile)'
                OR CASE
                       WHEN osCategoryId == 1 THEN 'Android'
                       WHEN osCategoryId == 2 THEN 'iOS'
                       WHEN osCategoryId == 3 THEN 'Linux'
                       WHEN osCategoryId == 4 THEN 'Mac'
                       WHEN osCategoryId == 5 THEN 'Other'
                       WHEN osCategoryId == 6 THEN 'WCOS'
                       WHEN osCategoryId == 7 THEN 'Windows 10+'
                       WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                       ELSE 'Unknown'
                   END NOT IN ('iOS',
                               'Android')))
          AND (CASE
                   WHEN tenant_type == 'All' THEN 'Desktop - All'
                   WHEN tenant_type == 'Client' THEN 'Desktop – Client'
                   WHEN tenant_type == 'PWA' THEN 'Desktop – PWA'
                   WHEN tenant_type == 'PWA_WithInfo' THEN 'Desktop – PWA_WithInfo'
                   WHEN tenant_type == 'WebView' THEN 'Desktop – WebView'
                   ELSE tenant_type
               END in ('Desktop – Client'))
          AND (CASE
                   WHEN osCategoryId == 1 THEN 'Android'
                   WHEN osCategoryId == 2 THEN 'iOS'
                   WHEN osCategoryId == 3 THEN 'Linux'
                   WHEN osCategoryId == 4 THEN 'Mac'
                   WHEN osCategoryId == 5 THEN 'Other'
                   WHEN osCategoryId == 6 THEN 'WCOS'
                   WHEN osCategoryId == 7 THEN 'Windows 10+'
                   WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                   ELSE 'Unknown'
               END in ('{os_category}'))
          AND (CASE
                   WHEN channel_latest_id == 1 THEN 'Canary'
                   WHEN channel_latest_id == 2 THEN 'Dev'
                   WHEN channel_latest_id == 3 THEN 'Beta'
                   WHEN channel_latest_id == 4 THEN 'Stable'
                   ELSE 'Unknown'
               END in ('{channel}'))
          AND (CASE
                   WHEN (a14RegionId == 1
                      AND ext_location_country == 'KR') THEN 'Korea'
                   WHEN ((ext_location_country == 'NZ'
                       AND a14RegionId == 1)
                      OR a14RegionId == 19) THEN 'ANZ'
                   WHEN a14RegionId == 1 THEN 'Asia Pacific'
                   WHEN a14RegionId == 2 THEN 'Canada'
                   WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
                   WHEN a14RegionId == 4 THEN 'France'
                   WHEN a14RegionId == 5 THEN 'Germany'
                   WHEN a14RegionId == 6 THEN 'Greater China'
                   WHEN a14RegionId == 7 THEN 'India'
                   WHEN a14RegionId == 8 THEN 'Japan'
                   WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
                   WHEN a14RegionId == 10 THEN 'Middle East & Africa'
                   WHEN a14RegionId == 11 THEN 'United Kingdom'
                   WHEN a14RegionId == 12 THEN 'United States of America'
                   WHEN a14RegionId == 13 THEN 'Western Europe'
                   WHEN a14RegionId == 0 THEN 'Unknown'
                   ELSE 'Other'
               END = '{region}'))
   GROUP BY CASE
                WHEN (a14RegionId == 1
                      AND ext_location_country == 'KR') THEN 'Korea'
                WHEN ((ext_location_country == 'NZ'
                       AND a14RegionId == 1)
                      OR a14RegionId == 19) THEN 'ANZ'
                WHEN a14RegionId == 1 THEN 'Asia Pacific'
                WHEN a14RegionId == 2 THEN 'Canada'
                WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
                WHEN a14RegionId == 4 THEN 'France'
                WHEN a14RegionId == 5 THEN 'Germany'
                WHEN a14RegionId == 6 THEN 'Greater China'
                WHEN a14RegionId == 7 THEN 'India'
                WHEN a14RegionId == 8 THEN 'Japan'
                WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
                WHEN a14RegionId == 10 THEN 'Middle East & Africa'
                WHEN a14RegionId == 11 THEN 'United Kingdom'
                WHEN a14RegionId == 12 THEN 'United States of America'
                WHEN a14RegionId == 13 THEN 'Western Europe'
                WHEN a14RegionId == 0 THEN 'Unknown'
                ELSE 'Other'
            END
   ORDER BY `mme_inner__` DESC
   LIMIT 25) AS `series_limit` ON CASE
                                      WHEN (a14RegionId == 1
                                            AND ext_location_country == 'KR') THEN 'Korea'
                                      WHEN ((ext_location_country == 'NZ'
                                             AND a14RegionId == 1)
                                            OR a14RegionId == 19) THEN 'ANZ'
                                      WHEN a14RegionId == 1 THEN 'Asia Pacific'
                                      WHEN a14RegionId == 2 THEN 'Canada'
                                      WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
                                      WHEN a14RegionId == 4 THEN 'France'
                                      WHEN a14RegionId == 5 THEN 'Germany'
                                      WHEN a14RegionId == 6 THEN 'Greater China'
                                      WHEN a14RegionId == 7 THEN 'India'
                                      WHEN a14RegionId == 8 THEN 'Japan'
                                      WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
                                      WHEN a14RegionId == 10 THEN 'Middle East & Africa'
                                      WHEN a14RegionId == 11 THEN 'United Kingdom'
                                      WHEN a14RegionId == 12 THEN 'United States of America'
                                      WHEN a14RegionId == 13 THEN 'Western Europe'
                                      WHEN a14RegionId == 0 THEN 'Unknown'
                                      ELSE 'Other'
                                  END = `region__`
WHERE `DateId` >= toDateTime('{start_date} 00:00:00')
  AND `DateId` < toDateTime('{end_date} 00:00:00')
  AND (((DataType IN ('ActiveUser',
                      'Mobile')
         AND RollingWindow = '1'))
       AND ((DataType = 'Mobile'
             OR tenant_type ='All(Desktop+Mobile)'
             OR CASE
                    WHEN osCategoryId == 1 THEN 'Android'
                    WHEN osCategoryId == 2 THEN 'iOS'
                    WHEN osCategoryId == 3 THEN 'Linux'
                    WHEN osCategoryId == 4 THEN 'Mac'
                    WHEN osCategoryId == 5 THEN 'Other'
                    WHEN osCategoryId == 6 THEN 'WCOS'
                    WHEN osCategoryId == 7 THEN 'Windows 10+'
                    WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                    ELSE 'Unknown'
                END NOT IN ('iOS',
                            'Android')))
       AND (CASE
                WHEN tenant_type == 'All' THEN 'Desktop - All'
                WHEN tenant_type == 'Client' THEN 'Desktop – Client'
                WHEN tenant_type == 'PWA' THEN 'Desktop – PWA'
                WHEN tenant_type == 'PWA_WithInfo' THEN 'Desktop – PWA_WithInfo'
                WHEN tenant_type == 'WebView' THEN 'Desktop – WebView'
                ELSE tenant_type
            END in ('Desktop – Client'))
       AND (CASE
                WHEN (a14RegionId == 1
                      AND ext_location_country == 'KR') THEN 'Korea'
                WHEN ((ext_location_country == 'NZ'
                       AND a14RegionId == 1)
                      OR a14RegionId == 19) THEN 'ANZ'
                WHEN a14RegionId == 1 THEN 'Asia Pacific'
                WHEN a14RegionId == 2 THEN 'Canada'
                WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
                WHEN a14RegionId == 4 THEN 'France'
                WHEN a14RegionId == 5 THEN 'Germany'
                WHEN a14RegionId == 6 THEN 'Greater China'
                WHEN a14RegionId == 7 THEN 'India'
                WHEN a14RegionId == 8 THEN 'Japan'
                WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
                WHEN a14RegionId == 10 THEN 'Middle East & Africa'
                WHEN a14RegionId == 11 THEN 'United Kingdom'
                WHEN a14RegionId == 12 THEN 'United States of America'
                WHEN a14RegionId == 13 THEN 'Western Europe'
                WHEN a14RegionId == 0 THEN 'Unknown'
                ELSE 'Other'
            END = '{region}')
       AND (CASE
                WHEN osCategoryId == 1 THEN 'Android'
                WHEN osCategoryId == 2 THEN 'iOS'
                WHEN osCategoryId == 3 THEN 'Linux'
                WHEN osCategoryId == 4 THEN 'Mac'
                WHEN osCategoryId == 5 THEN 'Other'
                WHEN osCategoryId == 6 THEN 'WCOS'
                WHEN osCategoryId == 7 THEN 'Windows 10+'
                WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                ELSE 'Unknown'
            END in ('{os_category}'))
       AND (CASE
                WHEN channel_latest_id == 1 THEN 'Canary'
                WHEN channel_latest_id == 2 THEN 'Dev'
                WHEN channel_latest_id == 3 THEN 'Beta'
                WHEN channel_latest_id == 4 THEN 'Stable'
                ELSE 'Unknown'
            END in ('{channel}')))
GROUP BY CASE
             WHEN (a14RegionId == 1
                   AND ext_location_country == 'KR') THEN 'Korea'
             WHEN ((ext_location_country == 'NZ'
                    AND a14RegionId == 1)
                   OR a14RegionId == 19) THEN 'ANZ'
             WHEN a14RegionId == 1 THEN 'Asia Pacific'
             WHEN a14RegionId == 2 THEN 'Canada'
             WHEN a14RegionId == 3 THEN 'Central and Eastern Europe'
             WHEN a14RegionId == 4 THEN 'France'
             WHEN a14RegionId == 5 THEN 'Germany'
             WHEN a14RegionId == 6 THEN 'Greater China'
             WHEN a14RegionId == 7 THEN 'India'
             WHEN a14RegionId == 8 THEN 'Japan'
             WHEN a14RegionId == 9 THEN 'Latin (Central & South) America'
             WHEN a14RegionId == 10 THEN 'Middle East & Africa'
             WHEN a14RegionId == 11 THEN 'United Kingdom'
             WHEN a14RegionId == 12 THEN 'United States of America'
             WHEN a14RegionId == 13 THEN 'Western Europe'
             WHEN a14RegionId == 0 THEN 'Unknown'
             ELSE 'Other'
         END,
         toStartOfDay(toDateTime(`DateId`))
ORDER BY `SUM(upscaledCnt)` DESC
LIMIT 5000;
""",
        "required_filters": ["start_date", "end_date"]
    },
    {
        "name": "edge_mac_upscaled_dau",
        "description": "get upscaled DAU count for specific tenant type, OS category, and channel",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["os_category", "channel", "rolling_window"],
        "template": """
SELECT toStartOfDay(toDateTime(`DateId`)) AS `__timestamp`,
       Sum(upscaledCnt) AS `Sum(upscaledCnt)`
FROM KPI_DailyUser
WHERE `DateId` >= toDateTime('{start_date} 00:00:00')
  AND `DateId` < toDateTime('{end_date} 00:00:00')
  AND (((DataType IN ('ActiveUser',
                      'Mobile')
         AND RollingWindow = '{rolling_window}'))
       AND ((DataType = 'Mobile'
             OR tenant_type ='All(Desktop+Mobile)'
             OR CASE
                    WHEN osCategoryId == 1 THEN 'Android'
                    WHEN osCategoryId == 2 THEN 'iOS'
                    WHEN osCategoryId == 3 THEN 'Linux'
                    WHEN osCategoryId == 4 THEN 'Mac'
                    WHEN osCategoryId == 5 THEN 'Other'
                    WHEN osCategoryId == 6 THEN 'WCOS'
                    WHEN osCategoryId == 7 THEN 'Windows 10+'
                    WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                    ELSE 'Unknown'
                END NOT IN ('iOS',
                            'Android')))
       AND (CASE
                WHEN tenant_type == 'All' THEN 'Desktop - All'
                WHEN tenant_type == 'Client' THEN 'Desktop – Client'
                WHEN tenant_type == 'PWA' THEN 'Desktop – PWA'
                WHEN tenant_type == 'PWA_WithInfo' THEN 'Desktop – PWA_WithInfo'
                WHEN tenant_type == 'WebView' THEN 'Desktop – WebView'
                ELSE tenant_type
            END IN ('Desktop – Client'))
       AND (CASE
                WHEN osCategoryId == 1 THEN 'Android'
                WHEN osCategoryId == 2 THEN 'iOS'
                WHEN osCategoryId == 3 THEN 'Linux'
                WHEN osCategoryId == 4 THEN 'Mac'
                WHEN osCategoryId == 5 THEN 'Other'
                WHEN osCategoryId == 6 THEN 'WCOS'
                WHEN osCategoryId == 7 THEN 'Windows 10+'
                WHEN osCategoryId == 8 THEN 'Windows Downlevel'
                ELSE 'Unknown'
            END in ('{os_category}'))
       AND (CASE
                WHEN channel_latest_id == 1 THEN 'Canary'
                WHEN channel_latest_id == 2 THEN 'Dev'
                WHEN channel_latest_id == 3 THEN 'Beta'
                WHEN channel_latest_id == 4 THEN 'Stable'
                ELSE 'Unknown'
            END IN ('{channel}')))
GROUP BY toStartOfDay(toDateTime(`DateId`))
LIMIT 50000;

""",
        "required_filters": ["start_date", "end_date"]
    }
]

