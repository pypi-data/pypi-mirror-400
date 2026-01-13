"""
lei_google_scholar - A Python package for searching Google Scholar.

This package provides tools for searching academic papers and authors on Google Scholar.
"""

__version__ = "0.1.0"
__author__ = "Lei"

from lei_google_scholar.core import google_scholar_search, advanced_google_scholar_search, get_author_info

__all__ = ["google_scholar_search", "advanced_google_scholar_search", "get_author_info"]
