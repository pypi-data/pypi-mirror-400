#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CN AI Browser Analysis Template for Showroom

This script is the professional analysis engine for CN AI Browser competitive analysis.
It generates comprehensive HTML-based visualizations from Titan query results.
This is the template script used by the Showroom CN AI Browser workflow (Template #5).

Usage:
    python showroom_cnaibrowser_template.py [--input_dir working_dir] [--output_file browser_analysis.html]
"""

import os
import sys
import csv
import json
import glob
import re
import datetime
import argparse
from collections import defaultdict

# Constants
# Default base working_dir
_BASE_WORKING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "working_dir")
# Fallback subfolder if user forgets to create a run specific directory (still isolated)
DEFAULT_INPUT_DIR = os.path.join(_BASE_WORKING_DIR, "_fallback_run")
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_DIR
os.makedirs(DEFAULT_INPUT_DIR, exist_ok=True)
DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')

# Visualization types mapped to CSV content features
VISUALIZATION_CONFIGS = [
    {
        "id": "browser_dad",
        "header_features": ["__timestamp", "Edge DAD", "360 DAD", "Chrome DAD"],  # Feature fields for CSV type identification
        "alt_header_features": ["Time", "Edge DAD", "360 DAD", "Chrome DAD"],  # Alternative feature fields supporting different formats
        "title": "China Major Browser Competitors - Daily Active Devices",
        "description": "Analysis of Daily Active Devices (DAD) for major browser competitors in China, including AI browsers",
        "chart_type": "line",
        "x_field": "__timestamp",  # Default time field
        "alt_x_field": "Time",     # Alternative time field
        "y_fields": ["Edge DAD", "360 DAD", "Chrome DAD", "Doubao DAD", "Quark DAD", "Cici DAD"],
        "analysis_fields": ["Edge DAD", "360 DAD", "Chrome DAD", "Doubao DAD", "Quark DAD"],
    },
    {
        "id": "edge_bsom_comparison",
        "header_features": ["__timestamp", "BSOM", "BSOM with AI Browser in China"],  # Feature fields
        "alt_header_features": ["Time", "BSOM", "BSOM with AI Browser in China"],  # Alternative feature fields
        "title": "Edge BSoM Comparison - With and Without CN AI Browsers",
        "description": "Comparison of Edge BSoM with and without including CN AI browsers in the calculation",
        "chart_type": "line",
        "x_field": "__timestamp",
        "alt_x_field": "Time",
        "y_fields": ["BSOM","BSOM with AI Browser in China"],
        "analysis_fields": ["BSOM","BSOM with AI Browser in China"],
        "percentage": True,
        "y_axis_min": 0.40,  # 40%
        "y_axis_max": 0.55,  # 55%
    },
    {
        "id": "edge_bsom_impact",
        "header_features": ["__timestamp", "BSOM Impact"],  # Feature fields
        "alt_header_features": ["Time", "BSOM Impact"],  # Alternative feature fields
        "title": "Edge BSoM Impact by CN AI Browsers",
        "description": "Calculation of the impact of CN AI browsers on Edge's BSoM",
        "chart_type": "bar",
        "x_field": "__timestamp",
        "alt_x_field": "Time",
        "y_fields": ["BSOM Impact"],
        "analysis_fields": ["BSOM Impact"],
        "percentage": True,
    },
    {
        "id": "ai_browsers_bsom",
        "header_features": ["__timestamp", "Doubao BSOM", "Quark BSOM"],  # Feature fields
        "alt_header_features": ["Time", "Doubao BSOM", "Quark BSOM"],  # Alternative feature fields
        "title": "AI Browsers BSoM Analysis",
        "description": "Analysis of the BSoM of Doubao and Quark AI browsers in China",
        "chart_type": "line",
        "x_field": "__timestamp",
        "alt_x_field": "Time",
        "y_fields": ["Doubao BSOM", "Quark BSOM"],
        "analysis_fields": ["Doubao BSOM", "Quark BSOM"],
        "percentage": True,
    },
    {
        "id": "ai_browsers_minutes",
        "header_features": ["__timestamp", "Doubao Minutes", "Quark Minutes"],  # Feature fields
        "alt_header_features": ["Time", "Doubao Minutes", "Quark Minutes"],  # Alternative feature fields
        "title": "AI Browsers Usage Minutes Analysis",
        "description": "Analysis of usage minutes for Doubao and Quark AI browsers in China",
        "chart_type": "line",
        "x_field": "__timestamp",
        "alt_x_field": "Time",
        "y_fields": ["Doubao Minutes", "Quark Minutes"],
        "analysis_fields": ["Doubao Minutes", "Quark Minutes"],
        "percentage": False,
    },
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate browser analysis visualizations")
    parser.add_argument("--input_dir", default=DEFAULT_INPUT_DIR,
                       help="Directory containing CSV files (default: working_dir)")
    parser.add_argument("--output_file", default=None,
                       help="(Deprecated) direct output file path; if provided overrides --output_dir")
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR,
                       help="Directory for output HTML (timestamped filename will be created inside)")
    return parser.parse_args()

def get_csv_headers(csv_file):
    """Read and return the headers (first row) of a CSV file."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return next(reader)
    except Exception as e:
        print(f"Error reading headers from {csv_file}: {e}")
        return []

def find_csv_files(input_dir):
    """Find CSV files matching our visualization types based on header features."""
    # Find all CSV files in directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Create mapping from config ID to matched files
    config_matches = {}
    
    # Use file content features for matching
    for csv_file in csv_files:
        headers = get_csv_headers(csv_file)
        if not headers:
            continue  # Skip files whose headers cannot be read
        
        # Try flexible field matching
        for config in VISUALIZATION_CONFIGS:
            # Create a deep copy of config to avoid affecting original configuration
            temp_config = config.copy()
            matched = False
            
            # Check standard time field
            time_field_found = False
            if "x_field" in temp_config and temp_config["x_field"] in headers:
                time_field_found = True
            elif "alt_x_field" in temp_config and temp_config["alt_x_field"] in headers:
                # If alternative time field is found, use it
                temp_config["x_field"] = temp_config["alt_x_field"]
                time_field_found = True
            else:
                # Try common time field names
                for field_name in ["Time", "time", "__timestamp", "Date", "DATE", "date", "timestamp"]:
                    if field_name in headers:
                        temp_config["x_field"] = field_name
                        time_field_found = True
                        break
            
            if not time_field_found and headers:
                # Use first column as time field (fallback option)
                temp_config["x_field"] = headers[0]
                time_field_found = True
            
            # Check data fields
            # 1. Try standard feature set
            if "header_features" in temp_config:
                data_fields = [f for f in temp_config["header_features"] if f != temp_config.get("x_field") and f != temp_config.get("alt_x_field")]
                if all(field in headers for field in data_fields):
                    matched = True
            
            # 2. If standard features don't match, try alternative feature set
            if not matched and "alt_header_features" in temp_config:
                alt_data_fields = [f for f in temp_config["alt_header_features"] if f != temp_config.get("x_field") and f != temp_config.get("alt_x_field")]
                if all(field in headers for field in alt_data_fields):
                    matched = True
            
            # 3. More flexible matching - check if contains necessary field types
            if not matched:
                required_fields = temp_config.get("y_fields", [])
                if all(any(field.lower() in header.lower() for header in headers) for field in required_fields):
                    print(f"Note: CSV file {os.path.basename(csv_file)} matched to {temp_config['title']} through required field type matching")
                    matched = True
            
            if matched:
                config_id = config["id"]
                # If this is the first match, or the file is newer than previously matched
                if config_id not in config_matches or os.path.getctime(csv_file) > os.path.getctime(config_matches[config_id][0]):
                    config_matches[config_id] = (csv_file, config)
    
    # Convert config mapping to matched files list
    matched_files = list(config_matches.values())
    
    # Show matching results
    for csv_file, config in matched_files:
        created_time = datetime.datetime.fromtimestamp(os.path.getctime(csv_file)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Match successful: {os.path.basename(csv_file)} (created at {created_time}) -> {config['title']}")
    
    # Verify if all configurations have been matched
    if len(matched_files) < len(VISUALIZATION_CONFIGS):
        matched_ids = [config["id"] for _, config in matched_files]
        missing_configs = [config["title"] for config in VISUALIZATION_CONFIGS if config["id"] not in matched_ids]
        print(f"Warning: Cannot find matching CSV files for the following chart types: {', '.join(missing_configs)}")
    
    return matched_files

def parse_date(date_str):
    """Parse date string to datetime object with robust support for multiple formats."""
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Remove quotes and strip whitespace
    date_str = date_str.strip().strip('"\'')
    
    # Try different date formats in order of preference
    formats = [
        # Standard formats
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M:%S",
        
        # ISO formats
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        
        # HTTP/RFC formats (like "Tue, 17 Jun 2025 00:00:00 GMT")
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S",
        
        # Common variations
        "%d/%m/%Y",
        "%d-%m-%Y", 
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        
        # Additional timestamp formats
        "%Y%m%d",
        "%Y%m%d_%H%M%S",
        "%Y-%m-%d_%H:%M:%S",
    ]
    
    # First try to extract YYYY-MM-DD pattern if it exists
    date_match = DATE_PATTERN.search(date_str)
    if date_match:
        extracted_date = date_match.group(0)
        try:
            return datetime.datetime.strptime(extracted_date, "%Y-%m-%d")
        except ValueError:
            pass
    
    # Try each format
    for fmt in formats:
        try:
            parsed_date = datetime.datetime.strptime(date_str, fmt)
            return parsed_date
        except ValueError:
            continue
    
    # If all standard formats fail, try using dateutil parser as fallback
    try:
        from dateutil import parser
        return parser.parse(date_str)
    except (ImportError, ValueError, TypeError):
        pass
    
    # If everything fails, try to extract numbers and create a date
    try:
        import re
        # Look for year, month, day patterns
        numbers = re.findall(r'\d+', date_str)
        if len(numbers) >= 3:
            # Assume first number > 1900 is year, or last 4-digit number
            year, month, day = None, None, None
            
            for num in numbers:
                if len(num) == 4 and int(num) > 1900 and int(num) < 2100:
                    year = int(num)
                    break
            
            # Find month and day from remaining numbers
            remaining_numbers = [int(n) for n in numbers if len(n) <= 2]
            if len(remaining_numbers) >= 2:
                # Try different combinations
                for i, m in enumerate(remaining_numbers):
                    for j, d in enumerate(remaining_numbers):
                        if i != j and 1 <= m <= 12 and 1 <= d <= 31:
                            month, day = m, d
                            break
                    if month and day:
                        break
            
            if year and month and day:
                return datetime.datetime(year, month, day)
    except:
        pass
    
    print(f"Warning: Unable to parse date format: {date_str}")
    return None

def read_csv_data(csv_file, config=None):
    """Read and parse CSV data.
    
    Args:
        csv_file: Path to the CSV file
        config: Configuration containing x_field information
        
    Returns:
        list: Parsed data with standardized keys
    """
    data = []
    time_field = "__timestamp"  # Default time field
    
    try:
        # First read headers to determine time field
        headers = get_csv_headers(csv_file)
        if not headers:
            print(f"Warning: Unable to read CSV file headers: {csv_file}")
            return data
            
        # Check various possible time field names
        possible_time_fields = ["__timestamp", "Time", "time", "DATE", "Date", "date", "timestamp", "Timestamp"]
        
        # If config is provided, prioritize fields in config
        if config:
            if config["x_field"] in headers:
                time_field = config["x_field"]
            elif "alt_x_field" in config and config["alt_x_field"] in headers:
                time_field = config["alt_x_field"]
        
        # If still haven't found time field, check common naming conventions
        if time_field not in headers:
            for field in possible_time_fields:
                if field in headers:
                    time_field = field
                    break
        
        # If still cannot find time field, use first column as time field
        if time_field not in headers and headers:
            time_field = headers[0]
            print(f"Warning: Standard time field not found, using first column '{time_field}' as time field")
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Read data rows
            for row in reader:
                # Convert numeric string values to float
                processed_row = {}
                for key, value in row.items():
                    # Standardize time field to __timestamp
                    if key == time_field:
                        processed_row["__timestamp"] = value
                    elif value and value.strip():  # Handle empty strings
                        try:
                            processed_row[key] = float(value)
                        except ValueError:
                            processed_row[key] = value
                    else:
                        processed_row[key] = 0
                data.append(processed_row)
        
        # Sort by timestamp with robust date parsing
        def get_sort_key(row):
            """Get sorting key for a data row, handling various date formats."""
            timestamp_str = row.get("__timestamp", "")
            parsed_date = parse_date(timestamp_str)
            
            if parsed_date:
                return parsed_date
            else:
                # If parsing fails, try to extract year-month-day for basic sorting
                try:
                    # Extract numbers from the string
                    import re
                    numbers = re.findall(r'\d+', str(timestamp_str))
                    if len(numbers) >= 3:
                        # Look for a 4-digit year
                        year = None
                        for num in numbers:
                            if len(num) == 4 and 1900 <= int(num) <= 2100:
                                year = int(num)
                                break
                        
                        if year:
                            # Use year as primary sort key, then try to get month/day
                            month = int(numbers[1]) if len(numbers) > 1 and int(numbers[1]) <= 12 else 1
                            day = int(numbers[2]) if len(numbers) > 2 and int(numbers[2]) <= 31 else 1
                            return datetime.datetime(year, month, day)
                
                    # Fallback: use string comparison
                    return datetime.datetime(1900, 1, 1)  # Very early date for failed parsing
                except:
                    return datetime.datetime(1900, 1, 1)
        
        # Sort data using the robust sorting key
        try:
            data.sort(key=get_sort_key)
            print(f"Successfully sorted data: from {data[0]['__timestamp'] if data else 'N/A'} to {data[-1]['__timestamp'] if data else 'N/A'}")
        except Exception as e:
            print(f"Error during sorting: {e}, data will be kept in original order")
    except Exception as e:
        print(f"Error reading CSV file {csv_file}: {str(e)}")
    
    return data

def format_date(date_str):
    """Format date string for display with robust parsing."""
    if not date_str:
        return ""
    
    # Try to parse the date first
    parsed_date = parse_date(date_str)
    if parsed_date:
        # Return in standard YYYY-MM-DD format
        return parsed_date.strftime("%Y-%m-%d")
    
    # If parsing fails, try to extract YYYY-MM-DD pattern
    date_match = DATE_PATTERN.search(str(date_str))
    if date_match:
        return date_match.group(0)
    
    # If all else fails, return the original string (cleaned)
    cleaned = str(date_str).strip().strip('"\'')
    print(f"Warning: Unable to format date, returning original value: {cleaned}")
    return cleaned

def calculate_rolling_average(values, window=7):
    """Calculate rolling average with specified window size.
    
    For days before we have enough data (first window-1 days), 
    return None to indicate no valid rolling average.
    """
    if len(values) < window:
        # If we don't have enough data at all, return array of None values
        return [None] * len(values)
    
    result = []
    for i in range(len(values)):
        if i < window - 1:
            # For the first (window-1) elements, we don't have enough previous data
            # Return None to leave these points empty in the chart
            result.append(None)
        else:
            # For remaining elements, calculate the moving average
            result.append(sum(values[i-(window-1):i+1]) / window)
    
    return result

def calculate_linear_trend(values):
    """Calculate simple linear regression trend slope, representing daily average change.
    
    Args:
        values: List of numerical values
        
    Returns:
        float: Linear trend slope (change in y per unit x)
    """
    if len(values) < 2:
        return 0
        
    n = len(values)
    x_values = list(range(n))
    
    # Calculate mean of x and y
    x_mean = sum(x_values) / n
    y_mean = sum(values) / n
    
    # Calculate linear regression slope: slope = sum((x-x_mean)(y-y_mean)) / sum((x-x_mean)^2)
    numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x - x_mean)**2 for x in x_values)
    
    if denominator == 0:
        return 0
        
    return numerator / denominator

def calculate_variation_coefficient(values):
    """Calculate coefficient of variation (CV), representing data volatility relative to the mean.
    
    Args:
        values: List of numerical values
        
    Returns:
        float: Coefficient of variation (standard deviation/mean), expressed as percentage
    """
    if not values or sum(values) == 0:
        return 0
        
    mean = sum(values) / len(values)
    if mean == 0:
        return 0
        
    # Calculate standard deviation
    variance = sum((x - mean)**2 for x in values) / len(values)
    std_dev = variance ** 0.5
    
    # Coefficient of variation = Standard deviation / Mean
    return (std_dev / mean) * 100

def calculate_weekday_average(data, field):
    """Calculate average value for weekdays (Monday to Friday).
    
    Args:
        data: Data list containing dates and values
        field: Field name to calculate
        
    Returns:
        float: Average value for weekdays
    """
    weekday_values = []
    for row in data:
        if field not in row:
            continue
            
        # Check if the date is a weekday (Monday to Friday)
        date_str = row.get("__timestamp", "")
        try:
            # Use robust date parsing function
            parsed_date = parse_date(date_str)
            if parsed_date:
                # 0 is Monday, 6 is Sunday
                if parsed_date.weekday() < 5:  # 0-4 is Monday to Friday
                    weekday_values.append(row[field])
            else:
                # If the new parsing function also fails, try the old method as fallback
                date_match = DATE_PATTERN.search(date_str)
                if date_match:
                    date_str = date_match.group(0)
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date_obj.weekday() < 5:  # 0-4 is Monday to Friday
                        weekday_values.append(row[field])
        except Exception as e:
            # If date parsing fails, skip this row
            print(f"Warning: Unable to parse date for weekday calculation: {date_str}, error: {e}")
            continue
    
    if not weekday_values:
        print(f"Warning: No weekday data found for field {field}")
        return 0  # If no weekday data, return 0
        
    avg_value = sum(weekday_values) / len(weekday_values)
    print(f"Field {field} weekday average: {avg_value:.2f} (based on {len(weekday_values)} weekdays)")
    return avg_value

def calculate_period_averages(values, window=7):
    """Calculate beginning and ending period averages.
    
    Args:
        values: List of values
        window: Window size for averaging, will be automatically adjusted for shorter data periods
        
    Returns:
        tuple: (beginning_avg, ending_avg, adjusted_window_size)
    """
    # Adjust window size based on data length
    data_points = len(values)
    adjusted_window = window
    
    # For short periods, use smaller window sizes
    if data_points < 14:  # Less than two weeks
        adjusted_window = max(2, data_points // 3)
    elif data_points < 30:  # Less than a month
        adjusted_window = max(3, min(7, data_points // 4))
    elif data_points < 60:  # Less than two months
        adjusted_window = max(5, min(window, data_points // 6))
    
    if data_points < adjusted_window * 2:
        # Not enough data for both beginning and ending periods with adjusted window
        # Use first half vs second half
        half_point = data_points // 2
        first_half = values[:half_point]
        second_half = values[half_point:]
        
        return (
            sum(first_half) / len(first_half) if first_half else 0,
            sum(second_half) / len(second_half) if second_half else 0,
            len(first_half)  # Return actual window size used
        )
    
    # Calculate average of first 'adjusted_window' values (beginning period)
    beginning_avg = sum(values[:adjusted_window]) / adjusted_window
    
    # Calculate average of last 'adjusted_window' values (ending period)
    ending_avg = sum(values[-adjusted_window:]) / adjusted_window
    
    return (beginning_avg, ending_avg, adjusted_window)

def analyze_browser_dad_data(data, fields):
    """Analyze DAD (Daily Active Devices) data for major browsers in China.
    
    Returns objective analysis results based on pure calculations, without any inference or subjective judgment.
    Display key indicator comparisons for each browser in tabular format.
    """
    analysis_results = []
    
    if not data or len(data) < 2:
        return ["Insufficient data for analysis."]
        
    # 1. Analysis period basic information
    first_date = format_date(data[0]["__timestamp"])
    last_date = format_date(data[-1]["__timestamp"])
    total_days = len(data)
    
    # 2. Calculate key indicators for all browsers
    browser_metrics = {}
    max_avg_dad = 0
    max_avg_browser = ""
    max_growth_pct = -float('inf')  # Initialize to negative infinity
    max_growth_browser = ""
    
    for field in fields:
        if field not in data[0]:
            continue
            
        values = [row[field] for row in data if field in row]
        if not values or values[0] == 0:
            continue
            
        # 2.1 First-last comparison
        first_val = values[0]
        last_val = values[-1]
        abs_change = last_val - first_val
        pct_change = (abs_change / first_val * 100) if first_val != 0 else 0
        trend_word = "Rise" if pct_change > 0 else "Decline" if pct_change < 0 else "Steady"
        
        # 2.2 Calculate mean, maximum, minimum
        avg_val = sum(values) / len(values)
        max_val = max(values)
        min_val = min(values)
        max_idx = values.index(max_val)
        min_idx = values.index(min_val)
        max_date = format_date(data[max_idx]["__timestamp"])
        min_date = format_date(data[min_idx]["__timestamp"])
          # 2.3 Calculate trend slope (daily average change)
        slope = calculate_linear_trend(values)
        daily_avg_change = slope  # Daily average change
        
        # 2.4 Calculate weekday average
        weekday_avg = calculate_weekday_average(data, field)
        
        # Save all calculation results to dictionary
        browser_metrics[field] = {
            'first_val': first_val,
            'last_val': last_val,
            'abs_change': abs_change,
            'pct_change': pct_change,
            'avg_val': avg_val,
            'weekday_avg': weekday_avg,
            'max_val': max_val,
            'max_date': max_date,
            'min_val': min_val,
            'min_date': min_date,
            'slope': slope,
            'trend_word': trend_word
        }
        
        # Update browser with highest average DAD
        if avg_val > max_avg_dad:
            max_avg_dad = avg_val
            max_avg_browser = field
            
        # Update browser with highest change rate
        if abs(pct_change) > abs(max_growth_pct):
            max_growth_pct = pct_change
            max_growth_browser = field
            
    # 3. Create comparison data table for all browsers
    # First prepare Edge browser data, then prepare other browser data
    all_browsers = []
    
    # If Edge browser exists, add it first
    if "Edge DAD" in browser_metrics:
        all_browsers.append(("Edge DAD", browser_metrics["Edge DAD"]))
    
    # Then add other browsers
    all_browsers.extend([
        (name, metrics) for name, metrics in browser_metrics.items() 
        if name != "Edge DAD"
    ])
    
    # Sort by average DAD
    all_browsers = sorted(all_browsers, key=lambda x: x[1]['avg_val'], reverse=True)
      # Create HTML table
    table_html = """    <style>    .browser-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 10px 0 25px 0; /* Reduce top margin */
        font-size: 14px;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .browser-table th, .browser-table td {
        padding: 14px 16px;
        text-align: center;
        border: none;
    }
    .browser-table th {
        background-color: #0078d4;
        color: white;
        font-weight: 500;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .browser-table tbody tr {
        border-bottom: 1px solid #f0f0f0;
    }
    .browser-table tbody tr:nth-child(even) {
        background-color: #fafafa;
    }
    .browser-table tbody tr:last-child {
        border-bottom: none;
    }
    .browser-table .positive {
        color: #2e8540;
        font-weight: 600;
    }
    .browser-table .negative {
        color: #d83b01;
        font-weight: 600;
    }
    .browser-table td:first-child {
        font-weight: 600;
        text-align: left;
        padding-left: 20px;
    }
    .browser-table tr:hover {
        background-color: rgba(0, 120, 212, 0.04);
    }
    </style>    <table class="browser-table">
      <thead>
        <tr>
          <th>Browser</th>
          <th>Start/End</th>
          <th>Change</th>
          <th>Change Rate</th>
          <th>Peak (Date)</th>
          <th>Trough (Date)</th>
          <th>Average</th>
          <th>Weekday Avg</th>
          <th>Trend (Slope/Day)</th>
        </tr>
      </thead>
      <tbody>
    """
    
    for browser_name, metrics in all_browsers:
        # Convert values to millions
        first_val_in_m = metrics['first_val'] / 1000000
        last_val_in_m = metrics['last_val'] / 1000000
        change_val_in_m = metrics['abs_change'] / 1000000
        max_val_in_m = metrics['max_val'] / 1000000
        min_val_in_m = metrics['min_val'] / 1000000
        avg_val_in_m = metrics['avg_val'] / 1000000
        weekday_avg_in_m = metrics['weekday_avg'] / 1000000
          # Convert slope to thousands, keep two decimal places
        slope_in_k = round(metrics['slope'] / 1000, 2)
        
        # Change rate color and symbol
        pct_change_class = "positive" if metrics['pct_change'] > 0 else "negative" if metrics['pct_change'] < 0 else ""
        sign = "+" if metrics['pct_change'] > 0 else "-" if metrics['pct_change'] < 0 else ""
        
        # Trend direction and color
        trend_direction = "Rise" if metrics['slope'] > 0 else "Decline" if metrics['slope'] < 0 else "Steady"
        trend_class = "positive" if metrics['slope'] > 0 else "negative" if metrics['slope'] < 0 else ""
        
        # Clean browser name, remove "DAD" suffix
        browser_display_name = browser_name.replace(" DAD", "")
        
        # Add table row
        table_html += f"""
        <tr>
          <td>{browser_display_name}</td>
          <td>{first_val_in_m:.2f}M → {last_val_in_m:.2f}M</td>
          <td>{change_val_in_m:.2f}M</td>
          <td class="{pct_change_class}">{sign}{abs(metrics['pct_change']):.2f}%</td>
          <td>{max_val_in_m:.2f}M<br/>({metrics['max_date']})</td>
          <td>{min_val_in_m:.2f}M<br/>({metrics['min_date']})</td>
          <td>{avg_val_in_m:.2f}M</td>
          <td>{weekday_avg_in_m:.2f}M</td>
          <td class="{trend_class}">{trend_direction}<br/>({slope_in_k}K/day)</td>
        </tr>
        """
    
    table_html += """
      </tbody>
    </table>
    """
    
    # Add table to analysis results
    analysis_results.append(table_html)
    
    return analysis_results

def analyze_edge_bsom_comparison(data, fields):
    """Analyze Edge BSoM comparison data.
    
    Compare Edge market share differences with and without AI browsers, and quantify the impact of AI browsers.
    """
    analysis_results = []
    
    if not data or len(data) < 2:
        return ["Insufficient data for analysis."]
    
    # Ensure there are two correct fields
    if len(fields) != 2 or not all(field in data[0] for field in fields):
        if "BSOM Impact" in fields[0]:
            # This is the third chart, not the second chart (the second chart doesn't need separate analysis)
            bsom_impact_field = fields[0]
            impact_values = [row[bsom_impact_field] for row in data if bsom_impact_field in row]
            
            if not impact_values:
                return ["Unable to get BSOM Impact data."]
                
            # 1. Calculate basic impact value changes
            first_val = impact_values[0]
            last_val = impact_values[-1]
            change_pp = (last_val - first_val) * 100  # Convert from decimal to percentage points
            trend = "Increase" if change_pp > 0 else "Decrease" if change_pp < 0 else "Steady"
              # Analysis period information
            first_date = format_date(data[0]["__timestamp"])
            last_date = format_date(data[-1]["__timestamp"])
            total_days = len(data)
            
            # Remove analysis period information display
            
            analysis_results.append(
                f"AI browser impact: Start {(first_val * 100):.2f}% → End {(last_val * 100):.2f}%, "
                f"Change {abs(change_pp):.2f} pt"
            )
            
            # 2. Calculate statistical indicators of impact
            avg_impact = sum(impact_values) / len(impact_values)
            max_impact = max(impact_values)
            min_impact = min(impact_values)
            max_idx = impact_values.index(max_impact)
            min_idx = impact_values.index(min_impact)
            max_date = format_date(data[max_idx]["__timestamp"])
            min_date = format_date(data[min_idx]["__timestamp"])
            
            analysis_results.append(
                f"Max impact: {(max_impact * 100):.2f}% ({max_date}), "
                f"Min impact: {(min_impact * 100):.2f}% ({min_date}), "
                f"Avg impact: {(avg_impact * 100):.2f}%"
            )
            
            # 3. Calculate impact trend
            slope = calculate_linear_trend(impact_values) * 100  # Convert to daily percentage point change
            trend_direction = "Rise" if slope > 0 else "Decline" if slope < 0 else "Steady"
            
            analysis_results.append(
                f"Impact trend: {trend_direction} (Avg daily change {abs(slope):.4f} pt)"
            )
              # 4. Calculate volatility (not displayed in analysis results)
            cv = calculate_variation_coefficient(impact_values)
            
            return analysis_results
        else:
            return ["Data format exception, unable to perform BSoM comparison analysis."]
            
    # The following is a comparative analysis of BSoM and BSOM with AI Browser
    regular_bsom_field = next((f for f in fields if f == "BSOM"), "")
    ai_bsom_field = next((f for f in fields if f == "BSOM with AI Browser in China"), "")
    
    if not regular_bsom_field or not ai_bsom_field:
        return ["Data fields do not match, unable to perform BSoM comparison analysis."]
    
    regular_values = [row[regular_bsom_field] for row in data if regular_bsom_field in row]
    ai_values = [row[ai_bsom_field] for row in data if ai_bsom_field in row]
    
    if not regular_values or not ai_values or len(regular_values) != len(ai_values):
        return ["Data incomplete, unable to perform BSoM comparison analysis."]
      # 1. Calculate basic period information
    first_date = format_date(data[0]["__timestamp"])
    last_date = format_date(data[-1]["__timestamp"])
    total_days = len(data)
    
    # Remove analysis period information display
    
    # 2. Calculate difference values
    diff_values = [(ai - reg) * 100 for ai, reg in zip(ai_values, regular_values)]  # Convert to percentage points
    avg_diff = sum(diff_values) / len(diff_values)
    max_diff = max(diff_values)
    max_diff_idx = diff_values.index(max_diff)
    max_diff_date = format_date(data[max_diff_idx]["__timestamp"])
    
    analysis_results.append(
        f"BSoM difference: Avg diff {avg_diff:.2f} pt, "
        f"Max diff {max_diff:.2f} pt ({max_diff_date})"
    )
    
    # 3. First-last comparison analysis
    for field, values, label in [(regular_bsom_field, regular_values, "Regular BSoM"), 
                               (ai_bsom_field, ai_values, "BSoM with AI Browsers")]:
        first_val = values[0]
        last_val = values[-1]
        change_pp = (last_val - first_val) * 100  # Convert to percentage points
        trend = "Rise" if change_pp > 0 else "Decline" if change_pp < 0 else "Steady"
        
        # Calculate statistical indicators
        avg_val = sum(values) / len(values)
        
        analysis_results.append(
            f"{label}: Start {(first_val * 100):.2f}% → End {(last_val * 100):.2f}%, "
            f"Change {abs(change_pp):.2f} pt ({trend}), Average {(avg_val * 100):.2f}%"
        )
      # 4. Stability comparison (not displayed in analysis results)
    reg_cv = calculate_variation_coefficient(regular_values)
    ai_cv = calculate_variation_coefficient(ai_values)
    
    # Remove coefficient of variation comparison display
    
    return analysis_results

def analyze_ai_browsers_bsom(data, fields):
    """Analyze CN AI browser market share data.
    
    Analyze market share performance and market concentration of each AI browser.
    """
    analysis_results = []
    
    if not data or len(data) < 2:
        return ["Insufficient data for analysis."]
      # 1. Basic analysis period information
    first_date = format_date(data[0]["__timestamp"])
    last_date = format_date(data[-1]["__timestamp"])
    total_days = len(data)
    
    # Remove analysis period information display
    
    # 2. Metrics calculation for each AI browser
    browser_metrics = {}
    max_avg_bsom = 0
    max_avg_browser = ""
    total_first_bsom = 0
    total_last_bsom = 0
    
    for field in fields:
        if field not in data[0]:
            continue
            
        values = [row[field] for row in data if field in row]
        if not values:
            continue
            
        # 2.1 First-last comparison
        first_val = values[0]
        last_val = values[-1]
        change_pp = (last_val - first_val) * 100  # Convert to percentage points
        trend_word = "Rise" if change_pp > 0 else "Decline" if change_pp < 0 else "Steady"
        
        # Cumulative market share total (for subsequent market concentration calculation)
        total_first_bsom += first_val
        total_last_bsom += last_val
        
        # 2.2 Calculate mean and maximum values
        avg_val = sum(values) / len(values)
        max_val = max(values)
        max_idx = values.index(max_val)
        max_date = format_date(data[max_idx]["__timestamp"])
        
        # 2.3 Calculate growth rate (slope)
        slope = calculate_linear_trend(values) * 100  # Convert to daily percentage point change
        
        # Save calculation results
        browser_name = "Doubao" if "Doubao" in field else "Quark" if "Quark" in field else field
        browser_metrics[browser_name] = {
            'first_val': first_val,
            'last_val': last_val,
            'change_pp': change_pp,
            'avg_val': avg_val,
            'max_val': max_val,
            'max_date': max_date,
            'slope': slope,
            'trend_word': trend_word
        }
        
        # Update browser with highest average BSoM
        if avg_val > max_avg_bsom:
            max_avg_bsom = avg_val
            max_avg_browser = browser_name
      # 3. Overall AI browser market overview
    # Remove market leader information
      # Calculate overall AI browser market share changes
    total_change_pp = (total_last_bsom - total_first_bsom) * 100
    trend = "Increase" if total_change_pp > 0 else "Decrease" if total_change_pp < 0 else "Steady"
    
    analysis_results.append(
        f"• Overall AI browser market share: Start {(total_first_bsom * 100):.2f}% → End {(total_last_bsom * 100):.2f}%, "
        f"{trend} {abs(total_change_pp):.2f} pt"
    )
    
    # Sort by average market share
    sorted_browsers = sorted(
        [(name, metrics) for name, metrics in browser_metrics.items()],
        key=lambda x: x[1]['avg_val'],
        reverse=True
    )
    
    for browser_name, metrics in sorted_browsers:
        browser_display_name = "Quark" if browser_name == "夸克" else "Doubao" if browser_name == "豆包" else browser_name
        analysis_results.append(
            f"• {browser_display_name}: Start {(metrics['first_val'] * 100):.2f}% → "
            f"End {(metrics['last_val'] * 100):.2f}%, Change {abs(metrics['change_pp']):.2f} pt ({metrics['trend_word']}); "
            f"Avg share {(metrics['avg_val'] * 100):.2f}%, Max {(metrics['max_val'] * 100):.2f}% ({metrics['max_date']}), "
            f"Avg daily change {metrics['slope']:.4f} pt"
        )
    
    # Remove market concentration analysis
    
    return analysis_results

def analyze_ai_browsers_minutes(data, fields):
    """Analyze CN AI browser usage duration data.
    
    Analyze usage duration performance and trend changes of each AI browser.
    Use M (million) as unit, display with two decimal places.
    """
    analysis_results = []
    
    if not data or len(data) < 2:
        return ["Insufficient data for analysis."]
        
    # 1. Basic analysis period information
    first_date = format_date(data[0]["__timestamp"])
    last_date = format_date(data[-1]["__timestamp"])
    total_days = len(data)
    
    # 2. Metrics calculation for each AI browser
    browser_metrics = {}
    max_avg_minutes = 0
    max_avg_browser = ""
    total_first_minutes = 0
    total_last_minutes = 0
    
    # Function to convert minutes to M (million) units, keeping two decimal places
    def format_to_millions(minutes):
        return round(minutes / 1000000, 2)
    
    for field in fields:
        if field not in data[0]:
            continue
            
        values = [row[field] for row in data if field in row]
        if not values:
            continue
            
        # 2.1 First-last comparison
        first_val = values[0]
        last_val = values[-1]
        change = last_val - first_val
        change_percent = (change / first_val) * 100 if first_val != 0 else 0
        trend_word = "Increase" if change > 0 else "Decrease" if change < 0 else "Steady"
        
        # Cumulative usage duration total
        total_first_minutes += first_val
        total_last_minutes += last_val
        
        # 2.2 Calculate mean and maximum values
        avg_val = sum(values) / len(values)
        max_val = max(values)
        max_idx = values.index(max_val)
        max_date = format_date(data[max_idx]["__timestamp"])
        
        # 2.3 Calculate growth rate (slope)
        slope = calculate_linear_trend(values)
        
        # Save calculation results
        browser_name = "Doubao" if "Doubao" in field else "Quark" if "Quark" in field else field
        browser_metrics[browser_name] = {
            'first_val': first_val,
            'last_val': last_val,
            'change': change,
            'change_percent': change_percent,
            'avg_val': avg_val,
            'max_val': max_val,
            'max_date': max_date,
            'slope': slope,
            'trend_word': trend_word
        }
        
        # Update browser with highest average usage duration
        if avg_val > max_avg_minutes:
            max_avg_minutes = avg_val
            max_avg_browser = browser_name
            
    # 3. Overall AI browser usage duration overview
    total_change = total_last_minutes - total_first_minutes
    total_change_percent = (total_change / total_first_minutes) * 100 if total_first_minutes != 0 else 0
    trend = "Increase" if total_change > 0 else "Decrease" if total_change < 0 else "Steady"
    

    analysis_results.append(
        f"• Total AI browser minutes: Start {format_to_millions(total_first_minutes):.2f}M → End {format_to_millions(total_last_minutes):.2f}M, "
        f"{trend} {format_to_millions(abs(total_change)):.2f}M minutes ({abs(total_change_percent):.2f}%)"
    )




    
    # Sort by average usage duration
    sorted_browsers = sorted(
        [(name, metrics) for name, metrics in browser_metrics.items()],
        key=lambda x: x[1]['avg_val'],
        reverse=True
    )
    
    for browser_name, metrics in sorted_browsers:
        browser_display_name = "Quark" if browser_name == "夸克" else "Doubao" if browser_name == "豆包" else browser_name
        analysis_results.append(
            f"• {browser_display_name}: Start {format_to_millions(metrics['first_val']):.2f}M → "
            f"End {format_to_millions(metrics['last_val']):.2f}M, Change {format_to_millions(abs(metrics['change'])):.2f}M minutes "
            f"({abs(metrics['change_percent']):.2f}%) ({metrics['trend_word']}); "
            f"Avg {format_to_millions(metrics['avg_val']):.2f}M minutes, Max {format_to_millions(metrics['max_val']):.2f}M minutes ({metrics['max_date']}), "
            f"Avg daily change {format_to_millions(metrics['slope']):.2f}M minutes"
        )
    
    return analysis_results

def analyze_data(data, config):
    """Generate completely calculation-based data analysis results.
    
    All analysis results are based only on computable statistical values, without any inference or subjective judgment.
    """
    if not data or len(data) < 2:
        return ["Insufficient data for analysis."]
    
    # Get fields to analyze
    fields = config.get("analysis_fields", [])
    
    # Determine chart type
    is_browser_dad_chart = any("DAD" in field for field in fields) and all("BSOM" not in field for field in fields)
    is_edge_bsom_comparison = len(fields) == 2 and "BSOM with AI Browser in China" in fields and "BSOM" in fields
    is_bsom_impact_chart = len(fields) == 1 and "BSOM Impact" in fields[0]
    is_ai_browsers_bsom_chart = len(fields) == 2 and "Doubao BSOM" in fields and "Quark BSOM" in fields
    is_ai_browsers_minutes_chart = len(fields) == 2 and "Doubao Minutes" in fields and "Quark Minutes" in fields
    
    # Call corresponding analysis function based on chart type
    if is_browser_dad_chart:
        return analyze_browser_dad_data(data, fields)
    elif is_edge_bsom_comparison or is_bsom_impact_chart:
        return analyze_edge_bsom_comparison(data, fields)
    elif is_ai_browsers_bsom_chart:
        return analyze_ai_browsers_bsom(data, fields)
    elif is_ai_browsers_minutes_chart:
        return analyze_ai_browsers_minutes(data, fields)
    else:
        # For unrecognized chart types, return basic analysis
        return ["Unrecognized chart type, unable to generate specialized analysis."]

def generate_chart_data(data, config):
    """Generate chart data for visualization."""
    # In standardized data processing, all data uses the __timestamp field
    x_field = "__timestamp"
    y_fields = config["y_fields"]
    
    # Prepare data for chart
    labels = [format_date(row[x_field]) for row in data]
    datasets = []
    rolling_datasets = []  # New: store 7-day rolling average data
    
    # Calculate appropriate X-axis settings based on data points count
    x_axis_settings = calculate_x_axis_settings(len(data))
    
    for field in y_fields:
        if field in data[0]:
            values = [row.get(field, 0) for row in data]
            datasets.append({
                "label": field,
                "data": values,
            })
              # New: calculate 7-day rolling average
            rolling_values = calculate_rolling_average(values, 7)
            rolling_datasets.append({
                "label": field,  # Use same label, don't add "(7-day average)" suffix
                "data": rolling_values,
            })
    
    return {
        "labels": labels,
        "datasets": datasets,
        "rolling_datasets": rolling_datasets,  # New: include 7-day rolling average
        "x_axis_settings": x_axis_settings,
        "data_period": {
            "start": format_date(data[0][x_field]) if data else "",
            "end": format_date(data[-1][x_field]) if data else "",
            "days": len(data)
        }
    }

def calculate_x_axis_settings(data_points_count):
    """Calculate appropriate X-axis display settings based on data points count.
    
    Args:
        data_points_count: Number of data points
        
    Returns:
        dict: Settings for X-axis display
    """
    settings = {
        'display_format': 'day',  # day, week, month
        'skip_factor': 1,        # show every Nth label
        'rotation': 0,           # rotation angle for labels
        'max_tick_limit': 12     # maximum number of ticks to display
    }
    
    # Adjust settings based on number of data points
    if data_points_count <= 14:  # Two weeks or less
        settings['display_format'] = 'day'
        settings['skip_factor'] = 1
        settings['max_tick_limit'] = data_points_count
    elif data_points_count <= 31:  # Up to a month
        settings['display_format'] = 'day'
        settings['skip_factor'] = max(1, data_points_count // 12)  # Aim for ~12 labels max
        settings['rotation'] = 0
        settings['max_tick_limit'] = 12
    elif data_points_count <= 60:  # Up to two months
        settings['display_format'] = 'day'
        settings['skip_factor'] = 3
        settings['rotation'] = 45
        settings['max_tick_limit'] = 15
    elif data_points_count <= 90:  # Up to a quarter
        settings['display_format'] = 'day'
        settings['skip_factor'] = 5
        settings['rotation'] = 45
        settings['max_tick_limit'] = 18
    elif data_points_count <= 180:  # Up to half a year
        settings['display_format'] = 'week'
        settings['skip_factor'] = 1
        settings['rotation'] = 45
        settings['max_tick_limit'] = 20
    elif data_points_count <= 365:  # Up to a year
        settings['display_format'] = 'month'
        settings['skip_factor'] = 1
        settings['rotation'] = 0
        settings['max_tick_limit'] = 12
    else:  # More than a year
        settings['display_format'] = 'month'
        settings['skip_factor'] = 2
        settings['rotation'] = 0
        settings['max_tick_limit'] = 12
    
    return settings

def generate_html_content(visualizations):
    """Generate HTML content for the report."""
    chart_containers = []
    chart_configs = []
    
    # Get current date and time for report
    now = datetime.datetime.now()
    report_date = now.strftime("%Y-%m-%d %H:%M")
    
    # Identify the Edge BSoM Comparison and Edge BSoM Impact charts
    bsom_comparison_index = -1
    bsom_impact_index = -1
    
    for i, vis in enumerate(visualizations):
        if "BSoM Comparison" in vis['title']:
            bsom_comparison_index = i
        elif "BSoM Impact" in vis['title']:
            bsom_impact_index = i
    
    # Process each visualization
    for i, vis in enumerate(visualizations):
        chart_id = f"chart-{i}"
        
        # Skip creating container for BSoM Comparison as it will be combined with BSoM Impact
        if i == bsom_comparison_index:
            # Just create chart config, don't create container
            config = {
                "id": chart_id,
                "type": vis["chart_type"],
                "data": vis["data"],
                "percentage": vis.get("percentage", False),
                "y_axis_min": vis.get("y_axis_min"),
                "y_axis_max": vis.get("y_axis_max")
            }
            chart_configs.append(config)
            continue
            
        # Special handling for BSoM Impact to include BSoM Comparison chart above it
        if i == bsom_impact_index and bsom_comparison_index != -1:
            # Create a combined container with both charts
            bsom_comp_chart_id = f"chart-{bsom_comparison_index}"
            
            # Get data period info for both charts
            comp_data_period = visualizations[bsom_comparison_index]["data"].get("data_period", {"days": 0, "start": "", "end": ""})
            impact_data_period = vis["data"].get("data_period", {"days": 0, "start": "", "end": ""})
            
            comp_period_info = f"<div class='data-period'>Data period: {comp_data_period['start']} to {comp_data_period['end']} ({comp_data_period['days']} days)</div>"
            impact_period_info = f"<div class='data-period'>Data period: {impact_data_period['start']} to {impact_data_period['end']} ({impact_data_period['days']} days)</div>"
            
            container = f"""
            <div class="chart-container">
                <!-- BSoM Comparison Chart -->                <div class="chart-title">{visualizations[bsom_comparison_index]['title']}</div>
                <div class="chart-description">{visualizations[bsom_comparison_index]['description']}</div>                <div class="data-controls-row">
                    <div class="data-period">
                        Data period: {comp_data_period['start']} to {comp_data_period['end']} ({comp_data_period['days']} days)
                        <button class="chart-reset-zoom" data-chart-id="{bsom_comp_chart_id}">↺ Reset Zoom</button>
                    </div>
                    <div class="chart-controls">
                        <div class="chart-toggle">
                            <button class="toggle-button active" data-mode="daily" data-chart-id="{bsom_comp_chart_id}">Daily Data</button>
                            <button class="toggle-button" data-mode="rolling" data-chart-id="{bsom_comp_chart_id}">RL7 Average</button>
                        </div>
                    </div>
                </div>
                <div class="chart{' large-dataset' if comp_data_period['days'] > 60 else ''}">
                    <canvas id="{bsom_comp_chart_id}"></canvas>
                </div>
                
                <!-- BSoM Impact Chart -->                <div class="chart-title" style="margin-top:40px;">{vis['title']}</div>
                <div class="chart-description">{vis['description']}</div>                <div class="data-controls-row">                    <div class="data-period">
                        Data period: {impact_data_period['start']} to {impact_data_period['end']} ({impact_data_period['days']} days)
                        <button class="chart-reset-zoom" data-chart-id="{chart_id}">↺ Reset Zoom</button>
                    </div>
                    <div class="chart-controls">
                        <div class="chart-toggle">
                            <button class="toggle-button active" data-mode="daily" data-chart-id="{chart_id}">Daily Data</button>
                            <button class="toggle-button" data-mode="rolling" data-chart-id="{chart_id}">RL7 Average</button>
                        </div>
                    </div>
                </div>
                <div class="chart{' large-dataset' if impact_data_period['days'] > 60 else ''}">
                    <canvas id="{chart_id}"></canvas>
                </div>
                <div class="analysis">
                    <div class="analysis-title">Data Analysis</div>
                    {''.join(f'<div class="analysis-point">• {point}</div>' for point in vis['analysis'])}
                </div>
            </div>
            """
        else:
            # For other charts, use standard container with analysis
            # Get data period info
            data_period = vis["data"].get("data_period", {"days": 0, "start": "", "end": ""})
            
            container = f"""
            <div class="chart-container">
                <div class="chart-title">{vis['title']}</div>
                <div class="chart-description">{vis['description']}</div>                <div class="data-controls-row">                    <div class="data-period">
                        Data period: {data_period['start']} to {data_period['end']} ({data_period['days']} days)
                        <button class="chart-reset-zoom" data-chart-id="{chart_id}">↺ Reset Zoom</button>
                    </div>
                    <div class="chart-controls">
                        <div class="chart-toggle">                            <button class="toggle-button active" data-mode="daily" data-chart-id="{chart_id}">Daily Data</button>
                            <button class="toggle-button" data-mode="rolling" data-chart-id="{chart_id}">RL7 Average</button>
                        </div>
                    </div>
                </div><div class="chart{' large-dataset' if data_period['days'] > 60 else ''}">
                    <canvas id="{chart_id}"></canvas>
                </div>
                <div class="analysis">
                    <div class="analysis-title">Data Analysis</div>
                    <div class="analysis-content">
                    {''.join(f'<div class="analysis-point">{point}</div>' for point in vis['analysis'])}
                    </div>
                </div>
            </div>
            """
        
        chart_containers.append(container)
        
        # Create chart config
        config = {
            "id": chart_id,
            "type": vis["chart_type"],
            "data": vis["data"],
            "percentage": vis.get("percentage", False),
            "y_axis_min": vis.get("y_axis_min"),
            "y_axis_max": vis.get("y_axis_max")
        }
        chart_configs.append(config)
    
    today = datetime.datetime.now()
    generation_date = today.strftime("%Y-%m-%d %H:%M")
    current_year = today.year
    timestamp_filename = today.strftime("%Y%m%d-%H%M")
      # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="zh-cn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CN AI Browser Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.0"></script>
    <style>        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #f8f9fc;
            background-image: linear-gradient(to bottom, #f8f9fc, #f1f4f9);
            overflow-x: hidden; /* Prevent horizontal scrollbar */
        }}
        
        /* Main layout - single column full width */
        .main-content {{
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px 50px;
        }}        .header {{
            background: linear-gradient(135deg, #0078d4, #0063b1);
            color: white;
            padding: 30px;
            border-radius: 14px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 120, 212, 0.15);
        }}        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header p {{
            margin: 8px 0 0;
            font-size: 16px;
            opacity: 0.9;}}        .chart-container {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            margin-bottom: 40px;
            padding: 28px;
            border: 1px solid rgba(230, 230, 230, 0.7);
            transition: all 0.3s ease;        }}
        .chart-container:hover {{
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }}        .chart-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 12px;
            color: #0078d4;
            letter-spacing: -0.3px;
            position: relative;
            display: inline-block;
        }}        .chart-description {{
            font-size: 15px;
            margin-bottom: 22px;
            color: #666;
            line-height: 1.5;
            max-width: 90%;
        }}
        .data-controls-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .data-period {{
            font-size: 14px;
            color: #666;
            display: flex;
            align-items: center;
        }}
        .chart-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}        .chart-reset-zoom {{
            background-color: rgba(0, 120, 212, 0.05);
            border: 1px solid rgba(0, 120, 212, 0.2);
            border-radius: 6px;
            padding: 5px 10px;
            margin-left: 10px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            color: #777;
            vertical-align: middle;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .chart-reset-zoom:hover {{
            background-color: #f0f0f0;
            color: #0078d4;
            border-color: #0078d4;
        }}
        .chart-toggle {{
            display: flex;
            border-radius: 4px;
            overflow: hidden;
        }}
        .toggle-button {{
            background-color: #f5f5f7;
            border: 1px solid #d1d1d1;
            padding: 5px 10px;
            font-size: 13px;
            cursor: pointer;
            color: #444;
            border-right: none;
        }}
        .toggle-button:last-child {{
            border-right: 1px solid #d1d1d1;
        }}
        .toggle-button:hover {{
            background-color: #e5e5e5;
        }}
        .toggle-button.active {{
            background-color: #0078d4;
            color: white;
            border-color: #0078d4;
        }}
        .chart {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        .chart.large-dataset {{
            height: 450px;
        }}        .analysis {{
            background-color: #FFF;
            border-radius: 8px;
            padding: 20px;
            margin-top: 25px;
            box-shadow: 1px 1px 8px 4px rgba(0,0,0,0.03);
        }}        .analysis-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 18px;
            color: #333;
            position: relative;
            padding-bottom: 10px;
        }}
        .analysis-content {{
            display: flex;
            flex-direction: column;
        }}
        .analysis-section {{
            font-size: 15px;
            font-weight: 600;
            color: #0078d4;
            margin: 10px 0 5px 0;
            padding-left: 5px;
            border-left: 3px solid #0078d4;
        }}
        .analysis-point {{
            font-size: 14px;
            line-height: 1.8;  /* Changed to 1.8, increase line spacing */
            margin-bottom: 10px;  /* Changed to 10px, increase paragraph spacing */
            padding-left: 5px;
        }}
        .double-chart {{
            padding-bottom: 30px;        }}        .footer {{
            text-align: center;
            margin-top: 0px;
            padding: 10px 20px;
            font-size: 14px;
            color: #666;
            position: relative;
                    }}.pm-studio-logo {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 15px auto;
            padding: 10px 24px;
            background: linear-gradient(90deg, #7928ca 0%, #2575fc 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
            font-size: 16px;
            box-shadow: 0 4px 10px rgba(106, 17, 203, 0.2);        }}        .pm-studio-logo:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(106, 17, 203, 0.3);
            background: linear-gradient(90deg, #8a37dd 0%, #377dff 100%);
        }}.pm-logo-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            color: #7928ca;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.3);
        }}.copyright-text {{
            display: block;
            margin-top: 10px;
            color: #888;
            font-size: 13px;
            letter-spacing: 0.3px;
            font-weight: 400;
        }}        /* Back to top button styles */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: rgba(0, 120, 212, 0.9);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            text-decoration: none;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            cursor: pointer;
        }}
        
        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}
        
        .back-to-top:hover {{
            background-color: #0063b1;
            transform: translateY(-3px);
        }}
          .back-to-top:active {{
            transform: translateY(-1px);
        }}
  
        .back-to-top-arrow {{
            width: 12px;
            height: 12px;
            border-left: 3px solid white;
            border-top: 3px solid white;
            transform: rotate(45deg);
            margin-top: 4px;
        }}
        
        @media print {{
            body {{
                background-color: white;
            }}
            .chart-container {{
                box-shadow: none;
                margin-bottom: 20px;
            }}
            .chart {{
                height: 350px !important;
            }}
            .header {{
                background-color: white;
                color: black;
                padding: 0;
            }}
            .back-to-top {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-content">
        <div class="container">
            <div class="header">
                <h1>CN AI Browser Analysis Report</h1>
                <p>Generated on: {report_date}</p>
            </div>
            
            {"".join(chart_containers)}

            <div class="footer">
                <p>This report is automatically generated based on Titan query data © {current_year} Microsoft EMS Team</p>
                <a href="https://pmstudio-aac5g7cxenedc0ex.westcentralus-01.azurewebsites.net/" target="_blank" class="pm-studio-logo">
                    <span class="pm-logo-icon">PM</span>
                    Powered by PM Studio
                    </a>
                </div>
            </div>
    </div>
    
    <!-- Back to top button -->
    <div id="backToTop" class="back-to-top" title="Back to top">
        <div class="back-to-top-arrow"></div>
    </div>
      <script>
        const chartConfigs = {json.dumps(chart_configs)};
        
        // Store references to all chart instances
        let chartInstances = {{}};
        // Store original data and rolling average data for charts
        let chartData = {{}};
          document.addEventListener('DOMContentLoaded', function() {{
            // Back to top button functionality
            const backToTopButton = document.getElementById('backToTop');
            
            // Click to return to top
            backToTopButton.addEventListener('click', function() {{
                window.scrollTo({{ 
                    top: 0, 
                    behavior: 'smooth' 
                }});
            }});
            
            // Control button show/hide
            function toggleBackToTopButton() {{
                if (window.scrollY > 300) {{
                    backToTopButton.classList.add('visible');
                }} else {{
                    backToTopButton.classList.remove('visible');
                }}
            }}
            
            // Listen to scroll events
            window.addEventListener('scroll', toggleBackToTopButton);
            // Initial check
            toggleBackToTopButton();
            
            // Add click events for reset zoom buttons
            document.querySelectorAll('.chart-reset-zoom').forEach(button => {{
                button.addEventListener('click', function() {{
                    const chartId = this.getAttribute('data-chart-id');
                    if (chartInstances[chartId]) {{
                        chartInstances[chartId].resetZoom();
                    }}
                }});
            }});
            
            // Add click events for toggle buttons
            document.querySelectorAll('.toggle-button').forEach(button => {{
                button.addEventListener('click', function() {{
                    const chartId = this.getAttribute('data-chart-id');
                    const mode = this.getAttribute('data-mode');
                    
                    // Update button styles
                    document.querySelectorAll('.toggle-button[data-chart-id="' + chartId + '"]').forEach(btn => {{
                        btn.classList.remove('active');
                    }});
                    this.classList.add('active');
                    
                    // Update chart data
                    if (chartInstances[chartId] && chartData[chartId]) {{
                        if (mode === 'daily') {{
                            chartInstances[chartId].data.datasets = chartData[chartId].daily;
                        }} else if (mode === 'rolling') {{
                            chartInstances[chartId].data.datasets = chartData[chartId].rolling;
                        }}
                        chartInstances[chartId].update();
                    }}
                }});
            }});
            
            chartConfigs.forEach(function(config) {{
                const ctx = document.getElementById(config.id).getContext('2d');
                
                // Set color scheme
                const colorScheme = [
                    'rgba(0, 120, 212, 0.7)',     // Edge Blue
                    'rgba(255, 99, 132, 0.7)',    // Red
                    'rgba(255, 205, 86, 0.7)',    // Yellow
                    'rgba(75, 192, 192, 0.7)',    // Cyan
                    'rgba(153, 102, 255, 0.7)',   // Purple
                    'rgba(255, 159, 64, 0.7)',    // Orange
                    'rgba(54, 162, 235, 0.7)',    // Blue
                    'rgba(40, 167, 69, 0.7)',     // Green
                ];
                
                // Prepare daily datasets
                const dailyDatasets = [];
                for (let i = 0; i < config.data.datasets.length; i++) {{
                    const dataset = config.data.datasets[i];
                    const dailyDataset = JSON.parse(JSON.stringify(dataset)); // Deep copy
                    
                    dailyDataset.backgroundColor = colorScheme[i % colorScheme.length];
                    dailyDataset.borderColor = colorScheme[i % colorScheme.length].replace('0.7', '1');
                    dailyDataset.borderWidth = 2;
                    dailyDataset.pointRadius = 3;
                    
                    // Format percentage values
                    if (config.percentage) {{
                        dailyDataset.data = dailyDataset.data.map(value => value * 100);
                    }}
                    
                    dailyDatasets.push(dailyDataset);
                }}
                
                // Prepare rolling average datasets
                const rollingDatasets = [];
                if (config.data.rolling_datasets) {{
                    for (let i = 0; i < config.data.rolling_datasets.length; i++) {{                        const dataset = config.data.rolling_datasets[i];
                        const rollingDataset = JSON.parse(JSON.stringify(dataset)); // Deep copy
                          // Use original label, don't add "(7-day average)" suffix
                        if (i < config.data.datasets.length) {{
                            rollingDataset.label = config.data.datasets[i].label;
                        }}
                        
                        rollingDataset.backgroundColor = colorScheme[i % colorScheme.length];
                        rollingDataset.borderColor = colorScheme[i % colorScheme.length].replace('0.7', '1');
                        rollingDataset.borderWidth = 2;
                        rollingDataset.pointRadius = 3;
                          // Format percentage values and keep null values
                        if (config.percentage) {{
                            rollingDataset.data = rollingDataset.data.map(value => 
                                value === null ? null : value * 100
                            );
                        }}
                        
                        rollingDatasets.push(rollingDataset);
                    }}
                }}
                
                // Store chart data
                chartData[config.id] = {{
                    daily: dailyDatasets,
                    rolling: rollingDatasets
                }};
                
                // Create chart instance
                chartInstances[config.id] = new Chart(ctx, {{
                    type: config.type,
                    data: {{
                        labels: config.data.labels,
                        datasets: dailyDatasets
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Date'
                                }},
                                ticks: {{
                                    // Apply X axis settings based on data point count
                                    maxRotation: config.data.x_axis_settings.rotation,
                                    minRotation: config.data.x_axis_settings.rotation,
                                    autoSkip: true,
                                    maxTicksLimit: config.data.x_axis_settings.max_tick_limit,
                                    callback: function(val, index) {{
                                        const label = this.getLabelForValue(val);
                                        // Get the label format based on config
                                        const skipFactor = config.data.x_axis_settings.skip_factor;
                                        const format = config.data.x_axis_settings.display_format;
                                        
                                        // For month format, simplify to just show month
                                        if (format === 'month') {{
                                            const dateParts = label.split('-');
                                            if (dateParts.length >= 2) {{
                                                return dateParts[1] + 'M';
                                            }}
                                        }}
                                        
                                        // For week format, only show dates at week boundaries
                                        if (format === 'week' && index % 7 !== 0) {{
                                            return '';
                                        }}
                                        
                                        // For day format with skip factor
                                        if (index % skipFactor !== 0) {{
                                            return '';
                                        }}
                                        
                                        return label;
                                    }}
                                }}
                            }},
                            y: {{
                                beginAtZero: config.y_axis_min == undefined,
                                min: config.y_axis_min != undefined ? (config.percentage ? config.y_axis_min * 100 : config.y_axis_min) : undefined,
                                max: config.y_axis_max != undefined ? (config.percentage ? config.y_axis_max * 100 : config.y_axis_max) : undefined,
                                title: {{
                                    display: true,
                                    text: config.percentage ? 'Percentage (%)' : 'Value'
                                }},
                                ticks: {{
                                    // For percentage charts, explicitly set the ticks
                                    ...(config.percentage && config.y_axis_min != undefined && config.y_axis_max != undefined ? {{
                                        // Generate ticks from y_axis_min to y_axis_max with step 2.5
                                        callback: function(value) {{
                                            return value.toFixed(1) + '%';
                                        }},
                                        stepSize: 2.5,
                                        autoSkip: false
                                    }} : {{
                                        callback: function(value) {{
                                            if (config.percentage) {{
                                                return Number(value).toFixed(1) + '%';
                                            }} else {{
                                                return value.toLocaleString('zh-CN');
                                            }}
                                        }}
                                    }})
                                }}
                            }}
                        }},
                        plugins: {{
                            tooltip: {{
                                mode: 'index',
                                intersect: false,
                                callbacks: {{
                                    title: function(tooltipItems) {{
                                        // Format the date for the tooltip title
                                        return tooltipItems[0].label;
                                    }},
                                    label: function(context) {{
                                        let label = context.dataset.label || '';
                                        if (label) {{
                                            label += ': ';
                                        }}                                        let value = context.raw;
                                        if (config.percentage) {{
                                            label += value.toFixed(2) + '%';
                                        }} else {{
                                            // Value formatting: >1M display as xx.xxM, >1K display as xxK, otherwise original value
                                            if (value >= 1000000) {{
                                                label += (value / 1000000).toFixed(2) + 'M';
                                            }} else if (value >= 1000) {{
                                                label += Math.round(value / 1000) + 'K';
                                            }} else {{
                                                label += value.toLocaleString('zh-CN');
                                            }}
                                        }}
                                        return label;
                                    }}
                                }}
                            }},
                            legend: {{
                                position: 'top',
                            }},
                            title: {{
                                display: false,
                            }},
                            zoom: {{
                                pan: {{
                                    enabled: true,
                                    mode: 'x'
                                }},
                                zoom: {{
                                    wheel: {{
                                        enabled: true,
                                    }},
                                    pinch: {{
                                        enabled: true
                                    }},
                                    mode: 'x',
                                }}
                            }}
                        }}
                    }}
                }});
            }});        }});
    </script>
</body>
</html>
"""
    return html_content

def generate_html_report(visualizations, output_file):
    """Generate HTML report and save to file."""
    html_content = generate_html_content(visualizations)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return output_file
    except Exception as e:
        print(f"Error writing HTML report: {str(e)}")
        return None
        
def main():
    """Main function."""
    args = parse_args()
    visualizations = []
    
    # Find and parse CSV files
    matched_files = find_csv_files(args.input_dir)
    if not matched_files:
        print("Error: No CSV files found")
        return 1
        
    # Process each CSV file with its matched config
    for csv_file, matched_config in matched_files:
        print(f"Processing file: {os.path.basename(csv_file)}")
            
        # Parse CSV data
        data = read_csv_data(csv_file, matched_config)
        if not data:
            print(f"Warning: Unable to read data from {os.path.basename(csv_file)}")
            continue
            
        # Generate chart data
        chart_data = generate_chart_data(data, matched_config)
        
        # Generate analysis
        analysis = analyze_data(data, matched_config)
          # Add to visualizations
        visualizations.append({
            "title": matched_config["title"],
            "description": matched_config["description"],
            "chart_type": matched_config.get("chart_type", "line"),
            "percentage": matched_config.get("percentage", False),
            "y_axis_min": matched_config.get("y_axis_min"),
            "y_axis_max": matched_config.get("y_axis_max"),
            "data": chart_data,
            "analysis": analysis,
            "config": matched_config,
        })
      # Check if any visualizations were created
    if not visualizations:
        print("Error: Unable to generate visualizations from any file")
        return 1
    
    # Sort visualization content according to the order in VISUALIZATION_CONFIGS
    # Create a mapping from configuration ID to index
    config_order = {config["id"]: idx for idx, config in enumerate(VISUALIZATION_CONFIGS)}
    
    # Sort visualizations according to configuration ID order
    visualizations.sort(key=lambda x: config_order.get(x["config"]["id"], 999))
    
    # Determine output directory (prefer explicit run directory)
    output_dir = args.output_dir
    if args.output_file and not os.path.isdir(args.output_file):
        # Backward compatibility: treat provided file path as final path (legacy behavior)
        legacy_file_path = args.output_file
    else:
        legacy_file_path = None

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate HTML report with timestamp filename
    try:
        # Create timestamped filename
        today = datetime.datetime.now()
        timestamp_filename = today.strftime("%Y%m%d_%H%M")
        if legacy_file_path:
            output_path = legacy_file_path
        else:
            output_filename = f"{timestamp_filename} - CN AI Browser Analysis Report.html"
            output_path = os.path.join(output_dir, output_filename)
        
        print(f"Generating HTML report: {output_path}")
        output_file = generate_html_report(visualizations, output_path)
        if output_file:
            print(f"[SUCCESS] Report generated: {output_file}")
            print(f"Open this file in your browser to view the analysis report.")
        else:
            print("Error: Failed to generate HTML report")
            return 1
    except Exception as e:
        print(f"Error generating HTML report: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())



