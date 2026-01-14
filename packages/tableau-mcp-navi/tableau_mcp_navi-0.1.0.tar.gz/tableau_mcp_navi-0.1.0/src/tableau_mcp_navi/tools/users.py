"""
User related MCP tools.
"""

import logging
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.users")


def register_user_tools(mcp: FastMCP) -> None:
    """Register all user-related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("list_users")
    def list_users(limit: int = 100) -> str:
        """
        List users on the Tableau Server.
        
        Args:
            limit: Maximum number of users to return (default 100)
        
        Returns:
            Markdown formatted list of users
        """
        try:
            client = get_client()
            users = client.list_users(limit)
            
            if not users:
                return "No users found."
            
            result = [f"### 👥 Users ({len(users)} shown)\n"]
            result.append("| ID | Name | Site Role | Last Login |")
            result.append("| --- | --- | --- | --- |")
            
            for user in users:
                name = user.name[:30] if user.name else "Unnamed"
                role = user.site_role or "N/A"
                last_login = user.last_login.strftime("%Y-%m-%d") if user.last_login else "Never"
                result.append(f"| {user.id[:8]}... | {name} | {role} | {last_login} |")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error listing users: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in list_users")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_user")
    def get_user(user_id: str) -> str:
        """
        Get detailed information about a specific user.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            User details
        """
        try:
            client = get_client()
            user = client.get_user(user_id)
            
            result = [f"## 👤 User: {user.name}"]
            result.append(f"**ID:** {user.id}")
            result.append(f"**Site Role:** {user.site_role or 'N/A'}")
            result.append(f"**Full Name:** {user.fullname or 'N/A'}")
            result.append(f"**Email:** {user.email or 'N/A'}")
            
            if user.last_login:
                result.append(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M')}")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Error getting user: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_user")
            return f"❌ Unexpected error: {str(e)}"
