"""
Excel Graph API - Read and write Excel files in OneDrive via Microsoft Graph API.

Usage:
    from excel_graph_api import ExcelClient
    
    client = ExcelClient()
    data = client.read_range("Book.xlsx", "Sheet1", "A1:C10")
"""

from .client import ExcelClient, get_client

__version__ = "1.0.0"
__all__ = ["ExcelClient", "get_client"]
