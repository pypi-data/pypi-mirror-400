"""
This module contains the CN AI Browser analysis workflow for Showroom system.
"""

SHOWROOM_CNAIBROWSER_WORKFLOW = """---
mode: 'agent'
---
# CN AI Browser Analysis Workflow

## Parameter Validation
If time period not provided, ask user: "Please specify the time period to analyze (e.g., 'last 30 days', '2024-01-01 to 2024-01-31')."

Stop if missing parameters.

## Task Confirmation
Before execution, present complete task plan:

"Task Plan - CN AI Browser Analysis:
1. Environment setup + isolated workspace creation
2. Parse time period to start/end dates (AI reasoning)
3. Search & execute Titan templates (≥2 required for success)
4. Run analysis engine to generate HTML report
5. All outputs saved to isolated RUN_DIR

Time period: {time_period}
Expected outputs: CSV files + HTML report

Confirm to proceed? (yes/no)"

Wait for explicit confirmation.

## Step 0: Environment Setup
```
1. Locate project root directory using AI reasoning:
   - Find the directory containing pyproject.toml, .venv, and working_dir
   - Navigate to that directory using run_in_terminal "cd [calculated_path]"
   - This should be the pm-studio-mcp project root directory
2. Verify project root location: run_in_terminal "dir pyproject.toml .venv working_dir"
3. Generate timestamp via AI reasoning (format: YYYYMMDD_HHMMSS)
4. Create isolated workspace using exact mkdir command:
   run_in_terminal "mkdir working_dir\<timestamp>_cnaibrowser"
5. Set RUN_DIR = working_dir\<timestamp>_cnaibrowser

Time parsing (AI reasoning only):
- Parse user time period to concrete start_date/end_date (YYYY-MM-DD)
- Apply 3-day buffer for recent periods
- NO command line date calculations
- NO Python date scripts
```
2. Verify project root location: run_in_terminal "dir pyproject.toml .venv working_dir"
3. Generate timestamp via AI reasoning (format: YYYYMMDD_HHMMSS)
4. Create isolated workspace using exact mkdir command:
   run_in_terminal "mkdir working_dir\<timestamp>_cnaibrowser"
5. Set RUN_DIR = working_dir\<timestamp>_cnaibrowser

Time parsing (AI reasoning only):
- Parse user time period to concrete start_date/end_date (YYYY-MM-DD)
- Apply 3-day buffer for recent periods
- NO command line date calculations
- NO Python date scripts
```

## Step 1: Titan Data Collection
```
Search keywords: "cn ai browser", "browser dad", "browser bsom", "ai browser"
Required datasets (minimum 2 for success):
1. Browser DAD comparison: Edge, Chrome, 360, Doubao, Quark
2. Edge BSoM comparison: with/without AI browsers  
3. BSoM impact quantification
4. AI browsers BSoM trends
5. AI browsers usage minutes

For each template:
- Generate SQL with date filters (start_date to end_date) + region filter
- Execute via titan_query_data_tool
- Save to RUN_DIR: {timestamp}_{dataset_tag}.csv
- Continue if individual templates fail
- Abort only if <2 succeed

NEVER re-execute queries. Check results once with dir command.
```

## Step 2: Analysis Engine Execution
```
Verify prerequisites:
- Check .venv: run_in_terminal "dir .venv"
- Check CSV files in RUN_DIR: run_in_terminal "dir {RUN_DIR}\*.csv"

Execute analysis script ONCE:
".venv\Scripts\python.exe" "src\pm_studio_mcp\showroom_builder\showroom_cnaibrowser_template.py" --input_dir "{RUN_DIR}" --output_dir "{RUN_DIR}"

After execution, immediately check outputs:
run_in_terminal "dir {RUN_DIR}\*CN*Browser*Analysis*.html"

DO NOT re-execute. Report results to user.
```

## Completion Protocol
```
Final verification: run_in_terminal "dir {RUN_DIR}"

Success criteria:
- ≥2 CSV files from Titan queries
- 1 HTML report with timestamp prefix
- All files isolated in RUN_DIR

Report completion with file locations.
```
"""

def get_showroom_cnaibrowser_workflow(time_period=None, template_name="basic"):
    """
    Get the CN AI Browser analysis workflow content.
    
    Args:
        time_period (str, optional): User specified time period for analysis
        template_name (str, optional): Template name (only "basic" is supported)
    
    Returns:
        str: The complete CN AI Browser workflow content
    """
    if time_period:
        # If provided, inject the time period acknowledgement
        workflow_with_time = SHOWROOM_CNAIBROWSER_WORKFLOW.replace(
            "Received time period: {time_period}",
            f"Received time period: {time_period}"
        ).replace(
            "Do you confirm starting the CN AI Browser analysis workflow for: {time_period}?",
            f"Do you confirm starting the CN AI Browser analysis workflow for: {time_period}?"
        )
        return workflow_with_time
    else:
        return SHOWROOM_CNAIBROWSER_WORKFLOW
