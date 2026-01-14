from pm_studio_mcp.utils.data_handlers.base_handler import BaseHandler
from datetime import datetime
from typing import Dict, Any
from pm_studio_mcp.config import config
import csv
import os
import logging

try:
    import praw
except ImportError:
    print("Please install required packages: pip install praw requests")

class RedditHandler(BaseHandler):
    """
    Handler for Reddit operations.
    This class is responsible for managing Reddit-related functionalities.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedditHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize the RedditHandler with the provided API credentials.
        
        :param client_id: Reddit API client ID
        :param client_secret: Reddit API client secret  
        :param subreddit_name: Subreddit to search (default: "all" for global search)
        """
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        
        try:
            self.client_id = config.REDDIT_CLIENT_ID
            if not self.client_id:
                raise ValueError("REDDIT_CLIENT_ID is missing in environment variables.")   
            
            self.client_secret = config.REDDIT_CLIENT_SECRET
            if not self.client_secret:
                raise ValueError("REDDIT_CLIENT_SECRET is missing in environment variables.")
            
            self.working_dir = config.WORKING_PATH
            if not self.working_dir:
                raise ValueError("WORKING_PATH is missing in environment variables.")
            
            # Create a user agent string
            user_agent = f"python:reddit-post-scraper:v1.0 (by u/anonymous)"
            
            # Initialize Reddit API connection
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=user_agent
            )
            # Test the connection to make sure authentication works
            _ = self.reddit.user.me()  # This will raise an exception if authentication fails
            
            self._initialized = True
            self.logger.info("Reddit handler initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Reddit handler: {str(e)}")
            # Still mark as initialized to prevent repeated init attempts
            self._initialized = True
            # Store the error for later reference
            self.init_error = str(e)

    def fetch_data(self, product_name, start_date=None, end_date=None, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from Reddit based on the provided parameters.
        
        Args:
            product_name (str): Name of the product to search for
            start_date: Start date for data range in format 'YYYY-MM-DD' or datetime object
            end_date: End date for data range in format 'YYYY-MM-DD' or datetime object
            **kwargs: Additional parameters including:
                - keywords (List[str]): List of keywords to search for
                - subreddit_name (str): Subreddit to search (default: "all")
                - post_limit (int): Maximum number of posts to retrieve
                - time_filter (str): Time filter for posts (all, year, month, week, day)
                - sort (str): Sort order - 'top', 'relevance', or 'latest'
                - debug (bool): Enable debug mode
        
        Returns:
            dict: Dictionary containing status, posts found, and output file path
        """
        # Check if there was an initialization error
        if hasattr(self, 'init_error'):
            return {
                "status": "error",
                "message": f"Reddit handler failed to initialize: {self.init_error}",
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
            self.logger.info(f"Reddit handler fetching data for product: {product_name}")
        
            # Extract parameters from kwargs
            # No need to check if kwargs is None since with **kwargs it will always be a dictionary
            keywords = kwargs.get('keywords', [product_name])
            if not isinstance(keywords, list):
                keywords = [keywords]
                
            # Add product name to keywords if not already included
            if product_name not in keywords:
                keywords.append(product_name)
                
            self.logger.info(f"Using keywords: {keywords}")
            
            # Get the primary subreddit name - support both 'subreddit_name' (from server.py) and 'subreddit' parameters
            subreddit_name = kwargs.get('subreddit_name', kwargs.get('subreddit', 'all'))
            
            # Process date parameters
            start_datetime, end_datetime = self._process_date_parameters(start_date, end_date)
            
            # Determine the appropriate time filter based on date range
            time_filter = self._determine_time_filter(start_date, end_date, start_datetime, end_datetime, kwargs)
                
            sort = kwargs.get('sort', 'relevance')
            
            # Default to an empty list before fetching any posts
            filtered_posts = []
            
            # Try multiple search approaches to maximize chances of finding posts
            search_methods = []
            post_ids_seen = set()  # Track post ID's to avoid duplicates
            
            # Determine which subreddits to search
            subreddits_to_search = self._determine_subreddits(subreddit_name, product_name)
            post_limit = kwargs.get('post_limit', 100)
            
            # Try each subreddit
            for current_subreddit in subreddits_to_search:
                try:
                    # Initialize subreddit object
                    subreddit = self.reddit.subreddit(current_subreddit)
                    
                    # Create search query from keywords
                    if isinstance(keywords, list) and keywords:
                        # Filter out non-string values and empty strings
                        valid_keywords = [k for k in keywords if isinstance(k, str) and k.strip()]
                        if valid_keywords:
                            query = f"{product_name} {' '.join(valid_keywords)}"
                            self.logger.info(f"Reddit search query for {current_subreddit}: {query}")
                        else:
                            query = product_name
                    else:
                        query = product_name
                    
                    # Try simple search with just product name
                    try:
                        simple_query = product_name
                        self.logger.info(f"Trying Reddit search with simple query in {current_subreddit}: {simple_query}")
                        simple_search_posts = list(subreddit.search(query=simple_query, sort="relevance", time_filter=time_filter, limit=min(post_limit, 50)))
                        search_methods.append((f"{current_subreddit}_simple_search", simple_search_posts))
                        self.logger.info(f"Simple search in {current_subreddit} returned {len(simple_search_posts)} posts")
                    except Exception as e:
                        self.logger.warning(f"Reddit simple search query failed in {current_subreddit}: {str(e)}")

                    # Try search with full query including keywords
                    try:
                        self.logger.info(f"Trying Reddit search with full query in {current_subreddit}: {query}")
                        search_posts = list(subreddit.search(query=query, sort="relevance", time_filter=time_filter, limit=min(post_limit, 50)))
                        search_methods.append((f"{current_subreddit}_full_search", search_posts))
                        self.logger.info(f"Full search in {current_subreddit} returned {len(search_posts)} posts")
                    except Exception as e:
                        self.logger.warning(f"Reddit full search query failed in {current_subreddit}: {str(e)}")
                    
                    # Get top posts and filter (only for specific subreddits, not 'all')
                    if current_subreddit.lower() != 'all':
                        try:
                            self.logger.info(f"Trying Reddit top posts for {current_subreddit}")
                            top_posts = list(subreddit.top(time_filter=time_filter, limit=min(post_limit, 30)))
                            search_methods.append((f"{current_subreddit}_top", top_posts))
                            self.logger.info(f"Top posts for {current_subreddit} returned {len(top_posts)} posts")
                        except Exception as e:
                            self.logger.warning(f"Reddit top posts query failed for {current_subreddit}: {str(e)}")
                    
                        # Get new posts and filter (only for specific subreddits, not 'all')
                        try:
                            self.logger.info(f"Trying Reddit new posts for {current_subreddit}")
                            new_posts = list(subreddit.new(limit=min(post_limit, 30)))
                            search_methods.append((f"{current_subreddit}_new", new_posts))
                            self.logger.info(f"New posts for {current_subreddit} returned {len(new_posts)} posts")
                        except Exception as e:
                            self.logger.warning(f"Reddit new posts query failed for {current_subreddit}: {str(e)}")
                
                except Exception as e:
                    self.logger.warning(f"Error searching subreddit {current_subreddit}: {str(e)}")
            
            # Process posts from all methods
            for method_name, posts in search_methods:
                current_sub = method_name.split('_')[0]  # Extract subreddit from method name
                
                for post in posts:
                    # Skip if we've already processed this post
                    if post.id in post_ids_seen:
                        continue
                    
                    post_ids_seen.add(post.id)
                    
                    # Apply date filtering if dates are provided
                    post_datetime = datetime.fromtimestamp(post.created_utc)
                    
                    # Skip posts before start date
                    if start_datetime and post_datetime < start_datetime:
                        continue
                        
                    # Skip posts after end date
                    if end_datetime and post_datetime > end_datetime:
                        continue
                    
                    # Check if this post matches our criteria
                    should_include, matched_reason = self._should_include_post(post, product_name, keywords, method_name, current_sub)
                    
                    if should_include:
                        post_data = {
                            "title": post.title,
                            "url": f"https://www.reddit.com{post.permalink}",
                            "author": str(post.author) if post.author else "[deleted]",
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "created_utc": datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                            "selftext": post.selftext[:500] + "..." if post.selftext and len(post.selftext) > 500 else post.selftext,
                            "subreddit": post.subreddit.display_name,
                            "matched_by": matched_reason
                        }
                        filtered_posts.append(post_data)
            
            # Save the results to CSV
            # Include date range in filename if provided
            date_suffix = self._create_date_suffix(start_date, end_date)
            output_file = f"reddit_{subreddit_name}_{product_name.replace(' ', '_')}{date_suffix}_posts.csv"
            output_path = os.path.join(self.working_dir, output_file)
                
            if filtered_posts:
                with open(output_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=filtered_posts[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_posts)
                
                self.logger.info(f"Found {len(filtered_posts)} matching posts for {product_name}")
                
                # Track which search methods produced results
                method_stats = {}
                for method_name, posts in search_methods:
                    method_stats[method_name] = len(posts)
                
                return {
                    "status": "success",
                    "data_length": len(filtered_posts),
                    "posts_found": len(filtered_posts),  # Add this for backward compatibility
                    "output_file": os.path.abspath(output_path),
                    "search_stats": {
                        "query": query if 'query' in locals() else product_name,
                        "methods_tried": len(search_methods),
                        "methods_breakdown": method_stats,
                        "subreddits_searched": subreddits_to_search,
                        "total_posts_searched": sum(len(posts) for _, posts in search_methods),
                        "unique_posts_found": len(post_ids_seen),
                        "filtered_posts": len(filtered_posts),
                        "date_range": {
                            "start_date": start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
                            "end_date": end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date
                        } if start_date or end_date else None
                    }
                }
            else:
                self.logger.warning(f"No posts found for {product_name} with keywords {keywords} across {len(subreddits_to_search)} subreddits")
                
                # Track which search methods were attempted
                method_stats = {}
                for method_name, posts in search_methods:
                    method_stats[method_name] = len(posts)
                    
                # Create a detailed debug info dict to help diagnose the issue
                debug_info = {
                    "product_name": product_name,
                    "keywords": keywords,
                    "methods_tried": len(search_methods),
                    "methods_breakdown": method_stats,
                    "subreddits_searched": subreddits_to_search,
                    "total_posts_searched": sum(len(posts) for _, posts in search_methods),
                    "unique_posts_found": len(post_ids_seen),
                    "time_filter": time_filter,
                    "start_date": start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
                    "end_date": end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date
                }
                self.logger.info(f"Debug info: {debug_info}")
                
                return {
                    "status": "success",
                    "data_length": 0,
                    "posts_found": 0,  # Add this for backward compatibility
                    "message": "No posts found matching the criteria.",
                    "debug_info": debug_info
                }
            
        except Exception as e:
            # Sanitize error message to ensure no sensitive info is exposed
            error_msg = str(e)
            error_type = type(e).__name__
            self.logger.error(f"Error in Reddit handler: {error_type} - {error_msg}")
            
            # Create more specific error messages based on error type
            if isinstance(e, AttributeError):
                # Often indicates issues with PRAW API or Reddit connection
                error_msg = "Error connecting to Reddit API. This might be due to authentication issues or API changes."
                self.logger.error(f"PRAW AttributeError: {str(e)}")
            elif "client_id" in error_msg.lower() or "client_secret" in error_msg.lower():
                error_msg = "Authentication error - please check Reddit API credentials"
            
            # Capture the full exception for debugging
            import traceback
            trace = traceback.format_exc()
            self.logger.debug(f"Full traceback: {trace}")
            
            # Create a debug info dict to help diagnose the issue
            debug_info = {
                "product_name": product_name,
                "subreddit": kwargs.get('subreddit_name', kwargs.get('subreddit', 'all')) if kwargs else 'all',
                "start_date": start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
                "end_date": end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date,
                "error_type": error_type,
                "error_details": str(e)
            }
            
            return {
                "status": "error",
                "message": f"Error scraping Reddit: {error_msg}",
                "debug_info": debug_info,
                "data_length": 0,
                "posts_found": 0  # Add this for backward compatibility
            }
        
    def _process_date_parameters(self, start_date=None, end_date=None):
        """
        Process date parameters to convert them to datetime objects.
        
        Args:
            start_date: Start date as string (YYYY-MM-DD) or datetime object
            end_date: End date as string (YYYY-MM-DD) or datetime object
            
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        start_datetime = None
        end_datetime = None
        
        # Convert start_date to datetime if provided
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
                
        return start_datetime, end_datetime
    
    def _determine_time_filter(self, start_date, end_date, start_datetime, end_datetime, kwargs):
        """
        Determine the appropriate time filter based on date range.
        
        Args:
            start_date: Original start date parameter
            end_date: Original end date parameter
            start_datetime: Processed start datetime object
            end_datetime: Processed end datetime object
            kwargs: Additional parameters
            
        Returns:
            String time filter value
        """
        # Default to month if not specified
        time_filter = kwargs.get('time_filter', 'month')
        
        # If both dates are provided, estimate appropriate time_filter
        if start_datetime and end_datetime:
            delta_days = (end_datetime - start_datetime).days
            if delta_days <= 7:
                time_filter = 'day'
            elif delta_days <= 30:
                time_filter = 'week'
            elif delta_days <= 365:
                time_filter = 'month'
            else:
                time_filter = 'year'
                
            self.logger.info(f"Date range of {delta_days} days maps to time_filter: {time_filter}")
        
        # Always allow explicit override via kwargs
        time_filter = kwargs.get('time_filter', time_filter)
        self.logger.info(f"Using time_filter: {time_filter}")
        
        return time_filter
    
    def _determine_subreddits(self, subreddit_name, product_name):
        """
        Determine which subreddits to search based on the product and primary subreddit.
        
        Args:
            subreddit_name: Primary subreddit to search
            product_name: Name of the product
            
        Returns:
            List of subreddits to search
        """
        subreddits_to_search = []
        
        # Always include the primary subreddit
        subreddits_to_search.append(subreddit_name)
        
        # For tech products, also try specific tech subreddits if not already specified
        if subreddit_name.lower() == 'all':
            product_lower = product_name.lower()
            product_words = product_lower.split()
            
            # Try product-specific subreddit if product has a single word name
            if len(product_words) == 1:
                subreddits_to_search.append(product_words[0])
            
            # Try product name without spaces as a subreddit
            if len(product_words) > 1:
                subreddits_to_search.append(product_name.replace(' ', ''))
            
            # Add general tech subreddits for tech products
            if any(term in product_lower for term in ['browser', 'app', 'software', 'tech']):
                subreddits_to_search.append('technology')
            
            if 'browser' in product_lower:
                subreddits_to_search.append('browsers')
            
            if 'app' in product_lower or 'mobile' in product_lower:
                subreddits_to_search.append('apps')
        
        # Remove duplicates while maintaining order
        subreddits_to_search = list(dict.fromkeys(subreddits_to_search))
        self.logger.info(f"Searching in subreddits: {subreddits_to_search}")
        
        return subreddits_to_search
    
    def _should_include_post(self, post, product_name, keywords, method_name, current_sub):
        """
        Determine if a post should be included in the results based on matching criteria.
        
        Args:
            post: The Reddit post object
            product_name: Name of the product to match
            keywords: List of keywords to match
            method_name: Name of the search method used
            current_sub: Current subreddit name
            
        Returns:
            Tuple of (should_include, matched_reason)
        """
        post_title = post.title.lower() if post.title else ""
        post_text = post.selftext.lower() if post.selftext else ""
        post_combined = f"{post_title} {post_text}"
        product_name_lower = product_name.lower()
        product_name_tokens = set(product_name_lower.split())
        
        # Use a more flexible matching approach
        should_include = False
        matched_reason = ""
        
        # Include all posts from search methods (already pre-filtered by Reddit's search)
        if "search" in method_name:
            should_include = True
            matched_reason = f"matched by {method_name}"
        
        # Check for direct product name match
        elif product_name_lower in post_combined:
            should_include = True
            matched_reason = "direct product name match"
            
        # Check for token-based match (e.g., match "Edge" in "Microsoft Edge")
        elif any(token in post_combined for token in product_name_tokens if len(token) > 2):
            should_include = True
            matched_reason = "product name token match"
        
        # Check for any keyword matches
        elif isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, str) and kw.lower().strip() in post_combined:
                    should_include = True
                    matched_reason = f"keyword match: {kw}"
                    break
        
        # For specific subreddits that are highly relevant, be more lenient
        elif current_sub.lower() != "all" and (
            product_name_lower in current_sub.lower() or
            any(token in current_sub.lower() for token in product_name_tokens if len(token) > 2)
        ):
            should_include = True
            matched_reason = "relevant subreddit content"
        
        return should_include, matched_reason
    
    def _create_date_suffix(self, start_date, end_date):
        """
        Create a date suffix for filenames based on the date parameters.
        
        Args:
            start_date: Start date parameter
            end_date: End date parameter
            
        Returns:
            String date suffix for filenames
        """
        date_suffix = ""
        if start_date and end_date:
            start_str = start_date.strftime('%Y%m%d') if isinstance(start_date, datetime) else start_date.replace('-', '')
            end_str = end_date.strftime('%Y%m%d') if isinstance(end_date, datetime) else end_date.replace('-', '')
            date_suffix = f"_{start_str}_to_{end_str}"
        elif start_date:
            start_str = start_date.strftime('%Y%m%d') if isinstance(start_date, datetime) else start_date.replace('-', '')
            date_suffix = f"_from_{start_str}"
        elif end_date:
            end_str = end_date.strftime('%Y%m%d') if isinstance(end_date, datetime) else end_date.replace('-', '')
            date_suffix = f"_to_{end_str}"
            
        return date_suffix
        

if __name__ == "__main__":
    # Example usage: global search across all subreddits
    reddit_handler = RedditHandler()
    
    # Set up logging for standalone testing
    logging.basicConfig(level=logging.INFO)
    
    # Product name to search for
    product_name = "Microsoft Edge"  # Try with different product names
    
    # Example: Get posts from last 3 months with specific date range
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    result = reddit_handler.fetch_data(
        product_name=product_name,
        start_date=start_date,
        end_date=end_date,
        kwargs={
            "keywords": [product_name, "browser", "mobile", "experience"],
            "post_limit": 50,
            "subreddit_name": "all",  # Try with specific subreddits like "browsers" or "MicrosoftEdge"
            "sort": "relevance"
        }
    )
    
    if result.get("data_length", 0) > 0:
        print(f"SUCCESS! Found {result['data_length']} posts about {product_name}")
        print(f"Output file: {result['output_file']}")
        # Print first few results if available
        if 'output_file' in result and os.path.exists(result['output_file']):
            try:
                with open(result['output_file'], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    print("\nSample results:")
                    for i, row in enumerate(reader):
                        if i >= 3:  # Show just first 3 results
                            break
                        print(f"- {row['title']} (from r/{row['subreddit']})")
            except Exception as e:
                print(f"Error reading results: {e}")
    else:
        print(f"NO RESULTS: {result.get('message', 'Unknown error')}")
        
    # Print detailed statistics
    if 'search_stats' in result:
        print("\nSearch Statistics:")
        for key, value in result['search_stats'].items():
            if key != 'methods_breakdown':
                print(f"- {key}: {value}")
            else:
                print(f"- methods_breakdown:")
                for method, count in value.items():
                    print(f"  - {method}: {count}")
    
    # Print debug info if available
    if 'debug_info' in result:
        print("\nDebug Info:")
        for key, value in result['debug_info'].items():
            print(f"- {key}: {value}")