"""
Excel Graph API Client - Core module for reading/writing Excel files in OneDrive.
"""

import requests
import json
import os
from typing import List, Optional, Dict, Any


class ExcelClient:
    """Client for reading/writing Excel files in OneDrive via Microsoft Graph API."""
    
    def __init__(self, config_path: str = None, access_token: str = None):
        """
        Initialize the Excel client.
        
        Args:
            config_path: Path to config.json. If None, looks in current directory.
            access_token: Direct access token (overrides config file).
        """
        if access_token:
            self.access_token = access_token
            self.default_file = ""
        else:
            if config_path is None:
                config_path = "config.json"
            
            self.config = self._load_config(config_path)
            self.access_token = self.config.get("access_token", "")
            self.default_file = self.config.get("default_file", "")
        
        if not self.access_token:
            raise ValueError(
                "No access token provided!\n"
                "Either pass access_token parameter or create config.json with:\n"
                '{"access_token": "YOUR_TOKEN_HERE"}\n\n'
                "Get token from: https://developer.microsoft.com/en-us/graph/graph-explorer"
            )
        
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Cache for file IDs to avoid repeated lookups
        self._file_cache: Dict[str, str] = {}
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            return {}
        
        with open(config_path, "r") as f:
            return json.load(f)
    
    def _make_request(self, method: str, url: str, json_data: dict = None) -> dict:
        """Make an HTTP request and return JSON response."""
        if method == "GET":
            response = requests.get(url, headers=self.headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=self.headers, json=json_data)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=json_data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        result = response.json()
        
        if "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            raise Exception(f"API Error: {error_msg}")
        
        return result
    
    # =========================================================================
    # File Discovery
    # =========================================================================
    
    def list_excel_files(self) -> List[Dict[str, str]]:
        """
        List all Excel files in OneDrive.
        
        Returns:
            List of dicts with 'name' and 'id' keys.
        """
        url = f"{self.base_url}/me/drive/root/search(q='.xlsx')"
        result = self._make_request("GET", url)
        
        files = []
        for item in result.get("value", []):
            files.append({
                "name": item["name"],
                "id": item["id"]
            })
        return files
    
    def get_file_id(self, file_name: str) -> str:
        """
        Get the OneDrive item ID for a file by name.
        
        Args:
            file_name: Name of the Excel file (e.g., "Book.xlsx")
            
        Returns:
            The file's OneDrive item ID.
        """
        # Check cache first
        if file_name in self._file_cache:
            return self._file_cache[file_name]
        
        # Search for the file
        files = self.list_excel_files()
        for f in files:
            if f["name"].lower() == file_name.lower():
                self._file_cache[file_name] = f["id"]
                return f["id"]
        
        raise FileNotFoundError(f"Excel file not found: {file_name}")
    
    def list_worksheets(self, file_name: str) -> List[str]:
        """
        List all worksheet names in an Excel file.
        
        Args:
            file_name: Name of the Excel file.
            
        Returns:
            List of worksheet names.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/worksheets"
        result = self._make_request("GET", url)
        
        return [sheet["name"] for sheet in result.get("value", [])]
    
    # =========================================================================
    # Range Operations (Read/Write Cells)
    # =========================================================================
    
    def read_range(self, file_name: str, sheet_name: str, range_address: str) -> List[List]:
        """
        Read a range of cells from an Excel file.
        
        Args:
            file_name: Name of the Excel file (e.g., "Book.xlsx")
            sheet_name: Name of the worksheet (e.g., "Sheet1")
            range_address: Cell range (e.g., "A1:C10")
            
        Returns:
            2D list of cell values.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')"
        result = self._make_request("GET", url)
        return result.get("values", [])
    
    def write_range(self, file_name: str, sheet_name: str, range_address: str, values: List[List]) -> bool:
        """
        Write values to a range of cells.
        
        Args:
            file_name: Name of the Excel file.
            sheet_name: Name of the worksheet.
            range_address: Cell range (e.g., "A1:B2")
            values: 2D list of values to write (must match range dimensions).
            
        Returns:
            True if successful.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/range(address='{range_address}')"
        self._make_request("PATCH", url, {"values": values})
        return True
    
    # =========================================================================
    # Table Operations
    # =========================================================================
    
    def list_tables(self, file_name: str) -> List[str]:
        """
        List all tables in an Excel file.
        
        Args:
            file_name: Name of the Excel file.
            
        Returns:
            List of table names.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/tables"
        result = self._make_request("GET", url)
        return [table["name"] for table in result.get("value", [])]
    
    def read_table(self, file_name: str, table_name: str) -> List[List]:
        """
        Read all rows from a table.
        
        Args:
            file_name: Name of the Excel file.
            table_name: Name of the table.
            
        Returns:
            2D list of row values.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/tables/{table_name}/rows"
        result = self._make_request("GET", url)
        
        rows = []
        for row in result.get("value", []):
            rows.append(row.get("values", [[]])[0])
        return rows
    
    def append_to_table(self, file_name: str, table_name: str, rows: List[List]) -> bool:
        """
        Append rows to an existing table.
        
        Args:
            file_name: Name of the Excel file.
            table_name: Name of the table.
            rows: List of rows to append. Each row is a list of values.
            
        Returns:
            True if successful.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/tables/{table_name}/rows"
        self._make_request("POST", url, {"values": rows})
        return True
    
    def get_table_headers(self, file_name: str, table_name: str) -> List[str]:
        """
        Get column headers from a table.
        
        Args:
            file_name: Name of the Excel file.
            table_name: Name of the table.
            
        Returns:
            List of header names.
        """
        item_id = self.get_file_id(file_name)
        url = f"{self.base_url}/me/drive/items/{item_id}/workbook/tables/{table_name}/headerRowRange"
        result = self._make_request("GET", url)
        values = result.get("values", [[]])
        return values[0] if values else []


def get_client(config_path: str = None, access_token: str = None) -> ExcelClient:
    """Get an ExcelClient instance."""
    return ExcelClient(config_path=config_path, access_token=access_token)
