"""
Workbook-related MCP tools.
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.workbooks")


def register_workbook_tools(mcp: FastMCP) -> None:
    """Register all workbook-related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("list_workbooks")
    def list_workbooks(project_id: Optional[str] = None, limit: int = 100) -> str:
        """
        List all workbooks on the Tableau Server.
        
        Args:
            project_id: Optional project ID to filter by
            limit: Maximum number of workbooks to return (default 100)
        
        Returns:
            Markdown formatted list of workbooks
        """
        try:
            client = get_client()
            workbooks, total = client.list_workbooks(project_id)
            
            if not workbooks:
                return "No workbooks found."
            
            workbooks = workbooks[:limit]
            
            result = [f"### 📚 Workbooks ({len(workbooks)} shown, {total} total)\n"]
            result.append("| ID | Name | Project | Updated |")
            result.append("| --- | --- | --- | --- |")
            
            for wb in workbooks:
                name = wb.name[:40] if wb.name else "Unnamed"
                project = (wb.project_name or "N/A")[:20]
                updated = wb.updated_at.strftime("%Y-%m-%d") if wb.updated_at else "N/A"
                result.append(f"| {wb.id[:8]}... | {name} | {project} | {updated} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error listing workbooks: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in list_workbooks")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_workbook")
    def get_workbook(workbook_id: str) -> str:
        """
        Get detailed information about a specific workbook.
        
        Args:
            workbook_id: The ID of the workbook
        
        Returns:
            Workbook details including views
        """
        try:
            client = get_client()
            wb = client.get_workbook(workbook_id)
            
            result = [f"## 📚 Workbook: {wb.name}"]
            result.append(f"**ID:** {wb.id}")
            result.append(f"**Project:** {wb.project_name or 'N/A'}")
            result.append(f"**Owner ID:** {wb.owner_id or 'N/A'}")
            result.append(f"**Content URL:** {wb.content_url or 'N/A'}")
            
            if wb.created_at:
                result.append(f"**Created:** {wb.created_at.strftime('%Y-%m-%d %H:%M')}")
            if wb.updated_at:
                result.append(f"**Updated:** {wb.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            if wb.views:
                result.append(f"\n### Views ({len(wb.views)})")
                result.append("| ID | Name | Total Views |")
                result.append("| --- | --- | --- |")
                for view in wb.views:
                    view_name = view.name[:40] if view.name else "Unnamed"
                    total_views = view.total_views or 0
                    result.append(f"| {view.id[:8]}... | {view_name} | {total_views} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting workbook: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_workbook")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("search_workbooks")
    def search_workbooks(query: str, limit: int = 20) -> str:
        """
        Search for workbooks by name.
        
        Args:
            query: Search term (searches in workbook names)
            limit: Maximum results to return (default 20)
        
        Returns:
            Matching workbooks
        """
        try:
            client = get_client()
            workbooks = client.search_workbooks(query, limit)
            
            if not workbooks:
                return f"No workbooks found matching '{query}'"
            
            result = [f"### 🔍 Workbooks matching '{query}'\n"]
            result.append("| ID | Name | Project | Updated |")
            result.append("| --- | --- | --- | --- |")
            
            for wb in workbooks:
                name = wb.name[:40] if wb.name else "Unnamed"
                project = (wb.project_name or "N/A")[:20]
                updated = wb.updated_at.strftime("%Y-%m-%d") if wb.updated_at else "N/A"
                result.append(f"| {wb.id[:8]}... | {name} | {project} | {updated} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error searching workbooks: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in search_workbooks")
            return f"❌ Unexpected error: {str(e)}"
