"""
Configuration management for Tableau MCP Server.
Handles environment variables and authentication settings.
"""

import os
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tableau-mcp")


class AuthMethod(Enum):
    """Authentication methods supported by the server."""
    PERSONAL_ACCESS_TOKEN = "pat"
    USERNAME_PASSWORD = "username_password"


@dataclass
class TableauConfig:
    """Configuration for Tableau Server connection."""
    server_url: str
    site_id: str
    auth_method: AuthMethod
    token_name: Optional[str] = None
    token_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    verify_ssl: bool = True
    api_version: Optional[str] = None
    
    def __post_init__(self):
        # Remove trailing slash from URL
        self.server_url = self.server_url.rstrip('/')
        
    @classmethod
    def from_env(cls) -> "TableauConfig":
        """Create configuration from environment variables."""
        server_url = os.getenv("TABLEAU_SERVER_URL")
        if not server_url:
            raise ValueError("TABLEAU_SERVER_URL environment variable is required")
        
        site_id = os.getenv("TABLEAU_SITE_ID", "")
        token_name = os.getenv("TABLEAU_TOKEN_NAME")
        token_secret = os.getenv("TABLEAU_TOKEN_SECRET")
        username = os.getenv("TABLEAU_USERNAME")
        password = os.getenv("TABLEAU_PASSWORD")
        verify_ssl = os.getenv("TABLEAU_VERIFY_SSL", "true").lower() != "false"
        api_version = os.getenv("TABLEAU_API_VERSION")
        
        # Determine auth method based on available credentials
        if token_name and token_secret:
            auth_method = AuthMethod.PERSONAL_ACCESS_TOKEN
            logger.info("Using Personal Access Token authentication")
        elif username and password:
            auth_method = AuthMethod.USERNAME_PASSWORD
            logger.info("Using Username/Password authentication")
        else:
            raise ValueError(
                "Authentication required: provide TABLEAU_TOKEN_NAME and TABLEAU_TOKEN_SECRET, "
                "or both TABLEAU_USERNAME and TABLEAU_PASSWORD"
            )
        
        return cls(
            server_url=server_url,
            site_id=site_id,
            auth_method=auth_method,
            token_name=token_name,
            token_secret=token_secret,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            api_version=api_version
        )


# Global config instance
_config: Optional[TableauConfig] = None


def get_config() -> TableauConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = TableauConfig.from_env()
    return _config
