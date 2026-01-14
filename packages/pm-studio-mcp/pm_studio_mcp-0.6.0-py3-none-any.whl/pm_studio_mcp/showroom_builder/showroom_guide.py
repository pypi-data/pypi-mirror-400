"""
Showroom Guide System
This module provides the unified Showroom workflow guide and capabilities## How to use
Pick the template you need. You'll get:
- Step-by-step guidance with interactive confirmations
- Exact MCP tool invocation hints
- A complete analysis process and outputs

## ⚠️ Final Reminder
**Before executing any workflow:**
1. ✅ Confirm the user has provided ALL required parameters
2. ✅ Validate parameter format and completeness  
3. ✅ Ask for clarification if anything is missing or unclear
4. ❌ NEVER assume or guess missing parameters
5. ❌ NEVER proceed with partial or unclear information

**All workflows require explicit user input - no assumptions allowed.**view.
"""

# Unified template descriptions configuration
WORKFLOW_TEMPLATES = {
    "showroom_simple_data_analysis": {
        "name": "Simple Data Analysis - Lightweight Metrics Template",
        "description": [
            "Use cases: Periodic analysis of 1–2 metrics",
            "Template traits: Customizable metrics and periods, AI-generated professional report",
            "Execution flow: Smart source selection → AI analysis + auto visualization → Personalized HTML report",
            "Highlights: Filename includes the metric; supports line and bar charts"
        ]
    },
    "showroom_reddit_user_voice_insight": {
        "name": "Reddit User Voice Insight - User Feedback Insight Template",
        "description": [
            "Use cases: Product user feedback analysis and market insights",
            "Template traits: Mine needs, pains, and opportunities from Reddit discussions",
            "Execution flow: Data collection → Cleaning & filtering → 5+5+5 structured analysis → Professional Apple-style report",
            "Highlights: Modern HTML report with user voice overview, needs & pains analysis, and product opportunities"
        ]
    },
    "showroom_reddit_subreddit_monitoring": {
        "name": "Reddit Subreddit Monitoring - Automated Monitoring Template",
        "description": [
            "Use cases: Continuous hot-post monitoring and alerting across multiple subreddits; supports competitor combinations",
            "Template traits: Smart threshold-based hot-post detection with optimized defaults (10+ upvotes), minimal configuration",
            "Subreddit input: Single or multiple; intelligently parses comma/semicolon/space-separated formats",
            "Execution flow: Configure topics → Detect hot posts → Teams notify → Store data (4-step automated flow)",
            "Highlights: Complements the user insight template; focuses on hot-post discovery over keyword search; cron-friendly",
            "Examples: Browser competitors (MicrosoftEdge,chrome,firefox) | Dev communities (programming;webdev;javascript) | Tech mix (technology browsers apps)",
            "Automation: Ready for cron/Task Scheduler for continuous PM competitor tracking"
        ]
    },
    "showroom_cnaibrowser": {
        "name": "CN AI Browser Analysis - China AI Browser Competitive Analysis",
        "description": [
            "Use cases: In-depth competitive analysis and business insights for China AI browsers",
            "Template traits: Professional Titan-based analysis; customizable time period; 5 core charts",
            "Execution flow: Time period setup → Titan auto query → Pro analysis engine → Interactive HTML report",
            "Highlights: DAD comparison, BSoM analysis, market impact quantification, AI browser trends, etc.",
            "Dimensions: Edge vs competitors, AI browser impact, share changes, usage minutes, ...",
            "Business value: Data-backed insights for browser strategy and competitor playbooks"
        ]
    }
}

SHOWROOM_GUIDE_TEMPLATE = """---
mode: 'agent'
---
# PM Studio Showroom Workflow Guide

## ⚠️ Important Notes ⚠️
Showroom includes multiple data analysis templates with different capabilities. **Each template requires specific parameters to function properly.**

**🚨 CRITICAL: DO NOT proceed with any workflow without confirming all required parameters with the user.**

After you choose, the system will confirm with you and execute the corresponding workflow.

## Core capabilities
This professional PM Studio workflow system includes several templates:
1. Simple Data Analysis: smart analysis flow (Titan → AI Analysis) **[Requires: metric name]**
2. Reddit User Voice Insight: professional user feedback and market insights **[Requires: product name]**
3. Reddit Subreddit Monitoring: automated hot-post monitoring and alerts **[Requires: subreddit list + Reddit API credentials]**
4. CN AI Browser Analysis: in-depth analysis for China AI browsers **[Requires: time period]**
5. More templates coming soon

## 🔒 Parameter Validation Rules
- **NEVER assume parameters**: Always ask users to provide required parameters explicitly
- **NEVER proceed with incomplete information**: Each workflow has mandatory parameters
- **ALWAYS validate before execution**: Confirm all parameters are provided and valid

The system will provide interactive guidance based on your selection.

## 🔥 Reddit monitoring templates at a glance
3 vs 4 — complementary:
- 3 (User Voice Insight): keyword search → deep analysis → insight report
- 4 (Subreddit Monitoring): multi-subreddit monitoring → hot-post discovery → automated alerts

Accepted subreddit formats for template 4:
- Single: `MicrosoftEdge`
- Multiple: `MicrosoftEdge,chrome,firefox` or `programming;webdev;javascript` or `technology browsers apps`
- Mixed separators are recognized: commas, semicolons, spaces

## Available workflows

{showroom_workflows}

## How to use
Pick the template you need. You’ll get:
- Step-by-step guidance with interactive confirmations
- Exact MCP tool invocation hints
- A complete analysis process and outputs

Each template has its own strengths; choose based on your scenario.
"""

def _setup_import_path():
    """Setup import path for local modules."""
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def _format_template_description(template_key: str) -> str:
    """Format template description from WORKFLOW_TEMPLATES."""
    if template_key not in WORKFLOW_TEMPLATES:
        return f"Unknown template: {template_key}"
    
    template = WORKFLOW_TEMPLATES[template_key]
    description_lines = [f"**{template['name']}**"]
    for desc in template['description']:
        description_lines.append(f"- {desc}")
    
    return "\n".join(description_lines)

def _detect_intent_from_text(user_text: str) -> str:
    """
    Heuristically detect intent from user text and recommend an appropriate Showroom template.
    
    Args:
        user_text (str): User input text
        
    Returns:
        str: Recommended template key
    """
    if not user_text:
        return "default"
    
    user_text_lower = user_text.lower()
    
    # CN AI Browser analysis keywords (Chinese keywords kept for matching)
    cnaibrowser_keywords = [
        "cn ai browser", "中国ai浏览器", "浏览器竞品", "browser competition",
        "edge bsom", "chrome bsom", "doubao", "quark", "360浏览器",
        "浏览器分析", "browser analysis", "竞品分析", "competitive analysis",
        "市场份额", "market share", "浏览器数据", "browser data"
    ]
    
    # Reddit subreddit monitoring keywords (Chinese keywords kept for matching)
    reddit_monitoring_keywords = [
        "监控reddit", "monitor reddit", "reddit监控", "reddit热帖",
        "多版块", "subreddit", "版块监控", "竞品版块", "competitor subreddit",
        "自动化reddit", "automated reddit", "版块热度", "subreddit activity",
        "热帖监控", "hot post monitoring", "版块跟踪", "subreddit tracking"
    ]
    
    # Reddit user voice insight keywords (Chinese keywords kept for matching)
    reddit_insight_keywords = [
        "用户声音", "user voice", "reddit分析", "reddit analysis",
        "用户反馈", "user feedback", "市场洞察", "market insight",
        "产品反馈", "product feedback", "关键词搜索", "keyword search"
    ]
    
    # Simple data analysis keywords (Chinese keywords kept for matching)
    data_analysis_keywords = [
        "数据分析", "data analysis", "指标分析", "metrics analysis",
        "dau", "mau", "retention", "bsom", "chrome", "edge",
        "titan", "数据查询", "data query"
    ]
    
    # 检查CN AI Browser分析相关
    if any(keyword in user_text_lower for keyword in cnaibrowser_keywords):
        return "showroom_cnaibrowser"
    
    # 检查Reddit监控相关
    if any(keyword in user_text_lower for keyword in reddit_monitoring_keywords):
        return "showroom_reddit_subreddit_monitoring"
    
    # 检查Reddit洞察相关
    if any(keyword in user_text_lower for keyword in reddit_insight_keywords):
        return "showroom_reddit_user_voice_insight"
    
    # 检查数据分析相关
    if any(keyword in user_text_lower for keyword in data_analysis_keywords):
        return "showroom_simple_data_analysis"
    
    return "default"

def _validate_workflow_parameters(workflow_type: str, metric_parameter) -> tuple:
    """
    统一的workflow参数验证器 - Showroom参数完整性检查
    
    Args:
        workflow_type (str): 工作流类型
        metric_parameter: 用户提供的参数
        
    Returns:
        tuple: (is_valid: bool, error_template: str)
    """
    
    parameter_requirements = {
        "showroom_simple_data_analysis": {
            "validation": lambda p: p is not None and str(p).strip() != "",
            "error_template": """---
mode: 'agent'
---
# ❌ Showroom Parameter Validation Failed

## Missing Required Parameter: Metric Name

**Workflow:** Simple Data Analysis
**Issue:** No metric specified for analysis

### Required Parameter:
- **metric_parameter**: A specific metric to analyze (e.g., "Edge Mobile DAU", "Chrome retention rate", "Quark BSoM")

### Example Usage:
```
get_showroom_guide("your_name", "showroom_simple_data_analysis", "Edge Mobile DAU")
```

### Sample Metrics:
- "Edge Mobile DAU" — Daily active users for Edge Mobile
- "Quark BSoM" — Monthly usage for Quark browser  
- "Chrome retention rate" — Chrome user retention analysis

**Please ask the user to specify which metric they want to analyze, then call the showroom guide again with the metric parameter.**"""
        },
        
        "showroom_reddit_user_voice_insight": {
            "validation": lambda p: p is not None and str(p).strip() != "",
            "error_template": """---
mode: 'agent'
---
# ❌ Showroom Parameter Validation Failed

## Missing Required Parameter: Product Name

**Workflow:** Reddit User Voice Insight
**Issue:** No product specified for analysis

### Required Parameter:
- **metric_parameter**: A specific product name to analyze (e.g., "Microsoft Edge", "ChatGPT", "Perplexity")

### Example Usage:
```
get_showroom_guide("your_name", "showroom_reddit_user_voice_insight", "Microsoft Edge")
```

### Sample Products:
- "Microsoft Edge" — Browser product analysis
- "ChatGPT" — AI conversation product analysis  
- "Perplexity" — AI search product analysis
- "Claude" — Anthropic AI analysis

**Please ask the user to specify which product they want to analyze, then call the showroom guide again with the product name.**"""
        },
        
        "showroom_reddit_subreddit_monitoring": {
            "validation": lambda p: (
                isinstance(p, dict) and 
                p.get('topics') and 
                str(p.get('topics')).strip() != "" and
                p.get('reddit_client_id') and 
                str(p.get('reddit_client_id')).strip() != "" and
                p.get('reddit_client_secret') and 
                str(p.get('reddit_client_secret')).strip() != ""
            ) if isinstance(p, dict) else False,
            "error_template": """---
mode: 'agent'
---
# ❌ Showroom Parameter Validation Failed

## Missing Required Parameters: Subreddit Topics AND Reddit API Credentials

**Workflow:** Reddit Subreddit Monitoring
**Issue:** Incomplete configuration - requires both subreddit list and Reddit API credentials

### Required Parameters (ALL required in single call):
- **topics**: Subreddit names to monitor
- **reddit_client_id**: Reddit API Client ID
- **reddit_client_secret**: Reddit API Client Secret

### Example Usage:
```
get_showroom_guide("your_name", "showroom_reddit_subreddit_monitoring", {
    "topics": "MicrosoftEdge,chrome,firefox", 
    "reddit_client_id": "your_reddit_client_id", 
    "reddit_client_secret": "your_reddit_client_secret"
})
```

### Sample Topics:
- Browser competitors: "MicrosoftEdge,chrome,firefox"
- Developer communities: "programming,webdev,javascript"  
- Tech discussions: "technology,browsers,apps"

### Get Reddit API Credentials:
1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" → Choose "script" type
3. Get Client ID and Client Secret

**⚠️ Important: This tool requires complete configuration in one call. Please ask the user to provide both subreddit topics AND Reddit API credentials, then call the showroom guide again with all parameters.**"""
        },
        
        "showroom_cnaibrowser": {
            "validation": lambda p: p is not None and str(p).strip() != "",
            "error_template": """---
mode: 'agent'
---
# ❌ Showroom Parameter Validation Failed

## Missing Required Parameter: Time Period

**Workflow:** CN AI Browser Analysis
**Issue:** No time period specified for analysis

### Required Parameter:
- **metric_parameter**: A specific time period to analyze (e.g., "last 30 days", "2024-01-01 to 2024-01-31")

### Example Usage:
```
get_showroom_guide("your_name", "showroom_cnaibrowser", "last 30 days")
```

### Sample Time Periods:
- "last 30 days" — Recent 30-day analysis
- "last 7 days" — Weekly analysis
- "2024-01-01 to 2024-01-31" — Specific date range
- "last quarter" — Quarterly analysis

**Please ask the user to specify which time period they want to analyze, then call the showroom guide again with the time period parameter.**"""
        }
    }
    
    # 检查是否为已知的workflow类型
    if workflow_type not in parameter_requirements:
        return True, ""  # 未知类型不拦截，交给下层处理
    
    req = parameter_requirements[workflow_type]
    if not req["validation"](metric_parameter):
        return False, req["error_template"]
    
    return True, ""

def _get_workflow_content(workflow_type: str, metric_parameter = None, template_name: str = "basic") -> str:
    """Get workflow content by type."""
    
    # 🚨 统一参数验证 - Showroom参数完整性检查
    is_valid, error_template = _validate_workflow_parameters(workflow_type, metric_parameter)
    if not is_valid:
        return error_template
    
    _setup_import_path()
    
    workflow_modules = {
        "showroom_simple_data_analysis": ("showroom_simple_data_analysis", "get_showroom_simple_data_analysis_workflow"),
        "showroom_reddit_user_voice_insight": ("showroom_reddit_user_voice_insight", "get_showroom_reddit_user_voice_insight_workflow"),
        "showroom_reddit_subreddit_monitoring": ("showroom_reddit_subreddit_monitoring", "get_showroom_reddit_subreddit_monitoring_workflow"),
        "showroom_cnaibrowser": ("showroom_cnaibrowser", "get_showroom_cnaibrowser_workflow")
    }
    
    if workflow_type in workflow_modules:
        module_name, function_name = workflow_modules[workflow_type]
        try:
            module = __import__(module_name)
            # Special handling for workflows that need parameters
            if workflow_type == "showroom_simple_data_analysis":
                return getattr(module, function_name)(metric_parameter, template_name)
            elif workflow_type == "showroom_reddit_user_voice_insight":
                return getattr(module, function_name)(metric_parameter, template_name)
            elif workflow_type == "showroom_reddit_subreddit_monitoring":
                # Note: metric_parameter for this workflow supports multiple formats:
                # - String formats: "MicrosoftEdge,chrome,firefox" or "programming;webdev;javascript" or "technology browsers apps"
                # - Dict format: {"topics": "浏览器", "reddit_client_id": "xxx", "reddit_client_secret": "yyy"}
                # The implementation should intelligently parse all formats
                return getattr(module, function_name)(metric_parameter, template_name)
            elif workflow_type == "showroom_cnaibrowser":
                # Note: metric_parameter for this workflow is the time period (e.g., "last 30 days", "2024-01-01 to 2024-01-31")
                return getattr(module, function_name)(metric_parameter, template_name)
            else:
                return getattr(module, function_name)()
        except ImportError as e:
            return f"Workflow {workflow_type} is not implemented yet. Import error: {str(e)}"
        except Exception as e:
            return f"Workflow {workflow_type} failed: {str(e)}"
    
    # Default placeholder content for general workflows
    return """
Available templates:
- showroom_simple_data_analysis: Simple data analysis template
- showroom_reddit_user_voice_insight: Reddit user voice insight (keyword-driven)
- showroom_reddit_subreddit_monitoring: Reddit subreddit monitoring (subreddit-driven; supports comma/semicolon/space separated lists)
- showroom_cnaibrowser: CN AI Browser competitive analysis (time period-driven)

Pick a template and the system will confirm, then execute the workflow.

Multiple subreddit examples:
- Browser competitors: "MicrosoftEdge,chrome,firefox"
- Developer communities: "programming;webdev;javascript"  
- Tech mix: "technology browsers apps"
"""

def _get_showroom_prompt_content(intent: str = "default", metric_parameter = None, template_name: str = "basic") -> str:
    """
    Get the Showroom prompt content with dynamically loaded content based on intent.
    
    Args:
        intent (str): The specific intent to customize the prompt for. 
                     Options: "showroom_simple_data_analysis", "default"
        metric_parameter (Union[str, dict], optional): User specified analysis metric, supports string and dict formats
        template_name (str, optional): Template name for custom workflows (deprecated, only "basic" is supported)
                     
    Returns:
        str: The complete Showroom prompt content with intent-specific content injected
    """
    # Define workflow mapping
    workflow_mapping = {
        "showroom_simple_data_analysis": "showroom_simple_data_analysis_workflow",
        "showroom_reddit_user_voice_insight": "showroom_reddit_user_voice_insight_workflow",
        "showroom_reddit_subreddit_monitoring": "showroom_reddit_subreddit_monitoring_workflow",
        "showroom_cnaibrowser": "showroom_cnaibrowser_workflow"
    }
    
    if intent == "default":
        # For default, show overview of available workflows using unified template descriptions
        template_descriptions = []
        for template_key in ["showroom_simple_data_analysis", "showroom_reddit_user_voice_insight", "showroom_reddit_subreddit_monitoring", "showroom_cnaibrowser"]:
            template_descriptions.append(_format_template_description(template_key))
        
        workflows_content = f"""
### Available templates:

{chr(10).join(template_descriptions)}

### How to select a template:
Run one of the following; the system will confirm then start:
- `get_showroom_guide("your_name", "showroom_simple_data_analysis")` - pick the simple data analysis template
- `get_showroom_guide("your_name", "showroom_simple_data_analysis", "metric name")` - specify the metric directly
- `get_showroom_guide("your_name", "showroom_reddit_user_voice_insight")` - pick Reddit user voice insight
- `get_showroom_guide("your_name", "showroom_reddit_user_voice_insight", "product name")` - specify the product directly
- `get_showroom_guide("your_name", "showroom_cnaibrowser")` - pick CN AI Browser analysis
- `get_showroom_guide("your_name", "showroom_cnaibrowser", "last 30 days")` - specify the time period

### 🚨 Reddit monitoring template - requires full configuration:
⚠️ Provide all required info in one call; stepwise config is not supported.

Required format (must include Reddit credentials):
```
get_showroom_guide("your_name", "showroom_reddit_subreddit_monitoring", {{
    "topics": "topics", 
    "reddit_client_id": "your_reddit_client_id", 
    "reddit_client_secret": "your_reddit_client_secret"
}})
```

Examples:
- Browsers: `{{"topics": "MicrosoftEdge、chrome、firefox", "reddit_client_id": "xxx", "reddit_client_secret": "yyy"}}`
- Dev communities: `{{"topics": "programming、webdev、javascript", "reddit_client_id": "xxx", "reddit_client_secret": "yyy"}}`
- Tech mix: `{{"topics": "technology、browsers、apps", "reddit_client_id": "xxx", "reddit_client_secret": "yyy"}}`

Notes:
- Provide both topics and Reddit API credentials in one call
- Calls with only subreddit names are not supported
- Frontend normalizes separators to the Chinese enumeration comma（、）

Each template confirms parameters and details before execution.
"""
    elif intent in workflow_mapping:
        # For specific intent, load only that workflow with metric_parameter and template_name
        if intent == "showroom_reddit_user_voice_insight":
            workflows_content = _get_workflow_content(intent, metric_parameter, template_name)
        elif intent == "showroom_reddit_subreddit_monitoring":
            # If no metric_parameter provided, return guidance content
            if not metric_parameter:
                workflows_content = f"""## 🔥 Reddit Subreddit Monitoring - Template 4

### ⚠️ Missing required parameters

This workflow requires the following:
1. Subreddit list to monitor
2. Reddit API credentials: Client ID and Client Secret

### 📝 Provide information in this format:

⚠️ Important: Provide topics and Reddit credentials in a single call.

Example:
```
get_showroom_guide("user", "showroom_reddit_subreddit_monitoring", {{"topics": "MicrosoftEdge,chrome,firefox", "reddit_client_id": "your_client_id", "reddit_client_secret": "your_client_secret"}})
```

### 🚨 Notes:
- No stepwise input: provide subreddits and credentials together
- No partial execution: monitoring won’t run if anything is missing
- Keep credentials intact when transforming the command

Supported subreddit formats:
- Single: `"MicrosoftEdge"`
- Multiple (comma): `"MicrosoftEdge,chrome,firefox"`
- Multiple (semicolon): `"programming;webdev;javascript"`
- Multiple (space): `"technology browsers apps"`

### 🔑 Get Reddit API credentials:

1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" type
4. Retrieve Client ID and Client Secret

### 💡 Usage suggestions:

Browser competitors:
```
{{"topics": "MicrosoftEdge,chrome,firefox,browsers", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}}
```

Developer communities:
```
{{"topics": "programming;webdev;javascript", "reddit_client_id": "your_id", "reddit_client_secret": "your_secret"}}
```

### 🔄 Independent flow notice:

This tool is an independent Showroom flow and is different from:
- ❌ Python files under `prompts/reddit_daily`
- ❌ MCP tool `fetch_product_insights`
- ❌ Any mock/synthetic data usage
- ✅ A standalone Reddit API monitoring tool using real data

Please re-invoke with complete configuration.
"""
            else:
                workflows_content = _get_workflow_content(intent, metric_parameter, template_name)
        else:
            workflows_content = _get_workflow_content(intent, metric_parameter, template_name)
    else:
        # Unknown intent, fallback to default
        workflows_content = "Unknown template type. Choose one of: 'showroom_simple_data_analysis', 'showroom_reddit_user_voice_insight', 'showroom_reddit_subreddit_monitoring', or 'showroom_cnaibrowser'."
    
    # Inject the workflows into the main prompt template
    return SHOWROOM_GUIDE_TEMPLATE.format(showroom_workflows=workflows_content)

def get_showroom_workflow_guide(name: str, intent: str = "default", metric_parameter = None, template_name: str = "basic") -> str:
    """
    Get a Showroom workflow guide for data analysis tasks.
    This is the unified entry point that combines greeting and workflow guidance.
    
    Args:
        name (str): User's name for personalization
        intent (str): Specific intent to customize the prompt for.
                     Options: "showroom_simple_data_analysis", "showroom_reddit_user_voice_insight", "showroom_reddit_subreddit_monitoring", "showroom_cnaibrowser", "default"
        metric_parameter (Union[str, dict], optional): User specified analysis metric, supports both string and dict formats.
                                     For string: "sub1,sub2,sub3" or "sub1;sub2;sub3" or "sub1 sub2 sub3"
                                     For dict: {"topics": "浏览器", "reddit_client_id": "xxx", "reddit_client_secret": "yyy"}
        template_name (str, optional): Template name for custom workflows (deprecated, only "basic" is supported)
    
    Returns:
        str: The complete Showroom guide content ready for use
    """
    try:
    # Do not auto-detect; only follow the user-specified intent
        # Get the appropriate prompt based on intent, passing all parameters to next layer
        prompt_content = _get_showroom_prompt_content(intent, metric_parameter, template_name)
        
        # Return the content with a personalized greeting
        return f"Use the chat: run prompt tool to run prompt from {prompt_content}"
        
        # Return the content with a personalized greeting
        return f"Use the chat: run prompt tool to run prompt from {prompt_content}"
            
    except Exception as e:
        # Fallback to the original greeting if there's any error
        return f"Hello {name}! Showroom workflow guide encountered an error: {str(e)}"

# For backward compatibility, create a default content
SHOWROOM_GUIDE = _get_showroom_prompt_content("default")
