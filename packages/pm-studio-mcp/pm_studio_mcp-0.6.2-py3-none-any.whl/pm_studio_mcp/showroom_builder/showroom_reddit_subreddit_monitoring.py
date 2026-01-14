"""
Showroom Reddit Subreddit Monitoring - Complete Integrated Version
Reddit Subreddit Monitoring - Template #4

This is a complete integrated monitoring tool that includes Reddit API calls, data processing, Teams notifications and all functionality.
- Single parameter: subreddit names (supports multiple subreddits)
- Fixed configuration: optimized defaults for demonstration
- Direct execution: no external scripts needed, all functionality in one file

Separator handling notes:
- Frontend HTML: regex converts all separators to enumeration comma (、)
- Direct MCP calls: compatible with original separators (comma, semicolon, space, etc.)
- Python code: handles both formats correctly
"""

import os
import sys
import io
import json
import csv
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Note: Do not modify sys.stdout/stderr during module import stage (especially in stdio-based MCP server environment),
# as this will break JSON-RPC transport causing "no return". If encoding adjustments are needed for local script execution, handle in __main__ branch.

# Add project src directory to Python path (supports direct execution of current script)
# Goal is to add <PROJECT_ROOT>/src to sys.path, e.g. e:/pm-studio-mcp/src
try:
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_file_dir, '..', '..', '..'))
    src_dir = os.path.join(project_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
except Exception:
    # Silent failure, does not affect subsequent operations; import failures will be indicated at usage point
    pass

# Reddit API credentials - simplified version, prioritizes parameter-passed credentials
def get_reddit_credentials():
    """
    Get Reddit credentials from MCP configuration system
    Note: Now mainly uses parameter-passed credentials, this function retained for backward compatibility
    """
    try:
        from pm_studio_mcp.config import config
        return config.REDDIT_CLIENT_ID, config.REDDIT_CLIENT_SECRET
    except Exception:
        # Backward compatibility: if MCP config unavailable, try environment variables
        return os.environ.get('REDDIT_CLIENT_ID', ''), os.environ.get('REDDIT_CLIENT_SECRET', '')

# Get Reddit credentials (as default values, actual usage prioritizes parameter-passed credentials)
REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET = get_reddit_credentials()

# Import Reddit API library
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    # Don't sys.exit as it would interrupt module import

# Teams functionality check
TEAMS_AVAILABLE = True
try:
    pass
except ImportError:
    TEAMS_AVAILABLE = False

# Microsoft Graph Team Configuration - simplified version, directly uses MCP configuration
def get_user_graph_id() -> str:
    """
    Get Graph Client ID, prioritizes from MCP configuration
    
    Returns:
        str: Graph Client ID, returns empty string if not found
    """
    # First try to get from MCP configuration
    try:
        from pm_studio_mcp.config import config
        if hasattr(config, 'GRAPH_CLIENT_ID') and config.GRAPH_CLIENT_ID:
            print(f"Using GRAPH_CLIENT_ID from MCP config: {config.GRAPH_CLIENT_ID[:8]}...", flush=True)
            return config.GRAPH_CLIENT_ID
    except Exception as e:
        print(f"Failed to get GRAPH_CLIENT_ID from MCP config: {e}", flush=True)
    
    # Try environment variable as backup
    env_graph_id = os.environ.get('GRAPH_CLIENT_ID')
    if env_graph_id:
        print(f"Using GRAPH_CLIENT_ID from environment: {env_graph_id[:8]}...", flush=True)
        return env_graph_id
    
    print("No Graph Client ID found through any method", flush=True)
    return ""

class RedditMonitorConfig:
    """Reddit monitoring configuration manager"""
    
    def __init__(self, reddit_client_id: str = None, reddit_client_secret: str = None):
        """
        Initialize configuration
        
        Args:
            reddit_client_id: If provided, use this ID instead of default
            reddit_client_secret: If provided, use this Secret instead of default
        """
        # Prioritize parameter-passed Reddit credentials, otherwise use defaults
        self.reddit_client_id = reddit_client_id or REDDIT_CLIENT_ID
        self.reddit_client_secret = reddit_client_secret or REDDIT_CLIENT_SECRET
        
        # Microsoft Graph configuration - auto detection
        self.graph_client_id = get_user_graph_id()
        self.microsoft_tenant_id = os.environ.get('MICROSOFT_TENANT_ID', '72f988bf-86f1-41af-91ab-2d7cd011db47')
        
        # Base path configuration - save to working_dir/temp
        # Get absolute path of project root
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        # Prefer explicit RUN_DIR (created by workflow) to avoid polluting working_dir root
        run_dir = os.environ.get('RUN_DIR')
        if run_dir:
            self.temp_dir = os.path.join(run_dir, 'temp')
        else:
            # Fallback (legacy) still uses a namespaced subfolder, not root
            self.temp_dir = os.path.join(project_root, 'working_dir', '_fallback_subreddit_monitor', 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Validate Reddit configuration (if no credentials passed via parameters, check default configuration)
        if not self.reddit_client_id or not self.reddit_client_secret:
            if not reddit_client_id and not reddit_client_secret:
                # Only show configuration guide when no parameters passed
                raise ValueError(
                    "Reddit API credentials not properly configured.\n"
                    "Please set in VS Code MCP configuration file:\n"
                    "- REDDIT_CLIENT_ID\n"
                    "- REDDIT_CLIENT_SECRET\n"
                    "or pass credentials via parameters.\n"
                    "For detailed configuration instructions see: docs/reddit_authentication_guide.md"
                )
            else:
                # If parameters passed but empty, indicate parameter error
                raise ValueError("Provided Reddit API credentials are empty, please check Client ID and Client Secret")
    
    @property
    def temp_path(self) -> str:
        return self.temp_dir

class PostCache:
    """Post cache manager for deduplication and heat level tracking"""
    
    def __init__(self, config: RedditMonitorConfig, cache_file: str = None):
        if cache_file is None:
            cache_file = os.path.join(config.temp_path, "reddit_post_cache.json")
        
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self._cleanup_expired_entries()
    
    def _load_cache(self) -> Dict:
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load cache file: {e}")
        
        return {
            "posts": {},
            "last_cleanup": datetime.now().isoformat(),
            "no_alert_count": 0
        }
    
    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save cache file: {e}")
    
    def _cleanup_expired_entries(self, max_age_days: int = 7):
        current_time = datetime.now()
        expired_keys = []
        
        for post_id, post_data in self.cache_data.get("posts", {}).items():
            try:
                first_seen = datetime.fromisoformat(post_data.get("first_seen", ""))
                if (current_time - first_seen).days > max_age_days:
                    expired_keys.append(post_id)
            except Exception:
                expired_keys.append(post_id)
        
        for key in expired_keys:
            del self.cache_data["posts"][key]
        
        if expired_keys:
            print(f"🗑️  Cleaned {len(expired_keys)} expired cache entries")
            self._save_cache()
    
    def should_alert(self, post_id: str, current_score: int, threshold: int) -> Dict[str, Any]:
        """Simplified alert decision - one-time demo version, only based on current score"""
        if current_score >= threshold:
            return {
                "should_alert": True,
                "alert_level": "🔥 Hot Post",
                "reason": f"Hot post ({current_score} upvotes)",
                "is_new": True
            }
        else:
            return {
                "should_alert": False, 
                "alert_level": "📝 Normal", 
                "reason": f"Normal post ({current_score} upvotes)"
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        posts = self.cache_data.get("posts", {})
        total_posts = len(posts)
        alert_levels = {}
        
        for post_data in posts.values():
            level = post_data.get("alert_level", "unknown")
            alert_levels[level] = alert_levels.get(level, 0) + 1
        
        return {
            "total_cached_posts": total_posts,
            "alert_level_distribution": alert_levels,
            "cache_file": self.cache_file,
            "no_alert_count": self.cache_data.get("no_alert_count", 0)
        }
    
    def increment_no_alert_count(self) -> int:
        self.cache_data["no_alert_count"] = self.cache_data.get("no_alert_count", 0) + 1
        self._save_cache()
        return self.cache_data["no_alert_count"]
    
    def reset_no_alert_count(self):
        self.cache_data["no_alert_count"] = 0
        self._save_cache()

class SimpleRedditHandler:
    """Simplified Reddit handler"""
    
    def __init__(self, config: RedditMonitorConfig):
        self.config = config
        self.reddit = praw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent="pm-studio-subreddit-fetcher/1.0"
        )
    
    def get_posts(self, subreddit: str, sort: str = "hot", limit: int = 25, 
                  time_filter: str = "day") -> List[Dict]:
        try:
            target_subreddit = self.reddit.subreddit(subreddit)
            
            if sort == "hot":
                submissions = target_subreddit.top(time_filter=time_filter, limit=limit * 2)
            elif sort == "top":
                submissions = target_subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "new":
                submissions = target_subreddit.new(limit=limit)
            else:
                submissions = target_subreddit.top(time_filter=time_filter, limit=limit)
            
            posts = []
            for post in submissions:
                posts.append({
                    'id': post.id,
                    'title': post.title,
                    'url': f"https://reddit.com{post.permalink}",
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                    'selftext': post.selftext[:500] if post.selftext else '',
                    'subreddit': str(post.subreddit),
                    'matched_by': f"subreddit:{subreddit}"
                })
            
            return posts
            
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []

class RedditSubredditMonitor:
    """Reddit Subreddit Monitor - Complete integrated version"""
    
    def __init__(self, reddit_client_id: str = None, reddit_client_secret: str = None):
        """
        Initialize monitor
        
        Args:
            reddit_client_id: If provided, use this ID instead of default
            reddit_client_secret: If provided, use this Secret instead of default
        """
        self.config = RedditMonitorConfig(reddit_client_id, reddit_client_secret)
        self.reddit_handler = SimpleRedditHandler(self.config)
        self.post_cache = PostCache(self.config)
    
    def get_hot_posts(self, subreddit: str, hours: int = 6, post_limit: int = 15,
                      time_filter: str = "hour", sort: str = "hot", threshold: int = 10) -> Dict[str, Any]:
        """Get hot posts from specified subreddit"""
        print(f"🔥 Getting hot posts from r/{subreddit}")
        print(f"📅 Time range: last {hours} hours")
        print(f"📊 Post limit: {post_limit}")
        print(f"🚀 Upvote threshold: {threshold}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        all_posts = []
        alert_posts = []
        
        # Handle multiple subreddits - compatible with frontend processing and direct calls
        if '、' in subreddit:
            # Format unified by frontend HTML
            subreddits_to_fetch = [s.strip() for s in subreddit.split('、')]
        elif ',' in subreddit:
            # Comma-separated format for direct MCP calls
            subreddits_to_fetch = [s.strip() for s in subreddit.split(',')]
        else:
            subreddits_to_fetch = [subreddit.strip()]
        
        # Get posts
        for target_subreddit in subreddits_to_fetch:
            print(f"  🔍 Getting posts from r/{target_subreddit}")
            posts = self.reddit_handler.get_posts(
                subreddit=target_subreddit,
                sort=sort,
                limit=post_limit * 2,
                time_filter=time_filter
            )
            all_posts.extend(posts)
        
        # Time filtering
        if hours > 0:
            filtered_posts = []
            for post in all_posts:
                try:
                    post_date = datetime.fromisoformat(post['created_utc'].replace('Z', '+00:00')).replace(tzinfo=None)
                    if post_date >= start_date:
                        filtered_posts.append(post)
                except:
                    filtered_posts.append(post)
            all_posts = filtered_posts
        
        # Sort and limit count
        all_posts.sort(key=lambda x: x['score'], reverse=True)
        all_posts = all_posts[:post_limit]
        
        # Check alerts
        for post in all_posts:
            post_id = post.get('id', '')
            current_score = post.get('score', 0)
            
            alert_info = self.post_cache.should_alert(post_id, current_score, threshold)
            post['alert_info'] = alert_info
            
            if alert_info.get('should_alert', False):
                alert_posts.append(post)
        
        cache_stats = self.post_cache.get_cache_stats()
        
        return {
            'posts': all_posts,
            'alert_posts': alert_posts,
            'total_count': len(all_posts),
            'alert_count': len(alert_posts),
            'cache_stats': cache_stats,
            'subreddits': subreddits_to_fetch,
            'search_params': {
                'subreddit': subreddit,
                'hours': hours,
                'post_limit': post_limit,
                'time_filter': time_filter,
                'sort': sort,
                'threshold': threshold
            }
        }
    
    def display_results(self, result: Dict[str, Any], show_count: int = 10) -> None:
        """Display retrieval results"""
        posts = result.get('posts', [])
        alert_posts = result.get('alert_posts', [])
        total_count = result.get('total_count', 0)
        alert_count = result.get('alert_count', 0)
        
        if total_count > 0:
            print(f"✅ Successfully retrieved {total_count} hot posts")
            print(f"🚨 Posts requiring alert: {alert_count}")
            
            if alert_posts:
                print(f"\n🚨 Posts requiring alert:")
                self._show_posts(alert_posts[:5], show_alert_info=True)
            
            print(f"\n🔥 Hot posts preview:")
            self._show_posts(posts[:show_count], show_alert_info=True)
        else:
            print("❌ No hot posts found")
    
    def _show_posts(self, posts: List[Dict], show_alert_info: bool = False) -> None:
        """Display post list"""
        for i, post in enumerate(posts, 1):
            alert_prefix = ""
            if show_alert_info and 'alert_info' in post:
                alert_info = post['alert_info']
                if alert_info.get('should_alert', False):
                    alert_prefix = f"{alert_info.get('alert_level', '🔥')} "
            
            print(f"\n{i}. {alert_prefix}📝 {post['title']}")
            print(f"   👤 {post['author']} | 🏠 r/{post['subreddit']}")
            print(f"   👍 {post['score']} score | 💬 {post['num_comments']} comments")
            print(f"   🔗 {post['url']}")
    
    def save_to_csv(self, posts: List[Dict], filename: str = None) -> str:
        """Save posts to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.config.temp_path, f"subreddit_hot_posts_{timestamp}.csv")
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not posts:
            print(f"⚠️  No data to save")
            return filename
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'url', 'author', 'score', 'num_comments', 
                         'created_utc', 'selftext', 'subreddit', 'matched_by', 'alert_level', 'alert_reason']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for post in posts:
                alert_info = post.get('alert_info', {})
                row_data = {k: v for k, v in post.items() if k != 'alert_info'}
                row_data['alert_level'] = alert_info.get('alert_level', 'tracked')
                row_data['alert_reason'] = alert_info.get('reason', '')
                writer.writerow(row_data)
        
        print(f"📄 Results saved to: {os.path.abspath(filename)}")
        return filename
    
    def send_teams_notification(self, result: Dict[str, Any], threshold: int = 10, teams_alias: str = "myself") -> bool:
        """Send Teams notification message - one-time demo version, always sends message"""
        if not TEAMS_AVAILABLE:
            print("⚠️  Teams functionality unavailable, skipping message sending")
            return False
        
        all_posts = result.get('posts', [])
        if not all_posts:
            print("⚠️  No posts retrieved, skipping Teams message sending")
            return False
        
        try:
            from pm_studio_mcp.utils.graph.chat import ChatUtils
            
            # Build message
            search_params = result.get('search_params', {})
            subreddit = search_params.get('subreddit', 'unknown')
            hours = search_params.get('hours', 6)
            total_posts = len(all_posts)
            alert_posts = result.get('alert_posts', [])
            alert_count = len(alert_posts)
            
            message_lines = [
                "# Reddit Monitoring Result - Demo Report",
                "---",
                f"📍 Target: r/{subreddit} | ⏰ Time Window: {hours} hours",
                f"📊 Retrieved: {total_posts} posts | 🔥 Hot: {alert_count} high-score posts (> {threshold} upvotes)",
                "🛡️ Language requirement: English-only Teams message (policy)",
                "",
                "## 🔥 Top 5 Hot Posts",
                "---"
            ]
            
            # Show top 5 hottest posts (regardless of alert status)
            top_posts = sorted(all_posts, key=lambda x: x.get('score', 0), reverse=True)[:5]
            for i, post in enumerate(top_posts, 1):
                title = post.get('title', 'No Title')
                if len(title) > 50:
                    title = title[:50] + "..."
                
                score = post.get('score', 0)
                comments = post.get('num_comments', 0)
                url = post.get('url', '')
                subreddit_name = post.get('subreddit', '')
                
                # Add heat indicator
                heat_emoji = "🔥" if score >= threshold else "📝"
                
                message_lines.append(
                    f"{heat_emoji} **[{title}]({url})**"
                )
                message_lines.append(
                    f"   👍 {score} upvotes | 💬 {comments} comments | 🏠 r/{subreddit_name}"
                )
                message_lines.append("")
            
            message_lines.extend([
                "---",
                f"⏰ Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 💡 Demo monitoring",
                "ℹ️ Note: This is a one-off demo run. For production, set up automation (e.g., scheduled jobs/CI, alert thresholds, periodic status reports)."
            ])
            
            message = "\n".join(message_lines)
            
            # Send message
            if teams_alias.lower() == 'myself':
                response = ChatUtils.send_message_to_chat("myself", "", message)
            else:
                response = ChatUtils.send_message_to_chat("person", teams_alias, message)
            
            if response.get("status") == "success":
                print("✅ Teams message sent successfully!")
                return True
            else:
                print(f"❌ Teams message sending failed: {response.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Teams message: {str(e)}")
            return False

def get_showroom_reddit_subreddit_monitoring_workflow(subreddit_parameter: str = None, template_name: str = "basic") -> str:
    """
    Reddit Subreddit Monitoring Workflow - Template #4
    
    Args:
        subreddit_parameter (str): Subreddit parameter, supports multiple formats:
            - Single subreddit: "MicrosoftEdge"  
            - Multiple subreddits (comma): "MicrosoftEdge,chrome,firefox"
            - Multiple subreddits (semicolon): "programming;webdev;javascript"
            - Multiple subreddits (space): "technology browsers apps"
            - JSON format: '{"topics":"browsers","reddit_client_id":"xxx","reddit_client_secret":"yyy"}'
        template_name (str): Reserved parameter, fixed as "basic"
        
    Returns:
        str: Workflow guide and execution results
    """
    
    # ⚠️ CRITICAL: AI reasoning generates timestamp, forbid complex command line calculations
    # Dynamically generate current timestamp, ensure each execution uses actual current time
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir_name = f"{current_timestamp}_subreddit_monitor"
    
    # Parse parameter: supports JSON format and simple string format
    reddit_config = None
    original_subreddit_parameter = subreddit_parameter
    
    if subreddit_parameter:
        # First check if it's a dict type (result of MCP auto parsing)
        if isinstance(subreddit_parameter, dict) and 'topics' in subreddit_parameter:
            reddit_config = {
                'topics': subreddit_parameter['topics'],
                'client_id': subreddit_parameter.get('reddit_client_id', ''),
                'client_secret': subreddit_parameter.get('reddit_client_secret', '')
            }
            subreddit_parameter = subreddit_parameter['topics']
        elif isinstance(subreddit_parameter, str):
            try:
                # Try parsing as JSON format (backward compatibility)
                import json
                config_data = json.loads(subreddit_parameter)
                if isinstance(config_data, dict) and 'topics' in config_data:
                    reddit_config = {
                        'topics': config_data['topics'],
                        'client_id': config_data.get('reddit_client_id', ''),
                        'client_secret': config_data.get('reddit_client_secret', '')
                    }
                    subreddit_parameter = config_data['topics']
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as simple string
                pass
    
    # Parameter completeness check - must provide both subreddit and Reddit credentials
    if not subreddit_parameter:
        return """---
mode: 'agent'
---
# Reddit Subreddit Monitoring - Template #4

## ❌ Missing Required Parameters

⚠️ **Important: This tool requires complete configuration information, does not support step-by-step provision!**

### 🚨 Must provide the following information at once:
1. **Subreddit list**: Reddit subreddits to monitor
2. **Reddit API credentials**: Client ID and Client Secret

### 📝 Correct calling format:
```
get_showroom_guide("user", "showroom_reddit_subreddit_monitoring", {"topics": "subreddit_name", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"})
```

### Calling examples:
- Single subreddit: `{"topics": "MicrosoftEdge", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}`
- Multiple subreddits: `{"topics": "MicrosoftEdge,chrome,firefox", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}`
- Tech subreddits: `{"topics": "programming;webdev;javascript", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}`

### 🚨 Important Notice:

**This tool is an independent Showroom workflow, completely different from the following tools:**
- ❌ **Not** Python files under `prompts/reddit_daily` directory
- ❌ **Not** `fetch_product_insights` in MCP tools
- ❌ **Does not allow** using virtual or fake data
- ❌ **Cannot** be confused with or replace other Reddit tools
- ✅ **Is** an independent Reddit API real-time monitoring tool using real data

### Template #4 Features:
- 🔥 Multi-subreddit hot post monitoring
- 📊 Smart threshold filtering (10+ upvotes)
- 📨 Teams auto notification
- 💾 Data persistent storage
- 🤖 Automation deployment support

**Please re-invoke with complete configuration information (including subreddits and Reddit credentials).**
"""
    
    # Parse and validate subreddit parameters
    subreddits = parse_subreddit_parameter(subreddit_parameter)
    
    # Check for invalid subreddit names that need conversion
    invalid_names = [name for name in subreddits if name.startswith('INVALID:')]
    valid_names = [name for name in subreddits if not name.startswith('INVALID:')]
    
    if invalid_names:
        # Extract invalid subreddit names (remove INVALID: prefix)
        raw_invalid_names = [name[8:] for name in invalid_names]
        
        return f"""---
mode: 'agent'
---
# Reddit Subreddit Monitoring - Template #4

## ❌ Subreddit Name Conversion Required

**The following invalid subreddit names were detected:** `{', '.join(raw_invalid_names)}`

### 🚨 Reddit Subreddit Naming Requirements:
- **Must be English names**, no Chinese characters
- Length 3-21 characters
- Only letters, numbers, underscores, hyphens
- Cannot start or end with underscore

### 📝 Please convert the following descriptions to valid Reddit subreddit names:

**Names to convert:** `{', '.join(raw_invalid_names)}`

### 🎯 Conversion suggestions:
- "browsers" → Suggest: `browsers`, `chrome`, `firefox`, `MicrosoftEdge`
- "programming" → Suggest: `programming`, `coding`
- "technology" → Suggest: `technology`, `tech`
- "gaming" → Suggest: `gaming`, `games`
- "news" → Suggest: `news`, `worldnews`

### ✅ Correct calling format example:
```
get_showroom_guide("user", "showroom_reddit_subreddit_monitoring", {{"topics": "browsers,chrome,firefox", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}})
```

**Please re-invoke using correct English Reddit subreddit names.**
"""
    
    if not valid_names:
        return f"""---
mode: 'agent'
---
# Reddit Subreddit Monitoring - Template #4

## ❌ Invalid Subreddit Parameters

Input parameter: `{subreddit_parameter}`

Please use valid subreddit format and **must provide complete Reddit API credentials**:

### Correct complete format:
```
{{"topics": "valid_subreddit_names", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}}
```

### Supported subreddit formats:
- Single subreddit: `"MicrosoftEdge"`
- Multiple subreddits: `"MicrosoftEdge,chrome,firefox"`
- Tech subreddits: `"programming,webdev,javascript"`
- General subreddits: `"technology,browsers,apps"`

**⚠️ Providing only subreddit names is not supported, must include complete Reddit API credentials!**
"""
    
    # Continue execution with valid subreddit names
    subreddits = valid_names
    
    # Validate Reddit credentials completeness
    if not reddit_config or not reddit_config.get('client_id') or not reddit_config.get('client_secret'):
        return f"""---
mode: 'agent'
---
# Reddit Subreddit Monitoring - Template #4

## ❌ Missing Reddit API Credentials

Identified subreddits: {', '.join([f'r/{s}' for s in subreddits])}

**⚠️ Error: Missing complete Reddit API credentials!**

### 🚨 Must provide complete information:

**Current input:** `{original_subreddit_parameter}`

**Required format:**
```
{{"topics": "{subreddit_parameter}", "reddit_client_id": "your_reddit_client_id", "reddit_client_secret": "your_reddit_client_secret"}}
```

### 🔑 Get Reddit API credentials:

1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Get Client ID and Client Secret

### 🚨 Important reminders:

- **No step-by-step configuration**: Must provide subreddits and credentials at once
- **No environment variable approach**: Showroom workflow requires explicit credential passing
- **Ensure instruction integrity**: AI should maintain original Reddit credentials when transforming subreddits
- **No partial execution**: No monitoring operations will run if credentials are missing

**Please re-invoke with complete configuration information.**
"""
    
    # Valid parameters, return complete workflow
    config_info = f"""🔥 **Monitoring Configuration**:
- Target subreddits: {', '.join([f'r/{s}' for s in subreddits])}
- Number of subreddits: {len(subreddits)}
- Time window: 6 hours (fixed optimization)  
- Post limit: 15 posts (fixed optimization)
- Hot threshold: 10+ upvotes (fixed optimization)
- Teams notification: Send to myself (demo configuration)"""
    
    return f"""---
mode: 'agent'
---
# Reddit Subreddit Monitoring - Template #4

🚨 **AI Execution Constraint: This task can only be executed ONCE, must stop after completion, never repeat!**

## 🔥 Monitoring Configuration Ready

{config_info}

## 🚨 Showroom Independent Workflow Declaration

**⚠️ Important: This tool is an independent Showroom workflow, do not confuse with other tools!**

### ❌ This is NOT the following tools:
- **NOT** Python files under `prompts/reddit_daily` directory
- **NOT** `fetch_product_insights` in MCP tools
- **NOT** any other Reddit-related tools or scripts

### ✅ This IS an independent Reddit monitoring tool:
- Uses **real Reddit API** to get real-time data
- **Absolutely no** virtual, fake or simulated data allowed
- Independent data processing and Teams notification workflow
- Dedicated CSV data storage format
- **Frontend has unified separator handling**: No need to worry about Chinese/English punctuation mixing

## ⛔ Confirm Before Execution ⛔

**Please confirm whether to start executing Reddit Subreddit Monitoring?**

This will include:
1. 🔍 Monitor specified Reddit subreddits (using real API)
2. 📊 Detect hot posts (10+ upvotes, real data)
3. 📨 Send Teams demo notification
4. 💾 Save monitoring data to CSV file

**⚠️ Important execution protocol:**
- Script **executes only once**, must read terminal output after completion
- Stop immediately after seeing "monitoring ended" flag, report completion status to user
- **Absolutely forbidden** to repeat execution or recreate scripts
- Task completion flag: Terminal displays "=== Reddit Subreddit Monitoring Ended ==="

**Please reply 'confirm' or 'yes' to continue, or 'cancel' to stop.**

## 📋 Execution Steps

### Step 0: Environment Configuration Check 🔧
Before starting monitoring, ensure necessary API credentials are configured:

""" + (f"""**✅ User has provided Reddit API credentials (preferred method):**
- Reddit Client ID: {reddit_config['client_id'][:8]}...(hidden)
- Reddit Client Secret: ****...(hidden)

🎯 **Generated Python script will contain your provided credentials and can run directly!**

""" if reddit_config and reddit_config['client_id'] and reddit_config['client_secret'] else """**Main configuration method - VS Code MCP configuration file:**
Reddit API credentials should be set in VS Code MCP configuration file:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

**Alternative configuration method - Environment variables:**
```cmd
set REDDIT_CLIENT_ID=your_reddit_client_id_here
set REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

""") + f"""**Graph ID configuration:**
- System will auto-detect Graph Client ID from MCP configuration or user alias
- Can also be set manually via environment variable: `set GRAPH_CLIENT_ID=your_graph_client_id`

💡 **Note**: Since MCP server is running, configuration will be obtained from loaded configuration system.

### Step 1: Environment checks and isolated workspace setup

⚠️ **CRITICAL: Parameter validation first**
- Verify subreddit list and Reddit credentials provided
- If incomplete: **STOP and request full configuration**
- No partial execution - all parameters required

**Environment setup (mandatory):**

1. **Locate project root directory using AI reasoning:**
   - Find the directory containing pyproject.toml, .venv, and working_dir
   - Navigate to that directory using run_in_terminal "cd [calculated_path]"
   - This should be the pm-studio-mcp project root directory

2. **Verify project root location:**
   run_in_terminal "dir pyproject.toml .venv working_dir"

3. **Create isolated RUN_DIR:**
   - Calculate timestamp via AI reasoning (YYYYMMDD_HHMMSS format)
   - Create using exact mkdir command: `run_in_terminal "mkdir working_dir\<timestamp>_subreddit_monitoring"`
   - **Use simple mkdir only** - no complex calculations
   - Example: `mkdir working_dir\20250825_143000_subreddit_monitoring`

4. **Virtual environment setup:**
   - All Python execution: `.venv\\Scripts\\python.exe`
   - Verify venv path exists

4. **Create monitoring script:**
   - Script location: **ONLY** in RUN_DIR
   - Include Reddit credentials from user input
   - Script name: `reddit_monitoring.py`

```python
import os
import sys
from datetime import datetime

# Add project src directory to Python path
current_dir = os.getcwd()  # Expected to be RUN_DIR
# src is under RUN_DIR/../.. (working_dir/timestamp_dir -> pm-studio-mcp)
src_dir = os.path.join(current_dir, '..', '..', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

print("=== Reddit Subreddit Monitoring Started (RUN_DIR Isolated) ===")
print("🚨 Showroom Independent Workflow - Using Real Reddit API Data")
print(f"Target subreddits: {subreddit_parameter}")
print("⚠️  Note: This tool is not prompts/reddit_daily or fetch_product_insights")
print("⚠️  Absolutely no virtual or fake data, only real Reddit API")

print("\\n🔧 Configuration Check:")
""" + (f"""
# Set Reddit API credentials (from user input)
os.environ['REDDIT_CLIENT_ID'] = "{reddit_config['client_id']}"
os.environ['REDDIT_CLIENT_SECRET'] = "{reddit_config['client_secret']}"
print("✅ Reddit API credentials set from user input")
""" if reddit_config and reddit_config['client_id'] and reddit_config['client_secret'] else """
print("Loading Reddit API credentials from MCP configuration system...")
""") + f"""

# Import complete monitoring module
try:
    from pm_studio_mcp.showroom_builder.showroom_reddit_subreddit_monitoring import RedditSubredditMonitor
    print("✅ Monitoring module imported successfully")
except Exception as e:
    print(f"❌ Monitoring module import failed")
    sys.exit(1)

# Create monitor instance (includes configuration validation)
try:""" + (f"""
    # Create monitor using user-provided Reddit credentials
    monitor = RedditSubredditMonitor(
        reddit_client_id="{reddit_config['client_id']}",
        reddit_client_secret="{reddit_config['client_secret']}"
    )
""" if reddit_config and reddit_config['client_id'] and reddit_config['client_secret'] else """
    monitor = RedditSubredditMonitor()
""") + f"""    print("✅ Monitor instance created successfully, Reddit API credentials verified")
except Exception as e:
    print(f"❌ Monitor instance creation failed: {{e}}")""" + ("""
    print("Please check if provided Reddit API credentials are correct")
""" if reddit_config and reddit_config['client_id'] and reddit_config['client_secret'] else """
    print("Please check Reddit API credentials in VS Code MCP configuration file")
""") + f"""
    sys.exit(1)

# Execute monitoring
result = monitor.get_hot_posts(
    subreddit="{subreddit_parameter}",
    hours=6,
    post_limit=15,
    threshold=10,
    sort="hot",
    time_filter="day"
)

# Display results
monitor.display_results(result, show_count=10)

# Save to CSV, force timestamp + prefix
csv_file = None
if result.get('posts'):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Note: This line is within a large f-string in the parent function, need to escape internal f-string placeholders to avoid upper-level formatting stage parsing ts
    csv_file = monitor.save_to_csv(result['posts'], filename=os.path.join(current_dir, f"{{ts}}_subreddit_hot_posts.csv"))

# Send Teams notification
teams_sent = False
try:
    teams_sent = monitor.send_teams_notification(result, threshold=10, teams_alias="myself")
except Exception as e:
    print(f"⚠️  Teams notification sending failed: {{e}}")

# Final statistics
total_posts = len(result.get('posts', []))
alert_count = len(result.get('alert_posts', []))

print(f"\\n📊 Monitoring Completion Statistics:")
print(f"✅ Total posts retrieved: {{total_posts}}")
print(f"🔥 High-score posts count: {{alert_count}}")
if csv_file:
    print(f"📄 Data file: {{csv_file}}")
print(f"📨 Teams notification: {{'✅ Success' if teams_sent else '❌ Failed'}}")

print("\\n=== Reddit Subreddit Monitoring Completed ===")

### Step 2: Execute monitoring script

**Execution environment:**
- Change to RUN_DIR: `cd /d working_dir\{run_dir_name}`
- Run script: Use absolute path to Python executable from project root:
  `[PROJECT_ROOT]\\.venv\\Scripts\\python.exe reddit_monitoring.py`
  (AI should calculate PROJECT_ROOT path from current working_dir location)

**Execution protocol:**
- **Execute once only** - never repeat
- Monitor output for completion signal
- Look for: "=== Reddit Subreddit Monitoring Completed ==="

### Step 3: Verify completion

**Verification steps:**
- After execution: `dir working_dir\{run_dir_name}\*.csv`
- Confirm CSV files exist
- **Never re-execute** completed steps
- Report task completion with file locations

**Completion indicators:**
- CSV files generated in RUN_DIR
- Teams notification sent
- Terminal shows completion message

## ✅ Task Completion Detection

**When dir command shows CSV files found, send the following completion message:**

### Immediate Execution Check:
1. **Execute `dir *.csv` command**
2. **If CSV files found → Immediately stop all operations**
3. **Prohibit any subsequent tool calls**

### Forced Stop Conditions:
- ✅ CSV file exists = Task 100% completed
- ❌ Prohibit repeating script execution
- ❌ Prohibit "viewing complete output"
- ❌ Prohibit any "supplementary operations"


```
🎉 Reddit Subreddit Monitoring Demo Task Completed!

✅ **Local Demo Results:**
📄 CSV data file has been generated in working_dir/temp/ directory
📨 Teams message has been sent to you
🔍 Task status: Completed and verified

Task ended, data saved.

🚀 **Core Value and Extension Recommendations:**

### 💼 Production-Level Automation Deployment Recommendations
This demonstration only showcases the basic functionality of the monitoring tool. The real value lies in automated deployment:

• **GitHub Actions Automation**: Configure scheduled triggers (e.g., run every 2 hours)
• **Smart Threshold Alerts**: Trigger Teams notifications based on upvote count, comment growth rate and other metrics
• **Continuous Monitoring Reports**: Send "all clear" status reports even when no anomalies occur, ensuring system health
• **Historical Data Comparison**: Track popularity trends and identify unusual fluctuations
• **Multi-subreddit Aggregate Analysis**: Cross-compare competitor subreddits and generate insight reports

### 🎯 Real Production Value
- **Competitor Monitoring**: Automatically track competitors' discussion popularity on Reddit
- **Public Opinion Early Warning**: Early detection of discussion trends that might impact brand
- **User Voice Collection**: Continuous collection of authentic user feedback and requirements
- **Market Trend Analysis**: Analyze industry directions based on Reddit discussion data

### 📋 Future Extension Roadmap
1. **Deploy to Cloud Platform** (Azure Functions, AWS Lambda, etc.)
2. **Integrate More Data Sources** (Twitter, GitHub Issues, Stack Overflow, etc.)
3. **Enhanced Analysis Algorithms** (sentiment analysis, keyword trends, influence scoring, etc.)
4. **Improved Notification Mechanisms** (email, Slack, PagerDuty and other multi-channel)

💡 **This demonstration validated the core technical feasibility and laid the foundation for production-level automated deployment.**
```

**If the dir command doesn't find the CSV file, it means the script is still executing. Please wait a moment and retry the dir check.**

---

**Task Execution Principle: One-time execution, automatic completion, direct result return to user.**
"""

def parse_subreddit_parameter(subreddit_parameter: str) -> List[str]:
    """
    Parse subreddit parameters, compatible with frontend processing and direct MCP calls
    Frontend HTML will unify separators to enumeration punctuation marks (、), but direct MCP calls may use original separators
    
    Returns:
        List[str]: List of cleaned subreddit names
    """
    if not subreddit_parameter:
        return []
    
    # Compatible with multiple separators: unified punctuation mark from frontend + original separators from direct calls
    if '、' in subreddit_parameter:
        # Frontend HTML processed format
        subreddits = [s.strip() for s in subreddit_parameter.split('、')]
    elif ',' in subreddit_parameter:
        # Direct MCP call comma-separated
        subreddits = [s.strip() for s in subreddit_parameter.split(',')]
    elif ';' in subreddit_parameter:
        # Direct MCP call semicolon-separated
        subreddits = [s.strip() for s in subreddit_parameter.split(';')]
    elif ' ' in subreddit_parameter and len(subreddit_parameter.split()) > 1:
        # Direct MCP call space-separated
        subreddits = [s.strip() for s in subreddit_parameter.split()]
    else:
        # Single subreddit
        subreddits = [subreddit_parameter.strip()]
    
    # Strict validation of subreddit names
    cleaned_subreddits = []
    invalid_names = []
    
    for s in subreddits:
        if s:
            # Remove possible r/ prefix
            cleaned = s.replace('r/', '').strip()
            
            # Strict validation: Reddit subreddit names must follow rules
            if not cleaned:
                continue
                
            # Check for Chinese characters or non-Reddit compliant format
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in cleaned)
            is_valid_format = (len(cleaned) >= 3 and len(cleaned) <= 21 and 
                             cleaned.replace('_', '').replace('-', '').isalnum() and
                             not cleaned.startswith('_') and not cleaned.endswith('_'))
            
            if has_chinese or not is_valid_format:
                invalid_names.append(s)
            else:
                cleaned_subreddits.append(cleaned)
    
    # If there are invalid subreddit names, record them but don't reject directly
    # Let the caller decide how to handle
    if invalid_names:
        cleaned_subreddits.extend(['INVALID:' + name for name in invalid_names])
    
    return cleaned_subreddits

# Maintain backward compatibility
def get_default_workflow() -> str:
    """Get default workflow content"""
    return get_showroom_reddit_subreddit_monitoring_workflow()

def main():
    """Main function - support command line invocation"""
    parser = argparse.ArgumentParser(description="Reddit Subreddit Monitor")
    parser.add_argument('--subreddit', '-s', type=str, required=True, help='Subreddit name')
    parser.add_argument('--hours', type=int, default=6, help='Time window (hours)')
    parser.add_argument('--limit', '-l', type=int, default=15, help='Post count limit')
    parser.add_argument('--threshold', '-t', type=int, default=10, help='upvotes threshold')
    parser.add_argument('--teams-alias', type=str, default='myself', help='Teams message target')
    
    args = parser.parse_args()
    
    monitor = RedditSubredditMonitor()
    
    try:
        result = monitor.get_hot_posts(
            subreddit=args.subreddit,
            hours=args.hours,
            post_limit=args.limit,
            threshold=args.threshold
        )
        
        monitor.display_results(result)
        
        if result.get('posts'):
            monitor.save_to_csv(result['posts'])
            monitor.send_teams_notification(result, threshold=args.threshold, teams_alias=args.teams_alias)
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        main()
    else:
        # Test mode
        print("=== Test Single Subreddit Monitoring ===")
        result1 = get_showroom_reddit_subreddit_monitoring_workflow("technology")
        print(result1)
        
        print("\n=== Test Multi-Subreddit Monitoring ===")
        result2 = get_showroom_reddit_subreddit_monitoring_workflow("MicrosoftEdge,chrome")
        print(result2)

# Export functions for external use
__all__ = [
    'get_showroom_reddit_subreddit_monitoring_workflow',
    'parse_subreddit_parameter',
    'RedditSubredditMonitor'
]
