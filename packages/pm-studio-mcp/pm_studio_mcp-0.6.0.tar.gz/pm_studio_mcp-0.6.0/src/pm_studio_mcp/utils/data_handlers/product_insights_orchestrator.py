from typing import List, Dict, Any, Union
import logging

# Import data handlers
from pm_studio_mcp.utils.data_handlers.dataai_handler import DataAIHandler
from pm_studio_mcp.utils.data_handlers.reddit_handler import RedditHandler
from pm_studio_mcp.utils.data_handlers.unwrap_handler import UnwrapHandler
from pm_studio_mcp.utils.data_handlers.google_ads_handler import GoogleAdsHandler
# Uncomment and implement other handlers as needed
# from pm_studio_mcp.utils.data_handlers.chromium_handler import ChromiumReleaseNoteHandler


class ProductInsightsOrchestrator:
    """
    Orchestrates the fetching of product insights from various data sources.
    This class handles the selection and coordination of different data handlers
    based on the insight goal.
    """
    
    def __init__(self):
        """Initialize the orchestrator with available data handlers."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize available handlers
        self.handlers = {}
        self._initialize_handlers()
        
        # Define default sources to use when no match is found
        self.default_sources = list(self.handlers.keys())
        
    def _initialize_handlers(self):
        """Initializes all available handlers, catching and logging any initialization errors."""
        handler_classes = {
            "data_ai": DataAIHandler,
            "reddit": RedditHandler,
            "unwrap_ai": UnwrapHandler,
            # Uncomment when these handlers are implemented
            # "chromium": ChromiumReleaseNoteHandler,
            "google_ads": GoogleAdsHandler,  # 已集成 Google Ads Handler
        }
        
        for name, handler_class in handler_classes.items():
            try:
                self.handlers[name] = handler_class()
                self.logger.info(f"Successfully initialized {name} handler")
            except Exception as e:
                init_error = str(e)
                self.logger.warning(f"Failed to initialize {name} handler: {init_error}")
                
    
    def determine_sources(self, goal: str, target_platform: str = None) -> List[str]:
        """
        Determine which data sources to use based on the insight goal and/or target platform.
        
        Args:
            goal (str): The type of insight desired (e.g., "user_sentiment", "campaign_analysis", "chrome_update")
            target_platform (str, optional): Specific platform to target (e.g., "reddit", "data ai")
            
        Returns:
            List[str]: List of source identifiers to query
        """
        # Sanitize inputs
        if not goal and not target_platform:
            self.logger.warning("Both goal and target_platform are empty or None, using default sources")
            return [src for src in self.default_sources if src in self.handlers]
            
        available_sources = set(self.handlers.keys())
        selected_sources = []
        
        # Create a mapping of platform variations to standardized keys
        platform_mapping = {
            # Unwrap AI variations
            "unwrap": "unwrap_ai",
            "unwrap ai": "unwrap_ai",
            "unwrapai": "unwrap_ai",
            
            # Reddit variations
            "reddit": "reddit",
            "subreddit": "reddit",
            "r/": "reddit",
            
            # Data.ai variations
            "data.ai": "data_ai", 
            "data ai": "data_ai",
            "dataai": "data_ai",
            "app store": "data_ai",
            "play store": "data_ai",
            "app reviews": "data_ai",
            "store reviews": "data_ai",
            "mobile reviews": "data_ai",
            
            # Chromium variations
            "chromium": "chromium",
            "chrome": "chromium",
            "chrome update": "chromium",
            "release notes": "chromium",
            "browser update": "chromium",
            
            # Google Ads variations
            "google ads": "google_ads",
            "googleads": "google_ads",
            "adwords": "google_ads",
            "ads": "google_ads",
            "campaign": "google_ads",
            "marketing": "google_ads"
        }
        
        # First check if a specific platform is requested
        if target_platform:
            # Normalize input
            platform = target_platform.lower().strip()
            
            # Try to match the platform using exact and partial matching
            matched = False
            
            # First try exact matches
            if platform in platform_mapping:
                source = platform_mapping[platform]
                if source in available_sources:
                    selected_sources.append(source)
                    matched = True
                    self.logger.info(f"Exact match found for platform '{platform}': {source}")
                else:
                    self.logger.warning(f"Platform '{platform}' matched to source '{source}', but handler is not available")
            
            # If no exact match, try partial matches
            if not matched:
                for key, value in platform_mapping.items():
                    if key in platform or platform in key:
                        if value in available_sources:
                            selected_sources.append(value)
                            self.logger.info(f"Partial match found for platform '{platform}' via '{key}': {value}")
                            matched = True
                            break
            
            # If we found a match by platform, we may want to return just that platform
            # rather than combining with goal-based sources
            if matched:
                return list(dict.fromkeys(selected_sources))  # Remove duplicates while preserving order
        
        # If no platform specified or no match found, use goal-based determination
        if (not target_platform or not selected_sources) and goal:
            try:
                normalized_goal = goal.lower().strip()
                
                # Goal-based mapping using pattern matching
                goal_source_mapping = {
                    # User sentiment patterns
                    "sentiment": ["unwrap_ai", "reddit", "data_ai"],
                    "feedback": ["unwrap_ai", "reddit", "data_ai"],
                    "review": ["data_ai", "reddit"],
                    "rating": ["data_ai"],
                    "user opinion": ["unwrap_ai", "reddit", "data_ai"],
                    "like": ["unwrap_ai", "reddit", "data_ai"],
                    "dislike": ["unwrap_ai", "reddit", "data_ai"],
                    "user experience": ["unwrap_ai", "reddit", "data_ai"],
                    
                    # Campaign analysis patterns
                    "campaign": ["google_ads"],
                    "advertising": ["google_ads"],
                    "ads performance": ["google_ads"],
                    "marketing": ["google_ads"],
                    "promotion": ["google_ads"],
                    
                    # Chrome/update patterns
                    "chrome": ["chromium"],
                    "update": ["data_ai", "chromium"],
                    "release": ["data_ai", "chromium"],
                    "version": ["data_ai", "chromium"],
                    "feature": ["chromium", "reddit"],
                    "timeline": ["data_ai"],
                    "release notes": ["data_ai"],
                    "version history": ["data_ai"],
                    "app update": ["data_ai"],
                    "version change": ["data_ai"],
                    
                    # Download and usage history patterns - NEW
                    "download": ["data_ai"],
                    "downloads": ["data_ai"],
                    "download history": ["data_ai"],
                    "download data": ["data_ai"],
                    "download trend": ["data_ai"],
                    "usage": ["data_ai"],
                    "usage history": ["data_ai"],
                    "usage data": ["data_ai"],
                    "active users": ["data_ai"],
                    "user activity": ["data_ai"],
                    "user engagement": ["data_ai"],
                    "retention": ["data_ai"],
                    "session": ["data_ai"],
                    "session data": ["data_ai"],
                    "app performance": ["data_ai"],
                    "performance metrics": ["data_ai"],
                    "analytics": ["data_ai"],
                    "metrics": ["data_ai"],
                    "statistics": ["data_ai"],
                    "installs": ["data_ai"],
                    "install data": ["data_ai"],
                    "revenue": ["data_ai"],
                    "paid downloads": ["data_ai"],
                    "organic downloads": ["data_ai"]
                }
                
                # Exact matches that should override pattern matching
                exact_matches = {
                    "user_sentiment": ["unwrap_ai", "reddit", "data_ai"],
                    "campaign_analysis": ["google_ads"],
                    "chrome_update": ["chromium"],
                    "chrome_release_notes": ["data_ai"],
                    "firefox_release_notes": ["data_ai"], 
                    "edge_release_notes": ["data_ai"],
                    "app_reviews": ["data_ai"],
                    "browser_updates": ["chromium"],
                    "timeline": ["data_ai"],
                    "release_notes": ["data_ai"],
                    "version_history": ["data_ai"],
                    
                    # Download and usage history exact matches - NEW
                    "download_history": ["data_ai"],
                    "usage_history": ["data_ai"],
                    "download_data": ["data_ai"],
                    "usage_data": ["data_ai"],
                    "download_analytics": ["data_ai"],
                    "usage_analytics": ["data_ai"],
                    "app_performance": ["data_ai"],
                    "user_metrics": ["data_ai"],
                    "engagement_metrics": ["data_ai"],
                    "retention_analysis": ["data_ai"],
                    "download_trends": ["data_ai"],
                    "usage_trends": ["data_ai"],
                    "install_data": ["data_ai"],
                    "revenue_data": ["data_ai"],
                    "monetization": ["data_ai"]
                }
                
                # First check for exact matches
                if normalized_goal in exact_matches:
                    goal_sources = exact_matches[normalized_goal]
                    self.logger.info(f"Exact goal match found for '{normalized_goal}': {goal_sources}")
                    selected_sources.extend(goal_sources)
                else:
                    # Otherwise use pattern matching
                    for pattern, sources in goal_source_mapping.items():
                        if pattern in normalized_goal:
                            self.logger.info(f"Pattern '{pattern}' found in goal '{normalized_goal}', adding sources: {sources}")
                            selected_sources.extend(sources)
                
                # Remove duplicates while preserving order
                selected_sources = list(dict.fromkeys(selected_sources))
                
            except Exception as e:
                self.logger.error(f"Error in goal-based source determination: {str(e)}")
        
        # Default to some common data sources if nothing matched
        if not selected_sources:
            self.logger.warning(f"No sources matched for goal='{goal}', target_platform='{target_platform}'. Using default sources.")
            selected_sources = self.default_sources
        
        # Filter out sources that don't have handlers
        valid_sources = [source for source in selected_sources if source in available_sources]
        
        if not valid_sources and selected_sources:
            self.logger.warning(f"Selected sources {selected_sources} have no available handlers.")
            # Fallback to any available handlers if the selected ones aren't available
            valid_sources = list(available_sources)[:2]  # Take at most 2 available sources as fallback
            self.logger.info(f"Falling back to available sources: {valid_sources}")
        
        return valid_sources
    
    def _process_handler_result(self, result: Union[Dict, List], source_name: str) -> List[Dict]:
        """
        Process results from data handlers into a standardized format.
        
        Args:
            result: The result from a handler (dict or list of dicts)
            source_name: Name of the data source
            
        Returns:
            List of processed result dictionaries
        """
        processed_results = []
        
        try:
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict):
                        # Handle successful results with output files
                        if "output_file" in item and (
                            item.get("data_length", 0) > 0 or 
                            item.get("posts_found", 0) > 0 or
                            "success" in item.get("status", "").lower()
                        ):
                            processed_item = {
                                "source": source_name,
                                "output_file": item["output_file"],
                                "count": item.get("data_length", item.get("posts_found", 0))
                            }
                            
                            # Add debug info if available
                            if "search_stats" in item:
                                processed_item["stats"] = item["search_stats"]
                            elif "debug_info" in item:
                                processed_item["debug_info"] = item["debug_info"]
                                
                            processed_results.append(processed_item)
                        # Handle error results
                        elif "error" in item.get("status", "").lower():
                            error_msg = item.get('message', 'Unknown error')
                            debug_info = item.get('debug_info', {})
                            self.logger.warning(f"Error from {source_name}: {error_msg}")
                            if debug_info:
                                self.logger.info(f"Debug info from {source_name}: {debug_info}")
            elif isinstance(result, dict):
                # Check if there's a nested results list (especially for DataAIHandler)
                if "results" in result and isinstance(result["results"], list):
                    nested_results = result["results"]
                    for item in nested_results:
                        if isinstance(item, dict) and "output_file" in item:
                            processed_item = {
                                "source": source_name,
                                "output_file": item["output_file"],
                                "count": item.get("data_length", item.get("posts_found", 0))
                            }
                            processed_results.append(processed_item)
                    
                    # If we processed nested results successfully, return them
                    if processed_results:
                        self.logger.info(f"Processed {len(processed_results)} nested results from {source_name}")
                        return processed_results
                
                # Handle successful results with output files
                if "output_file" in result and (
                    result.get("data_length", 0) > 0 or 
                    result.get("posts_found", 0) > 0 or
                    "success" in result.get("status", "").lower()
                ):
                    processed_item = {
                        "source": source_name,
                        "output_file": result["output_file"],
                        "count": result.get("data_length", result.get("posts_found", 0))
                    }
                    
                    # Add stats if available
                    if "search_stats" in result:
                        processed_item["stats"] = result["search_stats"]
                    
                    processed_results.append(processed_item)
                    self.logger.info(f"Processed {processed_item['count']} results from {source_name}")
                    
                # Handle error results
                elif "error" in result.get("status", "").lower():
                    error_msg = result.get("message", "Unknown error")
                    debug_info = result.get("debug_info", {})
                    self.logger.warning(f"Error from {source_name}: {error_msg}")
                    if debug_info:
                        self.logger.info(f"Debug info from {source_name}: {debug_info}")
                        
                # Handle empty results
                elif result.get("data_length", 0) == 0 or result.get("posts_found", 0) == 0:
                    debug_info = result.get("debug_info", {})
                    self.logger.info(f"No data found from {source_name}")
                    if debug_info:
                        self.logger.info(f"Debug info from {source_name}: {debug_info}")
                    
                    # Despite no results, include it in processed_results with count=0 
                    # if there's an output_file (some handlers might create empty files)
                    if "output_file" in result:
                        processed_results.append({
                            "source": source_name,
                            "output_file": result["output_file"],
                            "count": 0,
                            "message": result.get("message", "No data found")
                        })
        except Exception as e:
            self.logger.error(f"Error processing result from {source_name}: {str(e)}")
            
        return processed_results
    
    def fetch_insights(self, product_name: str, goal: str = "user_sentiment", 
                       start_date: str = None, end_date: str = None, 
                       target_platform: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch product insights from appropriate sources based on goal and target platform.
        
        Args:
            product_name (str): The product name to analyze (e.g., "Microsoft Edge", "Chrome")
            goal (str): Insight goal (e.g., "user_sentiment", "campaign_analysis", "download_history", "usage_history")
            start_date (str, optional): Start date for data in format 'YYYY-MM-DD'. Defaults to 3 months ago if not provided.
            end_date (str, optional): End date for data in format 'YYYY-MM-DD'. Defaults to current date if not provided.
            target_platform (str, optional): Specific platform to target, currently supports "reddit", "data ai", "unwrap ai". If social media platform is mentioned, then use "unwrap ai".
            kwargs: Additional parameters for specific handlers
                - keywords: List of keywords for filtering data for Reddit
                - subreddit_name: Name of the subreddit to scrape for Reddit
                - post_limit: Maximum number of posts to retrieve for Reddit
                - time_filter: Time filter for Reddit posts
                - device: Device to analyze ("ios", "android", "desktop", "all") for DataAI
                - target_data_type: Type of data to fetch ("reviews", "ratings", "metadata", "timeline", "download_history", "usage_history") for DataAI
                - sources: List of sources to filter by for Unwrap AI (e.g., ["reddit", "twitter", "gplay", "appstore"])
                - group_filters: Group filter objects for Unwrap AI filtering by group membership
                    Example: [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            
        Returns:
            dict: Dictionary containing:
                - status: "success", "partial_success", "warning", or "error"
                - goal: The insight goal
                - product: The product name
                - results: List of results from different data sources
        """
        try:
            # Parse dates based on the provided parameters
            from datetime import datetime, timedelta
            
            # Default: If no dates provided, use last 3 months to current date
            if start_date is None:
                # Calculate 3 months ago
                three_months_ago = datetime.now() - timedelta(days=90)
                start_date = three_months_ago.strftime('%Y-%m-%d')
                self.logger.info(f"Using default start date (3 months ago): {start_date}")
            else:
                self.logger.info(f"Using provided start date: {start_date}")
                
            if end_date is None:
                # Use current date
                end_date = datetime.now().strftime('%Y-%m-%d')
                self.logger.info(f"Using default end date (today): {end_date}")
            else:
                self.logger.info(f"Using provided end date: {end_date}")
                
            # Determine which data sources to use
            sources = self.determine_sources(goal, target_platform)
            self.logger.info(f"Using data sources: {sources} for goal: '{goal}', target_platform: '{target_platform}'")
            
            results = []
            errors = []
            search_attempts = []
            
            # Check if we have any sources to query
            if not sources:
                return {
                    "status": "warning",
                    "message": f"No valid data sources found for goal='{goal}', target_platform='{target_platform}'. No APIs configured or accessible.",
                    "goal": goal,
                    "product": product_name,
                    "date_range": f"{start_date} to {end_date}",
                    "target_platform": target_platform,
                    "sources_used": [],
                    "results": [],
                    "available_handlers": list(self.handlers.keys())
                }
            
            # Enhanced keywords handling - we'll add product-related terms if needed
            if 'keywords' in kwargs and isinstance(kwargs['keywords'], list):
                # Make sure the product name itself is included in keywords
                if product_name not in kwargs['keywords']:
                    kwargs['keywords'].append(product_name)
                
                # Try to extract product tokens for better matching
                product_tokens = product_name.split()
                for token in product_tokens:
                    if len(token) > 3 and token.lower() not in [k.lower() for k in kwargs['keywords'] if isinstance(k, str)]:
                        kwargs['keywords'].append(token)
                        
                self.logger.info(f"Enhanced keywords for search: {kwargs['keywords']}")
            
            # Fetch data from each source
            for source_name in sources:
                if source_name not in self.handlers:
                    self.logger.warning(f"Handler for source '{source_name}' not available")
                    continue
                    
                try:
                    handler = self.handlers[source_name]
                    
                    if handler is None:
                        self.logger.warning(f"Skipping handler {source_name} due to initialization error")
                        errors.append({"source": source_name, "error": "Handler not initialized, please check if you have set the required API keys."})
                        continue
                        
                    self.logger.info(f"Fetching data from {source_name} for product: {product_name}")
                    
                    # Create handler-specific kwargs
                    handler_kwargs = kwargs.copy() if kwargs else {}
                    
                    # Add some additional context that might help with debugging
                    if 'debug' not in handler_kwargs:
                        handler_kwargs['debug'] = True
                    
                    # Smart parameter mapping for DataAI Handler based on goal
                    if source_name == "data_ai":
                        normalized_goal = goal.lower().strip()
                        
                        # If goal indicates download history, set appropriate parameters
                        download_indicators = [
                            "download", "downloads", "download_history", "download_data", "download_trend",
                            "download_analytics", "download_trends", "install", "installs", "install_data"
                        ]
                        
                        # If goal indicates usage history, set appropriate parameters
                        usage_indicators = [
                            "usage", "usage_history", "usage_data", "active users", "user_activity",
                            "user_engagement", "retention", "session", "session_data", "app_performance",
                            "performance_metrics", "analytics", "metrics", "statistics", "engagement_metrics",
                            "retention_analysis", "usage_trends", "user_metrics"
                        ]
                        
                        # If goal indicates timeline/release notes, set appropriate parameters
                        timeline_indicators = [
                            "release", "version", "timeline", "release_notes", "chrome_release_notes",
                            "firefox_release_notes", "edge_release_notes", "version_history", 
                            "app_update", "version_change", "update"
                        ]
                        
                        if any(indicator in normalized_goal for indicator in download_indicators):
                            # Set target_data_type to download_history for download data
                            if 'target_data_type' not in handler_kwargs:
                                handler_kwargs['target_data_type'] = 'download_history'
                                self.logger.info(f"Setting target_data_type=download_history for goal: {goal}")
                                
                        elif any(indicator in normalized_goal for indicator in usage_indicators):
                            # Set target_data_type to usage_history for usage data
                            if 'target_data_type' not in handler_kwargs:
                                handler_kwargs['target_data_type'] = 'usage_history'
                                self.logger.info(f"Setting target_data_type=usage_history for goal: {goal}")
                                
                        elif any(indicator in normalized_goal for indicator in timeline_indicators):
                            # Set target_data_type to timeline for release notes
                            if 'target_data_type' not in handler_kwargs:
                                handler_kwargs['target_data_type'] = 'timeline'
                                self.logger.info(f"Setting target_data_type=timeline for goal: {goal}")
                            
                            # Set event_filters to version_change if not specified
                            if 'event_filters' not in handler_kwargs:
                                handler_kwargs['event_filters'] = 'version_change'
                                self.logger.info(f"Setting event_filters=version_change for timeline data")
                                
                        # Default to reviews if no specific data type specified
                        elif 'target_data_type' not in handler_kwargs:
                            handler_kwargs['target_data_type'] = 'reviews'
                            
                        # Ensure device is set if not specified
                        if 'device' not in handler_kwargs:
                            handler_kwargs['device'] = 'all'
                    
                    # Call handler's fetch_data method
                    result = handler.fetch_data(
                        product_name=product_name,
                        start_date=start_date,
                        end_date=end_date,
                        **handler_kwargs
                    )
                    
                    # Keep track of search attempts even if they don't yield results
                    search_attempt = {
                        "source": source_name,
                        "product": product_name,
                        "date_range": f"{start_date} to {end_date}",
                        "status": result.get("status", "unknown"),
                        "debug_info": result.get("debug_info", {}),
                        "search_stats": result.get("search_stats", {})
                    }
                    # 如果 handler 返回 error，把 message 填入 debug_info
                    if result.get("status") == "error" and result.get("message"):
                        search_attempt["debug_info"] = {"error_message": result.get("message")}
                    search_attempts.append(search_attempt)
                    
                    # Process and add results
                    processed_results = self._process_handler_result(result, source_name)
                    if processed_results:
                        results.extend(processed_results)
                    else:
                        # If no results were processed but the call was successful, log a warning
                        if result.get("status") == "success":
                            debug_info = result.get("debug_info", {})
                            message = f"No valid results from {source_name} for product: {product_name}"
                            if debug_info:
                                message += f" (Debug info available)"
                            self.logger.warning(message)
                    
                except Exception as e:
                    error_msg = f"Error fetching data from {source_name}: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append({"source": source_name, "error": str(e)})
            
            # Determine overall status
            if not sources:
                status = "error"
                message = "No valid data sources available"
            elif len(errors) == len(sources):
                status = "error"
                message = "All data sources failed"
            elif errors:
                status = "partial_success"
                message = f"{len(sources) - len(errors)}/{len(sources)} data sources succeeded"
            elif not results:
                status = "warning"
                message = "No results found from data sources"
            else:
                status = "success"
                message = f"Successfully fetched data from {len(sources)} sources"
            
            # Return consolidated results with metadata
            return {
                "status": status,
                "message": message,
                "goal": goal,
                "product": product_name,
                "date_range": f"{start_date} to {end_date}",
                "target_platform": target_platform,
                "sources_used": sources,
                "results": results,
                "errors": errors if errors else None,
                "debug": {
                    "search_attempts": search_attempts,
                    "processed_result_count": len(results)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in fetch_insights: {str(e)}")
            return {
                "status": "error",
                "message": f"Error orchestrating product insights: {str(e)}",
                "goal": goal,
                "product": product_name,
                "date_range": f"{start_date} to {end_date}" if start_date and end_date else "unknown",
                "target_platform": target_platform
            }
