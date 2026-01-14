"""
Microsoft Edge Mobile DAU Weekly Report Tools

This package provides comprehensive tools for generating Microsoft Edge Mobile 
weekly R7 DAU (7-day rolling Daily Active Users) analysis reports.

Target Product: Microsoft Edge Mobile (iOS & Android)
Data Source: EdgeMobileUserOverviewV3 table via Titan API
Report Features:
- Multi-dimensional data analysis (OS, Region, Customer Type, Install Source, New/Returning Users)
- Week-over-week trend analysis
- HTML and Markdown report generation
- Integration with Titan API authentication
"""

from .edge_mobile_weekly_report_utils import EdgeMobileWeeklyReportUtils
from .contributor_analysis import ContributorAnalysis, calculate_contributor_analysis

__all__ = [
    'EdgeMobileWeeklyReportUtils',
    'ContributorAnalysis',
    'calculate_contributor_analysis'
]
