from datetime import datetime
import requests
import pandas as pd
import os
import importlib.util
import sys
import re
import jwt
from pm_studio_mcp.utils.graph.auth import AuthUtils



# Import table metadata module
from pm_studio_mcp.utils.titan.titan_table_metadata import get_table_metadata
from pm_studio_mcp.config import config

class TitanQuery:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TitanQuery, cls).__new__(cls)
        return cls._instance

    def __init__(self , titan_endpoint):
        if self._initialized:
            return

        self.endpoint = titan_endpoint
        self.access_token = AuthUtils().getTitanToken()

        try:
            # Decode without verification (since we don't have the secret key)
            decoded_token = jwt.decode(self.access_token, options={"verify_signature": False})
            self.user_alias = decoded_token.get('unique_name').split('@')[0] if decoded_token.get('unique_name') else None
            print(f"self.user_alias: {self.user_alias}",flush=True)
        except Exception as e:
            print(f"Error decoding with PyJWT: {e}",flush=True)

        self._initialized = True

    def query_data_from_titan_tool(self, query_str, table, output_dir=None):
        """
        Query data from Titan tool and save directly to file

        Args:
            query_str (str): Query string
            table (str): Table name, can be in format "{database_name}.{table_name}"
            output_dir (str, optional): Output directory path, defaults to config.WORKING_PATH

        Returns:
            dict: Dictionary containing:
                - 'file_path': Path to the output file
                - 'row_count': Total number of rows
                - 'message': Status message
        """
        # Use default working path from config if output_dir is not provided
        if output_dir is None:
            output_dir = config.WORKING_PATH
            
        try:
            # Extract table name if it's in format {database_name}.{table_name}
            simple_table_name = table.split('.')[-1] if '.' in table else table
            
            # Clean up quotes if they exist
            simple_table_name = simple_table_name.strip("'").strip('"')
            
            # Clean up the query string to ensure it uses the simple table name
            # Replace patterns like: 'database'.'table' or "database"."table" or database.table with just the table name
            if '.' in query_str:
                # Various database.table pattern replacements
                patterns = [
                    r"'[^']+'\.'[^']+'",  # 'database'.'table'
                    r'"[^"]+"\."[^"]+"',   # "database"."table"
                    r'`[^`]+`\.`[^`]+`',   # `database`.`table`
                    r"\b\w+\.\w+\b"        # database.table (without quotes)
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, query_str)
                    for match in matches:
                        # Extract the table part from the match
                        table_part = match.split('.')[-1].strip("'").strip('"').strip('`')
                        # Only replace if this looks like our target table
                        if table_part.lower() == simple_table_name.lower():
                            query_str = query_str.replace(match, simple_table_name)
            
            api_headers = {
                "Authorization": "Bearer " + self.access_token,
                "Content-Type": "application/json",
            }
            api_body = {
                "query": query_str,
                "TableName": simple_table_name,
                "UserAlias": self.user_alias,
                "CreatedTimeUtc": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "UseCache": True,
                "UseDefaultDatabaseName": True,
            }

            response = requests.post(self.endpoint, json=api_body, headers=api_headers)

            # Check response status code
            if response.status_code != 200:
                return {
                    'file_path': None,
                    'row_count': 0,
                    'message': f"API request failed with status code {response.status_code}: {response.text}"
                }

            # Try to parse JSON response
            try:
                response_json = response.json()
            except ValueError as e:
                return {
                    'file_path': None,
                    'row_count': 0,
                    'message': f"Failed to parse API response as JSON: {str(e)}"
                }

            # Check response structure
            if "Result" not in response_json or "data" not in response_json["Result"]:
                return {
                    'file_path': None,
                    'row_count': 0,
                    'message': f"Invalid API response structure: {response_json}"
                }

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Generate output file path
            output_file = os.path.join(output_dir, f"titan_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")            # Convert data to DataFrame and get information
            try:
                data = pd.DataFrame(response_json["Result"]["data"])
                
                # Check if query returned no data
                if data.empty:
                    return {
                        'file_path': None,
                        'row_count': 0,
                        'message': 'Query executed successfully but returned 0 rows. Please check your filters and date range.'
                    }
                
                # Save to CSV only if we have data
                data.to_csv(output_file, index=False)

                # Prepare return information
                result = {
                    'file_path': output_file,
                    'row_count': len(data),
                    'message': 'Successfully retrieved data from Titan'
                }

                print(f"Successfully saved query results to: {output_file}")
                print(f"Total rows: {result['row_count']}")
                return result

            except Exception as e:
                return {
                    'file_path': None,
                    'row_count': 0,
                    'message': f"Failed to save data to CSV: {str(e)}"
                }

        except requests.exceptions.RequestException as e:
            return {
                'file_path': None,
                'row_count': 0,
                'message': f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'file_path': None,
                'row_count': 0,
                'message': f"Unexpected error: {str(e)}"
            }

    def get_sql_result_from_titan(self, query_str=None, table=None, sql_file=None):
        """ 
        Get SQL result from Titan tool
        Args:
            query_str (str): SQL query string
            sql_file (str, optional): Path to a file containing the SQL query, defaults to None
        Returns:
            dict: Dictionary containing the result data or an error message
        """        

        if sql_file:
            # If a content file is provided, read its content
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    query_str = f.read()
                    table = query_str.split("FROM")[-1].split()[0].strip() # Extract table name from the query
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read content file: {str(e)}"
                }
        
        api_headers = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json",
        }

        api_body = {
            "query": query_str,
            "TableName": table,
            "UserAlias": self.user_alias,
            "CreatedTimeUtc": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "UseCache": True,
            "UseDefaultDatabaseName": True,
        }

        response = requests.post(self.endpoint, json=api_body, headers=api_headers)

        # Check response status code
        if response.status_code != 200:
            return {
                'row_count': 0,
                'message': f"API request failed with status code {response.status_code}: {response.text}"
            }

        response_json = response.json()
        return response_json["Result"]["data"]