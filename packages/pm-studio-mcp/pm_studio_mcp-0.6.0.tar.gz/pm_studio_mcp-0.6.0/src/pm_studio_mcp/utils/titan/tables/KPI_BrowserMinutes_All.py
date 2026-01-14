"""
Metadata for KPI_BrowserMinutes_All table
"""

DESCRIPTION = """
Browser Minutes Share on Windows
"""

SAMPLE = \
"""
Date,BrowserName,CustomerGroup,CustomerSubGroup,EducationSegment,Manufacturer,OsSku,Os,FormFactorFamily,FormFactor,A14Region,DeviceType,NewDeviceFlag,HasMSA,DefaultInternetBrowser,TpidSegmentGroup,TpidSegment,TpidSubSegment,TpidIndustry,TpidIndustrySummary,TpidIsS500,TpidIsS2500,TelemetryActiveDevices_Daily,TelemetryBrowsingMinutes_Daily,TelemetryPrimaryActiveDevices_Daily,TelemetryPrimaryBrowsingMinutes_Daily,ActiveDevices_Daily,BrowsingMinutes_Daily,PrimaryActiveDevices_Daily,PrimaryBrowsingMinutes_Daily,TelemetryActiveDevices_RL7,TelemetryBrowsingMinutes_RL7,TelemetryPrimaryActiveDevices_RL7,TelemetryPrimaryBrowsingMinutes_RL7,ActiveDevices_RL7,BrowsingMinutes_RL7,PrimaryActiveDevices_RL7,PrimaryBrowsingMinutes_RL7,TelemetryActiveDevices_RL28,TelemetryBrowsingMinutes_RL28,TelemetryPrimaryActiveDevices_RL28,TelemetryPrimaryBrowsingMinutes_RL28,ActiveDevices_RL28,BrowsingMinutes_RL28,PrimaryActiveDevices_RL28,PrimaryBrowsingMinutes_RL28
2021-09-15 00:00:00,2345 Explorer,Commercial,Commercial Enterprise,Education HED,Other,Core,Windows 10 21H1 GA,PC,Convertible,ANZ,New,-1,Yes,2345Explorer,EDU,Major Public Sector,Major - Education,Higher Education,Education,0,0,0,0,0,0,0,0,0,0,0,0.0,0,0,0.0,0.0,0,0,1,11.617733333333332,0,0,1.8905642327532124,21.964071105664754,0,0
2021-09-15 00:00:00,2345 Explorer,Commercial,Commercial Enterprise,Education HED,Other,Core,Windows 10 21H1 GA,PC,Desktop,ANZ,Upgrade,-1,Yes,Chrome,EDU,Major Public Sector,Major - Education,Higher Education,Education,0,0,0,0,0,0,0,0,0,0,1,0.08125,0,0,1.8854546685368758,0.15319319181862118,0,0,1,1.5554833333333333,0,0,1.8854546685368758,2.9327933126646344,0,0
2021-09-15 00:00:00,2345 Explorer,Commercial,Commercial Enterprise,Education HED,Other,Core,Windows 10 19H2 GA,PC,Notebook,ANZ,New,-1,No,2345Explorer,EDU,Major Public Sector,Major - Education,Higher Education,Education,0,0,0,0,0,0,0,0,0,0,0,0.0,0,0,0.0,0.0,0,0,1,6.533833333333333,0,0,8.235838360017018,53.811595204624524,0,0
"""

FILTER_COLUMNS = {
    "A14Region": {
        "description": "User demographic region",
        "values": ["Greater China", "United States", "Latam", "APAC", "MEA", "Japan", "India", "UK", "Korea", "Canada", "ANZ", "Unknown", ""]
    },
    "start_date": {
        "description": "Start date for data analysis",
        "example": "2025-04-15"
    },
    "end_date": {
        "description": "End date for data analysis",
        "example": "2025-05-15"
    },
    "region": {
        "description": "Specific region for analysis (used in absolute browser minutes queries)",
        "values": ["Greater China", "United States", "Latam", "APAC", "MEA", "Japan", "India", "UK", "Korea", "Canada", "ANZ", "Unknown"],
        "default": "Greater China"
    },
    "segment": {
        "description": "Customer segment for data analysis",
        "values": ["Consumer", "Commercial", "Education", "Unknown"]
    },
}

SQL_TEMPLATES = [
    {
        "name": "edge_browser_minutes_windows_R7",
        "description": "Edge browser minutes for Windows,average over 7 days",
        "template": """
SELECT toStartOfDay(toDateTime(`Date`)) AS `__timestamp`,
       sumIf(BrowsingMinutes_RL7, BrowserName in('Ms1p', 'Edge (Overall) + IE')) / 
       sumIf(BrowsingMinutes_RL7, BrowserName in('AllUp', 'All Browsers')) AS `Total_MSFT_BSOM_R7`
FROM KPI_BrowserMinutes_All
WHERE `Date` >= toDateTime('{start_date}')
  AND `Date` < toDateTime('{end_date}')
  AND ((Date>=date_add(DAY, -720, now()))
       AND (FormFactorFamily IN ('PC',
                                 'Tablet',
                                 'Other',
                                 'Unknown'))
       AND (BrowserName IN ('AllUp',
                            'All Browsers',
                            'Ms1p',
                            'Edge (Overall) + IE',
                            'Edge (Overall)',
                            'Edge'))
       AND (DayOfWeek(Date) IN ('3'))
       AND (A14Region NOT IN ('CEE',
                              'France',
                              'Germany',
                              'Western Europe'))
       {region_filter}
       {segment_filter}
GROUP BY toStartOfDay(toDateTime(`Date`))
ORDER BY toStartOfDay(toDateTime(`Date`)) ASC
LIMIT 50000;
""",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["A14Region", "segment"],
        "template_params": {
            "region_filter": lambda params: f"AND (A14Region IN ('{params.get('A14Region')}'))" if params.get('A14Region') and params.get('A14Region') != '' else "",
            "segment_filter": lambda params: (
                "AND (IF(CustomerGroup == 'Consumer', 'Consumer', "
                "IF(CustomerGroup == 'Commercial', IF(startsWith(EducationSegment, 'Education'), 'Education', 'Commercial'), 'Unknown')) "
                f"IN ('{params.get('segment', '')}'))" if params.get('segment') else ""
            )
        }
    },
    {
        "name": "edge_browser_minutes_daily_absolute_R1",
        "description": "Get absolute browser minutes (R1 - daily) for MS1P and Edge separately, ordered by MS1P usage",
        "template": """
SELECT toStartOfDay(toDateTime(`Date`)) AS `__timestamp`,
       SUM(IF(BrowserName in('Ms1p', 'Edge (Overall) + IE'),BrowsingMinutes_Daily, 0)) AS `MS1P_BrowserMinutes_R1`,
       SUM(IF(BrowserName in('Edge', 'Edge (Overall)'),BrowsingMinutes_Daily, 0)) AS `Edge_BrowserMinutes_R1`
FROM `edge_prod`.`KPI_BrowserMinutes_All`
WHERE `Date` >= toDateTime('{start_date}')
  AND `Date` < toDateTime('{end_date}')
  AND ((A14Region = '{region}')
       AND (FormFactorFamily IN ('PC',
                                 'Tablet',
                                 'Other',
                                 'Unknown')))
GROUP BY toStartOfDay(toDateTime(`Date`))
ORDER BY `MS1P_BrowserMinutes_R1` DESC
LIMIT 10000;
""",
        "required_filters": ["start_date", "end_date", "region"],
        "optional_filters": ["segment"],
        "template_params": {
            "segment_filter": lambda params: (
                "AND (IF(CustomerGroup == 'Consumer', 'Consumer', "
                "IF(CustomerGroup == 'Commercial', IF(startsWith(EducationSegment, 'Education'), 'Education', 'Commercial'), 'Unknown')) "
                f"IN ('{params.get('segment', '')}'))" if params.get('segment') else ""
            )
        }
    }
]
