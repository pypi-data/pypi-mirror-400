"""
Data models for Tableau MCP Server.
"""

from dataclasses import dataclass
from typing import Any, List, Optional
from datetime import datetime


@dataclass
class WorkbookInfo:
    """Information about a Tableau workbook."""
    id: str
    name: str
    project_name: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content_url: Optional[str] = None
    views: Optional[List["ViewInfo"]] = None


@dataclass
class ViewInfo:
    """Information about a Tableau view (sheet/dashboard)."""
    id: str
    name: str
    workbook_id: Optional[str] = None
    owner_id: Optional[str] = None
    content_url: Optional[str] = None
    total_views: Optional[int] = None


@dataclass
class QueryResult:
    """Result from a query/data export."""
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    
    def to_markdown_table(self, max_rows: int = 100) -> str:
        """Convert to markdown table format."""
        if not self.columns:
            return "No data"
        
        # Header
        header = "| " + " | ".join(str(c)[:30] for c in self.columns) + " |"
        separator = "| " + " | ".join("---" for _ in self.columns) + " |"
        
        # Rows
        rows_to_show = self.rows[:max_rows]
        data_rows = []
        for row in rows_to_show:
            formatted = []
            for val in row:
                s = str(val) if val is not None else ""
                # Truncate long values
                if len(s) > 50:
                    s = s[:47] + "..."
                # Escape pipe characters
                s = s.replace("|", "\\|")
                formatted.append(s)
            data_rows.append("| " + " | ".join(formatted) + " |")
        
        result = [header, separator] + data_rows
        
        if len(self.rows) > max_rows:
            result.append(f"\n*... showing {max_rows} of {len(self.rows)} rows*")
        
        return "\n".join(result)
