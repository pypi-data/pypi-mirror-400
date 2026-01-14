"""
Data source related MCP tools.
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.datasources")


def register_datasource_tools(mcp: FastMCP) -> None:
    """Register all datasource-related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("list_datasources")
    def list_datasources(project_id: Optional[str] = None, limit: int = 100) -> str:
        """
        List all data sources on the Tableau Server.
        
        Args:
            project_id: Optional project ID to filter by
            limit: Maximum number of data sources to return (default 100)
        
        Returns:
            Markdown formatted list of data sources
        """
        try:
            client = get_client()
            datasources = client.list_datasources(project_id)
            
            if not datasources:
                return "No data sources found."
            
            datasources = datasources[:limit]
            
            result = [f"### 🗄️ Data Sources ({len(datasources)} shown)\n"]
            result.append("| ID | Name | Project | Type | Updated |")
            result.append("| --- | --- | --- | --- | --- |")
            
            for ds in datasources:
                name = ds.name[:35] if ds.name else "Unnamed"
                project = (ds.project_name or "N/A")[:15]
                ds_type = ds.datasource_type or "N/A"
                updated = ds.updated_at.strftime("%Y-%m-%d") if ds.updated_at else "N/A"
                result.append(f"| {ds.id[:8]}... | {name} | {project} | {ds_type} | {updated} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error listing data sources: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in list_datasources")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_datasource")
    def get_datasource(datasource_id: str) -> str:
        """
        Get detailed information about a specific data source.
        
        Args:
            datasource_id: The ID of the data source
        
        Returns:
            Data source details
        """
        try:
            client = get_client()
            ds = client.get_datasource(datasource_id)
            
            result = [f"## 🗄️ Data Source: {ds.name}"]
            result.append(f"**ID:** {ds.id}")
            result.append(f"**Project:** {ds.project_name or 'N/A'}")
            result.append(f"**Owner ID:** {ds.owner_id or 'N/A'}")
            result.append(f"**Type:** {ds.datasource_type or 'N/A'}")
            result.append(f"**Content URL:** {ds.content_url or 'N/A'}")
            
            if ds.created_at:
                result.append(f"**Created:** {ds.created_at.strftime('%Y-%m-%d %H:%M')}")
            if ds.updated_at:
                result.append(f"**Updated:** {ds.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            result.append(f"\n**Tips:**")
            result.append(f"- Use `refresh_datasource('{datasource_id}')` to trigger an extract refresh")
            result.append(f"- Use `get_datasource_extract_info('{ds.name}')` to check extract status")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting data source: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_datasource")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("refresh_datasource")
    def refresh_datasource(datasource_id: str) -> str:
        """
        Trigger a refresh of a data source extract.
        
        Args:
            datasource_id: The ID of the data source to refresh
        
        Returns:
            Refresh job status
        """
        try:
            client = get_client()
            job_id = client.refresh_datasource(datasource_id)
            
            return f"✅ Extract refresh triggered!\n\n**Job ID:** {job_id}\n\nThe refresh is running in the background. Use Tableau Server to monitor the job status."
            
        except TableauClientError as e:
            return f"❌ Error refreshing data source: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in refresh_datasource")
            return f"❌ Unexpected error: {str(e)}"
