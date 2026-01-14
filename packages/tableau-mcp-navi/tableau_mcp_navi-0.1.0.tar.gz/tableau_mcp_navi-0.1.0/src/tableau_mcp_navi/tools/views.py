"""
View/Dashboard related MCP tools.
"""

import logging
import base64
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..models import QueryResult
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.views")


def register_view_tools(mcp: FastMCP) -> None:
    """Register all view-related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("list_views")
    def list_views(workbook_id: Optional[str] = None, limit: int = 100) -> str:
        """
        List views (dashboards/sheets) on the server.
        
        Args:
            workbook_id: Optional workbook ID to filter views by
            limit: Maximum number of views to return (default 100)
        
        Returns:
            Markdown formatted list of views
        """
        try:
            client = get_client()
            views = client.list_views(workbook_id)
            
            if not views:
                msg = f"No views found in workbook {workbook_id}" if workbook_id else "No views found."
                return msg
            
            views = views[:limit]
            
            title = f"Views in Workbook" if workbook_id else "All Views"
            result = [f"### 📊 {title} ({len(views)} shown)\n"]
            result.append("| ID | Name | Workbook ID | Total Views |")
            result.append("| --- | --- | --- | --- |")
            
            for view in views:
                name = view.name[:40] if view.name else "Unnamed"
                wb_id = (view.workbook_id[:8] + "...") if view.workbook_id else "N/A"
                total = view.total_views or 0
                result.append(f"| {view.id[:8]}... | {name} | {wb_id} | {total} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error listing views: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in list_views")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_view")
    def get_view(view_id: str) -> str:
        """
        Get detailed information about a specific view.
        
        Args:
            view_id: The ID of the view
        
        Returns:
            View details
        """
        try:
            client = get_client()
            view = client.get_view(view_id)
            
            result = [f"## 📊 View: {view.name}"]
            result.append(f"**ID:** {view.id}")
            result.append(f"**Workbook ID:** {view.workbook_id or 'N/A'}")
            result.append(f"**Owner ID:** {view.owner_id or 'N/A'}")
            result.append(f"**Content URL:** {view.content_url or 'N/A'}")
            result.append(f"**Total Views:** {view.total_views or 0}")
            
            result.append("\n**Tips:**")
            result.append(f"- Use `get_view_data('{view_id}')` to get the underlying data")
            result.append(f"- Use `get_view_image('{view_id}')` to get a PNG preview")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting view: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_view")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_view_data")
    def get_view_data(view_id: str, max_rows: int = 100) -> str:
        """
        Get the underlying data from a view.
        
        Args:
            view_id: The ID of the view
            max_rows: Maximum rows to return (default 100)
        
        Returns:
            View data in markdown table format
        """
        try:
            client = get_client()
            headers, rows = client.get_view_data(view_id, max_rows)
            
            if not headers:
                return f"No data available for view {view_id}"
            
            query_result = QueryResult(
                columns=headers,
                rows=rows,
                row_count=len(rows)
            )
            
            result = [f"### 📊 View Data\n"]
            result.append(f"**Rows:** {len(rows)}")
            result.append(f"**Columns:** {len(headers)}\n")
            result.append(query_result.to_markdown_table(max_rows))
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting view data: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_view_data")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_view_image")
    def get_view_image(view_id: str) -> str:
        """
        Get a PNG image preview of a view.
        
        Args:
            view_id: The ID of the view
        
        Returns:
            Base64 encoded image data or error message
        """
        try:
            client = get_client()
            image_bytes = client.get_view_image(view_id)
            
            if not image_bytes:
                return f"No image available for view {view_id}"
            
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            result = [f"### 🖼️ View Image Preview\n"]
            result.append(f"**View ID:** {view_id}")
            result.append(f"**Image Size:** {len(image_bytes):,} bytes")
            result.append(f"\n**Base64 Data (first 100 chars):**")
            result.append(f"`{image_b64[:100]}...`")
            result.append(f"\n**Full Base64 length:** {len(image_b64)} characters")
            result.append("\n*Note: Use this base64 data with an image viewer or embed in HTML*")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting view image: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_view_image")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("download_view_image")
    def download_view_image(
        view_id: str, 
        output_dir: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Download a view's image and save it to disk.
        
        Args:
            view_id: The ID of the view to download
            output_dir: Directory to save the image (default: current directory)
            filename: Optional custom filename without extension (default: view name)
        
        Returns:
            Success message with file path or error message
        """
        try:
            client = get_client()
            
            if not output_dir:
                output_dir = "./output"
            
            success, result, size = client.save_view_image(view_id, output_dir, filename)
            
            if success:
                return f"✅ Image downloaded successfully!\n\n**File:** {result}\n**Size:** {size:,} bytes"
            else:
                return f"❌ Failed to download image: {result}"
                
        except TableauClientError as e:
            return f"❌ Error downloading view image: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in download_view_image")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("download_view_image_from_url")
    def download_view_image_from_url(
        url: str,
        output_dir: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Download a dashboard image directly from a Tableau URL.
        
        Supports URL formats:
        - https://tableau.server.com/#/views/WorkbookName/ViewName
        - https://tableau.server.com/views/WorkbookName/ViewName
        - https://tableau.server.com/#/site/SiteName/views/WorkbookName/ViewName
        
        Args:
            url: Full Tableau URL to the view/dashboard
            output_dir: Directory to save the image (default: current directory)
            filename: Optional custom filename without extension
        
        Returns:
            Success message with file path or error message
        """
        try:
            client = get_client()
            
            workbook_url, view_name = client.parse_tableau_url(url)
            
            if not workbook_url or not view_name:
                return f"❌ Could not parse Tableau URL: {url}\n\nExpected format: https://server/#/views/WorkbookName/ViewName"
            
            logger.info(f"Parsed URL - Workbook: {workbook_url}, View: {view_name}")
            
            view = client.find_view_by_content_url(workbook_url, view_name)
            
            if not view:
                return f"❌ View not found!\n\n**Workbook URL:** {workbook_url}\n**View Name:** {view_name}\n\nPlease verify the URL is correct and you have access to this view."
            
            if not output_dir:
                output_dir = "./output"
            
            if not filename:
                filename = view_name
            
            success, result, size = client.save_view_image(view.id, output_dir, filename)
            
            if success:
                return f"✅ Image downloaded successfully!\n\n**View:** {view.name}\n**View ID:** {view.id}\n**File:** {result}\n**Size:** {size:,} bytes"
            else:
                return f"❌ Failed to download image: {result}"
                
        except TableauClientError as e:
            return f"❌ Tableau API error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in download_view_image_from_url")
            return f"❌ Unexpected error: {str(e)}"
