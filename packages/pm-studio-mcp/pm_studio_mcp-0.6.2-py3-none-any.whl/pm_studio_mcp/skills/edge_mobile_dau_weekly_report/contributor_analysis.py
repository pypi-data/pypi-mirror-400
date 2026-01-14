"""
Contributor Analysis Module for Weekly DAU Reports

This module calculates key driver analysis by computing how much each breakdown dimension
contributes to the overall DAU change. The calculation method is:
contribution = (breakdown_change_amount / total_change_amount) * 100%

Where:
- breakdown_change_amount = current_value - previous_value for each breakdown segment
- total_change_amount = sum of all breakdown changes (should equal overall change)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class ContributorAnalysis:
    """Calculate contributor analysis for DAU changes across different dimensions."""
    
    def __init__(self, enhanced_data: Dict[str, pd.DataFrame]):
        """
        Initialize with enhanced data containing all breakdown tables.
        
        Args:
            enhanced_data: Dictionary containing DataFrames for different breakdowns
        """
        self.enhanced_data = enhanced_data
        self.analysis_results = {}
    
    def calculate_all_contributions(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate contributor analysis for all dimensions and metrics.
        
        Returns:
            Dictionary containing contributor analysis results for each metric type
        """
        # Define analysis configurations
        analysis_configs = [
            # DAU (client_count) analysis
            {
                'metric_type': 'dau',
                'value_column': 'client_count',
                'time_periods': ['7d', '14d', '21d', '28d', '1y'],
                'dimensions': {
                    'OS': 'dau_os_df',
                    'Customer Type': 'dau_customer_type_df', 
                    'Region': 'dau_region_df',
                    'Install Source': 'dau_install_source_df',
                    'New User': 'dau_is_new_df'
                }
            },
            # R7 DAU (rolling_7d_avg) analysis
            {
                'metric_type': 'r7_dau',
                'value_column': 'rolling_7d_avg',
                'time_periods': ['7d', '14d', '21d', '28d', '1y'],
                'dimensions': {
                    'OS': 'r7_dau_os_df',
                    'Customer Type': 'r7_dau_customer_type_df',
                    'Region': 'r7_dau_region_df', 
                    'Install Source': 'r7_dau_install_source_df',
                    'New User': 'r7_dau_is_new_df'
                }
            }
        ]
        
        for config in analysis_configs:
            metric_type = config['metric_type']
            value_column = config['value_column']
            time_periods = config['time_periods']
            dimensions = config['dimensions']
            
            # Calculate contributions for this metric type
            metric_results = self._calculate_metric_contributions(
                metric_type, value_column, time_periods, dimensions
            )
            
            self.analysis_results[metric_type] = metric_results
        
        return self.analysis_results
    
    def _calculate_metric_contributions(self, metric_type: str, value_column: str, 
                                      time_periods: List[str], 
                                      dimensions: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Calculate contributor analysis for a specific metric type.
        
        Args:
            metric_type: Type of metric ('dau' or 'r7_dau')
            value_column: Column name containing the metric values
            time_periods: List of time periods to analyze
            dimensions: Dictionary mapping dimension names to table names
            
        Returns:
            Dictionary containing contributor analysis for each time period
        """
        period_results = {}
        
        for period in time_periods:
            # Calculate contributions for this time period
            contributions = self._calculate_period_contributions(
                period, value_column, dimensions
            )
            
            if contributions is not None and not contributions.empty:
                period_results[period] = contributions
        
        return period_results
    
    def _calculate_period_contributions(self, period: str, value_column: str,
                                      dimensions: Dict[str, str]) -> pd.DataFrame:
        """
        Calculate contributor analysis for a specific time period.
        
        Args:
            period: Time period ('7d', '14d', etc.)
            value_column: Column name containing the metric values
            dimensions: Dictionary mapping dimension names to table names
            
        Returns:
            DataFrame containing contributor analysis results
        """
        contributions = []
        diff_ratio_col = f'diff_{period}_ratio'
        
        for dim_name, table_name in dimensions.items():
            if table_name not in self.enhanced_data:
                continue
                
            df = self.enhanced_data[table_name]
            
            # Get the latest data point for each breakdown
            latest_data = df.groupby(df.columns[1]).last().reset_index()  # Group by dimension column
            
            for _, row in latest_data.iterrows():
                current_value = row[value_column]
                value_7d_ago = row.get('value_7d_ago')
                diff_ratio = row.get(diff_ratio_col)
                breakdown_value = str(row[df.columns[1]])
                
                # Skip "overall" customer type - we want specific customer types only
                if dim_name == 'Customer Type' and breakdown_value.lower() in ['#overall#', 'overall']:
                    continue
                
                if pd.notna(current_value) and pd.notna(value_7d_ago) and pd.notna(diff_ratio):
                    # Calculate absolute change
                    absolute_change = current_value - value_7d_ago
                    
                    contribution_data = {
                        'dimension': dim_name,
                        'breakdown': breakdown_value,
                        'current_value': current_value,
                        'previous_value': value_7d_ago,
                        'absolute_change': absolute_change,
                        'percent_change': diff_ratio,
                        'period': period
                    }
                    
                    contributions.append(contribution_data)
        
        if not contributions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        contrib_df = pd.DataFrame(contributions)
        
        # Calculate contribution percentages
        contrib_df = self._calculate_contribution_percentages(contrib_df)
        
        return contrib_df
    
    def _calculate_contribution_percentages(self, contrib_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate contribution percentages for each dimension.
        
        Args:
            contrib_df: DataFrame with contribution data
            
        Returns:
            DataFrame with contribution percentages added
        """
        # Calculate total absolute change by dimension
        dimension_totals = contrib_df.groupby('dimension')['absolute_change'].sum().to_dict()
        
        # Calculate overall total change as actual total DAU change (not sum of breakdowns)
        # Use OS dimension as primary since users can only be on one OS (no double counting)
        overall_total_change = self._calculate_total_dau_change(contrib_df)
        
        # Calculate contribution percentages
        contrib_df['contribution_to_dimension'] = contrib_df.apply(
            lambda row: (row['absolute_change'] / dimension_totals[row['dimension']] * 100) 
            if dimension_totals[row['dimension']] != 0 else 0, axis=1
        )
        
        contrib_df['contribution_to_total'] = contrib_df.apply(
            lambda row: (row['absolute_change'] / overall_total_change * 100) 
            if overall_total_change != 0 else 0, axis=1
        )
        
        # Sort by absolute contribution to total
        contrib_df['abs_contribution_to_total'] = contrib_df['contribution_to_total'].abs()
        contrib_df = contrib_df.sort_values('abs_contribution_to_total', ascending=False)
        
        return contrib_df
    
    def _calculate_total_dau_change(self, contrib_df: pd.DataFrame) -> float:
        """
        Calculate the actual total DAU change by finding the overall change
        across all user segments, avoiding double counting.
        
        This uses the OS breakdown as the primary dimension since users
        can only be on one OS, ensuring no double counting.
        
        Args:
            contrib_df: DataFrame containing contribution analysis results
            
        Returns:
            Total DAU change as a single number
        """
        # Use OS dimension as primary since it has no overlap (users can only be on one OS)
        os_contributions = contrib_df[contrib_df['dimension'] == 'OS']
        
        if not os_contributions.empty:
            total_change = os_contributions['absolute_change'].sum()
        else:
            # Fallback: use the first dimension available
            first_dimension = contrib_df['dimension'].iloc[0] if not contrib_df.empty else None
            if first_dimension:
                total_change = contrib_df[contrib_df['dimension'] == first_dimension]['absolute_change'].sum()
            else:
                total_change = contrib_df['absolute_change'].sum()  # Last resort
        
        return total_change
    
    def get_top_contributors(self, metric_type: str = 'r7_dau', period: str = '7d', 
                           top_n: int = 10) -> pd.DataFrame:
        """
        Get top contributors for a specific metric and time period.
        
        Args:
            metric_type: Type of metric ('dau' or 'r7_dau')
            period: Time period ('7d', '14d', etc.)
            top_n: Number of top contributors to return
            
        Returns:
            DataFrame containing top contributors
        """
        if metric_type not in self.analysis_results:
            return pd.DataFrame()
        
        if period not in self.analysis_results[metric_type]:
            return pd.DataFrame()
        
        contrib_df = self.analysis_results[metric_type][period]
        
        # Return top N contributors by absolute contribution
        return contrib_df.head(top_n)
    
    def get_dimension_summary(self, metric_type: str = 'r7_dau', period: str = '7d') -> pd.DataFrame:
        """
        Get summary statistics by dimension.
        
        Args:
            metric_type: Type of metric ('dau' or 'r7_dau')
            period: Time period ('7d', '14d', etc.)
            
        Returns:
            DataFrame containing dimension-level summary
        """
        if metric_type not in self.analysis_results:
            return pd.DataFrame()
        
        if period not in self.analysis_results[metric_type]:
            return pd.DataFrame()
        
        contrib_df = self.analysis_results[metric_type][period]
        
        # Calculate dimension-level summaries
        dimension_summary = contrib_df.groupby('dimension').agg({
            'absolute_change': 'sum',
            'contribution_to_total': 'sum',
            'current_value': 'sum',
            'previous_value': 'sum'
        }).reset_index()
        
        # Calculate dimension-level percent change
        dimension_summary['dimension_percent_change'] = (
            (dimension_summary['current_value'] - dimension_summary['previous_value']) / 
            dimension_summary['previous_value'] * 100
        )
        
        # Sort by absolute contribution
        dimension_summary['abs_contribution'] = dimension_summary['contribution_to_total'].abs()
        dimension_summary = dimension_summary.sort_values('abs_contribution', ascending=False)
        
        return dimension_summary
    
    def generate_summary_report(self, metric_type: str = 'r7_dau', period: str = '7d') -> str:
        """
        Generate a text summary of the contributor analysis.
        
        Args:
            metric_type: Type of metric ('dau' or 'r7_dau')
            period: Time period ('7d', '14d', etc.)
            
        Returns:
            String containing summary report
        """
        if metric_type not in self.analysis_results:
            return f"No analysis results found for {metric_type}"
        
        if period not in self.analysis_results[metric_type]:
            return f"No analysis results found for {metric_type} {period}"
        
        # Get top contributors and dimension summary
        top_contributors = self.get_top_contributors(metric_type, period, 5)
        dimension_summary = self.get_dimension_summary(metric_type, period)
        
        report_lines = [
            f"# Contributor Analysis Summary",
            f"**Metric**: {metric_type.upper().replace('_', ' ')}",
            f"**Period**: {period}",
            f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Top 5 Individual Contributors",
        ]
        
        for idx, (_, row) in enumerate(top_contributors.iterrows(), 1):
            sign = "+" if row['absolute_change'] >= 0 else ""
            report_lines.append(
                f"{idx}. **{row['dimension']} - {row['breakdown']}**: "
                f"{sign}{row['absolute_change']:,.0f} ({row['contribution_to_total']:+.1f}% of total change)"
            )
        
        report_lines.extend([
            "",
            "## Dimension-Level Summary",
        ])
        
        for _, row in dimension_summary.iterrows():
            sign = "+" if row['absolute_change'] >= 0 else ""
            report_lines.append(
                f"- **{row['dimension']}**: {sign}{row['absolute_change']:,.0f} "
                f"({row['contribution_to_total']:+.1f}% of total, {row['dimension_percent_change']:+.1f}% change)"
            )
        
        return "\n".join(report_lines)


def calculate_contributor_analysis(enhanced_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Calculate contributor analysis for enhanced data.
    
    Args:
        enhanced_data: Dictionary containing enhanced DataFrames with diff ratios
        
    Returns:
        Dictionary containing contributor analysis results and summaries
    """
    # Initialize contributor analysis
    analyzer = ContributorAnalysis(enhanced_data)
    
    # Calculate all contributions
    analysis_results = analyzer.calculate_all_contributions()
    
    # Generate summaries for key metrics
    summaries = {}
    for metric_type in ['dau', 'r7_dau']:
        for period in ['7d', '14d', '28d']:
            key = f"{metric_type}_{period}"
            summaries[key] = {
                'top_contributors': analyzer.get_top_contributors(metric_type, period, 10),
                'dimension_summary': analyzer.get_dimension_summary(metric_type, period),
                'text_summary': analyzer.generate_summary_report(metric_type, period)
            }
    
    return {
        'analysis_results': analysis_results,
        'summaries': summaries,
        'analyzer': analyzer
    }


if __name__ == "__main__":
    # Example usage and testing
    print("Contributor Analysis Module")
    print("This module calculates key driver analysis for DAU changes.")
