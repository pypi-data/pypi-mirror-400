"""
Edge Mobile Weekly DAU Report Teams Summary Generator

This script generates a formatted Teams message summary from Edge Mobile Weekly DAU report data.
It reads the CSV report data, formats it according to Teams markdown specifications,
and saves it as an HTML file.
"""

import os
import csv
import re
from datetime import datetime
import argparse
from pathlib import Path


def parse_value(value_str):
    """Parse numerical values from strings with commas."""
    return int(value_str.replace(",", "")) if value_str else 0


def format_change(diff_ratio):
    """Format change percentage with appropriate color indicator."""
    # Extract percentage value from string like "Red:-4.41% (0.9%)"
    match = re.search(r'[-+]?\d+\.\d+(?=%)', diff_ratio)
    if not match:
        return "N/A"
    
    percentage = float(match.group())
    
    # Determine color indicator
    if percentage > 0:
        indicator = "🟢"  # Green for positive trends
    elif percentage < -2:
        indicator = "🔴"  # Red for negative trends
    else:
        indicator = "🟡"  # Yellow for neutral/slight changes
    
    return f"{indicator} **{percentage:.2f}%**"


def extract_percentage(diff_ratio):
    """Extract percentage value from diff_ratio string."""
    match = re.search(r'[-+]?\d+\.\d+(?=%)', diff_ratio)
    if not match:
        return 0.0
    return float(match.group())


def find_extremes(data_rows, value_idx=1, diff_idx=3):
    """Find items with largest increase and decrease."""
    if not data_rows or len(data_rows) == 0:
        return None, None
    
    max_increase_item = max(data_rows, key=lambda x: extract_percentage(x[diff_idx]))
    min_decrease_item = min(data_rows, key=lambda x: extract_percentage(x[diff_idx]))
    
    return max_increase_item, min_decrease_item


def generate_teams_summary(csv_path, html_report_url, output_path):
    """
    Generate Teams message summary from Edge Mobile Weekly DAU report data.
    
    Args:
        csv_path: Path to the CSV report data
        html_report_url: URL to the published HTML report
        output_path: Path where the Teams message HTML will be saved
    """
    # Extract date from CSV filename
    filename = os.path.basename(csv_path)
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        report_date = match.group(1)
        # Convert to more readable format (e.g., July 10, 2025)
        try:
            date_obj = datetime.strptime(report_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except ValueError:
            formatted_date = report_date
    else:
        formatted_date = datetime.now().strftime("%B %d, %Y")

    # Read CSV data
    overall_r7_dau = None
    overall_r7_diff = None
    ios_r7_dau = None
    ios_r7_diff = None
    android_r7_dau = None
    android_r7_diff = None
    
    # Lists to store region and install source data
    region_data = []
    install_source_data = []

    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header
            next(reader, None)
            
            for row in reader:
                if len(row) < 9:  # Ensure row has enough columns
                    continue
                
                dimension, value, _, diff_ratio, *_ = row
                row_type = row[-1] if len(row) > 8 else ""
                
                if row_type == "r7_dau_customer_type_df" and "commercial" in dimension.lower():
                    overall_r7_dau = value
                    overall_r7_diff = diff_ratio
                elif row_type == "r7_dau_os_df":
                    if "ios" in dimension.lower():
                        ios_r7_dau = value
                        ios_r7_diff = diff_ratio
                    elif "android" in dimension.lower():
                        android_r7_dau = value
                        android_r7_diff = diff_ratio
                elif row_type == "r7_dau_region_df":
                    region_data.append(row)
                elif row_type == "r7_dau_install_source_df":
                    install_source_data.append(row)
    
    except Exception as e:
        print(f"Error reading CSV file: {e}", flush=True)
        return False

    # Find extreme changes in region and install source data
    region_max_increase, region_max_decrease = find_extremes(region_data)
    install_source_max_increase, install_source_max_decrease = find_extremes(install_source_data)

    # Find the latest data date from the CSV file
    latest_data_date = None
    # Compose the path for the original data file
    edge_mobile_original_path = Path(csv_path).parent / f"edge_mobile_original_data_{report_date}.csv"
    try:
        with open(edge_mobile_original_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            for row in reader:
                if len(row) > 0:
                    # Try to find a date in the row (format: YYYY-MM-DD)
                    for cell in row:
                        match = re.search(r'\d{4}-\d{2}-\d{2}', cell)
                        if match:
                            cell_date = match.group(0)
                            if (latest_data_date is None) or (cell_date > latest_data_date):
                                latest_data_date = cell_date
        if latest_data_date:
            print(f"Latest data date in CSV: {latest_data_date}", flush=True)
        else:
            print("No data date found in CSV.", flush=True)
    except Exception as e:
        print(f"Error extracting latest data date: {e}", flush=True)

    # Prepare region insights content
    region_insights = ""
    if region_max_increase and region_max_decrease:
        region_insights = f"""<h3>📍 Region Insights</h3>
            <li>Best performing region: <b>{region_max_increase[0]}</b> (<b>{region_max_increase[1]}</b>) with <b>{format_change(region_max_increase[3])}</b> WoW</li>
            <li>Challenged region: <b>{region_max_decrease[0]}</b> (<b>{region_max_decrease[1]}</b>) with <b>{format_change(region_max_decrease[3])}</b> WoW</li>
    """

    # Prepare install source insights content
    install_insights = ""
    if install_source_max_increase and install_source_max_decrease:
        install_insights = f"""<h3>🔄 Install Source Insights</h3>
            <li>Top growing source: <b>{install_source_max_increase[0]}</b> (<b>{install_source_max_increase[1]}</b>) with <b>{format_change(install_source_max_increase[3])}</b> WoW</li>
            <li>Declining source: <b>{install_source_max_decrease[0]}</b> (<b>{install_source_max_decrease[1]}</b>) with <b>{format_change(install_source_max_decrease[3])}</b> WoW</li>
        """

    # Generate Teams message content
    message = f"""<div>
        <h1 style="color:#2564cf;font-weight:bold;">
           <b>Edge Mobile Commercial Weekly Report ({formatted_date})</b>
        </h1>
        <h3>📅 Latest Data Date: {latest_data_date}</h3>
        <h3>📊 Overall DAU Status</h3>
            <li>Overall R7 Average DAU: <b>{overall_r7_dau}</b> | Change: <b>{format_change(overall_r7_diff)}</b> WoW</li>
            <li>iOS R7 Average DAU: <b>{ios_r7_dau}</b> | Change: <b>{format_change(ios_r7_diff)}</b> WoW</li>
            <li>Android R7 Average DAU: <b>{android_r7_dau}</b> | Change: <b>{format_change(android_r7_diff)}</b> WoW</li>
        {region_insights}
        {install_insights}
        <hr>
            For comprehensive analysis, charts, and detailed breakdowns, please see the full online report: 
            <a href="{html_report_url}">{html_report_url}</a>
    </div>
    """

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to HTML file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"Teams summary saved to {output_path}", flush=True)
        return True
    except Exception as e:
        print(f"Error writing HTML file: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate Teams message summary from Edge Mobile Weekly DAU report')
    parser.add_argument('--csv-path', required=True, help='Path to the CSV report data')
    parser.add_argument('--html-report-url', required=True, help='URL to the published HTML report')
    parser.add_argument('--output-path', required=True, help='Path where the Teams message HTML will be saved')
    
    args = parser.parse_args()
    
    generate_teams_summary(args.csv_path, args.html_report_url, args.output_path)


if __name__ == "__main__":
    main()
