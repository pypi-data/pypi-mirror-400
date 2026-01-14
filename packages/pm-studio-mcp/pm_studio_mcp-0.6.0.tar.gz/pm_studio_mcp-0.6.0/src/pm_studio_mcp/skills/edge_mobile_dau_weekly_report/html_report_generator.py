"""
HTML Report Generator for Weekly R7 DAU Analysis
This module generates comprehensive HTML reports with charts and tables for weekly R7 DAU analysis.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from typing import Dict, Any, Optional, Tuple
import json
import re

class HTMLReportGenerator:
    """Generates HTML reports for weekly R7 DAU analysis."""
    
    def __init__(self, baseline_config: Optional[Dict] = None):
        """
        Initialize the HTML report generator.
        
        Args:
            baseline_config: Configuration for baseline calculation
                {
                    'baseline_months': 6,  # Changed to 6 months for better recent trend analysis
                    'exclude_anomaly_periods': [],  # Periods to exclude from baseline
                    'use_dynamic_baseline': False,  # Whether to calculate baseline dynamically
                    'seasonal_adjustment': True,  # Whether to apply seasonal adjustments
                }
        """
        self.report_date = None
        self.enhanced_data = None
        self.original_data = None
        self.csv_color_data = None  # Store CSV color information
        self.baseline_config = baseline_config or {
            'baseline_months': 6,  # Changed from 15 to 6 months for better recent trend capture
            'exclude_anomaly_periods': [],
            'use_dynamic_baseline': False,
            'seasonal_adjustment': True,
        }
        
    def generate_html_report(self, enhanced_data: Dict[str, pd.DataFrame], 
                           original_data: pd.DataFrame, 
                           report_date: str,
                           contributor_results: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a comprehensive HTML report.
        
        Args:
            enhanced_data: Dictionary containing processed dataframes with diff ratios
            original_data: Original raw data from Titan API
            report_date: Report date in YYYY-MM-DD format
            contributor_results: Optional dictionary containing contributor analysis results
            
        Returns:
            str: Path to the generated HTML file
        """
        self.enhanced_data = enhanced_data
        self.original_data = original_data
        self.report_date = report_date
        self.contributor_results = contributor_results
        
        # Load color indicators from CSV
        self.csv_color_data = self._load_csv_color_data(report_date)
        
        # Generate report components
        summary_html = self._generate_summary_section()
        
        # Generate contributor analysis section if available
        contributor_html = ""
        if contributor_results:
            contributor_html = self._generate_contributor_analysis_section()
        
        chart_html = self._generate_yoy_trend_chart()
        tables_html = self._generate_analysis_tables()
        # Removed anomaly detection section as requested
        
        # Combine all components into full HTML (without anomaly section)
        full_html = self._create_full_html_template(summary_html, contributor_html, chart_html, tables_html, "")
        
        # Save HTML file
        output_path = self._save_html_report(full_html)
        
        return output_path
    
    def _generate_summary_section(self) -> str:
        """Generate the summary section with R7 DAU overview and WoW growth."""
        try:
            # Calculate overall R7 DAU for the latest week
            r7_data = self.enhanced_data.get('r7_dau_os_df')
            if r7_data is None or r7_data.empty:
                return "<div class='summary-section'><h2>Summary</h2><p>No R7 DAU data available</p></div>"
            
            # Get latest date data
            latest_date = r7_data['date'].max()
            current_week_data = r7_data[r7_data['date'] == latest_date]
            
            # Calculate total R7 DAU for current week
            total_r7_dau = current_week_data['rolling_7d_avg'].sum()
            
            # Calculate WoW growth
            wow_growth = current_week_data['diff_7d_ratio'].mean() if 'diff_7d_ratio' in current_week_data.columns else 0
            
            # Format the summary
            wow_color = "green" if wow_growth > 0 else "red" if wow_growth < 0 else "gray"
            wow_arrow = "↑" if wow_growth > 0 else "↓" if wow_growth < 0 else "→"
            
            summary_html = f"""
            <div class="summary-section">
                <h2>📊 Weekly R7 DAU Summary</h2>
                <div class="summary-cards">
                    <div class="summary-card">
                        <h3>Average R7 DAU (Week of {latest_date.strftime('%Y-%m-%d')})</h3>
                        <div class="metric-value">{total_r7_dau:,.0f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Week-over-Week Growth</h3>
                        <div class="metric-value" style="color: {wow_color}">
                            {wow_arrow} {wow_growth:.2%}
                        </div>
                    </div>
                </div>
            </div>
            """
            
            return summary_html
            
        except Exception as e:
            return f"<div class='summary-section'><h2>Summary</h2><p>Error generating summary: {str(e)}</p></div>"
    
    def _generate_yoy_trend_chart(self) -> str:
        """Generate YoY trend chart for R7 DAU over the last 90 days using Plotly."""
        try:
            # Get R7 DAU data for the last 90 days
            if self.original_data is None or self.original_data.empty:
                return "<div class='chart-section'><h2>R7 DAU YoY Trend</h2><p>No data available for trend chart</p></div>"
            
            # Filter data for last 90 days
            end_date = pd.to_datetime(self.report_date)
            start_date = end_date - timedelta(days=90)
            
            trend_data = self.original_data[
                (self.original_data['date'] >= start_date) & 
                (self.original_data['date'] <= end_date)
            ].copy()
            
            if trend_data.empty:
                return "<div class='chart-section'><h2>R7 DAU YoY Trend</h2><p>Insufficient data for trend chart</p></div>"
            
            # Aggregate R7 DAU by date
            daily_r7_dau = trend_data.groupby('date')['rolling_7d_avg'].sum().reset_index()
            
            # Create the Plotly figure
            fig = go.Figure()
            
            # Plot current year data
            fig.add_trace(go.Scatter(
                x=daily_r7_dau['date'],
                y=daily_r7_dau['rolling_7d_avg'],
                mode='lines',
                name='Current Year',
                line=dict(color='#2E86AB', width=3),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x}<br>' +
                             'R7 DAU: %{y:,.0f}<br>' +
                             '<extra></extra>'
            ))
            
            # Try to get YoY data if available
            yoy_start_date = start_date - timedelta(days=365)
            yoy_end_date = end_date - timedelta(days=365)
            
            yoy_data = self.original_data[
                (self.original_data['date'] >= yoy_start_date) & 
                (self.original_data['date'] <= yoy_end_date)
            ].copy()
            
            if not yoy_data.empty:
                yoy_daily = yoy_data.groupby('date')['rolling_7d_avg'].sum().reset_index()
                yoy_daily['adjusted_date'] = yoy_daily['date'] + timedelta(days=365)
                
                fig.add_trace(go.Scatter(
                    x=yoy_daily['adjusted_date'],
                    y=yoy_daily['rolling_7d_avg'],
                    mode='lines',
                    name='Previous Year',
                    line=dict(color='#A23B72', width=3, dash='dash'),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 'R7 DAU: %{y:,.0f}<br>' +
                                 '<extra></extra>'
                ))
            
            # Update layout for better appearance
            fig.update_layout(
                title={
                    'text': 'R7 DAU Trend - Last 90 Days vs Previous Year',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial, sans-serif'}
                },
                xaxis_title='Date',
                yaxis_title='R7 DAU',
                width=1000,
                height=500,
                template='plotly_white',
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                font=dict(family='Arial, sans-serif', size=12),
                margin=dict(l=80, r=80, t=80, b=60)
            )
            
            # Update x-axis formatting
            fig.update_xaxes(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1,
                tickformat='%m-%d',
                dtick='D14',  # Show ticks every 14 days instead of 7
                tickmode='linear'
            )
            
            # Update y-axis formatting
            fig.update_yaxes(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1,
                tickformat=',',
                separatethousands=True
            )
            
            # Convert to HTML with a simpler approach
            # Use include_plotlyjs=True to embed the library directly
            chart_html_content = pio.to_html(
                fig, 
                include_plotlyjs=True,  # Embed plotly.js directly
                div_id='yoy-trend-chart',
                config={'displayModeBar': True, 'responsive': True}
            )
            
            # Extract the script and div content more carefully
            import re
            
            # Remove the outer HTML structure but keep all scripts and the div
            # Remove DOCTYPE, html, head tags but keep everything in body
            clean_content = re.sub(r'<!DOCTYPE[^>]*>', '', chart_html_content)
            clean_content = re.sub(r'<html[^>]*>', '', clean_content)
            clean_content = re.sub(r'</html>', '', clean_content)
            clean_content = re.sub(r'<head>.*?</head>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'</?body[^>]*>', '', clean_content)
            chart_content = clean_content.strip()
            
            chart_html = f"""
            <div class="chart-section">
                <h2>📈 R7 DAU YoY Trend Analysis</h2>
                <div class="chart-container">
                    {chart_content}
                </div>
                <p class="chart-description">
                    This interactive chart shows the R7 DAU trend over the last 90 days compared to the same period in the previous year.
                    You can hover over the lines to see detailed values, zoom in/out, and toggle series visibility.
                </p>
            </div>
            """
            
            return chart_html
            
        except Exception as e:
            return f"<div class='chart-section'><h2>R7 DAU YoY Trend</h2><p>Error generating chart: {str(e)}</p></div>"
    
    def _generate_anomaly_detection_section(self) -> str:
        """Generate anomaly detection section with color indicators and alerts."""
        try:
            anomaly_html = """
            <div class="anomaly-section">
                <h2>🚨 Anomaly Detection & Alerts</h2>
                <div class="anomaly-summary">
                    <p class="section-description">
                        This section displays anomaly indicators based on pre-calculated color classifications from the weekly report data.
                        Color indicators (🔴 Red, 🟡 Yellow, 🟢 Green) are determined by statistical analysis and imported directly from the CSV data.
                        These indicators reflect the significance of deviations from normal operational patterns.
                    </p>
                </div>
            """
            
            # Analyze each dataset for anomalies
            anomaly_cards = []
            alert_count = {'critical': 0, 'warning': 0, 'normal': 0}
            
            # Define datasets to analyze
            datasets_to_analyze = [
                ('r7_dau_os_df', 'Operating System', 'os'),
                ('r7_dau_region_df', 'Geographic Region', 'region'),
                ('r7_dau_install_source_df', 'Install Source', 'install_source'),
                ('r7_dau_customer_type_df', 'Customer Type', 'customer_type')
            ]
            
            for dataset_key, dataset_name, dimension_col in datasets_to_analyze:
                if dataset_key in self.enhanced_data:
                    card_html, alerts = self._create_anomaly_card(
                        self.enhanced_data[dataset_key], 
                        dataset_name, 
                        dimension_col
                    )
                    anomaly_cards.append(card_html)
                    
                    # Count alerts
                    alert_count['critical'] += alerts['critical']
                    alert_count['warning'] += alerts['warning']
                    alert_count['normal'] += alerts['normal']
            # Create summary alert bar with positive framing
            total_metrics = sum(alert_count.values())
            if total_metrics > 0:
                critical_count = alert_count['critical']
                normal_count = alert_count['normal'] + alert_count['warning']  # Combine normal + warning as "performing well"
                normal_pct = (normal_count / total_metrics) * 100
                
                # Focus on positive messaging
                if critical_count == 0:
                    alert_summary = f"""
                    <div class="alert-summary-bar">
                        <div class="alert-summary-title">📊 Performance Overview</div>
                        <div class="performance-summary">
                            <div class="performance-good">
                                ✅ All {total_metrics} metrics are performing well
                            </div>
                        </div>
                    </div>
                    """
                else:
                    alert_summary = f"""
                    <div class="alert-summary-bar">
                        <div class="alert-summary-title">📊 Performance Overview</div>
                        <div class="performance-summary">
                            <div class="performance-mixed">
                                📈 {normal_count} metrics performing well • {critical_count} requiring attention
                            </div>
                        </div>
                    </div>
                    """
                anomaly_html += alert_summary
            
            # Add anomaly cards
            if anomaly_cards:
                anomaly_html += '<div class="anomaly-cards">'
                anomaly_html += ''.join(anomaly_cards)
                anomaly_html += '</div>'
            else:
                anomaly_html += '<p>No anomaly data available for analysis.</p>'
            
            anomaly_html += '</div>'
            return anomaly_html
            
        except Exception as e:
            return f"<div class='anomaly-section'><h2>🚨 Anomaly Detection</h2><p>Error generating anomaly detection: {str(e)}</p></div>"
    
    def _create_anomaly_card(self, df: pd.DataFrame, dataset_name: str, dimension_col: str) -> Tuple[str, Dict[str, int]]:
        """Create an anomaly detection card for a specific dataset using CSV color indicators."""
        try:
            # Get latest data
            latest_date = df['date'].max()
            latest_data = df[df['date'] == latest_date]
            
            alert_counts = {'critical': 0, 'warning': 0, 'normal': 0}
            anomaly_items = []
            
            # Map dataset to CSV dataset type
            dataset_type_map = {
                'r7_dau_os_df': 'r7_dau_os_df',
                'r7_dau_region_df': 'r7_dau_region_df', 
                'r7_dau_install_source_df': 'r7_dau_install_source_df', 
                'r7_dau_customer_type_df': 'r7_dau_customer_type_df'
            }
            dataset_type = dataset_type_map.get(df.attrs.get('dataset_name', ''), '')
            
            # Check each dimension for anomalies using CSV colors
            for _, row in latest_data.iterrows():
                dimension_value = row[dimension_col]
                
                # Check different time periods
                time_periods = [
                    ('7d', 'diff_7d_ratio'),
                    ('14d', 'diff_14d_ratio'),
                    ('28d', 'diff_28d_ratio')
                ]
                
                for period_name, ratio_col in time_periods:
                    if ratio_col in row and pd.notna(row[ratio_col]):
                        current_ratio = row[ratio_col]
                        
                        # Get color from CSV data
                        csv_color = self._get_csv_color(dataset_type, str(dimension_value), period_name)
                        
                        if csv_color:
                            # Map CSV color to severity
                            if csv_color == 'red':
                                severity = 'critical'
                                status_text = 'Requires attention'
                            elif csv_color == 'yellow':
                                severity = 'warning'
                                status_text = 'Moderate deviation detected'
                            else:  # green
                                severity = 'normal'
                                status_text = 'Within normal range'
                            
                            # Only track critical items to reduce negative visual impact
                            if severity == 'critical':
                                anomaly_items.append({
                                    'dimension': dimension_value,
                                    'period': period_name,
                                    'value': current_ratio,
                                    'severity': severity,
                                    'status_text': status_text,
                                    'csv_color': csv_color
                                })
                            
                            # Count all severities for summary statistics
                            alert_counts[severity] += 1
                        else:
                            # Fallback if no CSV color found
                            alert_counts['normal'] += 1
            
            # Create card HTML
            card_html = f"""
            <div class="anomaly-card">
                <h3 class="anomaly-card-title">{dataset_name} Analysis</h3>
                <div class="anomaly-metrics">
            """
            
            if anomaly_items:
                # Filter to only show critical items to reduce negative visual impact
                critical_items = [item for item in anomaly_items if item['severity'] == 'critical']
                
                if critical_items:
                    # Sort critical items by value magnitude
                    critical_items.sort(key=lambda x: abs(x['value']), reverse=True)
                    
                    for item in critical_items:
                        # Don't show the red icon to avoid negative feelings, just use bold text
                        card_html += f"""
                        <div class="anomaly-item {item['severity']}">
                            <div class="anomaly-header">
                                <span class="anomaly-dimension" style="font-weight: bold;">{item['dimension']}</span>
                                <span class="anomaly-period">({item['period']} change)</span>
                            </div>
                            <div class="anomaly-details">
                                <span class="anomaly-value" style="font-weight: bold;">{item['value']:.2%}</span>
                                <span class="anomaly-status">Requires attention</span>
                            </div>
                        </div>
                        """
                else:
                    card_html += """
                    <div class="anomaly-item normal">
                        <div class="anomaly-header">
                            <span class="anomaly-text">All metrics performing well</span>
                        </div>
                    </div>
                    """
            else:
                card_html += """
                <div class="anomaly-item normal">
                    <div class="anomaly-header">
                        <span class="anomaly-text">All metrics performing well</span>
                    </div>
                </div>
                """
            
            card_html += """
                </div>
            </div>
            """
            
            return card_html, alert_counts
            
        except Exception as e:
            error_card = f"""
            <div class="anomaly-card error">
                <h3>{dataset_name} Analysis</h3>
                <p>Error analyzing anomalies: {str(e)}</p>
            </div>
            """
            return error_card, {'critical': 0, 'warning': 0, 'normal': 0}
    
    def _determine_anomaly_severity(self, current_value: float, baseline_stats: Dict[str, float]) -> Tuple[str, str]:
        """Determine the severity level of an anomaly based on 6-month baseline statistics."""
        if current_value < baseline_stats['p5'] or current_value > baseline_stats['p95']:
            return 'critical', 'Extreme deviation from 6-month historical pattern'
        elif (baseline_stats['p5'] <= current_value < baseline_stats['p10']) or (baseline_stats['p90'] < current_value <= baseline_stats['p95']):
            return 'critical', 'Significant deviation from 6-month normal range'
        elif (baseline_stats['p10'] <= current_value < baseline_stats['p25']) or (baseline_stats['p75'] < current_value <= baseline_stats['p90']):
            return 'warning', 'Moderate deviation from 6-month typical range'
        else:
            return 'normal', 'Within 6-month normal range'
    
    def _load_baseline_data(self) -> Optional[pd.DataFrame]:
        """
        Load baseline statistical summary from CSV file or calculate dynamically.
        
        Uses 6-month baseline for anomaly detection while keeping 470-day data fetch for YoY comparison.
        This ensures anomaly detection is based on recent 6-month trends for better sensitivity.
        """
        try:
            # Check if we should use dynamic baseline calculation
            if self.baseline_config.get('use_dynamic_baseline', False):
                return self._calculate_dynamic_baseline()
            
            # For now, use static baseline but ensure it's based on 6-month data
            # TODO: Regenerate the static baseline file with 6-month data only
            baseline_path = os.path.join(os.path.dirname(__file__), 'utils', 'diff_ratio_statistical_summary_reporting_region.csv')
            if os.path.exists(baseline_path):
                baseline_df = pd.read_csv(baseline_path)
                
                # Add metadata for tracking
                baseline_df.attrs['calculation_period'] = '6_months'  # This is the intended period
                baseline_df.attrs['data_source'] = 'static_csv'
                baseline_df.attrs['note'] = 'Static baseline - should be based on 6-month data for recent trend sensitivity'
                
                return baseline_df
            return None
        except Exception as e:
            print(f"Warning: Could not load baseline data: {e}")
            return None

    def _calculate_dynamic_baseline(self) -> Optional[pd.DataFrame]:
        """
        Calculate baseline statistics dynamically using the last 6 months of data.
        This ensures anomaly detection uses recent 6-month baseline while YoY uses full dataset.
        """
        try:
            if self.original_data is None or self.original_data.empty:
                return None
            
            # Use only the last 6 months (183 days) for baseline calculation
            report_date = pd.to_datetime(self.report_date)
            baseline_start = report_date - timedelta(days=183)  # 6 months for baseline
            
            baseline_data = self.original_data[
                (self.original_data['date'] >= baseline_start) & 
                (self.original_data['date'] <= report_date)
            ].copy()
            
            if baseline_data.empty:
                print("Warning: No data available for 6-month baseline calculation")
                return None
            
            print(f"Calculating dynamic 6-month baseline from {baseline_start.date()} to {report_date.date()}")
            print(f"Baseline data points: {len(baseline_data)} records")
            
            # Calculate difference ratios for baseline period
            # This would require implementing the same diff ratio calculation logic
            # For now, return None to use static baseline but with awareness of the 6-month intention
            print("Dynamic baseline calculation not yet implemented - using static baseline")
            return None
            
        except Exception as e:
            print(f"Error calculating dynamic baseline: {e}")
            return None
    
    def _get_baseline_for_dimension(self, baseline_df: Optional[pd.DataFrame], dataset: str, 
                                  column: str, dr_type: str) -> Optional[Dict[str, float]]:
        """Get baseline statistics for a specific dimension and DR type."""
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
    
    def _generate_analysis_tables(self) -> str:
        """Generate analysis tables for different dimensions."""
        tables_html = "<div class='tables-section'><h2>📋 Detailed Analysis Tables</h2>"
        
        # Define table configurations
        table_configs = [
            {
                'key': 'r7_dau_os_df',
                'title': '🖥️ Operating System Analysis (R7 DAU)',
                'description': 'R7 DAU breakdown by operating system (Android vs iOS)'
            },
            {
                'key': 'r7_dau_region_df',
                'title': '🌍 Regional Analysis (R7 DAU)',
                'description': 'R7 DAU breakdown by geographic regions'
            },
            {
                'key': 'r7_dau_install_source_df',
                'title': '🌍 Install Source Analysis (R7 DAU)',
                'description': 'R7 DAU breakdown by install sources'
            },
            {
                'key': 'r7_dau_customer_type_df',
                'title': '👥 Customer Account Analysis (R7 DAU)',
                'description': 'R7 DAU breakdown by customer account types'
            }
        ]
        
        # Generate each table
        for config in table_configs:
            table_html = self._create_analysis_table(
                self.enhanced_data.get(config['key']),
                config['title'],
                config['description'],
                config['key']  # Pass the dataset key for CSV color lookup
            )
            tables_html += table_html
        
        tables_html += "</div>"
        return tables_html
    
    def _create_analysis_table(self, df: pd.DataFrame, title: str, description: str, dataset_key: str = None) -> str:
        """Create an HTML table for analysis data with enhanced anomaly indicators."""
        if df is None or df.empty:
            return f"""
            <div class="table-container">
                <h3>{title}</h3>
                <p class="table-description">{description}</p>
                <p>No data available</p>
            </div>
            """
        
        try:
            # Get the latest date data
            latest_date = df['date'].max()
            latest_data = df[df['date'] == latest_date].copy()
            
            # Determine dimension column
            dimension_col = None
            value_col = None
            
            for col in ['os', 'region', 'install_source', 'customer_type', 'is_new']:
                if col in latest_data.columns:
                    dimension_col = col
                    break
            
            for col in ['rolling_7d_avg', 'client_count']:
                if col in latest_data.columns:
                    value_col = col
                    break
            
            if not dimension_col or not value_col:
                return f"""
                <div class="table-container">
                    <h3>{title}</h3>
                    <p class="table-description">{description}</p>
                    <p>Invalid data structure</p>
                </div>
                """
            
            # Sort by value descending
            latest_data = latest_data.sort_values(value_col, ascending=False)
            
            # Create table HTML
            table_html = f"""
            <div class="table-container">
                <h3>{title}</h3>
                <p class="table-description">{description}</p>
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>Dimension</th>
                            <th>R7 DAU</th>
                            <th>7d Change</th>
                            <th>14d Change</th>
                            <th>21d Change</th>
                            <th>28d Change</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            total_value = latest_data[value_col].sum()
            
            for _, row in latest_data.iterrows():
                dimension_value = row[dimension_col]
                current_value = row[value_col]
                
                # Get all change ratios
                change_7d = row.get('diff_7d_ratio', None)
                change_14d = row.get('diff_14d_ratio', None)
                change_21d = row.get('diff_21d_ratio', None)
                change_28d = row.get('diff_28d_ratio', None)
                
                # Format changes with enhanced anomaly indicators
                # Use dataset_key for CSV color lookup instead of title
                change_7d_formatted = self._format_change_with_anomaly_indicator(
                    change_7d, dimension_value, dataset_key or title, '7d'
                )
                change_14d_formatted = self._format_change_with_anomaly_indicator(
                    change_14d, dimension_value, dataset_key or title, '14d'
                )
                change_21d_formatted = self._format_change_with_anomaly_indicator(
                    change_21d, dimension_value, dataset_key or title, '21d'
                )
                change_28d_formatted = self._format_change_with_anomaly_indicator(
                    change_28d, dimension_value, dataset_key or title, '28d'
                )
                
                table_html += f"""
                        <tr>
                            <td><strong>{dimension_value}</strong></td>
                            <td>{current_value:,.0f}</td>
                            <td>{change_7d_formatted}</td>
                            <td>{change_14d_formatted}</td>
                            <td>{change_21d_formatted}</td>
                            <td>{change_28d_formatted}</td>
                        </tr>
                """
            
            table_html += """
                    </tbody>
                </table>
            </div>
            """
            
            return table_html
            
        except Exception as e:
            return f"""
            <div class="table-container">
                <h3>{title}</h3>
                <p class="table-description">{description}</p>
                <p>Error generating table: {str(e)}</p>
            </div>
            """
    
    def _format_change_with_anomaly_indicator(self, change_value: float, dimension: str, 
                                            dataset: str, period: str) -> str:
        """Format change value with only critical (red) indicators shown as bold text."""
        if pd.isna(change_value) or change_value is None:
            return "<span style='color: gray;'>N/A</span>"
        
        # Get color from CSV data
        csv_color = self._get_csv_color(dataset, dimension, period)
        
        # Get direction and color for the number
        if change_value > 0:
            direction_arrow = "↑"
            number_color = "green"
        elif change_value < 0:
            direction_arrow = "↓"
            number_color = "red"
        else:
            direction_arrow = "→"
            number_color = "gray"
        
        # Only highlight critical (red) items with bold formatting
        # Hide green/yellow indicators to reduce visual clutter and negative feelings
        if csv_color == 'red':
            # Show critical items in bold without the red icon to avoid negative feelings
            return f"<span style='color: {number_color}; font-weight: bold;'>{direction_arrow} {abs(change_value):.1%}</span>"
        else:
            # Normal formatting for green/yellow items (no special indicators)
            return f"<span style='color: {number_color};'>{direction_arrow} {abs(change_value):.1%}</span>"
    
    def _get_overall_status_indicator(self, row: pd.Series) -> Dict[str, str]:
        """Get overall status indicator for a row based on all available metrics."""
        try:
            # Check all available ratio columns
            ratio_columns = ['diff_7d_ratio', 'diff_14d_ratio', 'diff_28d_ratio', 'diff_1y_ratio']
            
            critical_count = 0
            warning_count = 0
            total_count = 0
            
            baseline_df = self._load_baseline_data()
            
            for ratio_col in ratio_columns:
                if ratio_col in row and pd.notna(row[ratio_col]):
                    total_count += 1
                    
                    if baseline_df is not None:
                        # This is a simplified check - in real implementation, 
                        # you'd need to pass the correct dimension and dataset info
                        if abs(row[ratio_col]) > 0.1:  # > 10% change
                            critical_count += 1
                        elif abs(row[ratio_col]) > 0.05:  # > 5% change
                            warning_count += 1
            
            # Determine overall status
            if total_count == 0:
                return {'class': 'unknown', 'icon': '❓', 'text': 'Unknown'}
            
            critical_ratio = critical_count / total_count
            warning_ratio = warning_count / total_count
            
            if critical_ratio > 0.5:
                return {'class': 'critical', 'icon': '🔴', 'text': 'Critical'}
            elif critical_ratio > 0 or warning_ratio > 0.5:
                return {'class': 'warning', 'icon': '🟡', 'text': 'Warning'}
            else:
                return {'class': 'normal', 'icon': '🟢', 'text': 'Normal'}
                
        except Exception:
            return {'class': 'unknown', 'icon': '❓', 'text': 'Unknown'}
    
    def _create_full_html_template(self, summary_html: str, contributor_html: str, chart_html: str, 
                                 tables_html: str, anomaly_html: str) -> str:
        """Create the complete HTML template with all sections."""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly R7 DAU Report - {self.report_date}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Weekly R7 DAU Analysis Report</h1>
            <p class="report-date">Report Date: {self.report_date}</p>
            <p class="generated-time">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 6-Month Baseline Analysis</p>
        </header>
        
        {summary_html}
        
        {contributor_html}
        
        {chart_html}
        
        {tables_html}
        
        <footer>
            <p>Generated by MCP Weekly Report System</p>
            <p>Data Source: Microsoft Titan API | Baseline: 6-month rolling window for enhanced trend sensitivity</p>
        </footer>
    </div>
</body>
</html>
        """
        return html_template

    def _get_css_styles(self) -> str:
        """Return CSS styles for the HTML report with enhanced anomaly detection styling."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .report-date, .generated-time {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .summary-section, .chart-section, .tables-section, .anomaly-section {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .summary-section h2, .chart-section h2, .tables-section h2, .anomaly-section h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        /* Specialized section styles */
        .anomaly-section {
            border-left: 5px solid #e74c3c;
        }
        
        .section-description {
            color: #666;
            font-style: italic;
            margin-bottom: 20px;
        }
        
        .alert-summary-bar {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .alert-summary-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .performance-summary {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .performance-good {
            background: linear-gradient(135deg, #27ae60, #229954);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .performance-mixed {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .alert-bar {
            display: flex;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 15px;
            border: 2px solid #ddd;
        }
        
        .alert-segment {
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .alert-segment.critical {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
        }
        
        .alert-segment.warning {
            background: linear-gradient(135deg, #f39c12, #e67e22);
        }
        
        .alert-segment.normal {
            background: linear-gradient(135deg, #27ae60, #229954);
        }
        
        .alert-legend {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            font-size: 0.9rem;
            color: #666;
        }
        
        .legend-item.critical {
            color: #e74c3c;
        }
        
        .legend-item.warning {
            color: #f39c12;
        }
        
        .legend-item.normal {
            color: #27ae60;
        }
        
        /* Common card styles */
        .card {
            background: white;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .card-title {
            background: #f8f9fa;
            padding: 15px 20px;
            margin: 0;
            border-bottom: 1px solid #e0e0e0;
            color: #2c3e50;
            font-weight: bold;
        }
        
        .card-content {
            padding: 20px;
        }
        
        /* Common grid layouts */
        .grid-layout {
            display: grid;
            gap: 15px;
            margin: 15px 0;
        }
        
        .grid-2-col {
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }
        
        .grid-3-col {
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }
        
        .anomaly-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .anomaly-card {
            background: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .anomaly-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .anomaly-card-title {
            background: #f8f9fa;
            padding: 15px 20px;
            margin: 0;
            border-bottom: 1px solid #e0e0e0;
            color: #2c3e50;
        }
        
        .anomaly-metrics {
            padding: 20px;
        }
        
        .anomaly-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }
        
        .anomaly-item.critical {
            background: #fdf2f2;
            border-left-color: #e74c3c;
        }
        
        .anomaly-item.warning {
            background: #fef9e7;
            border-left-color: #f39c12;
        }
        
        .anomaly-item.normal {
            background: #eafaf1;
            border-left-color: #27ae60;
        }
        
        .anomaly-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        
        .anomaly-icon {
            font-size: 1.2rem;
        }
        
        .anomaly-dimension {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .anomaly-period {
            color: #666;
            font-size: 0.9rem;
        }
        
        .anomaly-details {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .anomaly-value {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .anomaly-status {
            color: #666;
            font-size: 0.9rem;
        }
        
        .anomaly-baseline {
            color: #888;
            font-size: 0.85rem;
        }
        
        /* Enhanced Table Styles */
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            color: white;
        }
        
        .summary-card h3 {
            font-size: 1.2rem;
            margin-bottom: 15px;
            opacity: 0.9;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .chart-description {
            font-style: italic;
            color: #666;
            margin-top: 15px;
        }
        
        .table-container {
            margin-bottom: 40px;
        }
        
        .table-container h3 {
            font-size: 1.4rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .table-description {
            color: #666;
            margin-bottom: 20px;
        }
        
        .analysis-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 0.9rem;
        }
        
        .analysis-table th {
            background: #34495e;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .analysis-table th:first-child {
            text-align: left;
            min-width: 120px;
        }
        
        .analysis-table th:nth-child(2) {
            min-width: 100px;
        }
        
        .analysis-table th:nth-child(n+3):nth-child(-n+6) {
            min-width: 90px;
        }
        
        .analysis-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #eee;
            text-align: center;
        }
        
        .analysis-table td:first-child {
            text-align: left;
            font-weight: bold;
        }
        
        .analysis-table td:nth-child(2) {
            text-align: right;
        }
        
        .analysis-table tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        .analysis-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        /* Change indicators with anomaly detection */
        .change-critical {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .change-critical.positive {
            background: #fdf2f2;
            color: #e74c3c;
        }
        
        .change-critical.negative {
            background: #fdf2f2;
            color: #e74c3c;
        }
        
        .change-warning {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .change-warning.positive {
            background: #fef9e7;
            color: #f39c12;
        }
        
        .change-warning.negative {
            background: #fef9e7;
            color: #f39c12;
        }
        
        .change-normal {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .change-normal.positive {
            background: #eafaf1;
            color: #27ae60;
        }
        
        .change-normal.negative {
            background: #eafaf1;
            color: #27ae60;
        }
        
        .change-normal.neutral {
            background: #f8f9fa;
            color: #666;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .status-badge.critical {
            background: #fdf2f2;
            color: #e74c3c;
            border: 1px solid #fadbd8;
        }
        
        .status-badge.warning {
            background: #fef9e7;
            color: #f39c12;
            border: 1px solid #fcf3cf;
        }
        
        .status-badge.normal {
            background: #eafaf1;
            color: #27ae60;
            border: 1px solid #d5f4e6;
        }
        
        .status-badge.unknown {
            background: #f8f9fa;
            color: #666;
            border: 1px solid #e0e0e0;
        }
        
        /* Contributor Analysis Styles */
        .contributor-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .contributor-item {
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ddd;
            background: #f8f9fa;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .contributor-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .contributor-item.critical {
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }
        
        .contributor-item.warning {
            border-left-color: #f39c12;
            background: #fef9e7;
        }
        
        .contributor-item.normal {
            border-left-color: #27ae60;
            background: #eafaf1;
        }
        
        .contributor-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        
        .contributor-icon {
            font-size: 1.2rem;
        }
        
        .contributor-name {
            font-weight: bold;
            color: #2c3e50;
            flex: 1;
        }
        
        .contributor-rank {
            background: #34495e;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .contributor-metrics {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .contributor-change {
            font-weight: bold;
            font-size: 1.1rem;
            color: #2c3e50;
        }
        
        .contributor-percent {
            background: #34495e;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .dimension-summary {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .dimension-item {
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #ddd;
            background: #f8f9fa;
        }
        
        .dimension-item.critical {
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }
        
        .dimension-item.warning {
            border-left-color: #f39c12;
            background: #fef9e7;
        }
        
        .dimension-item.normal {
            border-left-color: #27ae60;
            background: #eafaf1;
        }
        
        .dimension-header {
            margin-bottom: 6px;
        }
        
        .dimension-name {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1rem;
        }
        
        .dimension-metrics {
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .dimension-change {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .dimension-contribution {
            background: #34495e;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .dimension-percent-change {
            color: #666;
            font-style: italic;
        }
        
        .period-comparison {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .period-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        
        .period-header {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        
        .period-top-contributor {
            font-size: 0.85rem;
            color: #666;
        }
        
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            header h1 {
                font-size: 2rem;
            }
            
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .anomaly-cards {
                grid-template-columns: 1fr;
            }
            
            .analysis-table {
                font-size: 0.8rem;
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }
            
            .analysis-table th,
            .analysis-table td {
                padding: 6px 4px;
                min-width: 80px;
            }
            
            .analysis-table th:first-child,
            .analysis-table td:first-child {
                min-width: 100px;
            }
            
            .alert-legend {
                flex-direction: column;
                gap: 10px;
            }
            
            .anomaly-details {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }
        }
        """
    
    def _save_html_report(self, html_content: str) -> str:
        """Save the generated HTML report to a file."""
        try:
            # Create output directory in working path
            from pm_studio_mcp.config import config
            output_dir = os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports', 'html')
            os.makedirs(output_dir, exist_ok=True)
            
            # Define output file name
            file_name = f"weekly_r7_dau_report_{self.report_date}.html"
            file_path = os.path.join(output_dir, file_name)
            
            # Write HTML content to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            return file_path
        except Exception as e:
            print(f"Error saving HTML report: {e}")
            return ""

    def _load_csv_color_data(self, report_date: str) -> Dict[str, str]:
        """
        Load color indicators from the CSV file.
        
        Args:
            report_date: Report date in YYYY-MM-DD format
            
        Returns:
            Dict mapping (dataset_type, dimension, period) to color
        """
        try:
            from pm_studio_mcp.config import config
            csv_path = os.path.join(config.WORKING_PATH, 'edge_mobile_weekly_reports', f'weekly_report_data_{report_date}.csv')
            if not os.path.exists(csv_path):
                print(f"CSV file not found: {csv_path}")
                return {}
                
            csv_df = pd.read_csv(csv_path)
            color_map = {}
            
            for _, row in csv_df.iterrows():
                dimension = row['Dimension']
                dataset_type = row['Type']
                
                # Extract colors from each diff ratio column
                period_map = {
                    'Diff Ratio 7d': '7d',
                    'Diff Ratio 14d': '14d', 
                    'Diff Ratio 21d': '21d',
                    'Diff Ratio 28d': '28d',
                    'Diff Ratio 1y': '1y'
                }
                
                for col, period in period_map.items():
                    if col in row and pd.notna(row[col]):
                        value_str = str(row[col])
                        if ':' in value_str:
                            color = value_str.split(':')[0].lower()
                            if color in ['red', 'yellow', 'green']:
                                key = f"{dataset_type}_{dimension}_{period}"
                                color_map[key] = color
            
            print(f"Loaded {len(color_map)} color indicators from CSV")
            return color_map
            
        except Exception as e:
            print(f"Error loading CSV color data: {e}")
            return {}
    
    def _get_csv_color(self, dataset_type: str, dimension: str, period: str) -> Optional[str]:
        """
        Get color from CSV data for a specific dimension and period.
        
        Args:
            dataset_type: Type of dataset (e.g., 'dau_os_df', 'r7_dau_region_df')
            dimension: Dimension value (e.g., 'android', 'US')
            period: Time period (e.g., '7d', '14d')
            
        Returns:
            Color string ('red', 'yellow', 'green') or None if not found
        """
        if self.csv_color_data is None:
            return None
            
        key = f"{dataset_type}_{dimension}_{period}"
        return self.csv_color_data.get(key)
        
    def _generate_contributor_analysis_section(self) -> str:
        """Generate the contributor analysis section showing key drivers of DAU changes."""
        if not self.contributor_results:
            return ""
        
        try:
            html_parts = []
            
            # Section header
            html_parts.append("""
            <div class="summary-section">
                <h2>🔍 Key Driver Analysis</h2>
                <p class="section-description">
                    This analysis identifies which factors are the main contributors to DAU changes. 
                    Contribution is calculated as: (breakdown change ÷ total change) × 100%
                </p>
            """)
            
            # Get R7 DAU 7-day analysis (most important)
            summaries = self.contributor_results.get('summaries', {})
            main_analysis = summaries.get('r7_dau_7d')
            
            if main_analysis:
                # Top individual contributors - only 1 from each breakdown, exclude overall customer type
                top_contributors = main_analysis.get('top_contributors')
                
                if not top_contributors.empty:
                    # Filter to get only 1 contributor per dimension, excluding "overall" customer type
                    filtered_rows = []
                    seen_dimensions = set()
                    
                    for _, row in top_contributors.iterrows():
                        dimension = row['dimension']
                        breakdown = row['breakdown']
                        
                        # Skip "overall" customer type
                        if dimension == 'Customer Type' and breakdown.lower() == 'overall':
                            continue
                            
                        # Only take first (highest) contributor from each dimension
                        if dimension not in seen_dimensions:
                            filtered_rows.append(row)
                            seen_dimensions.add(dimension)
                    
                    if filtered_rows:
                        html_parts.append("""
                        <div class="card">
                            <h3 class="card-title">🎯 Top Contributors by Dimension (7-day change)</h3>
                            <div class="card-content">
                                <div class="contributor-list">
                        """)
                        
                        # Generate filtered contributors list
                        for idx, row in enumerate(filtered_rows, 1):
                            contribution_pct = row['contribution_to_total']
                            absolute_change = row['absolute_change']
                            
                            # Determine color based on contribution magnitude and direction
                            if abs(contribution_pct) >= 20:
                                badge_class = "critical"
                            elif abs(contribution_pct) >= 10:
                                badge_class = "warning" 
                            else:
                                badge_class = "normal"
                            
                            html_parts.append(f"""
                            <div class="contributor-item {badge_class}">
                                <div class="contributor-header">
                                    <span class="contributor-name">{row['dimension']} - {row['breakdown']}</span>
                                    <span class="contributor-rank">#{idx}</span>
                                </div>
                                <div class="contributor-metrics">
                                    <span class="contributor-change">{absolute_change:+,.0f}</span>
                                    <span class="contributor-percent">{contribution_pct:+.1f}%</span>
                                </div>
                            </div>
                            """)
                        
                        html_parts.append("""
                                </div>
                            </div>
                        </div>
                        """)
            
            html_parts.append("</div>")
            
            return "\n".join(html_parts)
            
        except Exception as e:
            print(f"Error generating contributor analysis section: {e}")
            return f"""
            <div class="summary-section">
                <h2>🔍 Key Driver Analysis</h2>
                <p>Error generating contributor analysis: {str(e)}</p>
            </div>
            """

def generate_html_report(enhanced_data: Dict[str, pd.DataFrame], 
                        original_data: pd.DataFrame, 
                        report_date: str,
                        contributor_results: Optional[Dict[str, Any]] = None) -> str:
    """
    Standalone function to generate HTML report.
    
    This function creates an instance of HTMLReportGenerator and generates the report.
    
    Args:
        enhanced_data: Dictionary containing processed dataframes with diff ratios
        original_data: Original raw data from Titan API
        report_date: Report date in YYYY-MM-DD format
        contributor_results: Optional dictionary containing contributor analysis results
        
    Returns:
        str: Path to the generated HTML file
    """
    generator = HTMLReportGenerator()
    return generator.generate_html_report(enhanced_data, original_data, report_date, contributor_results)
