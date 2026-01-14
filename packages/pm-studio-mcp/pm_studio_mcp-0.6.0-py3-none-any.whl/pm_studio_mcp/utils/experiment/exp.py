#!/usr/bin/env python3
"""
Script to get experiment details by ID or search experiments by owner

Usage:
    Get experiment by ID:
        python exp.py <experiment_id>
    
    Get experiments by owner:
        python exp.py --owner <owner_alias>
    
Examples:
    python exp.py 9488a9cb-3bd7-4126-a2c4-7bdc3961a231
    python exp.py --owner john.doe
    python exp.py -o john.doe@microsoft.com
"""

import sys
import re
from .skydrill import SkyDrillConnector


def get_experiment_by_id(experiment_id: str) -> dict:
    """
    Get detailed information about an experiment by its ID from the SkyDrill database.
    
    Args:
        experiment_id (str): The unique experiment ID (UUID format)
    
    Returns:
        dict: Dictionary containing experiment details:
            - status: "success" or "error"
            - experiment_id: The queried experiment ID
            - title: Experiment title
            - owner: Experiment owner(s)
            - groups: List of configuration group names
            - group_count: Total number of configuration groups
            - message: Status message or error details
    """
    try:
        # Create connector
        connector = SkyDrillConnector()
        
        # Query for experiment details - using only safe columns
        query = f"""
        SELECT 
            exp_id,
            exp_title,
            exp_owner,
            groupname
        FROM expinsights.dbo.experimentationservicedata 
        WHERE exp_id = '{experiment_id}'
        """
        
        result = connector.query(query)
        
        if len(result) == 0:
            return {
                "status": "error",
                "experiment_id": experiment_id,
                "message": f"No experiment found with ID: {experiment_id}"
            }
        
        # Extract data from the result
        first_row = result.iloc[0]
        groups = result['groupname'].tolist()
        
        return {
            "status": "success",
            "experiment_id": experiment_id,
            "title": first_row['exp_title'],
            "owner": first_row['exp_owner'],
            "groups": groups,
            "group_count": len(groups),
            "message": f"Successfully retrieved experiment: {first_row['exp_title']}"
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "experiment_id": experiment_id,
            "message": f"Failed to retrieve experiment details: {str(e)}",
            "error_trace": error_trace
        }


def get_experiments_by_owner(owner_alias: str) -> dict:
    """
    Get all experiments owned by or related to a specific user.
    
    Args:
        owner_alias (str): The user's alias/email (can be partial match)
    
    Returns:
        dict: Dictionary containing:
            - status: "success" or "error"
            - owner_alias: The queried owner alias
            - experiments: List of experiment dictionaries with id, title, and owner
            - experiment_count: Total number of experiments found
            - message: Status message or error details
    """
    try:
        # Create connector
        connector = SkyDrillConnector()
        
        # Query for experiments by owner - using LIKE for partial matching
        query = f"""
        SELECT DISTINCT
            exp_id,
            exp_title,
            exp_owner
        FROM expinsights.dbo.experimentationservicedata 
        WHERE exp_owner LIKE '%%{owner_alias}%%'
        ORDER BY exp_title
        """
        
        result = connector.query(query)
        
        if len(result) == 0:
            return {
                "status": "error",
                "owner_alias": owner_alias,
                "message": f"No experiments found for owner: {owner_alias}"
            }
        
        # Extract unique experiments (avoid duplicates from multiple groups)
        experiments = result.drop_duplicates(subset=['exp_id']).to_dict('records')
        
        return {
            "status": "success",
            "owner_alias": owner_alias,
            "experiments": experiments,
            "experiment_count": len(experiments),
            "message": f"Successfully retrieved {len(experiments)} experiment(s) for owner: {owner_alias}"
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "owner_alias": owner_alias,
            "message": f"Failed to retrieve experiments: {str(e)}",
            "error_trace": error_trace
        }


def get_recent_experiments(owner_alias: str, limit: int = 10, days: int = 30) -> dict:
    """
    Get recent experiments for a specific user.
    
    Args:
        owner_alias (str): The user's alias/email
        limit (int): Maximum number of results to return (default: 10)
        days (int): Number of days to look back (default: 30, currently not used in query)
    
    Returns:
        dict: Dictionary containing recent experiments with same format as get_experiments_by_owner
    """
    # Call get_experiments_by_owner and add metadata
    result = get_experiments_by_owner(owner_alias)
    if result["status"] == "success":
        # Limit results
        result["experiments"] = result["experiments"][:limit]
        result["experiment_count"] = len(result["experiments"])
        result["query_type"] = "recent"
        result["limit_applied"] = limit
        result["days_lookback"] = days
        result["message"] = f"Retrieved {len(result['experiments'])} recent experiment(s) for owner: {owner_alias}"
    return result


def search_experiments_by_title(title_keyword: str, limit: int = 10) -> dict:
    """
    Search experiments by title keyword.
    
    Args:
        title_keyword (str): Keyword to search in experiment titles
        limit (int): Maximum number of results to return (default: 10)
    
    Returns:
        dict: Dictionary containing matching experiments
    """
    try:
        connector = SkyDrillConnector()
        query = f"""
        SELECT DISTINCT
            exp_id,
            exp_title,
            exp_owner
        FROM expinsights.dbo.experimentationservicedata 
        WHERE exp_title LIKE '%%{title_keyword}%%'
        ORDER BY exp_title
        """
        result = connector.query(query)
        
        if len(result) == 0:
            return {
                "status": "error",
                "query_type": "title",
                "title_keyword": title_keyword,
                "message": f"No experiments found with title containing: {title_keyword}"
            }
        
        experiments = result.drop_duplicates(subset=['exp_id']).to_dict('records')[:limit]
        
        return {
            "status": "success",
            "query_type": "title",
            "title_keyword": title_keyword,
            "experiments": experiments,
            "experiment_count": len(experiments),
            "limit_applied": limit,
            "message": f"Found {len(experiments)} experiment(s) matching title: {title_keyword}"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "query_type": "title",
            "title_keyword": title_keyword,
            "message": f"Failed to search experiments: {str(e)}",
            "error_trace": traceback.format_exc()
        }


def search_experiments(
    query: str, 
    search_type: str = "auto",
    limit: int = 10,
    days: int = 30
) -> dict:
    """
    Main dispatcher function that intelligently routes experiment queries to appropriate search methods.
    
    This function auto-detects the query type and calls the appropriate handler:
    - UUID format → get_experiment_by_id()
    - Email format → get_experiments_by_owner()
    - Keywords like 'my', 'mine', 'recent' → get_recent_experiments()
    - Other text → search by owner or title
    
    Args:
        query (str): The search query - can be:
            - Experiment ID (UUID format): "9488a9cb-3bd7-4126-a2c4-7bdc3961a231"
            - Owner alias/email: "john.doe" or "john.doe@microsoft.com"
            - Experiment title keyword: "Edge UIR"
            - Special keywords: "my", "mine", "recent"
        search_type (str): Explicit search type override:
            - "auto" (default): Auto-detect based on query format
            - "id": Force search by experiment ID
            - "owner": Force search by owner
            - "title": Force search by title
            - "recent": Get recent experiments for owner
            - "owner_or_title": Try owner first, fallback to title
        limit (int): Maximum results to return (default: 10)
        days (int): For recent searches, days to look back (default: 30)
    
    Returns:
        dict: Unified response containing:
            - status: "success" or "error"
            - query_type: Detected/used query type
            - results/experiments: Experiment data (format varies by query type)
            - message: Status message
    
    Examples:
        >>> search_experiments("9488a9cb-3bd7-4126-a2c4-7bdc3961a231")
        # Returns single experiment details
        
        >>> search_experiments("john.doe")
        # Returns all experiments owned by john.doe
        
        >>> search_experiments("Edge UIR", search_type="title")
        # Returns experiments with "Edge UIR" in title
        
        >>> search_experiments("john.doe", search_type="recent", limit=5)
        # Returns 5 most recent experiments for john.doe
    """
    # Auto-detection logic
    if search_type == "auto":
        # Check if UUID format (experiment ID)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, query.lower()):
            search_type = "id"
        # Check for email format
        elif '@' in query:
            search_type = "owner"
        # Check for special keywords indicating user wants their own experiments
        elif query.lower() in ['my', 'mine', 'recent', 'my experiments', 'my recent experiments']:
            search_type = "recent"
        # Default to trying owner first, then title
        else:
            search_type = "owner_or_title"
    
    # Route to appropriate function
    if search_type == "id":
        result = get_experiment_by_id(query)
        result["query_type"] = "id"
        return result
        
    elif search_type == "owner":
        result = get_experiments_by_owner(query)
        result["query_type"] = "owner"
        return result
        
    elif search_type == "recent":
        result = get_recent_experiments(query, limit, days)
        return result
        
    elif search_type == "title":
        result = search_experiments_by_title(query, limit)
        return result
        
    elif search_type == "owner_or_title":
        # Try owner first
        result = get_experiments_by_owner(query)
        if result["status"] == "error":
            # Fallback to title search
            result = search_experiments_by_title(query, limit)
            result["query_type"] = "title (fallback from owner)"
        else:
            result["query_type"] = "owner"
        return result
        
    else:
        return {
            "status": "error",
            "message": f"Invalid search_type: {search_type}. Valid options: auto, id, owner, title, recent, owner_or_title"
        }


def get_experiment_details(exp_id: str):
    """
    Print detailed information about an experiment (for CLI usage).
    This is a legacy function that prints to console.
    """
    # Get the data using the new function
    result = get_experiment_by_id(exp_id)
    
    # Print the results
    if result["status"] == "error":
        print(f"❌ {result['message']}")
        if "error_trace" in result:
            print("\nError trace:")
            print(result["error_trace"])
        return
    
    print(f"\n{'='*100}")
    print(f"📊 Experiment: {exp_id}")
    print(f"{'='*100}\n")
    
    print(f"Title:       {result['title']}")
    print(f"Owner:       {result['owner']}")
    
    print(f"\n{'='*100}")
    print(f"Configuration Groups ({result['group_count']} total):")
    print(f"{'='*100}\n")
    
    for group in result['groups']:
        print(f"  Group:  {group}")
    
    print(f"\n{'='*100}")


def list_user_experiments(owner_alias: str):
    """
    Print all experiments owned by a specific user (for CLI usage).
    """
    # Get the data using the new function
    result = get_experiments_by_owner(owner_alias)
    
    # Print the results
    if result["status"] == "error":
        print(f"❌ {result['message']}")
        if "error_trace" in result:
            print("\nError trace:")
            print(result["error_trace"])
        return
    
    print(f"\n{'='*100}")
    print(f"👤 Experiments for Owner: {owner_alias}")
    print(f"{'='*100}\n")
    
    print(f"Total Experiments: {result['experiment_count']}\n")
    
    for i, exp in enumerate(result['experiments'], 1):
        print(f"{i}. {exp['exp_title']}")
        print(f"   ID:    {exp['exp_id']}")
        print(f"   Owner: {exp['exp_owner']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Get experiment by ID:")
        print("    python exp.py <experiment_id>")
        print("\n  Get experiments by owner:")
        print("    python exp.py --owner <owner_alias>")
        print("\nExamples:")
        print("  python exp.py 9488a9cb-3bd7-4126-a2c4-7bdc3961a231")
        print("  python exp.py --owner john.doe")
        print("  python exp.py --owner john.doe@microsoft.com")
        sys.exit(1)
    
    # Check if user wants to search by owner
    if sys.argv[1] == "--owner" or sys.argv[1] == "-o":
        if len(sys.argv) < 3:
            print("Error: Please provide an owner alias")
            print("Usage: python exp.py --owner <owner_alias>")
            sys.exit(1)
        owner_alias = sys.argv[2]
        list_user_experiments(owner_alias)
    else:
        # Assume it's an experiment ID
        exp_id = sys.argv[1]
        get_experiment_details(exp_id)
