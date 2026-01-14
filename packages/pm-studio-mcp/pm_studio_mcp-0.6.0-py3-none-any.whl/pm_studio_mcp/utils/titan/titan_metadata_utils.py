"""
Titan Table Metadata Query Utility Class
"""

import os
import json
from datetime import datetime
from pm_studio_mcp.utils.titan.titan_table_metadata import get_table_metadata, get_table_metadata_extended, find_table_by_template_name
from pm_studio_mcp.utils.titan.tables.table_metadata import TABLE_METADATA, TEMPLATE_METADATA

class TitanMetadataUtils:
    @staticmethod
    def find_templates_tool(template_keyword: str, working_path: str = None):
        """
        Search for SQL templates based on template name or description keyword.
        This specialized tool only looks for SQL templates, making it more precise than the general metadata tool.

        Args:
            template_keyword (str): SQL template keyword to search for (e.g., "mac dau", "retention by browser")
            working_path (str, optional): Directory path to save the JSON file. If None, will use current directory.

        Returns:
            dict: Dictionary containing search results
                - status: Search status ("success" or "error")
                - message: Status message with summary of found templates
                - template_matches: List of matching templates with their table info:
                    - table: Table name containing the template
                    - template: Template name
                    - description: Template description
                - result_path: Path to the saved JSON file (if templates found)
                If no matches found, returns error status with suggestions
        """
        try:
            # Search for templates matching the keyword
            template_matches = find_table_by_template_name(template_keyword)
            
            if not template_matches:
                # No matches found - collect suggestions
                all_templates = []
                for table_name, metadata in TABLE_METADATA.items():
                    if 'sql_templates' in metadata:
                        for template in metadata['sql_templates']:
                            if 'name' in template and 'description' in template:
                                all_templates.append((table_name, template['name'], template['description']))
                
                # Get up to 5 random templates as suggestions
                import random
                suggestions = random.sample(all_templates, min(5, len(all_templates)))
                
                return {
                    "status": "error",
                    "message": f"No SQL templates found matching '{template_keyword}'",
                    "suggestions": [
                        {"table": t[0], "template": t[1], "description": t[2]} 
                        for t in suggestions
                    ]
                }
            
            # Format template matches
            matches = []
            for table_name, template_name, template_desc in template_matches:
                # Get table metadata for additional details
                table_metadata = get_table_metadata(table_name)
                extended_metadata = get_table_metadata_extended(table_name)
                
                match_info = {
                    "table": table_name,
                    "template": template_name,
                    "description": template_desc,
                    "table_description": table_metadata.get("description", "") if table_metadata else "",
                }
                
                # Add filter information if available
                if extended_metadata and "filter_columns" in extended_metadata:
                    match_info["filter_columns"] = extended_metadata["filter_columns"]
                
                matches.append(match_info)
            
            # Create a summary message
            if len(matches) == 1:
                message = f"Found template '{matches[0]['template']}' in table '{matches[0]['table']}'"
            else:
                message = f"Found {len(matches)} matching templates across {len(set(m['table'] for m in matches))} tables"
            
            # Save detailed results to file
            output_path = None
            if working_path:
                os.makedirs(working_path, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"template_search_{timestamp}.json"
                output_path = os.path.join(working_path, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "query": template_keyword,
                        "matches": matches
                    }, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": message, 
                "template_matches": matches,
                "result_path": output_path
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error searching for SQL templates: {str(e)}"
            }

    @staticmethod
    def generate_sql_from_template(template_name: str, filter_values: dict = None):
        """
        Generate executable SQL query from a template name and filter values.
        This method should be called after get_table_metadata_tool to generate the actual SQL.

        Args:
            template_name (str): Name of the SQL template to use (obtained from get_table_metadata_tool)
            filter_values (dict, optional): Dictionary of filter values to apply to the template.
            Keys should match the filter column names in the template.

        Returns:
            dict: Dictionary containing:
                - status: "success" or "error"
                - message: Status message
                - sql: Generated SQL query (if successful)
                - template_info: Original template information
                - filter_values: Applied filter values (including default values)
        """
        try:
            # Convert template name to lowercase for case-insensitive matching
            template_name = template_name.strip().lower()
            
            # Get template information directly
            if template_name not in TEMPLATE_METADATA:
                available_templates = list(TEMPLATE_METADATA.keys())[:20]
                return {
                    "status": "error",
                    "message": f"Template '{template_name}' not found. Please use search_table_metadata_tool to search for valid templates first.\nAvailable templates: {', '.join(available_templates)}",
                    "available_templates": available_templates
                }

            # Get template information
            template_info = TEMPLATE_METADATA[template_name]
            template = template_info["template_info"]
            
            # Get the SQL template
            sql_template = template.get("template", "")
            if not sql_template:
                return {
                    "status": "error",
                    "message": "Template does not contain SQL definition",
                    "template_info": template
                }

            # Initialize filter_values if None
            filter_values = filter_values or {}

            # Check start_date and end_date validity
            if "start_date" in filter_values and "end_date" in filter_values:
                from datetime import datetime
                try:
                    start = datetime.strptime(filter_values["start_date"], "%Y-%m-%d")
                    end = datetime.strptime(filter_values["end_date"], "%Y-%m-%d")
                    if start >= end:
                        return {
                            "status": "error",
                            "message": "start_date must be earlier than end_date."
                        }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Invalid date format: {str(e)}"
                    }

            # Get filter_columns
            filter_columns = template_info.get("filter_columns", {})
            required_filters = template.get("required_filters", [])
            optional_filters = template.get("optional_filters", [])

            # Handle parameters and default values
            final_filter_values = {}
            # Handle required parameters first
            for filter_name in required_filters:
                if filter_name in filter_values:
                    final_filter_values[filter_name] = filter_values[filter_name]
                elif filter_name in filter_columns and "default" in filter_columns[filter_name]:
                    final_filter_values[filter_name] = filter_columns[filter_name]["default"]
                else:
                    desc = filter_columns[filter_name]["description"] if filter_name in filter_columns and "description" in filter_columns[filter_name] else filter_name
                    return {
                        "status": "error",
                        "message": f"Missing required filter: {desc}",
                        "required_filters": required_filters,
                        "template_info": template
                    }
            # Then handle optional parameters
            for filter_name in optional_filters:
                if filter_name in filter_values:
                    final_filter_values[filter_name] = filter_values[filter_name]
                elif filter_name in filter_columns and "default" in filter_columns[filter_name]:
                    final_filter_values[filter_name] = filter_columns[filter_name]["default"]

            # Apply filter values to the template
            sql = sql_template
            import re
            
            # First handle template_params if they exist
            if "template_params" in template:
                for param_name, param_func in template["template_params"].items():
                    placeholder = f"{{{param_name}}}"
                    if placeholder in sql:
                        value = param_func(final_filter_values)
                        sql = sql.replace(placeholder, value)
            
            # Then handle regular filters
            for filter_name, filter_value in final_filter_values.items():
                # replace {filter.xxx} and { filter.xxx }
                sql = re.sub(r"\{\s*filter\." + re.escape(filter_name) + r"\s*\}", str(filter_value), sql)
                # replace {xxx} and  { xxx }
                sql = re.sub(r"\{\s*" + re.escape(filter_name) + r"\s*\}", str(filter_value), sql)

            # 检查是否有未替换的占位符
            remaining_placeholders = re.findall(r"\{\s*([^}]+)\s*\}", sql)
            if remaining_placeholders:
                return {
                    "status": "error",
                    "message": f"Found unresolved placeholder(s) in SQL template: {remaining_placeholders}",
                    "unresolved_placeholders": remaining_placeholders,
                    "template_info": template
                }

            return {
                "status": "success",
                "message": f"Successfully generated SQL from template '{template_name}'",
                "sql": sql,
                "template_info": template,
                "filter_values": final_filter_values,  # Return all filter values used (including defaults)
                "used_default_values": {k: v for k, v in final_filter_values.items() if k not in filter_values}
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating SQL: {str(e)}"
            }
