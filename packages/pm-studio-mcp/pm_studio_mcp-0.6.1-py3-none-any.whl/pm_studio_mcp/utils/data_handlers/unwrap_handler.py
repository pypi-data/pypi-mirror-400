from pm_studio_mcp.utils.data_handlers.base_handler import BaseHandler
from typing import List, Dict, Any, Optional
import os
import json
import requests
import csv
import logging
from datetime import datetime, timedelta
from pm_studio_mcp.config import config

class UnwrapHandler(BaseHandler):
    """Handler for Unwrap API operations."""
    _instance = None
    _initialized = False
    
    # Product-specific team ID mapping
    TEAM_ID_MAP = {
        "Microsoft Edge": 2317,
        "Chrome": 2319
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UnwrapHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the UnwrapHandler with API credentials from environment variables."""
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        
        try:
            # Get API credentials from environment variables
            self.access_token = config.UNWRAP_ACCESS_TOKEN
            if not self.access_token:
                raise ValueError("UNWRAP_ACCESS_TOKEN environment variable is required")
                
            # Use class-level team ID mapping
            self.team_id_map = self.TEAM_ID_MAP
                
            self.working_dir = config.WORKING_PATH
            if not self.working_dir:
                self.logger.warning("WORKING_PATH environment variable is not set. Output files may not be saved correctly.")
            
            self.url = "https://data.api.production.unwrap.ai/"
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            self._initialized = True
            self.logger.info("Unwrap AI handler initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Unwrap AI handler: {str(e)}")
            # Still mark as initialized to prevent repeated init attempts
            self._initialized = True
            # Store the error for later reference
            self.init_error = str(e)

    def fetch_data(self, product_name, start_date=None, end_date=None, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from Unwrap API.
        
        Args:
            product_name (str): Name of the product to search for
            start_date: Start date for data range in format 'YYYY-MM-DD' or datetime object
            end_date: End date for data range in format 'YYYY-MM-DD' or datetime object
            **kwargs: Additional parameters including:
                - take: Number of entries (default: 100)
                - skip: Entries to skip (default: 0)
                - group_filters: Group filter objects
                - source_filters: Source filter objects
                - sources: Simple list of sources
                - fetch_all: Get all entries with pagination
            
        Returns:
            Dict with status, posts found, and output file path
        """
        # Check if there was an initialization error
        if hasattr(self, 'init_error'):
            self.logger.error(f"Cannot fetch data due to initialization error: {self.init_error}")
            return {
                "status": "error",
                "message": f"Unwrap AI handler failed to initialize: {self.init_error}",
                "data_length": 0,
                "posts_found": 0,
                "debug_info": {
                    "error_type": "InitializationError",
                    "product_name": product_name,
                    "date_range": f"{start_date} to {end_date}" if start_date and end_date else "unknown"
                }
            }
        
        if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
            # Merge nested kwargs into the main kwargs
            nested_kwargs = kwargs.pop("kwargs")
            kwargs.update(nested_kwargs)
            
        try:
            self.logger.info(f"Unwrap AI handler fetching data for product: {product_name}")
            
            # Process date parameters
            # Convert start_date to datetime if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                if isinstance(start_date, str):
                    try:
                        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                        self.logger.info(f"Using start date filter: {start_date}")
                    except ValueError:
                        self.logger.warning(f"Invalid start_date format: {start_date}. Expected format: YYYY-MM-DD")
                elif isinstance(start_date, datetime):
                    start_datetime = start_date
                    self.logger.info(f"Using start date filter: {start_date.strftime('%Y-%m-%d')}")
            else:
                # Default to 3 months ago if start_date not provided
                start_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=90)
                self.logger.info(f"Using default start date (3 months ago): {start_datetime.strftime('%Y-%m-%d')}")
            
            # Convert end_date to datetime if provided
            if end_date:
                if isinstance(end_date, str):
                    try:
                        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                        # Set end date to end of day (23:59:59)
                        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                        self.logger.info(f"Using end date filter: {end_date}")
                    except ValueError:
                        self.logger.warning(f"Invalid end_date format: {end_date}. Expected format: YYYY-MM-DD")
                elif isinstance(end_date, datetime):
                    end_datetime = end_date
                    self.logger.info(f"Using end date filter: {end_date.strftime('%Y-%m-%d')}")
            else:
                # Default to current date if end_date not provided
                end_datetime = datetime.now().replace(hour=23, minute=59, second=59)
                self.logger.info(f"Using default end date (today): {end_datetime.strftime('%Y-%m-%d')}")
                
            # Extract parameters from kwargs
            take = kwargs.get('take', 100)
            skip = kwargs.get('skip', 0)
            
            # Get product-specific team ID or use default
            team_id = self._get_team_id_for_product(product_name)
            if not team_id:
                error_msg = f"No team ID found for product '{product_name}' and no default team ID set."
                self.logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "data_length": 0,
                    "posts_found": 0,
                    "debug_info": {
                        "error_type": "MissingTeamID",
                        "product_name": product_name,
                        "available_products": list(self.team_id_map.keys()) if hasattr(self, 'team_id_map') else []
                    }
                }
            
            # Build filter input with product name and date filters
            filter_input = self._build_filter_input(
                start_date=start_datetime,
                end_date=end_datetime,
                group_filters=kwargs.get('group_filters'),
                source_filters=kwargs.get('source_filters'),
                sources=kwargs.get('sources'),
                **kwargs.get('additional_filters', {})
            )
            
            # Fetch entries
            if kwargs.get('fetch_all', True):
                self.logger.info("Using fetch_all=True to get all entries with pagination...")
                entries = self._fetch_all_entries(filter_input, team_id)
                self.logger.info(f"Found {len(entries)} total entries")
            else:
                self.logger.info(f"Using single fetch with take={take}, skip={skip}...")
                entries = self._get_entries(take, skip, filter_input, team_id)
                self.logger.info(f"Found {len(entries)} entries")
            
            # Generate date suffix for filenames
            date_suffix = ""
            if start_datetime and end_datetime:
                start_str = start_datetime.strftime('%Y%m%d')
                end_str = end_datetime.strftime('%Y%m%d')
                date_suffix = f"_{start_str}_to_{end_str}"
            
            # Process and save results
            if self.working_dir and entries:
                # Create filename with product name and date range
                filename = f"unwrap_{product_name.replace(' ', '_')}{date_suffix}.csv"
                output_path = os.path.join(self.working_dir, filename)
                
                # Save entries to CSV
                with open(output_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=entries[0].keys())
                    writer.writeheader()
                    writer.writerows(entries)
                
                self.logger.info(f"Successfully saved {len(entries)} entries to {output_path}")
                
                return {
                    "status": "success",
                    "data_length": len(entries),
                    "posts_found": len(entries),  # For compatibility with other handlers
                    "output_file": os.path.abspath(output_path),
                    "date_filtering": "enabled",
                    "date_range_used": {
                        "start_date": start_datetime.strftime('%Y-%m-%d'),
                        "end_date": end_datetime.strftime('%Y-%m-%d')
                    }
                }
            else:
                return {
                        "status": "failure",
                        "data_length": 0,
                        "posts_found": 0,
                        "message": f"No entries found for '{product_name}' with the specified filters",
                        "debug_info": {
                            "product_name": product_name,
                            "team_id": team_id,
                            "filter_input": filter_input,
                            "date_filtering": "enabled",
                            "date_range_used": {
                                "start_date": start_datetime.strftime('%Y-%m-%d'),
                                "end_date": end_datetime.strftime('%Y-%m-%d')
                            }
                        }
                    }
                
        except Exception as e:
            # Sanitize error message to ensure no sensitive info is exposed
            error_msg = str(e)
            if "access_token" in error_msg.lower() or "authorization" in error_msg.lower():
                error_msg = "Authentication error - please check Unwrap AI credentials"
            
            # Create more detailed debugging information
            debug_dict = {
                "product_name": product_name,
                "error_details": str(e),
                "error_type": type(e).__name__,
                "date_filtering": "enabled",
                "date_range_used": {
                    "start_date": start_datetime.strftime('%Y-%m-%d') if start_datetime else None,
                    "end_date": end_datetime.strftime('%Y-%m-%d') if end_datetime else None
                },
                "unwrap_setup": {
                    "access_token_configured": bool(self.access_token),
                    "working_dir_configured": bool(self.working_dir),
                    "product_team_id_mapping": bool(hasattr(self, 'team_id_map') and self.team_id_map),
                    "team_id_used": team_id
                },
                "search_parameters": {
                    "sources": kwargs.get('sources', []),
                    "fetch_all": kwargs.get('fetch_all', False),
                    "take": kwargs.get('take', 100),
                    "skip": kwargs.get('skip', 0)
                }
            }
            
            self.logger.error(f"Error in Unwrap AI handler fetch_data: {error_msg}")
            self.logger.debug(f"Debug info: {json.dumps(debug_dict, indent=2)}")
            
            return {
                "status": "error",
                "message": f"Error fetching Unwrap data: {error_msg}",
                "data_length": 0,
                "posts_found": 0,
                "debug_info": debug_dict
            }
    
    def _get_entries(self, take: int = 100, skip: int = 0, filter_input: Optional[Dict] = None, team_id: int = None) -> List[Dict]:
        """
        Get entries for a team.
        
        Args:
            take: Number of entries to fetch (max 100)
            skip: Number of entries to skip
            filter_input: Optional filters
            team_id: Team ID to use for the request
            
        Returns:
            List of feedback entries
        """
        if team_id is None:
            return []
        # Log what we're searching for to help with debugging
        source_filter = filter_input.get('sourceFitler', [])
        group_filter = filter_input.get('groupFilter', [])
        
        self.logger.info(f"Unwrap search parameters:")
        self.logger.info(f" - Team ID: {team_id}")
        
        # Check if date filters are being used
        if 'startDate' in filter_input or 'endDate' in filter_input:
            start_date_str = filter_input.get('startDate', 'None')
            end_date_str = filter_input.get('endDate', 'None')
            self.logger.info(f" - Date filters: Enabled (Start: {start_date_str}, End: {end_date_str})")
        else:
            self.logger.info(f" - Date filters: None provided")
            
        self.logger.info(f" - Source filters: {json.dumps(source_filter, indent=2)}")
        if group_filter:
            self.logger.info(f" - Group filters: {json.dumps(group_filter, indent=2)}")
        self.logger.info(f" - Take: {take}, Skip: {skip}")
        self.logger.debug(f" - Full filter_input: {json.dumps(filter_input, indent=2)}")
        
        # Query from sample_unwrap_query.md - complete field set
        query = """
        query Entries($teamId: Int!, $filterInput: FilterInput, $take: Int, $skip: Int) {
            entries(teamId: $teamId, filterInput: $filterInput, take: $take, skip: $skip) {
                allGroupTitles
                source
                text
                date
                id
                source_permalink
                feedbackEntryText {
                    displayText
                }
                title
                stars
                sentiment
                submitter
                sentences {
                    text
                }
            }
        }
        """
        
        variables = {
            "teamId": team_id,  # Use product-specific team ID
            "take": take,
            "filterInput": filter_input or {},
            "skip": skip
        }
        
        # Standard GraphQL request structure
        data = {"query": query, "variables": variables}
        
        try:
            self.logger.info(f"Sending GraphQL request to Unwrap AI API")
            self.logger.info(f"Request variables: teamId={variables['teamId']}, take={variables['take']}, skip={variables['skip']}")
            self.logger.debug(f"Full GraphQL query:\n{query}")
            self.logger.debug(f"Full variables: {json.dumps(variables, indent=2)}")
            
            response = requests.post(url=self.url, json=data, headers=self.headers)
            
            # Log response status for debugging
            self.logger.info(f"Response status code: {response.status_code}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Try to parse the response as JSON
            try:
                result = response.json()
                self.logger.info(f"Response status code: {response.status_code}")
                self.logger.info(f"Response content type: {response.headers.get('Content-Type', 'unknown')}")
                self.logger.debug(f"Response size: {len(response.content)} bytes")
                
                if "errors" in result:
                    error_details = result.get('errors', [])
                    self.logger.error(f"GraphQL errors: {json.dumps(error_details, indent=2)}")
                    error_message = error_details[0].get('message', 'Unknown GraphQL error') if error_details else 'Unknown GraphQL error'
                    self.logger.error(f"Primary error message: {error_message}")
                    return []
                
                # Get the entries from the response
                entries = result.get("data", {}).get("entries", [])
                self.logger.info(f"Found {len(entries)} entries in response")
                
                # Log some info about the first entry for debugging if entries exist
                if entries:
                    self.logger.debug(f"First entry ID: {entries[0].get('id', 'unknown')}")
                    self.logger.debug(f"First entry source: {entries[0].get('source', 'unknown')}")
                    if 'date' in entries[0]:
                        self.logger.debug(f"First entry date: {entries[0].get('date', 'unknown')}")
                    if 'text' in entries[0]:
                        text_preview = entries[0].get('text', '')[:100] + '...' if len(entries[0].get('text', '')) > 100 else entries[0].get('text', '')
                        self.logger.debug(f"First entry text preview: {text_preview}")
                
                return entries
                
            except json.JSONDecodeError as json_err:
                self.logger.error(f"Failed to parse response as JSON: {json_err}")
                self.logger.error(f"Response status code: {response.status_code}")
                self.logger.error(f"Response headers: {dict(response.headers)}")
                self.logger.debug(f"Raw response content preview: {response.content[:200].decode('utf-8', errors='replace')}...")
                return []
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network request error: {e}")
            self.logger.error(f"Request details: URL={self.url}, TeamID={team_id}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response status code: {e.response.status_code}")
                self.logger.error(f"Response headers: {dict(e.response.headers)}")
                self.logger.debug(f"Response content: {e.response.content[:200].decode('utf-8', errors='replace')}...")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in _get_entries: {str(e)}")
            return []
    
    def _fetch_all_entries(self, filter_input: Dict = None, team_id: int = None) -> List[Dict]:
        """
        Fetch all entries with pagination.
        
        Args:
            filter_input: Filters to apply
            team_id: Team ID to use for the request
            
        Returns:
            List of all matching entries
        """
        page_size = 100
        index = 0
        has_results = True
        accumulated_results = []
        
        self.logger.info(f"Starting paginated fetch with team_id={team_id}")
        self.logger.info(f"Page size: {page_size}, will continue until empty page or limit reached")
        
        while has_results:
            self.logger.info(f"Fetching page {index + 1} with {page_size} entries per page (skip={index * page_size})")
            results = self._get_entries(
                take=page_size, 
                skip=index * page_size,
                filter_input=filter_input,
                team_id=team_id
            )
            
            self.logger.info(f"Page {index + 1}: Retrieved {len(results)} entries")
            index += 1
            accumulated_results.extend(results)
            
            if len(results) == 0:
                self.logger.info("No more results found, ending pagination")
                has_results = False
            elif len(results) < page_size:
                self.logger.info(f"Received fewer results ({len(results)}) than requested ({page_size}), likely at end of data")
            
            # Safety check to prevent infinite loops
            if index > 100:
                self.logger.warning("Reached maximum page limit (100). Breaking loop to prevent infinite pagination.")
                has_results = False
                
        self.logger.info(f"Total entries fetched across all {index} pages: {len(accumulated_results)}")
        return accumulated_results
    
    def _save_to_csv(self, entries: List[Dict], working_dir: str) -> str:
        """
        Save entries to CSV file.
        
        Args:
            entries: List of entries to save
            working_dir: Directory to save the file
            
        Returns:
            Path to the saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unwrap_entries_{timestamp}.csv"
            output_file = os.path.join(working_dir, filename)
            
            # Ensure working directory exists
            os.makedirs(working_dir, exist_ok=True)
            
            self.logger.info(f"Saving {len(entries)} entries to CSV at {output_file}")
            
            if entries:
                # Flatten the nested structure for CSV based on sample query fields
                flattened_entries = []
                for entry in entries:
                    feedback_text = entry.get('feedbackEntryText', {})
                    sentences = entry.get('sentences', [])
                    sentence_texts = [s.get('text', '') for s in sentences] if sentences else []
                    
                    # Format date to CSV-friendly format (YYYY-MM-DD HH:MM:SS)
                    raw_date = entry.get('date', '')
                    formatted_date = ''
                    if raw_date:
                        try:
                            # Convert Unix timestamp in milliseconds to readable date
                            timestamp = int(raw_date) / 1000  # Convert milliseconds to seconds
                            parsed_date = datetime.fromtimestamp(timestamp)
                            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        except (ValueError, TypeError, OSError):
                            formatted_date = str(raw_date)  # Keep original if parsing fails
                    
                    flattened_entry = {
                        'all_group_titles': entry.get('allGroupTitles', ''),
                        'source': entry.get('source', ''),
                        'text': entry.get('text', ''),
                        'date': formatted_date,
                        'id': entry.get('id'),
                        'source_permalink': entry.get('source_permalink', ''),
                        'display_text': feedback_text.get('displayText', ''),
                        'title': entry.get('title', ''),
                        'stars': entry.get('stars', ''),
                        'sentiment': entry.get('sentiment', ''),
                        'submitter': entry.get('submitter', ''),
                        'sentence_texts': ' | '.join(sentence_texts) if sentence_texts else ''
                    }
                    flattened_entries.append(flattened_entry)
                
                self.logger.debug(f"Flattened {len(flattened_entries)} entries for CSV writing")
                
                with open(output_file, 'w', newline='', encoding='utf-8') as file:
                    if flattened_entries:
                        writer = csv.DictWriter(file, fieldnames=flattened_entries[0].keys())
                        writer.writeheader()
                        writer.writerows(flattened_entries)
                        self.logger.info(f"Successfully wrote {len(flattened_entries)} rows to CSV file")
            else:
                # Create empty CSV with headers
                self.logger.warning("No entries to save, creating empty CSV with headers")
                with open(output_file, 'w', newline='', encoding='utf-8') as file:
                    headers = ['id', 'all_group_titles', 'source', 'text', 'date', 'source_permalink', 
                              'display_text', 'title', 'stars', 'sentiment', 'submitter', 'sentence_texts']
                    writer = csv.DictWriter(file, fieldnames=headers)
                    writer.writeheader()
            
            self.logger.info(f"CSV file saved to: {output_file}")
            return os.path.abspath(output_file)
            
        except Exception as e:
            self.logger.error(f"CSV save failed with error: {str(e)}")
            
            # If CSV save fails, save as JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"unwrap_entries_{timestamp}.json"
            json_output_file = os.path.join(working_dir, json_filename)
            
            self.logger.info(f"Falling back to JSON save with {len(entries)} entries")
            try:
                with open(json_output_file, 'w', encoding='utf-8') as file:
                    json.dump(entries, file, indent=2, default=str)
                
                self.logger.info(f"JSON fallback file saved to: {json_output_file}")
                return os.path.abspath(json_output_file)
            except Exception as json_err:
                self.logger.error(f"JSON fallback save also failed: {str(json_err)}")
                raise

    def get_entries_by_source(self, data_source: str, working_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get entries filtered by a specific data source.
        
        Args:
            data_source: Source to filter by (e.g., "reddit", "twitter", "gplay", "appstore")
            working_dir: Directory to save output files
            **kwargs: Additional options (take, skip, fetch_all, start_date, end_date, etc.)
            
        Returns:
            Dict with filtered entries data
            
        Examples:
            handler.get_entries_by_source("reddit")  # First 100 entries
            handler.get_entries_by_source("twitter", take=50)  # Specific number
            handler.get_entries_by_source("gplay", fetch_all=True)  # All entries
        """
        return self.fetch_data(
            working_dir=working_dir,
            additional_filters={'dataSource': data_source},
            **kwargs
        )
    
    def _get_team_id_for_product(self, product_name: str) -> int:
        """
        Get the Unwrap team ID for a specific product.
        
        Args:
            product_name (str): Name of the product
            
        Returns:
            int: Team ID for the product, or default team ID if not found
        """
        if not product_name:
            self.logger.warning("No product name provided, using default team ID")
            return self.default_team_id
            
        # Try exact match
        if hasattr(self, 'team_id_map') and product_name in self.team_id_map:
            team_id = self.team_id_map[product_name]
            print(f"Found team ID {team_id} for product '{product_name}' (exact match)", flush=True)
            self.logger.info(f"Found team ID {team_id} for product '{product_name}' (exact match)")
            return team_id
            
        # Try case-insensitive match
        if hasattr(self, 'team_id_map'):
            for mapped_name, team_id in self.team_id_map.items():
                if mapped_name.lower() == product_name.lower():
                    self.logger.info(f"Found team ID {team_id} for product '{product_name}' (case-insensitive match)")
                    return team_id
                    
            # Try partial match (when product name is a substring of a mapped name or vice versa)
            for mapped_name, team_id in self.team_id_map.items():
                if mapped_name.lower() in product_name.lower() or product_name.lower() in mapped_name.lower():
                    self.logger.info(f"Found team ID {team_id} for product '{product_name}' (partial match with '{mapped_name}')")
                    return team_id
        
        # Fallback to default team ID
        if hasattr(self, 'default_team_id') and self.default_team_id:
            self.logger.warning(f"No team ID mapping found for '{product_name}', using default team ID: {self.default_team_id}")
            return self.default_team_id
            
        self.logger.error(f"No team ID found for product '{product_name}' and no default team ID set")
        return None
    
    def _build_filter_input(self, start_date: datetime = None, end_date: datetime = None, 
                           group_filters: List[Dict] = None, 
                           source_filters: List[Dict] = None, sources: List[str] = None, 
                           **additional_filters) -> Dict[str, Any]:
        """
        Build filter input for GraphQL query.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            group_filters: Group filter objects
                Example: [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            source_filters: Source filter objects
                Example: [{"filterCondition": "OR", "sources": ["reddit", "twitter"]}]
            sources: Simple list of sources (converted to source_filters)
                Example: ["reddit", "twitter", "gplay", "appstore"]
            **additional_filters: Additional filter parameters
            
        Returns:
            Dictionary with filter input for GraphQL query
        """
        filter_input = {}
        
        # Enable date filters using ISO 8601 format with Z suffix (UTC)
        if start_date:
            # Format as ISO 8601 with Z suffix (UTC timezone)
            filter_input['startDate'] = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            self.logger.info(f"Using start date filter: {filter_input['startDate']}")
            
        if end_date:
            # Format as ISO 8601 with Z suffix (UTC timezone)
            filter_input['endDate'] = end_date.strftime('%Y-%m-%dT%H:%M:%S.999Z')
            self.logger.info(f"Using end date filter: {filter_input['endDate']}")
            
        # Add group filters
        if group_filters:
            filter_input['groupFilter'] = group_filters
            self.logger.info(f"Using group filters: {group_filters}")
            
        # Add source filters (note: API uses "sourceFitler" typo)
        if source_filters:
            filter_input['sourceFitler'] = source_filters
            self.logger.info(f"Using custom source filters: {source_filters}")
        elif sources:
            # Convert simple sources list to filter format
            filter_input['sourceFitler'] = [{
                "filterCondition": "OR",
                "sources": sources
            }]
            self.logger.info(f"Filtering by sources: {sources}")
        
        # Add additional filters
        if additional_filters:
            self.logger.info(f"Adding additional filters: {additional_filters}")
            filter_input.update(additional_filters)
            
        return filter_input

    def _build_fields_query(self, fields: List[str] = None) -> str:
        """
        Build the fields portion of the GraphQL query.
        
        Args:
            fields: List of field names to include. If None, uses default fields.
            
        Returns:
            String containing the fields portion of the GraphQL query
        """
        # Default fields if none specified
        default_fields = [
            'id',
            'feedbackEntryText { displayText }',
            'date',
            'source'
        ]
        
        # Available fields from the sample query
        available_fields = {
            'allGroupTitles': 'allGroupTitles',
            'source': 'source', 
            'text': 'text',
            'date': 'date',
            'id': 'id',
            'source_permalink': 'source_permalink',
            'feedbackEntryText': 'feedbackEntryText { displayText }',
            'title': 'title',
            'stars': 'stars',
            'sentiment': 'sentiment',
            'submitter': 'submitter',
            'sentences': 'sentences { text }'
        }
        
        if fields is None:
            return '\n            '.join(default_fields)
        
        # Validate and build field list
        query_fields = []
        for field in fields:
            if field in available_fields:
                query_fields.append(available_fields[field])
            else:
                print(f"Warning: Unknown field '{field}' ignored")
        
        return '\n            '.join(query_fields) if query_fields else '\n            '.join(default_fields)
    
    def get_entries_by_sources(self, sources: List[str], working_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get entries filtered by multiple sources.
        
        Args:
            sources: List of sources to filter by (e.g., ["reddit", "twitter", "gplay", "appstore"])
            working_dir: Directory to save output files
            **kwargs: Additional parameters (take, skip, fetch_all, start_date, end_date, etc.)
            
        Returns:
            Dict with filtered entries data
            
        Examples:
            handler.get_entries_by_sources(["reddit", "twitter"])  # Social media
            handler.get_entries_by_sources(["gplay", "appstore"])  # App stores
            handler.get_entries_by_sources(["reddit", "twitter"], start_date=datetime(2025, 6, 1))
        """
        return self.fetch_data(
            working_dir=working_dir,
            sources=sources,
            **kwargs
        )
    
    def get_entries_by_date_range(self, start_date: datetime, end_date: datetime, 
                                 working_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get entries within a specific date range.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            working_dir: Directory to save output files
            **kwargs: Additional parameters (sources, group_filters, take, skip, fetch_all, etc.)
            
        Returns:
            Dict with filtered entries data
            
        Examples:
            # Last 30 days
            handler.get_entries_by_date_range(
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now()
            )
            
            # Specific month with sources
            handler.get_entries_by_date_range(
                start_date=datetime(2025, 6, 1),
                end_date=datetime(2025, 6, 30),
                sources=["reddit", "twitter"]
            )
        """
        return self.fetch_data(
            start_date=start_date,
            end_date=end_date,
            working_dir=working_dir,
            **kwargs
        )
    
    def get_entries_with_group_filters(self, group_filters: List[Dict], working_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get entries filtered by group membership.
        
        Args:
            group_filters: List of group filter objects
                Example: [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            working_dir: Directory to save output files
            **kwargs: Additional parameters (sources, start_date, end_date, take, skip, fetch_all, etc.)
            
        Returns:
            Dict with filtered entries data
            
        Examples:
            # Single group
            group_filters = [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            handler.get_entries_with_group_filters(group_filters)
            
            # Multiple groups (any match)
            group_filters = [{
                "group": [{"id": 11764027}, {"id": 11764107}],
                "filterCondition": "OR"
            }]
            handler.get_entries_with_group_filters(group_filters)
        """
        return self.fetch_data(
            working_dir=working_dir,
            group_filters=group_filters,
            **kwargs
        )
    
    def get_entries_with_advanced_filters(self, sources: List[str] = None, 
                                        group_filters: List[Dict] = None,
                                        start_date: datetime = None, 
                                        end_date: datetime = None,
                                        working_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Get entries with advanced filtering combining multiple filter types.
        
        Args:
            sources: List of feedback sources
            group_filters: List of group filter objects
            start_date: Start date for filtering
            end_date: End date for filtering
            working_dir: Directory to save output files
            **kwargs: Additional parameters (take, skip, fetch_all, etc.)
            
        Returns:
            Dict with comprehensive filtered entries data
            
        Examples:
            # Product launch analysis
            handler.get_entries_with_advanced_filters(
                sources=["gplay", "appstore"],
                group_filters=[{"group": [{"id": 11764027}], "filterCondition": "OR"}],
                start_date=datetime(2025, 6, 1),
                end_date=datetime(2025, 6, 7),
                fetch_all=True
            )
            
            # Crisis monitoring
            handler.get_entries_with_advanced_filters(
                sources=["reddit", "twitter"],
                start_date=datetime(2025, 6, 10),
                end_date=datetime(2025, 6, 12),
                fetch_all=True
            )
        """
        return self.fetch_data(
            start_date=start_date,
            end_date=end_date,
            working_dir=working_dir,
            sources=sources,
            group_filters=group_filters,
            **kwargs        )
        
    def validate_output_files(self, working_dir: str) -> Dict[str, Any]:
        """
        Validate and compare output files in the working directory.
        
        Args:
            working_dir: Directory containing output files
            
        Returns:
            Dict with file analysis results
        """
        try:
            import glob
            import pandas as pd
            
            # Find all unwrap output files
            csv_files = glob.glob(os.path.join(working_dir, "unwrap_entries_*.csv"))
            json_files = glob.glob(os.path.join(working_dir, "unwrap_source_analysis_*.json"))
            json_entry_files = glob.glob(os.path.join(working_dir, "unwrap_entries_*.json"))
            
            results = {
                "status": "success",
                "csv_files": [],
                "json_analysis_files": [],
                "json_entry_files": [],
                "discrepancies": []
            }
            
            # Analyze CSV files
            for csv_file in csv_files:
                try:
                    if pd:
                        df = pd.read_csv(csv_file)
                        row_count = len(df)
                    else:
                        # Fallback without pandas
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            row_count = sum(1 for line in f) - 1  # Subtract header
                    
                    file_info = {
                        "file": os.path.basename(csv_file),
                        "path": csv_file,
                        "row_count": row_count,
                        "size_bytes": os.path.getsize(csv_file)
                    }
                    results["csv_files"].append(file_info)
                    print(f"CSV Analysis: {os.path.basename(csv_file)} has {row_count} rows")
                    
                except Exception as e:
                    print(f"Error analyzing CSV {csv_file}: {e}")
            
            # Analyze JSON analysis files
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    file_info = {
                        "file": os.path.basename(json_file),
                        "path": json_file,
                        "total_entries": data.get("total_entries", 0),
                        "size_bytes": os.path.getsize(json_file)
                    }
                    results["json_analysis_files"].append(file_info)
                    print(f"JSON Analysis: {os.path.basename(json_file)} reports {data.get('total_entries', 0)} total entries")
                    
                except Exception as e:
                    print(f"Error analyzing JSON analysis file {json_file}: {e}")
            
            # Analyze JSON entry files (raw data)
            for json_file in json_entry_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    entry_count = len(data) if isinstance(data, list) else 0
                    file_info = {
                        "file": os.path.basename(json_file),
                        "path": json_file,
                        "entry_count": entry_count,
                        "size_bytes": os.path.getsize(json_file)
                    }
                    results["json_entry_files"].append(file_info)
                    print(f"JSON Entries: {os.path.basename(json_file)} contains {entry_count} entries")
                    
                except Exception as e:
                    print(f"Error analyzing JSON entry file {json_file}: {e}")
            
            # Check for discrepancies
            for csv_info in results["csv_files"]:
                csv_count = csv_info["row_count"]
                csv_time = csv_info["file"].split("_")[-1].replace(".csv", "")
                
                # Look for corresponding JSON analysis files with similar timestamps
                for json_info in results["json_analysis_files"]:
                    json_count = json_info["total_entries"]
                    json_time = json_info["file"].split("_")[-1].replace(".json", "")
                    
                    # Check if timestamps are close (within same minute)
                    if abs(int(csv_time) - int(json_time)) < 100:  # Within same minute
                        if csv_count != json_count:
                            discrepancy = {
                                "csv_file": csv_info["file"],
                                "csv_count": csv_count,
                                "json_file": json_info["file"],
                                "json_count": json_count,
                                "difference": json_count - csv_count,
                                "likely_cause": "fetch_all=False vs fetch_all=True or CSV writing error"
                            }
                            results["discrepancies"].append(discrepancy)
                            print(f"⚠ DISCREPANCY: {csv_info['file']} has {csv_count} rows but {json_info['file']} reports {json_count} entries")
            
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error validating output files: {e}"            
            }

# Usage Examples
"""
UNWRAP HANDLER - USAGE EXAMPLES

Basic Setup:
from unwrap_handler import UnwrapHandler
from datetime import datetime, timedelta

handler = UnwrapHandler()
working_dir = "./output"

Simple Queries:
result = handler.fetch_data(working_dir=working_dir)  # Default: 100 entries
result = handler.get_entries_by_source("reddit", working_dir=working_dir)
result = handler.get_entries_by_source("reddit", fetch_all=True)  # All entries

Date Range:
result = handler.get_entries_by_date_range(
    start_date=datetime(2025, 6, 1),
    end_date=datetime(2025, 6, 30),
    sources=["reddit", "twitter"]
)

Advanced Filtering:
result = handler.get_entries_with_advanced_filters(
    sources=["gplay", "appstore"],
    group_filters=[{"group": [{"id": 11764027}], "filterCondition": "OR"}],
    start_date=datetime(2025, 6, 1),
    end_date=datetime(2025, 6, 7)
)
"""

if __name__ == "__main__":
    # Check environment variables
    unwrap_token = os.environ.get('UNWRAP_ACCESS_TOKEN')
    team_id = os.environ.get('UNWRAP_TEAM_ID')
    working_dir = os.environ.get('WORKING_DIR', '.')
    
    if not unwrap_token or not team_id:
        print("Error: UNWRAP_ACCESS_TOKEN and UNWRAP_TEAM_ID environment variables required")
        exit(1)
    
    try:
        handler = UnwrapHandler()
        
        # Sample query from sample_unwrap_query.md
        from datetime import datetime
        
        filter_input = {
            "startDate": "2025-06-01T07:00:00.000Z",
            "endDate": "2025-06-15T06:59:59.999Z",
            "groupFilter": [{
                "group": [{"id": 11764027}, {"id": 11764107}, {"id": 11722593}],
                "filterCondition": "OR"
            }],
            "sourceFitler": [{
                "filterCondition": "OR",
                "sources": ["reddit", "twitter", "gplay", "appstore"]
            }]
        }
        
        # Convert dates
        start_date = datetime.fromisoformat("2025-06-01T07:00:00.000Z".replace('Z', '+00:00'))
        end_date = datetime.fromisoformat("2025-06-15T06:59:59.999Z".replace('Z', '+00:00'))
          # Test fetch_all to get ALL matching entries
        result = handler.fetch_data(
            start_date=start_date,
            end_date=end_date,
            group_filters=filter_input["groupFilter"],
            source_filters=filter_input["sourceFitler"],
            working_dir=working_dir,
            fetch_all=True  # Get all entries with pagination
        )
        
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")