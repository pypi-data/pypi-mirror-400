"""
Microsoft Edge Mobile Weekly Report Generation Utils

This module provides functionality to generate weekly reports specifically for Microsoft Edge Mobile
using R7 DAU (7-day rolling Daily Active Users) data from Titan API.

Target Product: Microsoft Edge Mobile (iOS & Android platforms)
Data Source: EdgeMobileUserOverviewV3 table via Titan API
Report Scope: Weekly R7 DAU analysis with multi-dimensional breakdowns including:
- OS Category (iOS vs Android)
- Regional distribution 
- Customer type segmentation
- Install source analytics
- New vs returning user metrics

Integration: Works seamlessly with the existing PM Studio MCP framework and TitanQuery authentication.
"""

from datetime import datetime, timedelta
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pm_studio_mcp.utils.titan.titan_query_utils import TitanQuery
from pm_studio_mcp.config import config
from .html_report_generator import HTMLReportGenerator

# Import the teams summary generator from the local module
try:
    from .weekly_report_teams_summary import generate_teams_summary
except ImportError:
    # Module might not be available during development or testing
    pass


class EdgeMobileWeeklyReportUtils:
    """Utility class for generating Microsoft Edge Mobile weekly reports."""
    
    def __init__(self):
        """Initialize the EdgeMobileWeeklyReportUtils with Titan API connection."""
        self.titan_query = TitanQuery(config.TITAN_ENDPOINT)
    
    def generate_report(self, report_date: str, customer_type: str = None) -> str:
        """
        Generate a Microsoft Edge Mobile weekly report for the specified date.
        
        This method processes Edge Mobile data from EdgeMobileUserOverviewV3 table
        to create comprehensive R7 DAU analysis reports.
        
        Args:
            report_date (str): The date for which to generate the Edge Mobile report (YYYY-MM-DD format)
            customer_type (str, optional): Customer type filter for the report. Defaults to None.
            
        Returns:
            str: Status message indicating success or failure of Edge Mobile report generation
        """
        try:
            # Step 1: Fetch Edge Mobile data from Titan API
            weekly_data = self._get_edge_mobile_report_data(report_date, customer_type)
            if weekly_data is None or weekly_data.empty:
                return f"Failed to fetch Edge Mobile data for report date: {report_date}"
            
            print(f"Fetched Edge Mobile weekly data with {len(weekly_data)} rows")
            
            # Step 2: Process the Edge Mobile data
            processed_data = self._process_edge_mobile_report_data(weekly_data)
            print(f"Processed Edge Mobile data - DAU OS DF shape: {processed_data['dau_os_df'].shape}")
            
            # Step 3: Calculate difference ratios for Edge Mobile metrics
            enhanced_data = self._calculate_diff_ratios(processed_data)
            print(f"Enhanced Edge Mobile data - DAU OS DF shape: {enhanced_data['dau_os_df'].shape}")
            
            # Step 4: Calculate contributor analysis
            contributor_results = None
            try:
                from .contributor_analysis import calculate_contributor_analysis
                contributor_results = calculate_contributor_analysis(enhanced_data)
                print("Contributor analysis completed")
                
                # Print some key findings
                for metric_period, summary in contributor_results['summaries'].items():
                    if 'r7_dau_7d' in metric_period:  # Focus on R7 DAU 7-day changes
                        print(f"\n=== Key Contributors for {metric_period} ===")
                        top_contributors = summary['top_contributors']
                        if not top_contributors.empty:
                            for idx, (_, row) in enumerate(top_contributors.head(3).iterrows(), 1):
                                print(f"{idx}. {row['dimension']} - {row['breakdown']}: "
                                      f"{row['absolute_change']:+,.0f} ({row['contribution_to_total']:+.1f}%)")
            except Exception as e:
                print(f"Warning: Contributor analysis failed: {str(e)}")
            
            # Step 5: Save Edge Mobile report data
            report_path = self._save_edge_mobile_report_data(enhanced_data, report_date)
            
            # Step 6: Generate Edge Mobile HTML report with contributor analysis
            try:
                html_generator = HTMLReportGenerator()
                html_path = html_generator.generate_html_report(enhanced_data, weekly_data, report_date, contributor_results)
                print(f"Edge Mobile HTML report generated successfully: {html_path}")
                
                # Path to Teams message file
                teams_message_path = os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports', f'TeamsMessage_{report_date}.html')

                if os.path.exists(teams_message_path):
                    return f"Microsoft Edge Mobile weekly report generated successfully. Summary: {report_path}, HTML: {html_path}, Teams Message: {teams_message_path}"
                else:
                    return f"Microsoft Edge Mobile weekly report generated successfully. Summary: {report_path}, HTML: {html_path}"
            except Exception as e:
                print(f"Failed to generate Edge Mobile HTML report: {str(e)}")
                return f"Microsoft Edge Mobile weekly report generated successfully. Summary: {report_path}. HTML generation failed: {str(e)}"
            
        except Exception as e:
            return f"Failed to generate Microsoft Edge Mobile weekly report: {str(e)}"
    
    def _get_edge_mobile_report_data(self, report_date: str, customer_type:str=None) -> Optional[pd.DataFrame]:
        """
        Fetch Microsoft Edge Mobile report data from Titan API EdgeMobileUserOverviewV3 table.
        
        Args:
            report_date (str): The report date in YYYY-MM-DD format
            
        Returns:
            Optional[pd.DataFrame]: The fetched Edge Mobile data or None if failed
        """
        try:
            date_obj = datetime.strptime(report_date, '%Y-%m-%d')
            start_date = (date_obj - timedelta(days=460)).strftime('%Y-%m-%d')

            # Determine customer type filter
            customer_type_filter = ""
            if customer_type is not None:
                customer_type_filter = f"AND customer_type = '{customer_type}'"
                print(f"DEBUG customer_type filter applied: {customer_type_filter}",flush=True)

            sql_query = f"""
                SELECT
                    osCategory,
                    isNewUser,
                    customer_type,
                    reporting_region,
                    install_source,
                    date,
                    client_count,
                    rolling_7d_avg
                FROM (
                    SELECT
                        osCategory,
                        isNewUser,
                        customer_type,
                        CASE
                            WHEN a15Region = 'United States' THEN 'US'
                            WHEN a15Region IN ('France', 'UK', 'Canada', 'Germany', 'ANZ') THEN 'T5 FR, UK, AU, CA, DE'
                            WHEN a15Region IN ('Japan', 'Korea') THEN 'JP/KR'
                            WHEN a15Region = 'Greater China' THEN 'CN'
                            WHEN a15Region IN ('Western Europe', 'CEE') THEN 'Other EU'
                            WHEN a15Region = 'Latam' THEN 'LATAM'
                            WHEN a15Region = 'India' THEN 'IN'
                            WHEN a15Region IN ('APAC', 'MEA', 'Others', 'Unknown') THEN 'ROW'
                            ELSE 'ROW'
                        END AS reporting_region,
                        CASE
                            WHEN install_channel_l1 IN ('Organic', 'PaidAds', 'OEM') THEN install_channel_l1
                            WHEN install_channel_l1 = 'Upsell' AND install_channel_l2 IN ('EdgePC', 'Outlook') THEN install_channel_l2
                            WHEN install_channel_l1 = 'Upsell' AND client_build_type = 'browser_production' THEN 'EdgePC'
                            ELSE 'Others'
                        END AS install_source,
                        toStartOfDay(toDateTime(TitanProcessDate)) AS date,
                        SUM(cnt) AS client_count,
                        AVG(SUM(cnt)) OVER (
                            PARTITION BY osCategory, isNewUser, customer_type,
                                        CASE
                                            WHEN a15Region = 'United States' THEN 'US'
                                            WHEN a15Region IN ('France', 'UK', 'Canada', 'Germany', 'ANZ') THEN 'T5 FR, UK, AU, CA, DE'
                                            WHEN a15Region IN ('Japan', 'Korea') THEN 'JP/KR'
                                            WHEN a15Region = 'Greater China' THEN 'CN'
                                            WHEN a15Region IN ('Western Europe', 'CEE') THEN 'Other EU'
                                            WHEN a15Region = 'Latam' THEN 'LATAM'
                                            WHEN a15Region = 'India' THEN 'IN'
                                            WHEN a15Region IN ('APAC', 'MEA', 'Others', 'Unknown') THEN 'ROW'
                                            ELSE 'ROW'
                                        END,
                                        CASE
                                            WHEN install_channel_l1 IN ('Organic', 'PaidAds', 'OEM') THEN install_channel_l1
                                            WHEN install_channel_l1 = 'Upsell' AND install_channel_l2 IN ('EdgePC', 'Outlook') THEN install_channel_l2
                                            WHEN install_channel_l1 = 'Upsell' AND client_build_type = 'browser_production' THEN 'EdgePC'
                                            ELSE 'Others'
                                        END
                            ORDER BY toStartOfDay(toDateTime(TitanProcessDate))
                            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                        ) AS rolling_7d_avg,
                        ROW_NUMBER() OVER (
                            PARTITION BY osCategory, isNewUser, customer_type,
                                        CASE
                                            WHEN a15Region = 'United States' THEN 'US'
                                            WHEN a15Region IN ('France', 'UK', 'Canada', 'Germany', 'ANZ') THEN 'T5 FR, UK, AU, CA, DE'
                                            WHEN a15Region IN ('Japan', 'Korea') THEN 'JP/KR'
                                            WHEN a15Region = 'Greater China' THEN 'CN'
                                            WHEN a15Region IN ('Western Europe', 'CEE') THEN 'Other EU'
                                            WHEN a15Region = 'Latam' THEN 'LATAM'
                                            WHEN a15Region = 'India' THEN 'IN'
                                            WHEN a15Region IN ('APAC', 'MEA', 'Others', 'Unknown') THEN 'ROW'
                                            ELSE 'ROW'
                                        END,
                                        CASE
                                            WHEN install_channel_l1 IN ('Organic', 'PaidAds', 'OEM') THEN install_channel_l1
                                            WHEN install_channel_l1 = 'Upsell' AND install_channel_l2 IN ('EdgePC', 'Outlook') THEN install_channel_l2
                                            WHEN install_channel_l1 = 'Upsell' AND client_build_type = 'browser_production' THEN 'EdgePC'
                                            ELSE 'Others'
                                        END
                            ORDER BY toStartOfDay(toDateTime(TitanProcessDate))
                        ) AS rn
                    FROM EdgeMobileUserOverviewV3
                    WHERE TitanProcessDate >= toDateTime('{start_date}')
                    AND TitanProcessDate <= toDateTime('{report_date}')
                    AND rolling_window_range IN (1)
                    {customer_type_filter}
                    GROUP BY
                        osCategory,
                        isNewUser,
                        customer_type,
                        CASE
                            WHEN a15Region = 'United States' THEN 'US'
                            WHEN a15Region IN ('France', 'UK', 'Canada', 'Germany', 'ANZ') THEN 'T5 FR, UK, AU, CA, DE'
                            WHEN a15Region IN ('Japan', 'Korea') THEN 'JP/KR'
                            WHEN a15Region = 'Greater China' THEN 'CN'
                            WHEN a15Region IN ('Western Europe', 'CEE') THEN 'Other EU'
                            WHEN a15Region = 'Latam' THEN 'LATAM'
                            WHEN a15Region = 'India' THEN 'IN'
                            WHEN a15Region IN ('APAC', 'MEA', 'Others', 'Unknown') THEN 'ROW'
                            ELSE 'ROW'
                        END,
                        CASE
                            WHEN install_channel_l1 IN ('Organic', 'PaidAds', 'OEM') THEN install_channel_l1
                            WHEN install_channel_l1 = 'Upsell' AND install_channel_l2 IN ('EdgePC', 'Outlook') THEN install_channel_l2
                            WHEN install_channel_l1 = 'Upsell' AND client_build_type = 'browser_production' THEN 'EdgePC'
                            ELSE 'Others'
                        END,
                        toStartOfDay(toDateTime(TitanProcessDate))
                )
                WHERE rn >= 7
                ORDER BY date
            """
            
            table_name = "EdgeMobileUserOverviewV3"  # Edge Mobile specific table
            
            # Use the existing TitanQuery to fetch Edge Mobile data
            result = self.titan_query.query_data_from_titan_tool(sql_query, table_name)
            
            if isinstance(result, dict) and 'file_path' in result:
                # Read the CSV file that was created
                weekly_data = pd.read_csv(result['file_path'])
                weekly_data['date'] = pd.to_datetime(weekly_data['date'])
                weekly_data['client_count'] = weekly_data['client_count'].astype(int)
                weekly_data['rolling_7d_avg'] = weekly_data['rolling_7d_avg'].astype(float)
                
                # Save a copy for the Edge Mobile report
                os.makedirs(os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports'), exist_ok=True)
                original_data_path = os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports', f'edge_mobile_original_data_{report_date}.csv')
                weekly_data.to_csv(original_data_path, index=False)
                
                return weekly_data
            else:
                print(f"Unexpected result format from Titan query: {result}")
                return None
                
        except Exception as e:
            print(f"Error fetching Edge Mobile report data: {str(e)}")
            return None
    
    def _process_edge_mobile_report_data(self, weekly_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Process the raw Microsoft Edge Mobile weekly data into structured format.
        Same as reference project's process_report_data function.
        
        Args:
            weekly_data (pd.DataFrame): Raw Edge Mobile weekly data from EdgeMobileUserOverviewV3
            
        Returns:
            Dict[str, pd.DataFrame]: Processed Edge Mobile data with different dimensional views
        """
        try:
            # Group by different dimensions - same structure as reference project
            processed_data = {}
            
            # DAU tables (client_count)
            processed_data['dau_os_df'] = weekly_data.groupby(['date', 'osCategory'])['client_count'].sum().reset_index()
            processed_data['dau_os_df'].columns = ['date', 'os', 'client_count']
            
            processed_data['dau_is_new_df'] = weekly_data[weekly_data['isNewUser'] == 1].groupby(['date', 'osCategory'])['client_count'].sum().reset_index()
            processed_data['dau_is_new_df'].columns = ['date', 'is_new', 'client_count']
            
            processed_data['dau_customer_type_df'] = weekly_data.groupby(['date', 'customer_type'])['client_count'].sum().reset_index()
            processed_data['dau_customer_type_df'].columns = ['date', 'customer_type', 'client_count']
            
            processed_data['dau_region_df'] = weekly_data.groupby(['date', 'reporting_region'])['client_count'].sum().reset_index()
            processed_data['dau_region_df'].columns = ['date', 'region', 'client_count']
            
            processed_data['dau_install_source_df'] = weekly_data.groupby(['date', 'install_source'])['client_count'].sum().reset_index()
            processed_data['dau_install_source_df'].columns = ['date', 'install_source', 'client_count']

            # R7 DAU tables (rolling_7d_avg)
            processed_data['r7_dau_os_df'] = weekly_data.groupby(['date', 'osCategory'])['rolling_7d_avg'].sum().reset_index()
            processed_data['r7_dau_os_df'].columns = ['date', 'os', 'rolling_7d_avg']
            
            processed_data['r7_dau_is_new_df'] = weekly_data[weekly_data['isNewUser'] == 1].groupby(['date', 'osCategory'])['rolling_7d_avg'].sum().reset_index()
            processed_data['r7_dau_is_new_df'].columns = ['date', 'is_new', 'rolling_7d_avg']
            
            processed_data['r7_dau_customer_type_df'] = weekly_data.groupby(['date', 'customer_type'])['rolling_7d_avg'].sum().reset_index()
            processed_data['r7_dau_customer_type_df'].columns = ['date', 'customer_type', 'rolling_7d_avg']
            
            processed_data['r7_dau_region_df'] = weekly_data.groupby(['date', 'reporting_region'])['rolling_7d_avg'].sum().reset_index()
            processed_data['r7_dau_region_df'].columns = ['date', 'region', 'rolling_7d_avg']
            
            processed_data['r7_dau_install_source_df'] = weekly_data.groupby(['date', 'install_source'])['rolling_7d_avg'].sum().reset_index()
            processed_data['r7_dau_install_source_df'].columns = ['date', 'install_source', 'rolling_7d_avg']
            
            # Sort all DataFrames by date
            for key, df in processed_data.items():
                processed_data[key] = df.sort_values('date').reset_index(drop=True)
                print(f"DEBUG processed table {key}: {df.shape[0]} rows, columns: {df.columns.tolist()}")
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing Edge Mobile report data: {str(e)}")
            return {}
    
    def _calculate_diff_ratios(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Calculate week-over-week difference ratios for the processed data.
        Same logic as reference project's calculate_diff_ratios function.
        
        Args:
            processed_data (Dict[str, pd.DataFrame]): Processed data from _process_report_data
            
        Returns:
            Dict[str, pd.DataFrame]: Enhanced data with difference ratios
        """
        def add_diff_ratios(df: pd.DataFrame, value_column: str, dimension_column: str) -> pd.DataFrame:
            """Add difference ratio columns to a DataFrame"""
            df = df.copy()
            result_dfs = []
            
            # Process each dimension separately
            for dimension_value in df[dimension_column].unique():
                dim_df = df[df[dimension_column] == dimension_value].sort_values('date').reset_index(drop=True)
                
                if len(dim_df) >= 28:  # Ensure we have enough data points
                    # Get the last value
                    last_value = dim_df[value_column].iloc[-1]
                    
                    # Calculate diff ratios safely
                    def safe_diff_ratio(current_val, past_val):
                        if pd.isna(past_val) or past_val == 0:
                            return None
                        return (current_val - past_val) / past_val
                    
                    # Add difference ratio columns
                    dim_df['diff_7d_ratio'] = None
                    dim_df['diff_14d_ratio'] = None
                    dim_df['diff_21d_ratio'] = None
                    dim_df['diff_28d_ratio'] = None
                    dim_df['diff_1y_ratio'] = None
                    dim_df['value_7d_ago'] = None

                    # Only calculate for the last row
                    if len(dim_df) > 7:
                        past_7d_val = dim_df[value_column].iloc[-8] if len(dim_df) >= 8 else None
                        dim_df.loc[dim_df.index[-1], 'diff_7d_ratio'] = safe_diff_ratio(last_value, past_7d_val)
                        dim_df.loc[dim_df.index[-1], 'value_7d_ago'] = past_7d_val
                    if len(dim_df) > 14:
                        dim_df.loc[dim_df.index[-1], 'diff_14d_ratio'] = safe_diff_ratio(
                            last_value, dim_df[value_column].iloc[-15] if len(dim_df) >= 15 else None
                        )
                    if len(dim_df) > 21:
                        dim_df.loc[dim_df.index[-1], 'diff_21d_ratio'] = safe_diff_ratio(
                            last_value, dim_df[value_column].iloc[-22] if len(dim_df) >= 22 else None
                        )
                    if len(dim_df) > 28:
                        dim_df.loc[dim_df.index[-1], 'diff_28d_ratio'] = safe_diff_ratio(
                            last_value, dim_df[value_column].iloc[-29] if len(dim_df) >= 29 else None
                        )
                    if len(dim_df) > 364:
                        dim_df.loc[dim_df.index[-1], 'diff_1y_ratio'] = safe_diff_ratio(
                            last_value, dim_df[value_column].iloc[-365] if len(dim_df) >= 365 else None
                        )
                
                # Keep only the last row for analysis
                dim_df = dim_df.tail(1)
                result_dfs.append(dim_df)
            
            return pd.concat(result_dfs, ignore_index=True).sort_values('date')
        
        enhanced_data = {}
        
        # Process each table - same configuration as reference project
        table_configs = [
            ('dau_os_df', 'client_count', 'os'),
            ('dau_is_new_df', 'client_count', 'is_new'),
            ('dau_customer_type_df', 'client_count', 'customer_type'),
            ('dau_region_df', 'client_count', 'region'),
            ('dau_install_source_df', 'client_count', 'install_source'),
            ('r7_dau_os_df', 'rolling_7d_avg', 'os'),
            ('r7_dau_is_new_df', 'rolling_7d_avg', 'is_new'),
            ('r7_dau_customer_type_df', 'rolling_7d_avg', 'customer_type'),
            ('r7_dau_region_df', 'rolling_7d_avg', 'region'),
            ('r7_dau_install_source_df', 'rolling_7d_avg', 'install_source')]
        
        for table_name, value_col, dim_col in table_configs:
            if table_name in processed_data:
                print(f"DEBUG processing {table_name} with {value_col} and {dim_col}")
                enhanced_data[table_name] = add_diff_ratios(
                    processed_data[table_name], value_col, dim_col
                )
                print(f"DEBUG {table_name} processed, final shape: {enhanced_data[table_name].shape}")
        
        return enhanced_data
    
    def _save_edge_mobile_report_data(self, enhanced_data: Dict[str, pd.DataFrame], report_date: str) -> str:
        """
        Save the enhanced Microsoft Edge Mobile report data to files.
        Same logic as reference project's save_report_data function.
        
        Args:
            enhanced_data (Dict[str, pd.DataFrame]): Enhanced Edge Mobile data with calculations
            report_date (str): Report date for file naming
            
        Returns:
            str: Path to the main Edge Mobile report file
        """
        try:
            print("\n\n\n-------------------- START save_report_data --------------------")
            all_data = []
            for table_name, df in enhanced_data.items():
                # Display each table with its visualization
                data = self._get_summary_table(df, table_name)
                print(f"DEBUG save_report_data {table_name} summary data: {data.shape[0]} rows, columns: {data.columns.tolist()}")
                print(f"DEBUG save_report_data {table_name} data:\n{data.head()}")
                
                # Add type column and collect data
                data['Type'] = table_name
                all_data.append(data)
            
            # Combine all data into one DataFrame
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\nCombined DataFrame shape: {combined_df.shape}")
            print(f"Combined DataFrame columns: {combined_df.columns.tolist()}")
            print(f"Combined DataFrame:\n{combined_df}")

            # Create Edge Mobile report directory
            report_dir = os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports')
            os.makedirs(report_dir, exist_ok=True)
            
            # Save combined report data
            report_path = os.path.join(report_dir, f'weekly_report_data_{report_date}.csv')
            combined_df.to_csv(report_path, index=False)
            
            # Generate Teams summary file
            try:
                # Use the local module import
                from .weekly_report_teams_summary import generate_teams_summary
                
                # Create EDGE_MOBILE_WEEKLY_REPORTS directory for Teams message
                teams_dir = report_dir
                os.makedirs(teams_dir, exist_ok=True)
                
                # Define Teams message output path
                teams_message_path = os.path.join(teams_dir, f'TeamsMessage_{report_date}.html')
                
                # HTML report URL
                html_report_url = f"https://gim-home.github.io/pm-studio-mcp/weekly_r7_dau_report_{report_date}.html"
                
                # Generate Teams summary
                print(f"Generating Teams summary at {teams_message_path} with report URL {html_report_url}", flush=True)
                generate_teams_summary(report_path, html_report_url, teams_message_path)
                print(f"Teams summary generated successfully: {teams_message_path}", flush=True)
            except Exception as e:
                print(f"Warning: Failed to generate Teams summary: {str(e)}", flush=True)

            return report_path
            
        except Exception as e:
            print(f"Error saving Edge Mobile report data: {str(e)}", flush=True)
            return f"Error saving Edge Mobile report: {str(e)}"
    
    def _get_summary_table(self, df: pd.DataFrame, table_name: str):
        """Display summary statistics in table format using Chainlit DataFrame"""
        
        # Load baseline data
        baseline_df = self._load_baseline_data()
        
        # Get the latest date
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        # Determine the dimension column and value column
        dimension_col = None
        value_col = None
        
        if 'os' in df.columns:
            dimension_col = 'os'
        elif 'is_new' in df.columns:
            dimension_col = 'is_new'
        elif 'customer_type' in df.columns:
            dimension_col = 'customer_type'
        elif 'region' in df.columns:
            dimension_col = 'region'
        elif 'install_source' in df.columns:
            dimension_col = 'install_source'
        
        if 'client_count' in df.columns:
            value_col = 'client_count'
        elif 'rolling_7d_avg' in df.columns:
            value_col = 'rolling_7d_avg'
        
        if dimension_col and value_col and not latest_data.empty:
            # Create summary DataFrame
            summary_data = []
            
            for _, row in latest_data.iterrows():
                dimension_value = row[dimension_col]
                current_value = row[value_col]
                value_7d_ago = row['value_7d_ago']
                
                # Prepare row data
                row_data = {
                    'Dimension': str(dimension_value),
                    # 'Latest Date': latest_date.strftime('%Y-%m-%d'),
                    'Value': f"{current_value:,.0f}",
                    'Value Last Week': f"{value_7d_ago:,.0f}" if pd.notna(value_7d_ago) else "N/A",
                }
                
                # Add difference ratios with baseline comparison
                ratio_cols = ['diff_7d_ratio', 'diff_14d_ratio', 'diff_21d_ratio', 'diff_28d_ratio', 'diff_1y_ratio']
                ratio_labels = ['7d', '14d', '21d', '28d', '1y']
                dr_types = ['DR7', 'DR14', 'DR21', 'DR28', 'DR1y']
                
                for ratio_col, label, dr_type in zip(ratio_cols, ratio_labels, dr_types):
                    if ratio_col in row and pd.notna(row[ratio_col]):
                        current_ratio = row[ratio_col]
                        
                        # Get baseline statistics
                        baseline_stats = self._get_baseline_for_dimension(baseline_df, table_name, str(dimension_value), dr_type)
                        
                        # Format with color indicator and baseline
                        color_indicator = self._get_color_indicator(current_ratio, baseline_stats)
                        if baseline_stats:
                            baseline_text = f" ({baseline_stats['median']:.1%})"
                        else:
                            baseline_text = ""
                        
                        row_data[f'Diff Ratio {label}'] = f"{color_indicator}{current_ratio:.2%}{baseline_text}"
                    else:
                        row_data[f'Diff Ratio {label}'] = "N/A"
                
                summary_data.append(row_data)
            
            if summary_data:
                # Create DataFrame from summary data
                summary_df = pd.DataFrame(summary_data)
            return summary_df

    def _get_baseline_for_dimension(self, baseline_df, dataset, column, dr_type):
        """Get baseline statistics for a specific dimension and DR type"""
        if baseline_df is None:
            return None
        
        mask = (baseline_df['Dataset'] == dataset) & (baseline_df['Column'] == column) & (baseline_df['DR_Type'] == dr_type)
        baseline_row = baseline_df[mask]
        
        if not baseline_row.empty:
            return {
                'median': baseline_row.iloc[0]['Median'],
                'p10': baseline_row.iloc[0]['P10'],
                'p25': baseline_row.iloc[0]['P25'],
                'p75': baseline_row.iloc[0]['P75'],
                'p90': baseline_row.iloc[0]['P90'],
                'p5': baseline_row.iloc[0]['P5'],
                'p95': baseline_row.iloc[0]['P95']
            }
        return None

    def _get_color_indicator(self, current_value, baseline_stats):
        """Get color indicator based on current value vs baseline percentiles"""
        if baseline_stats is None or current_value is None:
            return ""
        
        if baseline_stats['p25'] <= current_value <= baseline_stats['p75']:
            return "Green:"  # Green: Normal range
        elif (baseline_stats['p10'] <= current_value < baseline_stats['p25']) or (baseline_stats['p75'] < current_value <= baseline_stats['p90']):
            return "Yellow:"  # Yellow: Warning range
        else:
            return "Red:"  # Red: Abnormal range

    def _load_baseline_data(self):
        """Load baseline statistical summary from CSV file"""
        try:
            baseline_path = os.path.join(os.path.dirname(__file__), 'baseline', 'diff_ratio_statistical_summary_reporting_region.csv')
            baseline_df = pd.read_csv(baseline_path)
            return baseline_df
        except Exception as e:
            print(f"Warning: Could not load baseline data: {e}")
            return None
