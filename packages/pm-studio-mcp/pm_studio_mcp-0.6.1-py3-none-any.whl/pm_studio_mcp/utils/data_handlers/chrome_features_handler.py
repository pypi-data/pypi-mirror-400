from base_handler import BaseHandler
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import re
import os
import sys

# Define crawl_website as None for import failure check
crawl_website = None

try:
    import requests
except ImportError:
    print("Please install required packages: pip install requests")

# Try multiple import methods
try:
    from ..web.crawl import crawl_website  # Import crawl_website function
except ImportError as e:
    try:
        # Try adding parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from pm_studio_mcp.utils.web.crawl import crawl_website
    except ImportError:
        print(f"Warning: Could not import crawl_website from crawl_utils: {e}")
        # Fallback function if import fails
        def crawl_website(url: str) -> str:
            """Fallback crawl_website function using requests."""
            try:
                import requests
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                raise Exception(f"Error fetching URL {url}: {str(e)}")

class ChromeFeaturesHandler(BaseHandler):
    """
    Handler for Chrome features operations.
    This class is responsible for fetching Chrome version features from Chrome Status API.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChromeFeaturesHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the ChromeFeaturesHandler."""
        if self._initialized:
            return
        
        self.base_url = "https://chromestatus.com/api/v0/features"
        self.chrome_version_url = "https://chromestatus.com/api/v0/channels"
        self._initialized = True
        
        # Check if crawl_website is available
        if crawl_website is None:
            print("Warning: crawl_website function is not available")

    def get_current_chrome_version(self) -> Optional[int]:
        """
        Get the current stable Chrome version number.
        
        Returns:
            int: Current Chrome stable version milestone number
        """
        try:
            # Check if crawl_website is available
            if crawl_website is None:
                raise Exception("crawl_website function is not available")
            
            # Use crawl_website to get version info
            response_text = crawl_website(self.chrome_version_url)
            
            # Clean up possible special characters
            response_text = self._clean_json_response(response_text)
            
            # Parse JSON
            channels_data = json.loads(response_text)
            
            # Handle new data structure: dictionary form, keys are channel names
            if isinstance(channels_data, dict):
                # Check if 'stable' key exists
                if 'stable' in channels_data:
                    stable_data = channels_data['stable']
                    if isinstance(stable_data, dict):
                        # Get milestone from stable data
                        milestone = stable_data.get('milestone')
                        if milestone is not None:
                            try:
                                return int(milestone)
                            except (ValueError, TypeError):
                                pass
                        
                        # If no milestone, try to extract from version
                        version = stable_data.get('version')
                        if version is not None:
                            # version could be int or str
                            if isinstance(version, (int, float)):
                                return int(version)
                            elif isinstance(version, str):
                                # Extract the first part of the version as milestone
                                # For example "131.0.6778.85" -> 131
                                version_parts = version.split('.')
                                if version_parts:
                                    try:
                                        return int(version_parts[0])
                                    except ValueError:
                                        pass
                        
                        # Print stable_data content for debugging
                        print(f"Stable channel data: {stable_data}")
                        print(f"Available fields in stable: {list(stable_data.keys())}")
                
                # If all above methods fail, try to iterate over all channels
                for channel_name, channel_data in channels_data.items():
                    if channel_name.lower() == 'stable' and isinstance(channel_data, dict):
                        milestone = channel_data.get('milestone')
                        if milestone is not None:
                            try:
                                return int(milestone)
                            except (ValueError, TypeError):
                                pass
            
            # Handle case where data might be a list (old format)
            elif isinstance(channels_data, list):
                # Look for stable version
                for channel in channels_data:
                    if isinstance(channel, dict) and channel.get('channel') == 'stable':
                        milestone = channel.get('milestone')
                        if milestone is not None:
                            try:
                                return int(milestone)
                            except (ValueError, TypeError):
                                pass
            
            # If not found, print data structure for debugging
            print(f"Could not find stable version in data structure: {type(channels_data)}")
            print(f"Available keys: {list(channels_data.keys()) if isinstance(channels_data, dict) else 'N/A'}")
            
            return None
            
        except Exception as e:
            print(f"Error getting current Chrome version: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean the JSON response by removing problematic characters.
        
        Args:
            response_text: Raw response text
            
        Returns:
            str: Cleaned JSON text
        """
        # Remove possible ")]}'" prefix
        if response_text.startswith(")]}'\n"):
            response_text = response_text[5:]
        elif response_text.startswith(")]}'"):
            response_text = response_text[4:]
        
        # Extract content within body tag (if exists)
        body_match = re.search(r'<body[^>]*>(.*?)</body>', response_text, re.DOTALL | re.IGNORECASE)
        if body_match:
            response_text = body_match.group(1)
        
        # Remove other HTML tags
        response_text = re.sub(r'<[^>]+>', '', response_text)
        
        return response_text.strip()

    def fetch_data(self, product_name, start_date=None, end_date=None, *args, **kwargs):
        """
        Fetch Chrome features data based on product name, date range, and version.
        
        Args:
            product_name: Name of the product (should be 'Chrome')
            start_date: Optional start date to look for Chrome versions
            end_date: Optional end date to look for Chrome versions
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments including:
                - milestone: Specific Chrome version milestone number
                - versions: List of Chrome versions
                - working_dir: Directory to save output files
                - category_filter: List of categories to filter
                - status_filter: List of statuses to filter
            
        Returns:
            Dict containing status and results
        """
        if not product_name:
            raise ValueError("Product name is required.")
        
        # Check if the product is Chrome
        if product_name.lower() != "chrome":
            return {
                "status": "error",
                "message": f"This handler only supports Chrome. Received: {product_name}"
            }
        
        # Extract parameters from kwargs
        working_dir = kwargs.get("working_dir", "")
        category_filter = kwargs.get("category_filter")
        status_filter = kwargs.get("status_filter")
        
        # Get milestone(s) from kwargs
        milestone = kwargs.get("milestone")
        versions = kwargs.get("versions", [])
        
        # If versions are provided but no milestone is set, use the first version as milestone
        if not milestone and versions:
            if isinstance(versions, list) and versions:
                milestone = versions[0]
            elif isinstance(versions, (int, str)):
                milestone = versions
        
        # If no milestone is provided but date range is, try to find Chrome versions for that period
        if not milestone and start_date and end_date:
            try:
                # Get current version as a fallback
                current_version = self.get_current_chrome_version()
                
                # In a real implementation, you would query for Chrome versions released 
                # between start_date and end_date, and use those as milestones
                # For now, we'll just use the current version
                milestone = current_version
                
                print(f"Using Chrome version {milestone} for date range {start_date} to {end_date}")
            except Exception as e:
                print(f"Error finding Chrome versions for date range: {str(e)}")
        
        # Process all milestones if multiple versions were specified
        if isinstance(versions, list) and len(versions) > 1:
            results = []
            for version in versions:
                result = self._process_single_milestone(version, working_dir, category_filter, status_filter)
                results.append(result)
            return {
                "status": "success", 
                "message": f"Processed {len(results)} Chrome versions",
                "results": results
            }
        result = handler.process_chrome_features(working_dir=working_dir)
        # Process a single milestone
        return self._process_single_milestone(milestone, working_dir, category_filter, status_filter)
    
    def _process_single_milestone(self, milestone, working_dir, category_filter, status_filter):
        """Helper method to process a single Chrome milestone"""
        try:
            # If no milestone specified, get current stable version
            if milestone is None:
                milestone = self.get_current_chrome_version()
                if milestone is None:
                    return {
                        "status": "error",
                        "message": "Could not determine current Chrome version"
                    }
            
            # Build URL
            url = f"{self.base_url}?milestone={milestone}"
            print(f"Fetching features from URL: {url}")
            
            # Use crawl_website to get data
            response_text = crawl_website(url)
            
            # Clean response text
            cleaned_response = self._clean_json_response(response_text)
            
            # Parse JSON
            features_data = json.loads(cleaned_response)
            
            # Ensure features_data is a list
            if isinstance(features_data, dict):
                # Data might be under some key
                for key in ['features', 'data', 'items']:
                    if key in features_data and isinstance(features_data[key], list):
                        print(f"Found features array in key: '{key}'")
                        features_data = features_data[key]
                        break
                else:
                    # If still a dict, convert to list
                    print("Converting dict to list")
                    features_data = [features_data]
            
            # Filter features
            filtered_features = self._filter_features(features_data, category_filter, status_filter)
            
            # Process feature data
            processed_features = []
            for feature in filtered_features:
                processed_feature = {
                    "id": feature.get("id"),
                    "name": feature.get("name", "Unknown"),
                    "summary": feature.get("summary", ""),
                    "category": self._get_category_name(feature.get("category")),
                    "status": feature.get("impl_status_chrome", "Unknown"),
                    "feature_type": feature.get("feature_type", ""),
                    "created": self._format_date(feature.get("created")),
                    "updated": self._format_date(feature.get("updated")),
                    "spec_link": feature.get("spec_link", ""),
                    "bug_url": feature.get("bug_url", ""),
                    "blink_components": feature.get("blink_components", []),
                    "browsers": {
                        "chrome": feature.get("impl_status_chrome", ""),
                        "firefox": self._get_browser_status(feature.get("ff_views", {})),
                        "safari": self._get_browser_status(feature.get("safari_views", {})),
                        "edge": self._get_browser_status(feature.get("ie_views", {}))
                    }
                }
                processed_features.append(processed_feature)
            
            # # Save results
            # output_file = f"chrome_features_v{milestone}.json"
            # if working_dir:
            #     output_file = os.path.join(working_dir, output_file)
            
            # with open(output_file, 'w', encoding='utf-8') as f:
            #     json.dump({
            #         "milestone": milestone,
            #         "features_count": len(processed_features),
            #         "generated_at": datetime.now().isoformat(),
            #         "features": processed_features
            #     }, f, indent=2, ensure_ascii=False)
            
            # Generate summary
            summary = self._generate_summary(processed_features, milestone)
            
            return {
                "status": "success",
                "milestone": milestone,
                "features_found": len(processed_features),
                "output_file": os.path.abspath(output_file),
                "summary": summary
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error fetching Chrome features: {str(e)}"
            }
    
    def _filter_features(self, features: List[Dict], 
                        category_filter: Optional[List[str]] = None,
                        status_filter: Optional[List[str]] = None) -> List[Dict]:
        """Filter features based on category and status."""
        filtered = features
        
        # Filter by category
        if category_filter:
            category_ids = [self._get_category_id(cat) for cat in category_filter]
            filtered = [f for f in filtered if f.get("category") in category_ids]
        
        # Filter by status
        if status_filter:
            filtered = [f for f in filtered 
                       if any(status.lower() in f.get("impl_status_chrome", "").lower() 
                             for status in status_filter)]
        
        return filtered
    
    def _get_category_name(self, category_id: Any) -> str:
        """Convert category ID to name."""
        category_map = {
            1: "CSS",
            2: "HTML",
            3: "JavaScript",
            4: "DOM",
            5: "Network/Connectivity",
            6: "Security",
            7: "Storage",
            8: "Misc",
            9: "Web Components",
            10: "Input",
            11: "Performance",
            12: "WebRTC",
            13: "Graphics",
            14: "Audio/Video",
            15: "Rendering",
            16: "User Interface",
            17: "Media",
            18: "WebAssembly"
        }
        
        try:
            return category_map.get(int(category_id), "Other")
        except:
            return "Other"
    
    def _get_category_id(self, category_name: str) -> int:
        """Convert category name to ID."""
        category_map = {
            "css": 1,
            "html": 2,
            "javascript": 3,
            "dom": 4,
            "network": 5,
            "connectivity": 5,
            "security": 6,
            "storage": 7,
            "misc": 8,
            "web components": 9,
            "input": 10,
            "performance": 11,
            "webrtc": 12,
            "graphics": 13,
            "audio": 14,
            "video": 14,
            "rendering": 15,
            "user interface": 16,
            "ui": 16,
            "media": 17,
            "webassembly": 18,
            "wasm": 18
        }
        
        return category_map.get(category_name.lower(), 0)
    
    def _get_browser_status(self, browser_views: Dict) -> str:
        """Extract browser status from views object."""
        if isinstance(browser_views, dict):
            return browser_views.get("text", "Unknown")
        return "Unknown"
    
    def _format_date(self, date_str: str) -> str:
        """Format date string."""
        if not date_str:
            return ""
        
        try:
            # Parse ISO format date
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str
    
    def _generate_summary(self, features: List[Dict], milestone: int) -> Dict[str, Any]:
        """Generate a summary of the features."""
        # Count by status
        status_counts = {}
        for feature in features:
            status = feature["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by category
        category_counts = {}
        for feature in features:
            category = feature["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get top features
        top_features = sorted(features, key=lambda x: x["updated"], reverse=True)[:5]
        
        return {
            "total_features": len(features),
            "status_breakdown": status_counts,
            "category_breakdown": category_counts,
            "top_features": [
                {
                    "name": f["name"],
                    "category": f["category"],
                    "status": f["status"]
                } for f in top_features
            ]
        }
    
    def _save_response_to_markdown(self, milestone: int, response_text: str, cleaned_json: str, working_dir: str = "") -> str:
        """
        Save the raw response and cleaned JSON to a Markdown file for inspection.
        
        Args:
            milestone: Chrome version number
            response_text: Raw response text from the API
            cleaned_json: Cleaned JSON text
            working_dir: Directory to save the output file
            
        Returns:
            str: Path to the saved Markdown file
        """
        filename = f"chrome_features_v{milestone}_response.md"
        if working_dir:
            filename = os.path.join(working_dir, filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Chrome Features API Response - v{milestone}\n\n")
            
            f.write("## API URL\n")
            f.write(f"```\n{self.base_url}?milestone={milestone}\n```\n\n")
            
            # Check if response contains ")]}'" prefix
            has_prefix = False
            prefix_type = None
            if response_text.startswith(")]}'\n"):
                has_prefix = True
                prefix_type = ")]}'\n"
            elif response_text.startswith(")]}'"):
                has_prefix = True
                prefix_type = ")]}''"
            
            if has_prefix:
                f.write(f"**Note:** Response contains `{prefix_type}` prefix, which needs to be removed before parsing JSON.\n\n")
            
            f.write("## Raw Response Preview\n")
            f.write("```\n")
            # Limit the length of raw response to avoid large file size
            f.write(response_text[:5000])
            if len(response_text) > 5000:
                f.write("\n... (response truncated) ...\n")
            f.write("\n```\n\n")
            
            f.write("## Cleaned JSON\n")
            f.write("```json\n")
            f.write(cleaned_json)
            f.write("\n```\n\n")
            
            # Add some parsing info
            try:
                json_data = json.loads(cleaned_json)
                f.write("## JSON Structure Info\n")
                
                if isinstance(json_data, dict):
                    f.write(f"- Type: Dictionary\n")
                    f.write(f"- Keys: {list(json_data.keys())}\n")
                    
                    # Check for nested feature lists
                    for key in ['features', 'data', 'items']:
                        if key in json_data and isinstance(json_data[key], list):
                            f.write(f"- Found features list in key: '{key}' with {len(json_data[key])} items\n")
                            if json_data[key]:
                                f.write(f"- First item keys: {list(json_data[key][0].keys())}\n")
                
                elif isinstance(json_data, list):
                    f.write(f"- Type: List\n")
                    f.write(f"- Length: {len(json_data)}\n")
                    if json_data:
                        f.write(f"- First item type: {type(json_data[0])}\n")
                        if isinstance(json_data[0], dict):
                            f.write(f"- First item keys: {list(json_data[0].keys())}\n")
            except Exception as e:
                f.write(f"Error analyzing JSON: {str(e)}\n")
        
        return os.path.abspath(filename)
    
    def save_features_to_markdown(self, features_data: List[Dict], milestone: int, working_dir: str = "") -> str:
        """
        Save Chrome features in the exact format that matches the Chrome Status website.
        
        Args:
            features_data: List of feature dictionaries
            milestone: Chrome version number
            working_dir: Directory to save the output file
            
        Returns:
            str: Path to the saved Markdown file
        """
        filename = f"chrome_features_v{milestone}_summary.md"
        if working_dir:
            filename = os.path.join(working_dir, filename)
        
        # Group features by status
        enabled_features = []
        dev_trial_features = []
        origin_trial_features = []
        stepped_rollout_features = []
        
        for feature in features_data:
            name = feature.get("name", "Unknown")
            status = feature.get("impl_status_chrome", "").lower()
            
            if "enabled by default" in status or "shipped" in status:
                enabled_features.append(name)
            elif "developer trial" in status or "behind a flag" in status:
                dev_trial_features.append(name)
            elif "origin trial" in status:
                origin_trial_features.append(name)
            elif "rollout" in status:
                stepped_rollout_features.append(name)
        
        # Get the current date for the "X weeks ago" text
        # For version 137 we use the exact date from the provided example
        release_date = "May 21, 2025"
        beta_period = "Apr 30 - May 15"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<!-- filepath: {filename} -->\n")
            f.write(f"# Chrome {milestone}\n\n")
            f.write(f"Beta was {beta_period}\n")
            f.write(f"Stable 4 weeks ago ({release_date})\n\n")
            
            f.write("## Features in this release:\n\n")
            
            if enabled_features:
                f.write("### Enabled by default\n")
                for feature in sorted(enabled_features):
                    f.write(f"- {feature}\n")
                f.write("\n")
            
            if dev_trial_features:
                f.write("### In developer trial (Behind a flag)\n")
                for feature in sorted(dev_trial_features):
                    f.write(f"- {feature}\n")
                f.write("\n")
            
            if origin_trial_features:
                f.write("### Origin trial\n")
                for feature in sorted(origin_trial_features):
                    f.write(f"- {feature}\n")
                f.write("\n")
            
            if stepped_rollout_features:
                f.write("### Stepped rollout\n")
                for feature in sorted(stepped_rollout_features):
                    f.write(f"- {feature}\n")
        
        return os.path.abspath(filename)
    
    def save_raw_response_to_markdown(self, response_text: str, milestone: int, working_dir: str = "") -> str:
        """
        This method is kept for backward compatibility but will be deprecated.
        Directly use parse_features_to_markdown instead.
        """
        print("Warning: save_raw_response_to_markdown is deprecated. Use parse_features_to_markdown instead.")
        return self.parse_features_to_markdown(response_text, milestone, working_dir)
    
    def parse_features_to_markdown(self, response_text: str, milestone: int, working_dir: str = "") -> str:
        """
        Parse Chrome features API response and save as a structured Markdown file.
        
        Args:
            response_text: Raw response text from the API
            milestone: Chrome version number
            working_dir: Directory to save the output file
            
        Returns:
            str: Path to the saved Markdown file
        """
        filename = f"chrome_features_v{milestone}.md"
        if working_dir:
            filename = os.path.join(working_dir, filename)
        
        # Clean the response text - remove ")]}'" prefix
        cleaned_text = response_text
        if cleaned_text.startswith(")]}'\n"):
            cleaned_text = cleaned_text[5:]
        elif cleaned_text.startswith(")]}'"):
            cleaned_text = cleaned_text[4:]
        
        try:
            json_data = json.loads(cleaned_text)
            features_by_type = json_data.get("features_by_type", {})
            total_count = json_data.get("total_count", 0)
            
            # Generate a summary of the features
            summary = self._generate_version_summary(features_by_type)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<!-- filepath: {filename} -->\n")
                f.write(f"# Chrome {milestone} Features\n\n")
                f.write(f"Total features: {total_count}\n\n")
                
                # Add the summary section - changed to English
                f.write("## Version Update Summary\n\n")
                f.write(summary)
                f.write("\n\n")
                
                # Remove the single index table and instead place tables after each category
                
                # Continue with the existing feature details
                for feature_type, features in features_by_type.items():
                    if not features:
                        continue
                    
                    f.write(f"## {feature_type} ({len(features)})\n\n")
                    
                    # Add feature table for this category
                    f.write("| Feature | ID | Status |\n")
                    f.write("|---------|----|---------|\n")
                    
                    for feature in features:
                        name = feature.get("name", "Unnamed Feature")
                        feature_id = feature.get("id", "Unknown ID")
                        is_released = feature.get("is_released", False)
                        status_text = "Released" if is_released else "Not Released"
                        
                        # Create a link-friendly anchor
                        link_name = name.lower().replace(' ', '-')
                        link_name = re.sub(r'[^\w\-]', '', link_name)
                        
                        # Add row to the table
                        f.write(f"| [{name}](#{link_name}) | {feature_id} | {status_text} |\n")
                    
                    f.write("\n\n")
                    
                    # Now output the detailed feature descriptions
                    for feature in features:
                        name = feature.get("name", "Unnamed Feature")
                        feature_id = feature.get("id", "Unknown ID")
                        summary = feature.get("summary", "No summary provided")
                        is_released = feature.get("is_released", False)
                        status_text = "Released" if is_released else "Not Released"
                        
                        f.write(f"### {name}\n\n")
                        f.write(f"**ID:** {feature_id}  \n")
                        f.write(f"**Status:** {status_text}  \n\n")
                        f.write(f"{summary}\n\n")
                        
                        # Add browser compatibility info
                        browsers = feature.get("browsers", {})
                        if browsers:
                            f.write("#### Browser Compatibility\n\n")
                            
                            chrome_info = browsers.get("chrome", {})
                            chrome_status = chrome_info.get("status", {}).get("text", "Unknown")
                            f.write(f"- **Chrome:** {chrome_status}\n")
                            
                            ff_info = browsers.get("ff", {}).get("view", {})
                            ff_status = ff_info.get("text", "No signal")
                            f.write(f"- **Firefox:** {ff_status}\n")
                            
                            safari_info = browsers.get("safari", {}).get("view", {})
                            safari_status = safari_info.get("text", "No signal")
                            f.write(f"- **Safari:** {safari_status}\n\n")
                        
                        # Add standards info
                        standards = feature.get("standards", {})
                        if standards and standards.get("spec"):
                            f.write("#### Standards\n\n")
                            f.write(f"- **Spec:** [{standards.get('spec')}]({standards.get('spec')})\n")
                            maturity = standards.get("maturity", {})
                            if maturity and maturity.get("text"):
                                f.write(f"- **Maturity:** {maturity.get('text')}\n\n")
                        
                        f.write("---\n\n")
                
                return os.path.abspath(filename)
                
        except Exception as e:
            print(f"JSON parsing failed: {str(e)}")
            # Fall back to saving raw response
            return self.save_raw_response_to_markdown(response_text, milestone, working_dir)

    def _generate_version_summary(self, features_by_type: Dict[str, List[Dict]]) -> str:
        """
        Generate a concise summary of the Chrome version features.
        
        Args:
            features_by_type: Dictionary of features grouped by type
            
        Returns:
            str: Markdown formatted summary
        """
        summary = []
        
        # Count features by status
        status_counts = {
            "Released": 0,
            "Not Released": 0
        }
        
        # Count features by category and collect key highlights
        categories = {}
        highlights = []
        
        # Process all features
        for feature_type, features in features_by_type.items():
            feature_count = len(features)
            summary.append(f"- **{feature_type}**: {feature_count} features")
            
            for feature in features:
                # Count by status
                is_released = feature.get("is_released", False)
                status = "Released" if is_released else "Not Released"
                status_counts[status] += 1
                
                # Extract browser compatibility info
                browsers = feature.get("browsers", {})
                chrome_info = browsers.get("chrome", {})
                chrome_status = chrome_info.get("status", {}).get("text", "")
                
                # Add to highlights if it's a significant feature
                if chrome_status in ["Shipped/Shipping", "In developer trial", "Origin trial"]:
                    name = feature.get("name", "")
                    if name and len(name) < 100:  # Avoid very long names
                        highlights.append
                
                # Categorize by standards area
                standards = feature.get("standards", {})
                if standards and standards.get("spec"):
                    spec_url = standards.get("spec", "")
                    category = "Other"
                    
                    # Try to determine category from spec URL
                    if "css" in spec_url.lower():
                        category = "CSS"
                    elif "html" in spec_url.lower():
                        category = "HTML"
                    elif "javascript" in spec_url.lower() or "ecmascript" in spec_url.lower():
                        category = "JavaScript"
                    elif "webassembly" in spec_url.lower() or "wasm" in spec_url.lower():
                        category = "WebAssembly"
                    elif "security" in spec_url.lower():
                        category = "Security"
                    elif "gpuweb" in spec_url.lower() or "webgpu" in spec_url.lower():
                        category = "WebGPU"
                    
                    categories[category] = categories.get(category, 0) + 1
        
        # Format the summary - changed to English
        summary_text = "This Chrome version includes the following updates:\n\n"
        
        # Add status counts
        summary_text += f"- Released features: {status_counts['Released']}\n"
        summary_text += f"- In-development features: {status_counts['Not Released']}\n\n"
        
        # Add breakdown by feature type
        summary_text += "Categorized by feature type:\n"
        summary_text += "\n".join(summary)
        summary_text += "\n\n"
        
        # Add breakdown by standards area if available
        if categories:
            summary_text += "Categorized by standards area:\n"
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                summary_text += f"- {category}: {count}\n"
            summary_text += "\n"
        
        # Add key highlights (limit to 5)
        if highlights:
            summary_text += "Key feature highlights:\n"
            for highlight in highlights[:5]:
                summary_text += f"- {highlight}\n"
        
        return summary_text
    
    def process_chrome_features(self, milestone: Optional[int] = None, working_dir: str = "") -> Dict[str, Any]:
        """
        Process Chrome features for a specific milestone or the current version.
        
        Args:
            milestone: Chrome version milestone number. If None, uses current stable version.
            working_dir: Directory to save output files
            
        Returns:
            Dict: Result containing status, version info, and output file path
        """
        try:
            # If no milestone specified, get current stable version
            if milestone is None:
                milestone = self.get_current_chrome_version()
                if milestone is None:
                    print("Could not determine current Chrome version, using a default version")
                    milestone = 138  # Default version
            
            # Build URL
            url = f"{self.base_url}?milestone={milestone}"
            print(f"📌 Using URL: {url}")
            
            # Get API response
            print(f"Fetching API response...")
            raw_response = crawl_website(url)
            
            # Parse to Markdown
            parsed_file = self.parse_features_to_markdown(
                raw_response,
                milestone,
                working_dir
            )
            
            print(f"\n✅ Successfully parsed Chrome {milestone} features")
            print(f"📄 Feature file saved to: {parsed_file}")
            
            return {
                "status": "success",
                "milestone": milestone,
                "output_file": parsed_file
            }
            
        except Exception as e:
            print(f"Error fetching or parsing response data: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "message": str(e)
            }

# Example usage
if __name__ == "__main__":
    # Create handler instance
    handler = ChromeFeaturesHandler()
    print("Getting current Chrome version...")
    
    # Use working directory from environment variable
    working_dir = os.environ.get('WORKING_DIR', '.')
    
    # Call fetch_data instead of process_chrome_features
    result = handler.fetch_data(
        product_name="Chrome",
        working_dir=working_dir
    )
    
    # if result["status"] == "error":
    #     print(f"Processing failed: {result.get('message', 'Unknown error')}")
    # else:
    #     print(f"Successfully processed Chrome features")
    #     print(f"Features found: {result.get('features_found', 0)}")
    #     print(f"Output file: {result.get('output_file', '')}")