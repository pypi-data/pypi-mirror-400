"""
Metadata for KPI_DeviceFlow table
"""

# Description of the table
DESCRIPTION = """
The KPI_DeviceFlow table tracks the state transitions of devices over time. 
It contains metrics on Edge Windows Existing User retention, churn, and upgrades, primarily for analyzing user behavior 
and product build loyalty, such as for the Edge browser (codename 'Anaheim').
"""

# Sample data showing the table structure
SAMPLE = \
"""
Sample data for KPI_DeviceFlow:

DateId,PB_Last_label,PB_This_label,DevicesScaled_Last,Devices,HasMissingUsageData,DeviceChurnType_Last_Corrected,DeviceChurnType_This_Corrected,A15Region,IngestDate
2024-05-20 00:00:00,Anaheim,Anaheim,1000,1050,0,Retained,Retained,USA,2024-05-21 00:00:00
2024-05-20 00:00:00,Anaheim,Other,50,50,0,Retained,Churned,USA,2024-05-21 00:00:00
2024-05-20 00:00:00,Chrome,Anaheim,25,25,0,New-Organic,Retained,CEE,2024-05-21 00:00:00
2024-05-21 00:00:00,Anaheim,Anaheim,980,990,0,Retained,Upgrade-Win11,Japan,2024-05-22 00:00:00
"""

# Description of filterable columns and mappings (for template use)
# ----------------------------------------------------------------
FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for the analysis (inclusive).",
    },
    "end_date": {
        "description": "End date for the analysis (exclusive).",
    },
    "region": {
        "description": "A15Region for filtering the user base. The original query excluded European regions, but this template allows for positive selection.",
        "mapping": {
            "USA": "USA",
            "APAC": "APAC",
            "Japan": "Japan",
            "India": "India",
            "LATAM": "LATAM",
            "CEE": "CEE",
            "France": "France",
            "Germany": "Germany",
            "Western Europe": "Western Europe"
        }
    },
    "day_of_week": {
        "description": "Filter data for a specific day of the week (1=Monday, 7=Sunday).",
        "mapping": {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday"
        },
        "default": "3" # Default to Wednesday, as in the original query
    }
}

# SQL Templates with placeholders for customizable filters
# ----------------------------------------------------------------
SQL_TEMPLATES = [
    {
        "name": "Edge_Windows_Existing_User_retention_rate_by_day",
        "description": "Calculates the daily retention rate for existing Edge Windows users, defined as the ratio of users who were Anaheim and remained Anaheim, to all users who were previously Anaheim. The query is filtered to specific days of the week and regions.",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["region", "day_of_week"],
        "template": """
SELECT toStartOfDay(toDateTime(`DateId`)) AS `__timestamp`,
       sumIf(DevicesScaled_Last, PB_This_label == 'Anaheim'
             and PB_Last_label == 'Anaheim')/sumIf(DevicesScaled_Last, PB_Last_label == 'Anaheim') AS `retention_rate`
FROM
  (SELECT DateId,
          PB_Last_label,
          PB_This_label,
          DevicesScaled_Last,
          Devices,
          A15Region,
          DayOfWeek(DateId) as day_of_week_num
   FROM KPI_DeviceFlow
   WHERE HasMissingUsageData == 0
     AND PB_This_label != 'None'
     AND DeviceChurnType_Last_Corrected NOT like ('New-%')
     AND DeviceChurnType_This_Corrected in ('Retained',
                                            'Upgrade-Win11')
     AND IngestDate ==
       (SELECT MAX(IngestDate)
        FROM KPI_DeviceFlow)) AS `virtual_table`
WHERE `DateId` >= toDateTime('{start_date} 00:00:00')
  AND `DateId` < toDateTime('{end_date} 00:00:00')
  AND day_of_week_num = {day_of_week}
  {region_filter}
GROUP BY toStartOfDay(toDateTime(`DateId`))
ORDER BY `retention_rate` ASC
LIMIT 50000;
""",
        "template_params": {
            "region_filter": lambda params: f"AND A15Region = '{params.get('region')}'" if params.get('region') else "",
        }
    }
]