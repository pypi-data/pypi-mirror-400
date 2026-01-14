"""
Metadata for Device_Aggregate_Analytics table focused on China browser market analysis
"""

# Description of the table
DESCRIPTION = \
"""
Provides browser market analysis for China, including metrics for major competitors and AI browsers.
This module contains templates for analyzing China's browser market competition, Edge's BSoM (Browser Share of Minutes),
and the impact of AI browsers such as Doubao, Quark on the market.
"""

# Sample data showing the table structure (simplified)
SAMPLE = \
"""
Sample data for Device_Aggregate_Analytics (China Browser):

Date                | DeviceWeight | EdgeSeconds | ChromeSeconds | Fast360BrowserSeconds | DoubaoSeconds | QuarkSeconds | CiciSeconds | AllBrowserSeconds_Upscaled | Ms1pBrowserSeconds_Upscaled
-------------------:|-------------:|-----------:|-------------:|---------------------:|-------------:|-------------:|------------:|---------------------------:|---------------------------:
2025-05-10 00:00:00 | 1.2          | 300        | 450          | 120                  | 200          | 150          | 50          | 1270                       | 300
2025-05-11 00:00:00 | 0.9          | 280        | 420          | 100                  | 220          | 180          | 60          | 1260                       | 280
"""

# Define filterable columns
FILTER_COLUMNS = \
{
    "start_date": {
        "description": "Start date for analysis period",
        "example": "2025-05-01"
    },
    "end_date": {
        "description": "End date for analysis period",
        "example": "2025-06-01"
    },
    "region": {
        "description": "Region for analysis",
        "values": ["Greater China"],
        "default": "Greater China"
    }
}

# SQL Templates
SQL_TEMPLATES = [
    {
        "name": "cn_major_competitor_browsers_dad",
        "description": "Analyze Daily Active Devices (DAD) for major browser competitors in China, including AI browsers",
        "required_filters": ["start_date", "end_date"],
        "template": """
SELECT toStartOfDay(toDateTime(Date)) AS __timestamp,
       SUM(IF(AnaheimSeconds>0, DeviceWeight, NULL)) AS "Edge DAD",
       SUM(IF((Fast360BrowserSeconds > 0
               OR Safe360BrowserSeconds > 0), DeviceWeight, NULL)) AS "360 DAD",
       SUM(IF(ChromeSeconds > 0, DeviceWeight, NULL)) AS "Chrome DAD",
       COUNT(IF(LenovoBrowserSeconds > 0, DeviceWeight, NULL)) AS "Lenovo DAD",
       COUNT(IF(QQBrowserSeconds > 0, DeviceWeight, NULL)) AS "QQ DAD",
       COUNT(IF(DoubaoSeconds > 0, DeviceWeight, NULL)) AS "Doubao DAD",
       COUNT(IF(QuarkSeconds > 0, DeviceWeight, NULL)) AS "Quark DAD"
FROM Device_Aggregate_Analytics
WHERE Date >= toDate('{start_date}')
  AND Date < toDate('{end_date}')
  AND ((DeviceFamily IN ('Windows.Desktop'))
       AND (Country = 'China')
       AND (FormFactorFamily IN ('PC',
                                 'Unknown',
                                 'Tablet',
                                 'Other')))
GROUP BY toStartOfDay(toDateTime(Date))
ORDER BY "Edge DAD" DESC
LIMIT 10000;
"""
    },
    {
        "name": "edge_bsom_comparison_cn_ai_browsers",
        "description": "Compare Edge BSoM with and without including CN AI browsers in the calculation",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["region"],
        "template": """
SELECT toStartOfDay(toDateTime(Date)) AS __timestamp,
       SUM(Ms1pBrowserSeconds_Upscaled)/(SUM(AllBrowserSeconds_Upscaled) + SUM(DoubaoSeconds*DeviceWeight) + SUM(QuarkSeconds*DeviceWeight) + SUM(CiciSeconds*DeviceWeight)) AS "BSOM with AI Browser in China",
       SUM(Ms1pBrowserSeconds_Upscaled)/SUM(AllBrowserSeconds_Upscaled) AS "BSOM"
FROM Device_Aggregate_Analytics
WHERE Date >= toDate('{start_date}')
  AND Date < toDate('{end_date}')
  AND ((Region = '{region}'))
GROUP BY toStartOfDay(toDateTime(Date))
ORDER BY "BSOM with AI Browser in China" DESC
LIMIT 10000;
"""
    },
    {
        "name": "edge_bsom_impact_by_cn_ai_browsers",
        "description": "Calculate the impact of CN AI browsers on Edge's BSoM",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["region"],
        "template": """
SELECT toStartOfDay(toDateTime(Date)) AS __timestamp,
       (SUM(Ms1pBrowserSeconds_Upscaled)/SUM(AllBrowserSeconds_Upscaled)) - (SUM(Ms1pBrowserSeconds_Upscaled)/(SUM(AllBrowserSeconds_Upscaled) + SUM(DoubaoSeconds*DeviceWeight) + SUM(QuarkSeconds*DeviceWeight) + SUM(CiciSeconds*DeviceWeight))) AS "BSOM Impact"
FROM Device_Aggregate_Analytics
WHERE Date >= toDate('{start_date}')
  AND Date < toDate('{end_date}')
  AND ((Region = '{region}'))
GROUP BY toStartOfDay(toDateTime(Date))
ORDER BY "BSOM Impact" DESC
LIMIT 10000;
"""
    },
    {
        "name": "ai_browsers_bsom_analysis",
        "description": "Analyze the BSoM of Doubao and Quark AI browsers in China",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["region"],
        "template": """
SELECT toStartOfDay(toDateTime(Date)) AS __timestamp,
       SUM(DoubaoSeconds*DeviceWeight)/(SUM(AllBrowserSeconds_Upscaled) + SUM(DoubaoSeconds*DeviceWeight) + SUM(QuarkSeconds*DeviceWeight) + SUM(CiciSeconds*DeviceWeight)) AS "Doubao BSOM",
       SUM(QuarkSeconds*DeviceWeight)/(SUM(AllBrowserSeconds_Upscaled) + SUM(DoubaoSeconds*DeviceWeight) + SUM(QuarkSeconds*DeviceWeight) + SUM(CiciSeconds*DeviceWeight)) AS "Quark BSOM"
FROM Device_Aggregate_Analytics
WHERE Date >= toDate('{start_date}')
  AND Date < toDate('{end_date}')
  AND ((Region = '{region}'))
GROUP BY toStartOfDay(toDateTime(Date))
ORDER BY "Doubao BSOM" DESC
LIMIT 10000;
"""
    },
    {
        "name": "ai_browsers_minutes_analysis",
        "description": "Analyze the Minutes of Doubao and Quark AI browsers in China",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["region"],
        "template": """
SELECT toStartOfDay(toDateTime(Date)) AS __timestamp,
       SUM(DoubaoSeconds*DeviceWeight)/60 AS "Doubao Minutes",
       SUM(QuarkSeconds*DeviceWeight)/60 AS "Quark Minutes"
FROM Device_Aggregate_Analytics
WHERE Date >= toDate('{start_date}')
  AND Date < toDate('{end_date}')
  AND ((FormFactorFamily IN ('PC',
                             'Unknown',
                             'Tablet',
                             'Other'))
       AND (Region = '{region}'))
GROUP BY toStartOfDay(toDateTime(Date))
ORDER BY "Doubao Minutes" DESC
LIMIT 10000;
"""
    },
]
