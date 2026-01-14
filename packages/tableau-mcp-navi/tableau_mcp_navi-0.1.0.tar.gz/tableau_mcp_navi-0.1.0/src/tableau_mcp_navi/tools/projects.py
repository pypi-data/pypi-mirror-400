"""
Project related MCP tools.
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.projects")


def register_project_tools(mcp: FastMCP) -> None:
    """Register all project-related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("list_projects")
    def list_projects(parent_id: Optional[str] = None) -> str:
        """
        List all projects on the Tableau Server.
        
        Args:
            parent_id: Optional parent project ID to filter by
        
        Returns:
            Markdown formatted list of projects
        """
        try:
            client = get_client()
            projects = client.list_projects(parent_id)
            
            if not projects:
                return "No projects found."
            
            result = [f"### 📁 Projects ({len(projects)} found)\n"]
            result.append("| ID | Name | Parent ID | Description |")
            result.append("| --- | --- | --- | --- |")
            
            for project in projects:
                name = project.name[:30] if project.name else "Unnamed"
                parent = (project.parent_id[:8] + "...") if project.parent_id else "Root"
                desc = (project.description or "")[:30]
                if len(project.description or "") > 30:
                    desc += "..."
                result.append(f"| {project.id[:8]}... | {name} | {parent} | {desc} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error listing projects: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in list_projects")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_project")
    def get_project(project_id: str) -> str:
        """
        Get detailed information about a specific project.
        
        Args:
            project_id: The ID of the project
        
        Returns:
            Project details
        """
        try:
            client = get_client()
            project = client.get_project(project_id)
            
            result = [f"## 📁 Project: {project.name}"]
            result.append(f"**ID:** {project.id}")
            result.append(f"**Parent ID:** {project.parent_id or 'Root (no parent)'}")
            result.append(f"**Content Permissions:** {project.content_permissions or 'N/A'}")
            
            if project.description:
                result.append(f"\n**Description:**\n{project.description}")
            
            result.append(f"\n**Tips:**")
            result.append(f"- Use `list_workbooks(project_id='{project_id}')` to see workbooks in this project")
            result.append(f"- Use `list_datasources(project_id='{project_id}')` to see data sources in this project")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting project: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_project")
            return f"❌ Unexpected error: {str(e)}"
