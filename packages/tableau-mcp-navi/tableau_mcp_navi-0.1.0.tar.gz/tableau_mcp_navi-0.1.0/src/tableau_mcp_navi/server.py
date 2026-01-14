"""
Tableau MCP Server.
Main server module that registers all tools and starts the MCP server.
"""

import logging
import sys
from mcp.server.fastmcp import FastMCP

from .config import logger, get_config
from .client import get_client
from .analytics import track_server_start, track_tool_call
from .tools import (
    register_workbook_tools,
    register_view_tools,
    register_datasource_tools,
    register_project_tools,
    register_user_tools,
    register_metadata_tools
)

# Configure logging to stderr (stdout is used for MCP communication)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    
    # Initialize FastMCP server
    mcp = FastMCP("tableau")
    
    # Register all tools
    logger.info("Registering workbook tools...")
    register_workbook_tools(mcp)
    
    logger.info("Registering view tools...")
    register_view_tools(mcp)
    
    logger.info("Registering datasource tools...")
    register_datasource_tools(mcp)
    
    logger.info("Registering project tools...")
    register_project_tools(mcp)
    
    logger.info("Registering user tools...")
    register_user_tools(mcp)
    
    logger.info("Registering metadata API tools...")
    register_metadata_tools(mcp)
    
    # Add connection test tool
    @mcp.tool()
    @track_tool_call("test_connection")
    def test_connection() -> str:
        """
        Test the connection to Tableau Server.
        Use this to verify connectivity and authentication.
        
        Returns:
            Connection status and user information
        """
        try:
            client = get_client()
            result = client.test_connection()
            
            if result["success"]:
                return f"""### ✅ Connection Successful

**Server URL:** {result['server_url']}
**API Version:** {result['api_version']}
**Site ID:** {result['site_id']}
**User:** {result['user_name']}
**User Role:** {result['user_role']}
"""
            else:
                return f"""### ❌ Connection Failed

**Error:** {result['error']}
**Error Code:** {result.get('error_code', 'N/A')}
"""
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"
    
    # Add list sites tool
    @mcp.tool()
    @track_tool_call("list_sites")
    def list_sites() -> str:
        """
        List all sites on the Tableau Server.
        Note: Requires server administrator permissions.
        
        Returns:
            List of sites
        """
        try:
            client = get_client()
            sites = client.list_sites()
            
            if not sites:
                return "No sites found (or insufficient permissions)."
            
            result = [f"### 🌐 Sites ({len(sites)} found)\n"]
            result.append("| ID | Name | Content URL | State |")
            result.append("| --- | --- | --- | --- |")
            
            for site in sites:
                name = site.name[:30] if site.name else "Unnamed"
                content_url = site.content_url or "default"
                state = site.state or "Active"
                result.append(f"| {site.id[:8]}... | {name} | {content_url} | {state} |")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error listing sites: {str(e)}"
    
    logger.info("MCP server created successfully")
    return mcp


def main():
    """Run the MCP server."""
    try:
        # Validate configuration
        config = get_config()
        logger.info(f"Starting Tableau MCP server for {config.server_url}")
        
        # Track server start
        track_server_start()
        
        # Create and run server
        mcp = create_server()
        mcp.run(transport="stdio")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
