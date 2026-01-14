"""
Metadata for EdgeMobileUserOverviewV3 table
"""

# Description of this table
DESCRIPTION = """
EdgeMobileUserOverviewV3 table contains Edge mobile user overview data including metrics such as 
user counts, activity levels, and usage patterns. This can be used to analyze mobile user trends 
across different time periods.
"""

# Sample data showing the table structure
SAMPLE = """
Sample data for EdgeMobileUserOverviewV3:

TitanProcessDate,cnt,rolling_window_range,platform_id,app_market,browser_id,release_channel,version_number,package_name
2025-02-21,1025,1,1,1,1,1,111.0.1661.36,com.microsoft.emmx
2025-02-22,1134,1,1,1,1,1,111.0.1661.36,com.microsoft.emmx
2025-02-23,989,1,1,1,1,1,111.0.1661.36,com.microsoft.emmx
"""

# Define filterable columns for templates
FILTER_COLUMNS = {
    "start_date": {
        "description": "Start date for data analysis",
    },
    "end_date": {
        "description": "End date for data analysis",
    },
    "rolling_window": {
        "description": "Time aggregation window for measurements",
        "values": {"1": "daily data", "7": "weekly data", "30": "monthly data"},
        "default": "1"
    },    "customer_type": {
        "description": "Type of customer account",
        "values": ["commercial", "consumer"]
    },    "osCategory": {
        "description": "Operating system category",
        "values": ["android", "ios"]
    },
    "install_channel_l1": {
        "description": "Installation channel identifier",
        "mapping": {
            "organic": "Organic installs",
            "upsell": "Upsell from other products",
            "paidads": "Paid advertising",
            "EdgePC": "Edge PC referrals",
            "Others": "Other channels",
            "OEM": "OEM installations"
        },
        "default": "organic"
    },
    "a15Region": {
        "description": "Geographic region identifiers (A15 regions)",
        "values": ["Greater China", "United States", "LATAM", "APAC", "MEA", "Japan", "India", "UK", "Korea", "Canada", "ANZ", "Unknown", ""]
    },
    "isNewUser": {
        "description": "Type of user based on experience",
        "mapping": {
            "0": "Existing users",
            "1": "New users"
        }
    },
}

SQL_TEMPLATES = [    {
        "name": "edge_mobile_dau",
        "description": "Edge mobile - Daily DAU with Rolling 7-Day Average",
        "template": """
WITH daily_data AS (
    SELECT toStartOfDay(toDateTime(`TitanProcessDate`)) AS `__timestamp`,
           SUM(cnt) AS `Total_Mobile_Daily_DAU`
    FROM `edge_prod`.`EdgeMobileUserOverviewV3`
    WHERE `TitanProcessDate` >= toDateTime('{start_date}')
      AND `TitanProcessDate` < toDateTime('{end_date}')
      AND ((rolling_window_range in (1)))
      {customer_type_filter}
      {os_category_filter}
      {region_filter}
    GROUP BY toStartOfDay(toDateTime(`TitanProcessDate`))
)
SELECT `__timestamp`,
       `Total_Mobile_Daily_DAU`,
       AVG(`Total_Mobile_Daily_DAU`) OVER (
           ORDER BY `__timestamp` ASC
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS `Rolling_7Day_Avg_DAU`
FROM daily_data
ORDER BY `__timestamp` ASC
LIMIT 50000;
""",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["a15Region", "customer_type", "osCategory"],
        "template_params": {
            "region_filter": lambda params: f"AND (a15Region IN ('{params.get('a15Region')}'))" if params.get('a15Region') and params.get('a15Region') != '' else "",
            "customer_type_filter": lambda params: f"AND (customer_type in ('{params.get('customer_type', 'consumer')}'))" if params.get('customer_type') else "",
            "os_category_filter": lambda params: f"AND (osCategory = '{params.get('osCategory', 'android')}')" if params.get('osCategory') else ""
        }
    },    {
        "name": "edge_mobile_install_source_breakdown_daily_dau",
        "description": "Edge mobile users by install source - Daily DAU breakdown with Rolling 7-Day Average",
        "template": """
WITH daily_breakdown AS (
    SELECT case
               when install_channel_l1 IN ('Organic',
                                           'PaidAds',
                                           'OEM') then install_channel_l1
               when install_channel_l1 = 'Upsell'
                    and install_channel_l2 IN ('EdgePC',
                                               'Outlook') then install_channel_l2
               when install_channel_l1 = 'Upsell'
                    and client_build_type = 'browser_production' then 'EdgePC'
               else 'Others'
           end AS `install_source`,
           toStartOfDay(toDateTime(`TitanProcessDate`)) AS `__timestamp`,
           SUM(cnt) AS `Daily_DAU`
    FROM `edge_prod`.`EdgeMobileUserOverviewV3` GLOBAL
    JOIN
      (SELECT case
                  when install_channel_l1 IN ('Organic',
                                              'PaidAds',
                                              'OEM') then install_channel_l1
                  when install_channel_l1 = 'Upsell'
                       and install_channel_l2 IN ('EdgePC',
                                                  'Outlook') then install_channel_l2
                  when install_channel_l1 = 'Upsell'
                       and client_build_type = 'browser_production' then 'EdgePC'
                  else 'Others'
              end AS `install_source__`,
              SUM(cnt) AS `mme_inner__`
       FROM `edge_prod`.`EdgeMobileUserOverviewV3`
       WHERE ((rolling_window_range in (1)))
         {customer_type_filter_inner}
         {os_category_filter_inner}
       GROUP BY case
                    when install_channel_l1 IN ('Organic',
                                                'PaidAds',
                                                'OEM') then install_channel_l1
                    when install_channel_l1 = 'Upsell'
                         and install_channel_l2 IN ('EdgePC',
                                                    'Outlook') then install_channel_l2
                    when install_channel_l1 = 'Upsell'
                         and client_build_type = 'browser_production' then 'EdgePC'
                    else 'Others'
                end
       ORDER BY SUM(cnt) DESC
       LIMIT 25) AS `series_limit` ON case
                                          when install_channel_l1 IN ('Organic',
                                                                      'PaidAds',
                                                                      'OEM') then install_channel_l1
                                          when install_channel_l1 = 'Upsell'
                                               and install_channel_l2 IN ('EdgePC',
                                                                          'Outlook') then install_channel_l2
                                          when install_channel_l1 = 'Upsell'
                                               and client_build_type = 'browser_production' then 'EdgePC'
                                          else 'Others'
                                      end = `install_source__`
    WHERE `TitanProcessDate` >= toDateTime('{start_date}')
      and `TitanProcessDate` < toDateTime('{end_date}')
      and ((rolling_window_range in (1)))
      {customer_type_filter}
      {os_category_filter}
      {region_filter}
    GROUP BY case
                 when install_channel_l1 IN ('Organic',
                                             'PaidAds',
                                             'OEM') then install_channel_l1
                 when install_channel_l1 = 'Upsell'
                      and install_channel_l2 IN ('EdgePC',
                                                 'Outlook') then install_channel_l2
                 when install_channel_l1 = 'Upsell'
                      and client_build_type = 'browser_production' then 'EdgePC'
                 else 'Others'
             end,
             toStartOfDay(toDateTime(`TitanProcessDate`))
)
SELECT `install_source`,
       `__timestamp`,
       `Daily_DAU`,
       AVG(`Daily_DAU`) OVER (
           PARTITION BY `install_source`
           ORDER BY `__timestamp` ASC
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS `Rolling_7Day_Avg_DAU`
FROM daily_breakdown
ORDER BY `Daily_DAU` DESC, `__timestamp` ASC
LIMIT 10000;
""",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["a15Region", "customer_type", "osCategory"],
        "template_params": {
            "region_filter": lambda params: f"AND (a15Region IN ('{params.get('a15Region')}'))" if params.get('a15Region') and params.get('a15Region') != '' else "",
            "customer_type_filter": lambda params: f"AND (customer_type in ('{params.get('customer_type', 'consumer')}'))" if params.get('customer_type') else "",
            "customer_type_filter_inner": lambda params: f"AND (customer_type in ('{params.get('customer_type', 'consumer')}'))" if params.get('customer_type') else "",
            "os_category_filter": lambda params: f"AND (osCategory = '{params.get('osCategory', 'android')}')" if params.get('osCategory') else "",
            "os_category_filter_inner": lambda params: f"AND (osCategory = '{params.get('osCategory', 'android')}')" if params.get('osCategory') else ""
        }
    },    {
        "name": "edge_mobile_region_breakdown_daily_dau",
        "description": "Edge mobile users by region - Daily DAU breakdown with Rolling 7-Day Average",
        "template": """
WITH daily_breakdown AS (
    SELECT `a15Region` AS `a15Region`,
           toStartOfDay(toDateTime(`TitanProcessDate`)) AS `__timestamp`,
           SUM(cnt) AS `Daily_DAU`
    FROM `edge_prod`.`EdgeMobileUserOverviewV3` GLOBAL
    JOIN
      (SELECT `a15Region` AS `a15Region__`,
              SUM(cnt) AS `mme_inner__`
       FROM `edge_prod`.`EdgeMobileUserOverviewV3`
       WHERE ((rolling_window_range in (1)))
         {customer_type_filter_inner}
         {os_category_filter_inner}
       GROUP BY `a15Region`
       ORDER BY SUM(cnt) DESC
       LIMIT 25) AS `series_limit` ON `a15Region` = `a15Region__`
    WHERE `TitanProcessDate` >= toDateTime('{start_date}')
      and `TitanProcessDate` < toDateTime('{end_date}')
      and ((rolling_window_range in (1)))
      {customer_type_filter}
      {os_category_filter}
      {region_filter}
    GROUP BY `a15Region`,
             toStartOfDay(toDateTime(`TitanProcessDate`))
)
SELECT `a15Region`,
       `__timestamp`,
       `Daily_DAU`,
       AVG(`Daily_DAU`) OVER (
           PARTITION BY `a15Region`
           ORDER BY `__timestamp` ASC
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS `Rolling_7Day_Avg_DAU`
FROM daily_breakdown
ORDER BY `Daily_DAU` DESC, `__timestamp` ASC
LIMIT 10000;
""",
        "required_filters": ["start_date", "end_date"],
        "optional_filters": ["a15Region", "customer_type", "osCategory"],
        "template_params": {
            "region_filter": lambda params: f"AND (a15Region IN ('{params.get('a15Region')}'))" if params.get('a15Region') and params.get('a15Region') != '' else "",
            "customer_type_filter": lambda params: f"AND (customer_type in ('{params.get('customer_type', 'consumer')}'))" if params.get('customer_type') else "",
            "customer_type_filter_inner": lambda params: f"AND (customer_type in ('{params.get('customer_type', 'consumer')}'))" if params.get('customer_type') else "",
            "os_category_filter": lambda params: f"AND (osCategory = '{params.get('osCategory', 'android')}')" if params.get('osCategory') else "",
            "os_category_filter_inner": lambda params: f"AND (osCategory = '{params.get('osCategory', 'android')}')" if params.get('osCategory') else ""
        }
    }
]
