from mcp.server.fastmcp import FastMCP
import asyncio
import os
from typing import List, Dict, Optional, Union
from pm_studio_mcp.utils.file_utils import FileUtils
from pm_studio_mcp.utils.data_visualization_utils import SimpleDataViz
from pm_studio_mcp.utils.graph.chat import ChatUtils
from pm_studio_mcp.utils.graph.calendar import CalendarUtils
from pm_studio_mcp.utils.graph.mail import MailUtils
from pm_studio_mcp.utils.greeting import GreetingUtils
from .showroom_builder.showroom_guide import get_showroom_workflow_guide
from pm_studio_mcp.utils.titan.titan_metadata_utils import TitanMetadataUtils
from pm_studio_mcp.utils.titan.titan_query_utils import TitanQuery
from pm_studio_mcp.utils.data_handlers.product_insights_orchestrator import ProductInsightsOrchestrator
from pm_studio_mcp.config import config
import logging
from pm_studio_mcp.utils.graph.channel import ChannelUtils
from pm_studio_mcp.utils.publish.publish_utils import PublishUtils
from pm_studio_mcp.utils.experiment.exp import search_experiments
from pm_studio_mcp.utils.design.pin_headless_browser.searcher import PinterestSearcher
from pm_studio_mcp.utils.design.dribbble_headless_browser.searcher import search_dribbble
from pm_studio_mcp.skills.edge_mobile_dau_weekly_report.edge_mobile_weekly_report_utils import EdgeMobileWeeklyReportUtils

# Create MCP server instance with uppercase log level
logging.basicConfig(level=logging.INFO)
mcp = FastMCP("pm-studio-mcp")

logger = logging.getLogger(__name__)

# Ensure logger has at least one handler to avoid "No handlers" warnings
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Log initialization
logger.info("🎨 PM Studio MCP - Mobbin & Dribbble & Pinterest Search")

# Pinterest and Dribbble require no auth
logger.info("📌 Pinterest search available (no auth required)")
logger.info("🎯 Dribbble search available (no auth required)")
logger.info("📱 Mobbin search available (local catalog data)")

# All business logic and tool functions below, use config.XXX directly for configuration.
# For example: config.WORKING_PATH, config.REDDIT_CLIENT_ID, config.DATA_AI_API_KEY, etc.

@mcp.tool()
async def get_pm_studio_guide(name: str, intent: str = "default"):  # this is the one of the tool of my MCP server
    """
    Get a PM Studio system prompt when user send a greeting or ask for help.
    Get a PM Studio workflow guide when user want to perform a PM task, for example, product research, user feedback analysis, competitor analysis, data analysis, mission review, information gathering etc.
    Invoke this as an entry before you started a PM task, Do not invoke when user already started a PM task.

    Args:
        name (str): User's name for personalization
        intent (str): Specific intent to customize the prompt for.
                     Options: "feedback_analysis", "competitor_analysis", "data_analysis", "mission_review", "default"
                     - "default": General PM Studio guide with lightweight workflow descriptions
                     - "feedback_analysis": user feedback analysis, user verbatim analysis, feedback sentiment analysis, feedback summarization
                     - "competitor_analysis": Full competitor analysis, information gathering, SWOT analysis, market research, industry analysis  
                     - "data_analysis": Full Titan data analysis, metrics analysis, data insights
                     - "mission_review": Mission statement review, cycle planning
    """
    return GreetingUtils.get_pm_studio_guide(name, intent)

@mcp.tool()
async def get_showroom_guide(name: str, intent: str = "default", metric_parameter = None, template_name: str = "basic"):
    """
    Showroom workflow guide for PM data analysis workflows.

    This tool should ONLY be called when:
    1. User explicitly mentions "showroom", "show room", or "样板间" (required keywords)
    2. User combines showroom keywords with specific requests like:
       - "showroom reddit insights" or "show room reddit analysis"
       - "样板间数据分析" or "showroom data analysis"
       - "build a showroom" or "create showroom template"
    3. User provides explicit command format like get_showroom_guide(...)

    CRITICAL: The keywords "showroom", "show room", or "样板间" MUST be present in the user's request.
    Do NOT trigger for standalone requests like "data analysis" or "reddit insights" without showroom keywords.

    Args:
        name (str): User's name
        intent (str): one of ["default", "showroom_simple_data_analysis",
            "showroom_reddit_user_voice_insight", "showroom_reddit_subreddit_monitoring", "showroom_cnaibrowser"]
        metric_parameter (Union[str, dict], optional): May be complete or partial; robust parsing is handled downstream.
        template_name (str, optional): deprecated
    """
    return get_showroom_workflow_guide(name, intent, metric_parameter, template_name)


@mcp.tool()
async def convert_to_markdown_tool(file_path: str):
    """
    Convert a document (doc/excel/ppt/pdf/images/csv/json/xml) to markdown format using MarkItDown.

    Args:
        file_path (str): Path to the input document file

    Returns:
        str: Path to the generated markdown file or error message
    """
    return FileUtils.convert_to_markdown_tool(file_path, config.WORKING_PATH)

@mcp.tool()
async def send_message_to_chat_tool(chat_type: str, chat_name: str, message: str, message_content_path: str = None, user_index: int = None, image_path: str = None):
    """
    Send a message to a private Teams chat (not for public team channels).
    This tool is ONLY for private conversations:
        - One-on-one chats with colleagues
        - Small group chats outside of formal teams
        - Self-chat (sending messages to yourself)

    DO NOT use this tool for sending messages to public team channels. For that purpose, use send_message_to_channel_tool instead.

    Send a note to Teams chat, it can be a group chat, a self chat or a oneOnOne chat.
    when type is "person", it will search for the person in your Teams contacts and send the message to the matched person.
    When multiple users match the name, prompt matched items in the chat for user to choose.
    
    Args:
        chat_type (str): The type of chat to send the message to. Can be
            * "myself"  - Self chat, send message to yourself
            * "group"-  Group chat, send message to a group chat
            * "person" - One-on-one chat with a person
        chat_name (str): The name of the chat
            * if type is "myself", it's optinal"
            * if type is "group", it's the name of the group chat
            * if type is "person", it's the name of the person to chat with, when multiple users match the name, pls show the matched list and DO ask user to select which one is the correct one to send, make sure don't send to some user directly for multiple matches case.
        message (str): The message to send.
        message_content_path (str, optional): Path to a file containing the message content. If provided, the content of the file will be used as the message.
        user_index (int, optional): If multiple users match the name, this is the index of the user to select (1-based).
        image_path (str, optional): path of the image file to send instead of (or along with) the text message.
   
    Returns:
        dict: Dictionary containing status and response data
    """

    if message_content_path:
        # If a content file is provided, read its content
        try:
            with open(message_content_path, 'r', encoding='utf-8') as f:
                message = f.read()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read content file: {str(e)}"
            }


    response = ChatUtils.send_message_to_chat(chat_type, chat_name, message, user_index=user_index, image_path=image_path)

    if response.get("status") == "multiple_matches" and response.get("users"):
            return {
                "status": "multiple_matches",
                "users": response.get("users", []),
                "message": f"Multiple users match the name '{chat_name}'. Please choose one from the following list:\n\n",
                "requires_user_input": True
            }
    else:
        return response
   


@mcp.tool()
async def send_message_to_channel_tool(channel_info: dict, message: str):
    """
    Send a message to a public Teams channel within a team (not for private chats).
    
    This tool is ONLY for sending messages to official Teams channels that exist within a team workspace.
    DO NOT use this tool for:
    - Private one-to-one chats (@mentions to individuals)
    - Group chats outside of a formal team
    - Self chats (sending messages to yourself)
    
    Args:
        channel_info (dict): Dictionary containing one of the following:
            - 'team_name' and 'channel_name': e.g. {"team_name": "Marketing Team", "channel_name": "General"}
            - 'team_id' and 'channel_id': For direct API references
            - 'channel_url': Full URL to the channel
        message (str): The message content (supports HTML and @mentions)
    
    For private chats or group conversations, use send_message_to_chat_tool instead.
    
    Returns:
        dict: Response status and details
    """
    return ChannelUtils.send_message_to_channel(channel_info, message)

@mcp.tool()
async def get_calendar_events(start_date: str, end_date: str):
    """
    get the calendar events from Microsoft Graph API.
    Args:
        start_date: Start date in ISO format withh Beijing timezone, e.g. 2023-10-01T00:00:00+08:00
        end_date: End date in ISO format withh Beijing timezone, e.g. 2023-10-31T23:59:59+08:00
    Returns:
        dict: Dictionary containing status and response data    """
    return CalendarUtils.get_calendar_events(start_date, end_date)

@mcp.tool()
async def send_mail_tool(to_recipients: List[str], subject: str, body: str, is_html: bool = False):
    """
    Send an email using Microsoft Graph API.
    
    Args:
        to_recipients (List[str]): List of email addresses to send to
        subject (str): Email subject
        body (str): Email body content
        is_html (bool, optional): Whether the body content is HTML format. Defaults to False.
        
    Returns:
        dict: Dictionary containing status and response data with keys:
            - status: "success" or "error"
            - message: Status message or error details
    """
    return MailUtils.send_mail(to_recipients, subject, body, is_html)

@mcp.tool()
async def generate_data_visualization(visualization_type: str, data_source: str, chart_options: Dict):
    """
    🎯 Simple Data Visualization Tool - Generates PNG image files only
    
    ⚠️ IMPORTANT: This tool ONLY generates PNG format image files, NOT for HTML files!
    
    Args:
        visualization_type: Chart type ('bar', 'line', 'pie', 'scatter')
            - 'line': Line chart, suitable for time series data and trend display (preferred)
            - 'bar': Bar chart, suitable for categorical data comparison
            - 'pie': Pie chart, suitable for proportion/share data
            - 'scatter': Scatter plot, only for correlation analysis between two variables
        data_source: Absolute path to CSV file (must be a CSV file)
        chart_options: Chart options dictionary
            - title (optional): Chart title
            - filename (optional): Output filename, must end with .png
            
    Returns:
        dict: Result dictionary containing:
            - success: bool - Whether successful
            - output_path: str - Absolute path to generated PNG image file
            - message: str - Status message
            - chart_type: str - Actual chart type used
            
    Output format: Generates high-quality PNG image files (300 DPI), saved in working_dir directory
    """
    try:
        # Force ensure PNG image generation
        viz = SimpleDataViz()
        
        # Ensure filename ends with .png
        if 'filename' in chart_options and chart_options['filename']:
            if not chart_options['filename'].endswith('.png'):
                chart_options['filename'] = chart_options['filename'].rsplit('.', 1)[0] + '.png'
        
        result = viz.generate_chart(
            chart_type=visualization_type,
            data_source=data_source,
            **chart_options
        )
        
        # Additional validation: ensure output path is PNG file
        if result.get('success') and result.get('output_path'):
            if not result['output_path'].endswith('.png'):
                result['message'] += " Warning: Output file is not PNG format!"
            else:
                result['message'] += f" PNG image saved to: {result['output_path']}"
        
        return result
    
    except Exception as e:
        return {"success": False, "message": f"Error generating PNG visualization: {str(e)}"}

@mcp.tool()
async def titan_query_data_tool(query_str: str, table: str):
    """
    Query data from Titan API and save results to a CSV file.
    
    ⚠️ CRITICAL TIME RANGE HANDLING REQUIREMENT ⚠️
    >>> ALL "RECENT" TIME QUERIES MUST ADD 3 EXTRA DAYS FOR DATA DELAYS <<<
    * For "recent week"/"last 7 days" use (current_date - 10 days) to (current_date - 1)
    * For "recent month"/"last month" use (current_date - 33 days) to (current_date - 1)
    * This rule is MANDATORY for ALL time-series data queries with keywords like "last 7 days", "recent", "last week", "past" etc.
    
    Applicable Scenarios:
    - Retrieving product core metrics (e.g., DAU, MAU, DAD, BSoM, Minutes)
    - Analyzing internal system structured data
    - Querying data with precise date ranges and parameter filtering
    
    Not Applicable For:
    - Analyzing user sentiment feedback
    - Collecting app store reviews
    - Social media user discussion analysis
    
    Examples:
    - Querying Edge Browser, or Edge Mac, or Edge Mobile, or CN AI Browser (like Doubao or Quark) daily active users (or DAU, DAD, BSoM, Minutes) for the last 30 days
    - Analyzing product usage duration and retention rate
    """
    try:
        titan_query = TitanQuery(
            titan_endpoint=config.TITAN_ENDPOINT,
        )
        result = titan_query.query_data_from_titan_tool(
            query_str=query_str,
            table=table,
            output_dir=config.WORKING_PATH
        )
        return result
    except Exception as e:
        return {
            "error": str(e)
        }

@mcp.tool()
async def titan_search_table_metadata_tool(table_name: str):
    """
    Search for SQL templates based on template name or description keyword.
    This tool performs exact and fuzzy matching on SQL templates.

    Applicable Scenarios:
    - Finding pre-defined SQL templates
    - Discovering available core metric query templates
    - Exploring data structure and field information
    
    Not Applicable For:
    - Directly retrieving data (must be used with titan_query_data_tool)
    - Searching for user feedback or comments
    - Finding unstructured data
    
    Examples:
    - Searching for "DAU, DAD, BSoM, Minutes, etc" related templates
    - Finding query templates for "RETENTION" metrics
    
    Args:
        table_name (str): Template name or keyword (e.g., "mac_dau", "retention by browser")

    Returns:
        dict: Dictionary containing search results
            - status: Search status ("success" or "error")
            - message: Status message with summary of found templates
            - template_matches: List of matching templates with their table info:
                - table: Table name containing the template
                - template: Template name
                - description: Template description
                - table_description: Table description
                - filter_columns: Filter configurations
            - result_path: Path to the saved JSON file (if templates found)
    """
    return TitanMetadataUtils.find_templates_tool(table_name, config.WORKING_PATH)

@mcp.tool()
async def titan_generate_sql_from_template_tool(template_name: str, filter_values: dict = None):
    """
    Generate SQL query from a template with provided filter values.
    This tool generates executable SQL by replacing placeholders in the template with provided filter values.
    
    ⚠️ CRITICAL TIME RANGE HANDLING REQUIREMENT ⚠️
    >>> ALL "RECENT" TIME QUERIES MUST ADD 3 EXTRA DAYS FOR DATA DELAYS <<<
    * For "recent week"/"last 7 days" use (current_date - 10 days) to (current_date - 1)
    * For "recent month"/"last month" use (current_date - 33 days) to (current_date - 1)
    * This rule is MANDATORY for ALL time-series data queries with keywords like "last 7 days", "recent", "last", "past" etc.
    
    Applicable Scenarios:
    - Generating executable SQL queries from templates
    - Customizing queries for specific products and time ranges
    - Retrieving structured data without writing complete SQL queries
    
    Not Applicable For:
    - Directly executing queries (must be used with titan_query_data_tool)
    - Processing unstructured data
    - Sentiment analysis and user feedback collection
    
    Examples:
    - Generating SQL to query Edge Browser, or Edge Mac, or Edge Mobile, or CN AI Browser (like Doubao or Quark, etc) DAU for the last 30 days
    - Creating RETENTION queries with date filtering conditions
    
    Args:
        template_name (str): Name of the SQL template to use (obtained from search_table_metadata_tool)
        filter_values (dict, optional): Dictionary of filter values to apply to the template.
            Keys should match the filter column names in the template.
            If not provided, default values will be used where available.

    Returns:
        dict: Dictionary containing:
            - status: "success", "error", or "warning"
            - message: Status message
            - sql: Generated SQL query (if successful)
            - template_info: Original template information
            - filter_values: Applied filter values (including default values)
            - used_default_values: Dictionary of values that used defaults (if any)
            - remaining_filters: List of optional filters that were not provided (if warning)
    """
    return TitanMetadataUtils.generate_sql_from_template(
        template_name=template_name,
        filter_values=filter_values
    )

@mcp.tool()
async def fetch_product_insights(product_name: str, goal: str = "user_sentiment", start_date: str = None, end_date: str = None, target_platforms: Union[List[str], str] = None, **kwargs):
    """
    MCP tool to fetch product insights from appropriate sources based on goal and target platforms.
    
    Applicable Scenarios:
    - Analyzing user sentiment and feedback for products
    - Gathering app store reviews and ratings
    - Monitoring social media discussions about products
    - Tracking customer perception across multiple platforms
    
    Not Applicable For:
    - Retrieving product core metrics (DAU, MAU, etc.)
    - Analyzing internal system structured data
    - Querying data with precise numerical metrics
    
    Examples:
    - Analyzing user sentiment for Microsoft Edge in the past 3 months
    - Collecting app store reviews for Edge iOS or Android app
    - Monitoring Twitter discussions about browser features
    - Comparing user feedback across Reddit and app stores

    Args:
        product_name (str): The product or service name to analyze (e.g., "Microsoft Edge", "Chrome", "Brave", "DuckDuckGo" etc.)
        goal (str): Insight goal. Options include:
            - "user_sentiment": User sentiment and feedback analysis
            - "campaign_analysis": Marketing campaign performance analysis
            - "product_update": Product update and feature analysis
            - "release_notes": Application release notes and version history (uses Timeline API)
            - "chrome_release_notes": Chrome-specific release notes
            - "firefox_release_notes": Firefox-specific release notes  
            - "edge_release_notes": Microsoft Edge-specific release notes
            - "timeline": Application timeline events and changes
            - "version_history": Version change history
            - "download_history": Historical download data for apps (NEW)
            - "usage_history": Historical usage and active user data for apps (NEW)
            - "download_data": App download statistics and trends (NEW)
            - "active_users": Active user metrics and engagement data (NEW)
            - "app_performance": App performance metrics including sessions and retention (NEW)
            - "user_engagement": User engagement and activity metrics (NEW)
            - Any goal containing "release", "version", "update", or "timeline" will automatically use Timeline API
            - Any goal containing "download", "install", "usage", "active users" will automatically use History APIs
        start_date (str, optional): Start date for data in format 'YYYY-MM-DD'. Defaults to 3 months ago if not provided.
        end_date (str, optional): End date for data in format 'YYYY-MM-DD'. Defaults to current date if not provided.
        target_platforms (Union[List[str], str], optional): One or more platforms to target (currently supports "reddit", "data ai", "unwrap ai"). Can be a single string or a list of strings. Defaults to None, which means all platforms will be considered. If twitter or X is mentioned, then use "unwrap ai"
        kwargs: Additional parameters for specific handlers 
            - keywords (List[str]): List of keywords for filtering data for Reddit
            - sources: Simple list of sources to filter by for Unwrap AI (e.g., ["reddit", "twitter", "gplay", "appstore"])
            - group_filters (List[Dict]): Group filter objects for Unwrap AI filtering by group membership
                Example: [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            - subreddit_name (str): Name of the subreddit to search for Reddit (default: "all")
            - post_limit (int): Maximum number of posts to retrieve for Reddit
            - time_filter (str): Time filter for Reddit posts
            - device (str): Device to analyze ("ios", "android", "desktop", "all") for DataAI
            - target_data_type (str): Type of data to fetch ("reviews", "ratings", "metadata", "timeline", "download_history", "usage_history") for DataAI
            - event_filters (str): Event filters for Timeline API ("version_change", "screenshot_change", etc.)
            - sources (List[str]): List of sources to filter by for Unwrap AI (e.g., ["reddit", "twitter", "gplay", "appstore"])
            - fetch_all (bool): Whether to fetch all entries with pagination for Unwrap AI (default: False)
            - customer_id (str): Customer ID for Google Ads API (optional, if not provided, will use the first client ID under the manager account)

    Returns:
        dict: Dictionary containing fetched insights from relevant platforms
    """

    # Initialize the orchestrator as a module-level singleton
    product_insights_orchestrator = ProductInsightsOrchestrator()

    # Process inputs and initialize result structure
    platforms_to_process = []
    
    if target_platforms:
        # Handle both string and list inputs for target_platforms
        if isinstance(target_platforms, str):
            platforms_to_process = [target_platforms]
        else:
            platforms_to_process = target_platforms
    else:
        # If no specific platforms provided, use None to get default behavior
        platforms_to_process = [None]
    
    # Initialize consistent result structure
    result = {
        "goal": goal,
        "product": product_name,
        "date_range": f"{start_date} to {end_date}" if start_date and end_date else "default range",
        "platforms_processed": platforms_to_process if platforms_to_process != [None] else ["auto-selected"],
        "platform_results": {},
        "platform_statuses": {},
        "combined_results": []
    }
    
    # Process each platform (or default if None)
    for platform in platforms_to_process:
        # Delegate the work to the orchestrator for each platform
        platform_result = product_insights_orchestrator.fetch_insights(
            product_name=product_name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            target_platform=platform,
            **kwargs
        )
        
        # Track which platforms were actually used (may differ from input if platform=None)
        platform_key = platform if platform else "auto-selected"
        result["platform_results"][platform_key] = platform_result
        
        # Track the status of each platform
        platform_status = platform_result.get("status", "unknown")
        result["platform_statuses"][platform_key] = platform_status
        
        # Add to combined results list
        if "results" in platform_result and platform_result["results"]:
            result["combined_results"].extend(platform_result["results"])
    
    # Determine overall status based on individual platform statuses
    statuses = result["platform_statuses"].values()
    
    if all(status == "success" for status in statuses):
        result["status"] = "success"
        result["message"] = f"Successfully fetched insights from all {len(platforms_to_process)} platform(s)"
    elif all(status in ["error", "failure"] for status in statuses):
        result["status"] = "error"
        result["message"] = f"Failed to fetch insights from any platform"
    elif any(status in ["error", "failure"] for status in statuses):
        result["status"] = "partial_success"
        success_count = sum(1 for status in statuses if status == "success")
        result["message"] = f"Successfully fetched insights from {success_count} out of {len(platforms_to_process)} platform(s)"
    elif any(status == "warning" for status in statuses):
        result["status"] = "warning"
        result["message"] = f"Fetched insights with warnings from some platform(s)"
    else:
        result["status"] = "unknown"
        result["message"] = f"Fetched insights with mixed or unknown statuses"
    
    # Add summary information
    result["total_results_count"] = len(result["combined_results"])
    
    return result

@mcp.tool()
async def publish_html_to_github_pages_tool(html_file_path: str, image_paths: Optional[List[str]] = None):
    """
    Publish local HTML file and associated images to reports branch and return GitHub Pages access link.
    
    The tool automatically analyzes the HTML file to detect image references (img src attributes)
    and places uploaded images at the corresponding paths to maintain correct relative references.
    
    Args:
        html_file_path (str): Local HTML file path
        image_paths (List[str], optional): List of image file paths to upload. Images will be
            automatically placed at paths that match their references in the HTML file.
        
    Returns:
        dict: Contains status, url, message
        
    Examples:
        - If HTML contains: <img src="charts/revenue.png" />
          And image_paths includes: ["/local/path/revenue.png"]
          Then revenue.png will be uploaded to: charts/revenue.png
          
        - If HTML contains: <img src="assets/images/logo.jpg" />
          And image_paths includes: ["/local/path/logo.jpg"]  
          Then logo.jpg will be uploaded to: assets/images/logo.jpg
          
        - If an image is not referenced in HTML, it will be placed in assets/images/ as fallback
        
    Notes:
        - Supports relative paths in HTML (e.g., "images/chart.png", "assets/logo.jpg")
        - Skips external URLs (http://, https://, data:, etc.)
        - Automatically creates necessary directories
        - Supports common image formats: jpg, jpeg, png, gif, svg, webp, etc.
    """
    import asyncio
    import time
    loop = asyncio.get_running_loop()
    try:
        start = time.time()
        print(f"[DEBUG] [start] Publishing HTML file: {html_file_path}", flush=True)
        url = await loop.run_in_executor(
            None,
            lambda: PublishUtils.publish_html(html_file_path, image_paths)
        )
        print(f"[DEBUG] [done] PublishUtils.publish_html finished in {time.time()-start:.2f}s", flush=True)
        message = f"HTML report published to GitHub Pages: {url}"
        if image_paths:
            message += f"\nUploaded {len(image_paths)} image(s) to assets/images/"
        print(f"[DEBUG] [return] Returning success result", flush=True)
        return {
            "status": "success",
            "url": url,
            "message": message
        }
    except Exception as e:
        print(f"[DEBUG] [error] Exception: {e}", flush=True)
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def experiment_tool(
    query: str,
    search_type: str = "auto",
    limit: int = 10,
    days: int = 30
):
    """
    Generic experiment management tool - intelligently handles various experiment queries.
    
    This tool auto-detects user intent and routes to appropriate functionality.
    The LLM can use natural language queries without needing to know the specific implementation.
    
    Auto-Detection Examples:
    - "9488a9cb-3bd7-4126-a2c4-7bdc3961a231" → Get experiment by ID
    - "john.doe" or "john.doe@microsoft.com" → Get experiments by owner
    - "Edge UIR" → Search experiments by title
    - "my experiments" or "recent" → Get user's recent experiments
    
    Query Types Supported:
    1. **By Experiment ID (UUID)**:
       - Automatically detected from UUID format
       - Returns detailed experiment info including all configuration groups
       
    2. **By Owner (alias/email)**:
       - Searches for all experiments owned by the user
       - Supports partial matching on owner field
       - Returns list of experiments
       
    3. **By Title Keyword**:
       - Searches experiment titles
       - Supports partial matching
       - Returns list of matching experiments
       
    4. **Recent Experiments**:
       - Get recent experiments for a specific owner
       - Can limit number of results
       
    Args:
        query (str): The search query - can be:
            - Experiment ID (UUID format): "9488a9cb-3bd7-4126-a2c4-7bdc3961a231"
            - Owner alias/email: "john.doe" or "john.doe@microsoft.com"  
            - Experiment title keyword: "Edge UIR Color"
            - Special keywords: "my", "mine", "recent" (for user's own experiments)
            
        search_type (str, optional): Explicit search type override (default: "auto"):
            - "auto": Auto-detect based on query format (recommended)
            - "id": Force search by experiment ID
            - "owner": Force search by owner
            - "title": Force search by title keyword
            - "recent": Get recent experiments for owner
            - "owner_or_title": Try owner first, fallback to title
            
        limit (int, optional): Maximum number of results to return (default: 10)
            - Applies to owner, title, and recent searches
            - Single ID lookups always return 1 result
            
        days (int, optional): For recent searches, days to look back (default: 30)
            - Currently informational, may be used for filtering in future
    
    Returns:
        dict: Unified response structure containing:
            - status: "success" or "error"
            - query_type: The detected or specified query type
            - message: Human-readable status message
            
            For ID queries:
                - experiment_id: The queried ID
                - title: Experiment title
                - owner: Experiment owner(s)
                - groups: List of configuration group names
                - group_count: Total number of groups
                
            For owner/title/recent queries:
                - experiments: List of experiment dictionaries
                - experiment_count: Number of experiments found
                - owner_alias or title_keyword: The search parameter used
    
    Examples:
        # Get specific experiment by ID
        experiment_tool("9488a9cb-3bd7-4126-a2c4-7bdc3961a231")
        
        # Get all experiments for a user
        experiment_tool("john.doe")
        experiment_tool("john.doe@microsoft.com")
        
        # Search by title
        experiment_tool("Edge UIR", search_type="title")
        
        # Get recent experiments (limited to 5)
        experiment_tool("john.doe", search_type="recent", limit=5)
        
        # Let auto-detection work
        experiment_tool("copilot feature test")
    """
    return search_experiments(query, search_type, limit, days)

@mcp.tool()
async def generate_edge_mobile_weekly_report_tool(report_date: str,customer_type: str = None):
    """
    Generate a comprehensive weekly report for Microsoft Edge Mobile R7 DAU analysis.
    
    This tool generates a detailed weekly report based on Microsoft Edge Mobile data 
    from EdgeMobileUserOverviewV3 table via Titan API. It processes Edge Mobile usage 
    data and creates both CSV data files and an HTML report with visualizations.
    
    The Edge Mobile report includes:
    - DAU breakdown by OS category (iOS vs Android)
    - Regional analysis for Edge Mobile users
    - Customer type segmentation (Consumer vs Commercial)
    - Install source analytics (Organic, PaidAds, OEM, etc.)
    - New vs returning Edge Mobile user metrics
    - Week-over-week change calculations
    - HTML report with tables and insights
    
    Args:
        report_date (str): The date for which to generate the Edge Mobile report in YYYY-MM-DD format.
                          This should be a valid date string that will be used to fetch
                          and analyze relevant Edge Mobile data for that week.
        customer_type (str, optional): The type of customer to filter the report by.
                                       Can be "consumer" or "commercial". If not provided,
                                       the report will include both customer types.  
    
    Returns:
        str: Status message indicating success or failure of Edge Mobile report generation,
             including paths to generated report files if successful.
    
    Example:
        generate_edge_mobile_weekly_report_tool("2025-06-23") -> "Microsoft Edge Mobile weekly report generated successfully. Summary: /path/to/summary.md, HTML: /path/to/report.html"
    """
    try:
        edge_mobile_report_utils = EdgeMobileWeeklyReportUtils()
        result = edge_mobile_report_utils.generate_report(report_date,customer_type)
        return result
    except Exception as e:
        return f"Error generating Microsoft Edge Mobile weekly report: {str(e)}"


@mcp.tool()
async def search_pinterest_images(query: str, max_images: int = 10):
    """
    Search Pinterest.com public pins by keyword and return image results.

    Args:
        query (str, required): Search query, e.g., 'living room', 'mobile onboarding'.
        max_images (int, optional): Maximum number of images to return. Defaults to 10.

    Returns:
        Dict containing:
        - status: "success" or "error"
        - query: Original search query
        - images: List of image data with URLs, titles, and optional pin links
        - total_found: Total number of images found
        - message: Status message or error details
    """
    try:
        searcher = PinterestSearcher(headless=True)
        result = await searcher.search(query, max_images)
        # result is a PinterestSearchResult dataclass; return dict for MCP clients
        return result.to_dict() if hasattr(result, "to_dict") else result
    except Exception as e:
        logger.error(f"Error in search_pinterest_images: {e}")
        return {
            "status": "error",
            "query": query,
            "message": f"Pinterest search failed: {str(e)}",
            "images": [],
            "total_found": 0,
        }

@mcp.tool()
async def search_dribbble_shots(query: str, max_shots: int = 12):
    """
    Search Dribbble.com for design shots by keyword and return shot results.

    Args:
        query (str, required): Search query, e.g., 'mobile app design', 'login page ui', 'dashboard'.
        max_shots (int, optional): Maximum number of shots to return. Defaults to 12.

    Returns:
        Dict containing:
        - status: "success" or "error"
        - query: Original search query
        - shots: List of shots, each with shot_url, image_url, and title
        - total_found: Total number of shots found
        - message: Status message or error details (if error)
    """
    try:
        result = await search_dribbble(query, max_shots)
        # result is a DribbbleSearchResult dataclass; return dict for MCP clients
        return result.to_dict() if hasattr(result, "to_dict") else result
    except Exception as e:
        logger.error(f"Error in search_dribbble_shots: {e}")
        return {
            "status": "error",
            "query": query,
            "message": f"Dribbble search failed: {str(e)}",
            "shots": [],
            "total_found": 0,
        }

@mcp.tool()
async def search_mobbin(
    app_names: Union[str, List[str]], 
    flow_names: Union[str, List[str]] = None,
    return_screens: bool = False
):
    """
    Search Mobbin for app flows and screens from local catalog data.
    
    This unified tool can:
    1. Discover available flows for app(s) (default behavior)
    2. Retrieve actual screen URLs for specific app(s) and flow(s) (when return_screens=True)
    
    Args:
        app_names (Union[str, List[str]], required): Single app name (e.g., "Instagram") or list of app names.
                                                     Supports partial matching.
        flow_names (Union[str, List[str]], optional): Single flow name or list of flow names.
                                                      - When return_screens=False: Ignored
                                                      - When return_screens=True: Filters screens by these flows (returns all flows if not specified)
        return_screens (bool, optional): If False (default), returns available flows for the app(s).
                                        If True, returns actual screen URLs.
    
    Returns:
        When return_screens=False (flows mode):
            Dict containing:
            - status: "success", "partial", or "not_found"
            - results: List of apps with their flows and details
            - not_found: List of apps not found (if any)
            - suggestions: Similar app names for not found apps (if any)
            
        When return_screens=True (screens mode):
            Dict containing:
            - status: "success" or "error"
            - results: List of results grouped by app and flow with screen URLs
            - total_screens: Total number of screens found
            - message: Error message if no screens found
        
    Examples:
        # Get available flows for an app
        search_mobbin("Instagram")
        search_mobbin(["Instagram", "Twitter"])
        
        # Get screens for specific flows
        search_mobbin("Instagram", "Onboarding", return_screens=True)
        search_mobbin(["Instagram", "Twitter"], ["Onboarding", "Profile"], return_screens=True)
        
        # Get all screens for an app
        search_mobbin("Instagram", return_screens=True)
    """
    try:
        if return_screens:
            from pm_studio_mcp.utils.design.mobbin_search.searcher import search_mobbin_screens
            result = search_mobbin_screens(app_names, flow_names)
        else:
            from pm_studio_mcp.utils.design.mobbin_search.searcher import search_mobbin_flows
            result = search_mobbin_flows(app_names)
        return result
    except Exception as e:
        logger.error(f"Error in search_mobbin: {e}")
        if return_screens:
            return {
                "status": "error",
                "message": f"Mobbin screens search failed: {str(e)}",
                "results": [],
                "total_screens": 0
            }
        else:
            return {
                "status": "error",
                "message": f"Mobbin flows search failed: {str(e)}",
                "results": []
            }


def serve():
    mcp.run(transport='stdio')
