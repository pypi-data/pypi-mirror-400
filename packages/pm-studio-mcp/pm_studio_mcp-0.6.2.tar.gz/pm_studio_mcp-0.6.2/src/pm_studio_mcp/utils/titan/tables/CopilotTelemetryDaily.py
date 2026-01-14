"""
Metadata for Copilot Mac DAU table
"""

# Description of the table
DESCRIPTION = """
Copilotmac table contains daily active user metrics for Copilot Mac app across different platforms, 
operating systems, regions, and channels. 
"""

# Sample data showing the table structure
SAMPLE = \
"""
Sample data for Copilotmac:

EventTime,CopilotEventName,AppName,InputMethod,UserId_Muid
2023-05-15 00:00:00,copilotCompose,CopilotN-prod-web-mac,text,12345
2023-05-15 00:00:00,copilotResponseRender,CopilotN-prod-web-mac,voice,12345
2023-05-16 00:00:00,copilotCompose,CopilotN-prod-web-mac,text,67890
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
    "rolling_window": {
        "description": "Time aggregation window for measurements",
        "values": {"1": "daily data", "7": "weekly data", "30": "monthly data"},
        "default": "7"
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
        "name": "copilot_mac_daily_dau_trend",
        "description": "Get Copilot Mac daily DAU trend data with rolling window support",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["rolling_window"],
        "template": """
SELECT toStartOfDay(toDateTime(EventTime)) AS `Date`,
       count(DISTINCT IF((CopilotEventName in ('copilotCompose')
                         and lower(InputMethod) in ('text', 'voice'))
                        OR (CopilotEventName in ('copilotResponseRender')
                            and lower(InputMethod) in ('voice')), UserId_Muid, NULL)) AS `DailyActiveUsers`
FROM bing_prod.CopilotTelemetryDaily
WHERE EventTime >= toDateTime('{start_date} 00:00:00')
  AND EventTime < toDateTime('{end_date} 00:00:00')
  AND AppName LIKE '%prod%' -- prod apps only
  AND (NOT COALESCE(eventInfo_surfaceVisible, TRUE) = FALSE) -- remove non-visible
  AND AppName IN ('CopilotN-prod-web-mac')
GROUP BY toStartOfDay(toDateTime(EventTime))
HAVING count(DISTINCT UserId_Muid) > 100
ORDER BY toStartOfDay(toDateTime(EventTime))
"""
    },
    {
        "name": "copilot_mac_weekly_dau_trend",
        "description": "Get Copilot Mac weekly DAU trend with rolling window aggregation",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["rolling_window"],
        "template": """
WITH daily_data AS (
  SELECT 
    toStartOfDay(toDateTime(EventTime)) AS Date,
    count(DISTINCT IF((CopilotEventName in ('copilotCompose')
                       and lower(InputMethod) in ('text', 'voice'))
                      OR (CopilotEventName in ('copilotResponseRender')
                          and lower(InputMethod) in ('voice')), UserId_Muid, NULL)) AS DailyActiveUsers
  FROM bing_prod.CopilotTelemetryDaily
  WHERE EventTime >= toDateTime('{start_date} 00:00:00')
    AND EventTime < toDateTime('{end_date} 00:00:00')
    AND AppName LIKE '%prod%' -- prod apps only
    AND (NOT COALESCE(eventInfo_surfaceVisible, TRUE) = FALSE) -- remove non-visible
    AND AppName IN ('CopilotN-prod-web-mac')
  GROUP BY toStartOfDay(toDateTime(EventTime))
  HAVING count(DISTINCT UserId_Muid) > 100
)
SELECT 
  CASE 
    WHEN {rolling_window} = 1 THEN toStartOfDay(Date)
    WHEN {rolling_window} = 7 THEN toStartOfWeek(Date)
    WHEN {rolling_window} = 30 THEN toStartOfMonth(Date)
    ELSE toStartOfDay(Date)
  END AS Period,
  CASE 
    WHEN {rolling_window} = 1 THEN 'Daily'
    WHEN {rolling_window} = 7 THEN 'Weekly'
    WHEN {rolling_window} = 30 THEN 'Monthly'
    ELSE 'Daily'
  END AS PeriodType,
  round(AVG(DailyActiveUsers), 0) AS AvgActiveUsers,
  COUNT(*) AS DaysInPeriod,
  SUM(DailyActiveUsers) AS TotalActiveUsers
FROM daily_data
GROUP BY 
  CASE 
    WHEN {rolling_window} = 1 THEN toStartOfDay(Date)
    WHEN {rolling_window} = 7 THEN toStartOfWeek(Date)
    WHEN {rolling_window} = 30 THEN toStartOfMonth(Date)
    ELSE toStartOfDay(Date)
  END
ORDER BY Period
"""
    },
    {
        "name": "copilot_mac_rolling_average",
        "description": "Get Copilot Mac DAU with N-day rolling average based on rolling_window parameter",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["rolling_window"],
        "template": """
WITH daily_data AS (
  SELECT 
    toStartOfDay(toDateTime(EventTime)) AS Date,
    count(DISTINCT IF((CopilotEventName in ('copilotCompose')
                       and lower(InputMethod) in ('text', 'voice'))
                      OR (CopilotEventName in ('copilotResponseRender')
                          and lower(InputMethod) in ('voice')), UserId_Muid, NULL)) AS DailyActiveUsers
  FROM bing_prod.CopilotTelemetryDaily
  WHERE EventTime >= toDateTime('{start_date} 00:00:00')
    AND EventTime < toDateTime('{end_date} 00:00:00')
    AND AppName LIKE '%prod%' -- prod apps only
    AND (NOT COALESCE(eventInfo_surfaceVisible, TRUE) = FALSE) -- remove non-visible
    AND AppName IN ('CopilotN-prod-web-mac')
  GROUP BY toStartOfDay(toDateTime(EventTime))
  HAVING count(DISTINCT UserId_Muid) > 100
)
SELECT 
  Date,
  DailyActiveUsers,
  round(AVG(DailyActiveUsers) OVER (
    ORDER BY Date 
    ROWS BETWEEN {rolling_window} - 1 PRECEDING AND CURRENT ROW
  ), 0) AS RollingAverage,
  {rolling_window} AS WindowSize
FROM daily_data
ORDER BY Date
"""
    },
    {
        "name": "copilot_mac_weekly_comparison",
        "description": "Get Copilot Mac weekly DAU with week-over-week comparison",
        "required_filters": [],
        "optional_filters": ["rolling_window"],
        "template": """
WITH daily_data AS (
  SELECT 
    toStartOfDay(toDateTime(EventTime)) AS Date,
    count(DISTINCT IF((CopilotEventName in ('copilotCompose')
                       and lower(InputMethod) in ('text', 'voice'))
                      OR (CopilotEventName in ('copilotResponseRender')
                          and lower(InputMethod) in ('voice')), UserId_Muid, NULL)) AS DailyActiveUsers
  FROM bing_prod.CopilotTelemetryDaily
  WHERE EventTime >= toDateTime(today() - INTERVAL 21 DAY)  -- 3 weeks for comparison
    AND EventTime < toDateTime(today())
    AND AppName LIKE '%prod%' -- prod apps only
    AND (NOT COALESCE(eventInfo_surfaceVisible, TRUE) = FALSE) -- remove non-visible
    AND AppName IN ('CopilotN-prod-web-mac')
  GROUP BY toStartOfDay(toDateTime(EventTime))
  HAVING count(DISTINCT UserId_Muid) > 100
),
weekly_data AS (
  SELECT 
    toStartOfWeek(Date) AS Week,
    round(AVG(DailyActiveUsers), 0) AS AvgWeeklyDAU,
    COUNT(*) AS DaysInWeek,
    formatDateTime(MIN(Date), '%Y-%m-%d') AS StartDate,
    formatDateTime(MAX(Date), '%Y-%m-%d') AS EndDate,
    ROW_NUMBER() OVER (ORDER BY toStartOfWeek(Date) DESC) AS rn
  FROM daily_data
  GROUP BY toStartOfWeek(Date)
  HAVING COUNT(*) >= 3  -- Only include weeks with at least 3 days of data
),
weekly_with_prev AS (
  SELECT 
    w1.Week,
    w1.StartDate,
    w1.EndDate,
    w1.AvgWeeklyDAU,
    w1.DaysInWeek,
    w2.AvgWeeklyDAU AS PreviousWeekDAU,
    CASE 
      WHEN w2.AvgWeeklyDAU > 0 THEN
        round((w1.AvgWeeklyDAU - w2.AvgWeeklyDAU) * 100.0 / w2.AvgWeeklyDAU, 2)
      ELSE NULL 
    END AS WeekOverWeekChangePercent
  FROM weekly_data w1
  LEFT JOIN weekly_data w2 ON w1.rn = w2.rn - 1
  WHERE w1.rn <= 2
)
SELECT 
  Week,
  StartDate,
  EndDate,
  AvgWeeklyDAU,
  DaysInWeek,
  PreviousWeekDAU,
  WeekOverWeekChangePercent
FROM weekly_with_prev
ORDER BY Week DESC
"""
    }
]

