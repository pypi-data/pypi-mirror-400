"""
Metadata API related MCP tools.
Uses Tableau's GraphQL Metadata API for extract refresh info, lineage, etc.
"""

import logging
from mcp.server.fastmcp import FastMCP

from ..client import get_client, TableauClientError
from ..analytics import track_tool_call

logger = logging.getLogger("tableau-mcp.tools.metadata")


def register_metadata_tools(mcp: FastMCP) -> None:
    """Register all Metadata API related tools with the MCP server."""
    
    @mcp.tool()
    @track_tool_call("get_datasource_extract_info")
    def get_datasource_extract_info(datasource_name: str) -> str:
        """
        Get extract refresh information for a datasource using the Metadata API.
        Shows when the extract was last refreshed, updated, and which workbooks use it.
        
        Args:
            datasource_name: Name of the datasource (e.g., "GI Business Data Model")
        
        Returns:
            Extract information including last refresh time
        """
        try:
            client = get_client()
            info = client.get_datasource_extract_info(datasource_name)
            
            if not info.get("found"):
                return f"❌ Datasource '{datasource_name}' not found. Try using the exact name from `list_datasources`."
            
            result = [f"## 📊 Datasource Extract Info: {info['name']}"]
            result.append(f"**ID:** `{info['id']}`")
            result.append(f"**Project:** {info['project_name'] or 'N/A'}")
            result.append(f"**Owner:** {info['owner'] or 'N/A'}")
            result.append(f"**Has Extracts:** {'✅ Yes' if info['has_extracts'] else '❌ No'}")
            
            result.append("\n### ⏰ Extract Refresh Times")
            
            if info['extract_last_refresh_time']:
                result.append(f"**Last Full Refresh:** `{info['extract_last_refresh_time']}`")
            else:
                result.append("**Last Full Refresh:** Not available")
            
            if info['extract_last_update_time']:
                result.append(f"**Last Update:** `{info['extract_last_update_time']}`")
            
            if info['extract_last_incremental_update_time']:
                result.append(f"**Last Incremental Update:** `{info['extract_last_incremental_update_time']}`")
            
            if info['upstream_databases']:
                result.append("\n### 🔗 Upstream Databases (Data Sources)")
                for db in info['upstream_databases']:
                    result.append(f"- **{db.get('name', 'Unknown')}** ({db.get('connectionType', 'N/A')})")
            
            if info['downstream_workbooks']:
                result.append("\n### 📈 Downstream Workbooks (Using This Data)")
                for wb in info['downstream_workbooks'][:10]:
                    result.append(f"- {wb.get('name', 'Unknown')} ({wb.get('projectName', 'N/A')})")
                if len(info['downstream_workbooks']) > 10:
                    result.append(f"- ... and {len(info['downstream_workbooks']) - 10} more")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_datasource_extract_info")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_dashboard_extract_info")
    def get_dashboard_extract_info(workbook_name: str) -> str:
        """
        Get extract refresh information for all datasources used by a dashboard/workbook.
        Shows when each underlying datasource was last refreshed.
        
        Args:
            workbook_name: Name of the workbook/dashboard (e.g., "Daily Sales Metrics")
        
        Returns:
            Workbook info with all datasource extract refresh times
        """
        try:
            client = get_client()
            info = client.get_workbook_datasources_extract_info(workbook_name)
            
            if not info.get("found"):
                return f"❌ Workbook '{workbook_name}' not found. Try using the exact name from `list_workbooks`."
            
            result = [f"## 📊 Dashboard Extract Info: {info['name']}"]
            result.append(f"**ID:** `{info['id']}`")
            result.append(f"**Project:** {info['project_name'] or 'N/A'}")
            result.append(f"**Owner:** {info['owner'] or 'N/A'}")
            result.append(f"**Workbook Updated:** `{info['updated_at'] or 'N/A'}`")
            
            datasources = info.get('datasources', [])
            
            if not datasources:
                result.append("\n⚠️ No datasources found for this workbook.")
                return "\n".join(result)
            
            result.append(f"\n### 🗄️ Datasources ({len(datasources)} found)")
            result.append("")
            result.append("| Datasource | Has Extract | Last Refresh | Last Update |")
            result.append("| --- | --- | --- | --- |")
            
            for ds in datasources:
                name = ds['name'][:30] if ds['name'] else "Unknown"
                has_extract = "✅" if ds['has_extracts'] else "❌"
                last_refresh = ds['extract_last_refresh_time'] or "N/A"
                if last_refresh != "N/A":
                    last_refresh = last_refresh[:19].replace('T', ' ')
                last_update = ds['extract_last_update_time'] or "N/A"
                if last_update != "N/A":
                    last_update = last_update[:19].replace('T', ' ')
                
                result.append(f"| {name} | {has_extract} | {last_refresh} | {last_update} |")
            
            extract_datasources = [ds for ds in datasources if ds['has_extracts']]
            if extract_datasources:
                result.append("\n### 📋 Summary")
                
                refresh_times = []
                for ds in extract_datasources:
                    if ds['extract_last_refresh_time']:
                        refresh_times.append((ds['name'], ds['extract_last_refresh_time']))
                
                if refresh_times:
                    oldest = min(refresh_times, key=lambda x: x[1])
                    newest = max(refresh_times, key=lambda x: x[1])
                    result.append(f"**Oldest Extract:** {oldest[0]} (`{oldest[1][:19].replace('T', ' ')}`)")
                    result.append(f"**Newest Extract:** {newest[0]} (`{newest[1][:19].replace('T', ' ')}`)")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_dashboard_extract_info")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("find_stale_extracts")
    def find_stale_extracts(hours_threshold: int = 24) -> str:
        """
        Find all datasources with extracts that haven't been refreshed recently.
        Useful for monitoring data freshness across your Tableau environment.
        
        Args:
            hours_threshold: Number of hours - extracts older than this are considered stale (default: 24)
        
        Returns:
            List of datasources with stale or never-refreshed extracts
        """
        try:
            client = get_client()
            stale = client.search_datasources_by_extract_time(hours_threshold)
            
            if not stale:
                return f"✅ No stale extracts found! All extract datasources were refreshed within the last {hours_threshold} hours."
            
            result = [f"## ⚠️ Stale Extracts Report"]
            result.append(f"*Datasources not refreshed in the last {hours_threshold} hours*\n")
            
            never_refreshed = [ds for ds in stale if ds['status'] == 'never_refreshed']
            stale_only = [ds for ds in stale if ds['status'] == 'stale']
            
            if never_refreshed:
                result.append(f"### 🚫 Never Refreshed ({len(never_refreshed)})")
                result.append("| Datasource | Project | Owner |")
                result.append("| --- | --- | --- |")
                for ds in never_refreshed[:20]:
                    name = ds['name'][:35] if ds['name'] else "Unknown"
                    project = (ds['project_name'] or "N/A")[:20]
                    owner = ds['owner'] or "N/A"
                    result.append(f"| {name} | {project} | {owner} |")
                if len(never_refreshed) > 20:
                    result.append(f"\n*... and {len(never_refreshed) - 20} more*")
            
            if stale_only:
                result.append(f"\n### ⏰ Stale Extracts ({len(stale_only)})")
                result.append("| Datasource | Project | Hours Since Refresh | Last Refresh |")
                result.append("| --- | --- | --- | --- |")
                
                stale_only.sort(key=lambda x: x['hours_since_refresh'] or 0, reverse=True)
                
                for ds in stale_only[:20]:
                    name = ds['name'][:30] if ds['name'] else "Unknown"
                    project = (ds['project_name'] or "N/A")[:15]
                    hours = ds['hours_since_refresh']
                    last_refresh = ds['extract_last_refresh_time'][:19].replace('T', ' ') if ds['extract_last_refresh_time'] else "N/A"
                    result.append(f"| {name} | {project} | {hours}h | {last_refresh} |")
                
                if len(stale_only) > 20:
                    result.append(f"\n*... and {len(stale_only) - 20} more*")
            
            result.append(f"\n**Total:** {len(stale)} datasources need attention")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in find_stale_extracts")
            return f"❌ Unexpected error: {str(e)}"

    @mcp.tool()
    @track_tool_call("get_datasource_tables")
    def get_datasource_tables(datasource_name: str) -> str:
        """
        Get the actual upstream tables (e.g., corp_analytics tables) used by a datasource.
        This is the KEY tool for RCA - shows exactly which tables power a Tableau datasource.
        
        Use this to answer: "What tables does this datasource query?"
        
        Args:
            datasource_name: Name of the datasource (e.g., "NAVI Pay DM", "GI Business Data Model")
        
        Returns:
            List of upstream tables with schema and database info
        """
        try:
            client = get_client()
            info = client.get_datasource_upstream_tables(datasource_name)
            
            if not info.get("found"):
                return f"❌ Datasource '{datasource_name}' not found. Try using the exact name from `list_datasources`."
            
            result = [f"## 🔍 Datasource Tables: {info['name']}"]
            result.append(f"**ID:** `{info['id']}`")
            result.append(f"**Project:** {info['project_name'] or 'N/A'}")
            result.append(f"**Owner:** {info['owner'] or 'N/A'}")
            result.append(f"**Has Extracts:** {'✅ Yes' if info['has_extracts'] else '❌ No'}")
            
            upstream_tables = info.get('upstream_tables', [])
            if upstream_tables:
                result.append(f"\n### 📊 Upstream Tables ({len(upstream_tables)} found)")
                result.append("")
                result.append("| Table | Schema | Database | Connection |")
                result.append("| --- | --- | --- | --- |")
                
                for table in upstream_tables:
                    name = table.get('name', 'Unknown')
                    full_name = table.get('full_name', '')
                    schema = table.get('schema', 'N/A')
                    db_name = table.get('database_name', 'N/A')
                    conn_type = table.get('connection_type', 'N/A')
                    
                    display_name = full_name if full_name else name
                    result.append(f"| `{display_name}` | {schema} | {db_name} | {conn_type} |")
            else:
                result.append("\n⚠️ No upstream tables found. The datasource might use custom SQL or a live connection.")
            
            upstream_dbs = info.get('upstream_databases', [])
            if upstream_dbs:
                result.append(f"\n### 🗄️ Database Connections")
                for db in upstream_dbs:
                    result.append(f"- **{db.get('name', 'Unknown')}** ({db.get('connectionType', 'N/A')})")
            
            field_count = info.get('field_count', 0)
            if field_count > 0:
                result.append(f"\n### 📋 Fields")
                result.append(f"**Total Fields:** {field_count}")
                
                fields = info.get('fields', [])[:15]
                if fields:
                    field_names = [f"`{f['name']}`" for f in fields]
                    result.append(f"**Sample:** {', '.join(field_names)}")
                    if field_count > 15:
                        result.append(f"*... and {field_count - 15} more*")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_datasource_tables")
            return f"❌ Unexpected error: {str(e)}"
    
    @mcp.tool()
    @track_tool_call("get_dashboard_tables")
    def get_dashboard_tables(workbook_name: str) -> str:
        """
        Get ALL upstream tables used by a dashboard/workbook.
        Traces through all datasources to find every table powering the dashboard.
        
        This is the MAIN RCA tool - answer "What's behind this Tableau dashboard?"
        
        Args:
            workbook_name: Name of the workbook/dashboard (e.g., "RCBPSlackcards", "50Cr Slack Report")
        
        Returns:
            Complete list of all tables powering the dashboard
        """
        try:
            client = get_client()
            info = client.get_workbook_upstream_tables(workbook_name)
            
            if not info.get("found"):
                return f"❌ Workbook '{workbook_name}' not found. Try using the exact name from `list_workbooks`."
            
            result = [f"## 🔍 Dashboard Lineage: {info['name']}"]
            result.append(f"**ID:** `{info['id']}`")
            result.append(f"**Project:** {info['project_name'] or 'N/A'}")
            result.append(f"**Owner:** {info['owner'] or 'N/A'}")
            if info.get('updated_at'):
                result.append(f"**Last Updated:** `{info['updated_at'][:19].replace('T', ' ')}`")
            
            all_tables = info.get('all_upstream_tables', [])
            table_count = info.get('table_count', 0)
            
            if all_tables:
                result.append(f"\n### 📊 All Upstream Tables ({table_count} found)")
                result.append("")
                result.append("| Table | Schema | Connection | Source |")
                result.append("| --- | --- | --- | --- |")
                
                for table in all_tables:
                    full_name = table.get('full_name', table.get('name', 'Unknown'))
                    schema = table.get('schema', 'N/A')
                    conn_type = table.get('connection_type', 'N/A')
                    source = table.get('source', 'N/A')
                    
                    if source.startswith('datasource:'):
                        source = source.replace('datasource:', 'DS: ')[:25]
                    
                    result.append(f"| `{full_name}` | {schema} | {conn_type} | {source} |")
            else:
                result.append("\n⚠️ No upstream tables found directly on the workbook.")
            
            datasources = info.get('datasources', [])
            if datasources:
                result.append(f"\n### 🗄️ Datasources ({len(datasources)} found)")
                
                for ds in datasources:
                    ds_name = ds.get('name', 'Unknown')
                    has_extract = "✅" if ds.get('has_extracts') else "❌"
                    ds_tables = ds.get('tables', [])
                    
                    result.append(f"\n**{ds_name}** (Extract: {has_extract})")
                    if ds_tables:
                        for t in ds_tables[:5]:
                            result.append(f"  - `{t.get('full_name', t.get('name', 'Unknown'))}`")
                        if len(ds_tables) > 5:
                            result.append(f"  - *... and {len(ds_tables) - 5} more*")
                    else:
                        result.append("  - *(no tables detected)*")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_dashboard_tables")
            return f"❌ Unexpected error: {str(e)}"

    @mcp.tool()
    @track_tool_call("get_dashboard_sql_from_url")
    def get_dashboard_sql_from_url(url: str) -> str:
        """
        Get ALL custom SQL queries for a Tableau dashboard from its URL.
        This is the MAIN tool for reverse engineering - give it a URL, get the SQL.
        
        Use this to answer: "What SQL/tables power this Tableau dashboard?"
        
        Args:
            url: Full Tableau dashboard URL (e.g., https://tableau.server.com/authoring/Workbook/View)
        
        Returns:
            Complete breakdown: Dashboard info, sheets, datasources, and custom SQL for each
        """
        try:
            client = get_client()
            info = client.get_dashboard_custom_sql_from_url(url)
            
            if not info.get("found"):
                error = info.get("error", "Unknown error")
                return f"❌ Could not find dashboard: {error}\n\nTip: Make sure the URL is a valid Tableau dashboard URL."
            
            result = [f"## 📊 Dashboard SQL Analysis"]
            result.append(f"**URL:** `{info['url']}`")
            result.append(f"**Workbook:** {info['workbook_name']}")
            result.append(f"**View:** {info['view_name']}")
            result.append(f"**Project:** {info['project'] or 'N/A'}")
            result.append(f"**Dashboard:** {info['dashboard_name']}")
            
            sheets = info.get('sheets', [])
            if sheets:
                result.append(f"\n### 📋 Sheets ({len(sheets)})")
                for sheet in sheets:
                    result.append(f"- {sheet}")
            
            datasources = info.get('datasources', [])
            if datasources:
                result.append(f"\n### 🗄️ Datasources ({len(datasources)})")
                for ds in datasources:
                    result.append(f"- {ds}")
            
            custom_sql = info.get('custom_sql', [])
            if custom_sql:
                result.append(f"\n### 📝 Custom SQL Queries ({len(custom_sql)} found)")
                
                for i, sql_info in enumerate(custom_sql, 1):
                    result.append(f"\n{'─'*60}")
                    result.append(f"#### SQL #{i}")
                    result.append(f"**Sheets:** {', '.join(sql_info.get('sheets', []))}")
                    result.append(f"**Dashboards:** {', '.join(sql_info.get('dashboards', []))}")
                    
                    source_tables = sql_info.get('source_tables', [])
                    if source_tables:
                        result.append(f"**Source Tables:**")
                        for table in source_tables:
                            result.append(f"  - `{table}`")
                    
                    query = sql_info.get('query', '')
                    if query:
                        result.append(f"\n**Query:**")
                        result.append("```sql")
                        lines = query.split('\n')
                        for line in lines[:30]:
                            result.append(line)
                        if len(lines) > 30:
                            result.append(f"-- ... ({len(lines) - 30} more lines)")
                        result.append("```")
                
                all_tables = set()
                for sql_info in custom_sql:
                    all_tables.update(sql_info.get('source_tables', []))
                
                if all_tables:
                    result.append(f"\n### 🎯 All Source Tables")
                    for table in sorted(all_tables):
                        result.append(f"- `{table}`")
            else:
                result.append("\n⚠️ No custom SQL found. The dashboard may use:")
                result.append("- Published datasources (use `get_datasource_tables` with datasource names above)")
                result.append("- Live connections to tables")
            
            return "\n".join(result)
            
        except TableauClientError as e:
            return f"❌ Metadata API Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in get_dashboard_sql_from_url")
            return f"❌ Unexpected error: {str(e)}"
