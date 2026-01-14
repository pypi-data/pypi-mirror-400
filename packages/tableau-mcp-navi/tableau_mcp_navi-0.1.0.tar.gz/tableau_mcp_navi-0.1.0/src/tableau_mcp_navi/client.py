"""
Tableau Server API Client.
Handles all communication with the Tableau Server REST API and Metadata API (GraphQL).
"""

import logging
import os
import re
import requests
import base64
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
from urllib.parse import unquote
from datetime import datetime

import tableauserverclient as TSC

from .config import TableauConfig, AuthMethod, get_config

logger = logging.getLogger("tableau-mcp.client")


class TableauClientError(Exception):
    """Custom exception for Tableau API errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code


class TableauClient:
    """
    Client for Tableau Server REST API.
    Uses tableauserverclient library for API interactions.
    """
    
    def __init__(self, config: Optional[TableauConfig] = None):
        """Initialize the client with configuration."""
        self.config = config or get_config()
        self._server: Optional[TSC.Server] = None
        self._auth: Optional[TSC.TableauAuth] = None
    
    def _create_auth(self) -> TSC.TableauAuth:
        """Create the appropriate auth object based on config."""
        if self.config.auth_method == AuthMethod.PERSONAL_ACCESS_TOKEN:
            return TSC.PersonalAccessTokenAuth(
                self.config.token_name,
                self.config.token_secret,
                self.config.site_id
            )
        else:
            return TSC.TableauAuth(
                self.config.username,
                self.config.password,
                self.config.site_id
            )
    
    def _create_server(self) -> TSC.Server:
        """Create and configure the server object."""
        server = TSC.Server(self.config.server_url, use_server_version=True)
        
        # Configure SSL verification
        if not self.config.verify_ssl:
            server.add_http_options({'verify': False})
        
        # Set API version if specified
        if self.config.api_version:
            server.version = self.config.api_version
        
        return server
    
    @contextmanager
    def connection(self):
        """
        Context manager for authenticated Tableau Server connection.
        
        Usage:
            with client.connection() as server:
                workbooks = server.workbooks.get()
        """
        server = self._create_server()
        auth = self._create_auth()
        
        try:
            server.auth.sign_in(auth)
            logger.debug("Successfully authenticated to Tableau Server")
            yield server
        except TSC.ServerResponseError as e:
            raise TableauClientError(f"Tableau API error: {e.summary}", e.code)
        except Exception as e:
            raise TableauClientError(f"Connection error: {str(e)}")
        finally:
            try:
                server.auth.sign_out()
            except:
                pass
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection and return server/user info."""
        try:
            with self.connection() as server:
                user = server.users.get_by_id(server.user_id)
                return {
                    "success": True,
                    "server_url": self.config.server_url,
                    "api_version": server.version,
                    "site_id": server.site_id or "Default",
                    "user_id": server.user_id,
                    "user_name": user.name,
                    "user_role": user.site_role
                }
        except TableauClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.error_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== Workbook Methods =====
    
    def list_workbooks(self, project_id: Optional[str] = None) -> Tuple[List[TSC.WorkbookItem], int]:
        """List all workbooks, optionally filtered by project."""
        with self.connection() as server:
            req_options = TSC.RequestOptions(pagesize=100)
            if project_id:
                req_options.filter.add(TSC.Filter(
                    TSC.RequestOptions.Field.ProjectId,
                    TSC.RequestOptions.Operator.Equals,
                    project_id
                ))
            
            all_workbooks = []
            for workbook in TSC.Pager(server.workbooks, req_options):
                all_workbooks.append(workbook)
                if len(all_workbooks) >= 500:
                    break
            
            return all_workbooks, len(all_workbooks)
    
    def get_workbook(self, workbook_id: str) -> TSC.WorkbookItem:
        """Get detailed information about a workbook."""
        with self.connection() as server:
            workbook = server.workbooks.get_by_id(workbook_id)
            server.workbooks.populate_views(workbook)
            return workbook
    
    def search_workbooks(self, query: str, limit: int = 20) -> List[TSC.WorkbookItem]:
        """Search workbooks by name."""
        with self.connection() as server:
            req_options = TSC.RequestOptions(pagesize=limit)
            req_options.filter.add(TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.Has,
                query
            ))
            workbooks, _ = server.workbooks.get(req_options)
            return list(workbooks)
    
    # ===== View Methods =====
    
    def list_views(self, workbook_id: Optional[str] = None) -> List[TSC.ViewItem]:
        """List views, optionally filtered by workbook."""
        with self.connection() as server:
            if workbook_id:
                workbook = server.workbooks.get_by_id(workbook_id)
                server.workbooks.populate_views(workbook)
                return list(workbook.views)
            else:
                all_views = []
                for view in TSC.Pager(server.views):
                    all_views.append(view)
                    if len(all_views) >= 200:
                        break
                return all_views
    
    def get_view(self, view_id: str) -> TSC.ViewItem:
        """Get detailed information about a view."""
        with self.connection() as server:
            view = server.views.get_by_id(view_id)
            return view
    
    def get_view_image(self, view_id: str) -> bytes:
        """Get PNG image of a view."""
        with self.connection() as server:
            view = server.views.get_by_id(view_id)
            server.views.populate_image(view)
            return view.image
    
    def get_view_data(self, view_id: str, max_rows: int = 100) -> Tuple[List[str], List[List[Any]]]:
        """Get underlying data from a view (CSV format)."""
        with self.connection() as server:
            view = server.views.get_by_id(view_id)
            server.views.populate_csv(view)
            
            import csv
            import io
            
            csv_content = b''.join(view.csv).decode('utf-8')
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return [], []
            
            headers = rows[0]
            data = rows[1:max_rows+1]
            
            return headers, data
    
    def parse_tableau_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a Tableau URL to extract workbook and view names."""
        url = unquote(url)
        
        patterns = [
            r'#/(?:site/[^/]+/)?views/([^/]+)/([^/?#]+)',
            r'/views/([^/]+)/([^/?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                workbook_url = match.group(1)
                view_name = match.group(2)
                return workbook_url, view_name
        
        return None, None
    
    def find_view_by_content_url(self, workbook_url: str, view_name: str) -> Optional[TSC.ViewItem]:
        """Find a view by its workbook content URL and view name."""
        with self.connection() as server:
            for workbook in TSC.Pager(server.workbooks):
                if workbook.content_url and workbook.content_url.lower() == workbook_url.lower():
                    server.workbooks.populate_views(workbook)
                    for view in workbook.views:
                        view_content_url = view.content_url or ""
                        if view_name.lower() in view_content_url.lower():
                            return view
                        if view.name and view_name.lower().replace(" ", "") == view.name.lower().replace(" ", ""):
                            return view
            
            return None
    
    def save_view_image(
        self, 
        view_id: str, 
        output_dir: str, 
        filename: Optional[str] = None
    ) -> Tuple[bool, str, int]:
        """Download a view's image and save it to disk."""
        with self.connection() as server:
            try:
                view = server.views.get_by_id(view_id)
                server.views.populate_image(view)
                
                if not view.image:
                    return False, "No image data returned from server", 0
                
                os.makedirs(output_dir, exist_ok=True)
                
                if not filename:
                    filename = re.sub(r'[^\w\-]', '_', view.name or view_id)
                
                filepath = os.path.join(output_dir, f"{filename}.png")
                
                with open(filepath, 'wb') as f:
                    f.write(view.image)
                
                return True, filepath, len(view.image)
                
            except Exception as e:
                return False, str(e), 0
    
    # ===== Data Source Methods =====
    
    def list_datasources(self, project_id: Optional[str] = None) -> List[TSC.DatasourceItem]:
        """List all data sources."""
        with self.connection() as server:
            req_options = TSC.RequestOptions(pagesize=100)
            if project_id:
                req_options.filter.add(TSC.Filter(
                    TSC.RequestOptions.Field.ProjectId,
                    TSC.RequestOptions.Operator.Equals,
                    project_id
                ))
            
            all_datasources = []
            for ds in TSC.Pager(server.datasources, req_options):
                all_datasources.append(ds)
                if len(all_datasources) >= 200:
                    break
            
            return all_datasources
    
    def get_datasource(self, datasource_id: str) -> TSC.DatasourceItem:
        """Get detailed information about a data source."""
        with self.connection() as server:
            return server.datasources.get_by_id(datasource_id)
    
    def refresh_datasource(self, datasource_id: str) -> str:
        """Trigger a refresh of a data source extract."""
        with self.connection() as server:
            datasource = server.datasources.get_by_id(datasource_id)
            job = server.datasources.refresh(datasource)
            return job.id
    
    # ===== Project Methods =====
    
    def list_projects(self, parent_id: Optional[str] = None) -> List[TSC.ProjectItem]:
        """List all projects."""
        with self.connection() as server:
            all_projects = []
            for project in TSC.Pager(server.projects):
                if parent_id is None or project.parent_id == parent_id:
                    all_projects.append(project)
            return all_projects
    
    def get_project(self, project_id: str) -> TSC.ProjectItem:
        """Get project details."""
        with self.connection() as server:
            return server.projects.get_by_id(project_id)
    
    # ===== User Methods =====
    
    def list_users(self, limit: int = 100) -> List[TSC.UserItem]:
        """List users on the server."""
        with self.connection() as server:
            all_users = []
            for user in TSC.Pager(server.users):
                all_users.append(user)
                if len(all_users) >= limit:
                    break
            return all_users
    
    def get_user(self, user_id: str) -> TSC.UserItem:
        """Get user details."""
        with self.connection() as server:
            return server.users.get_by_id(user_id)
    
    # ===== Site Methods =====
    
    def list_sites(self) -> List[TSC.SiteItem]:
        """List all sites (requires server admin)."""
        with self.connection() as server:
            sites, _ = server.sites.get()
            return list(sites)
    
    # ===== Metadata API (GraphQL) Methods =====
    
    def _get_metadata_api_url(self) -> str:
        """Get the Metadata API GraphQL endpoint URL."""
        base_url = self.config.server_url.rstrip('/')
        return f"{base_url}/api/metadata/graphql"
    
    def _execute_metadata_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the Tableau Metadata API."""
        with self.connection() as server:
            auth_token = server.auth_token
            
            headers = {
                "Content-Type": "application/json",
                "X-Tableau-Auth": auth_token
            }
            
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
            
            response = requests.post(
                self._get_metadata_api_url(),
                json=payload,
                headers=headers,
                verify=self.config.verify_ssl
            )
            
            if response.status_code != 200:
                raise TableauClientError(
                    f"Metadata API error: {response.status_code} - {response.text}"
                )
            
            result = response.json()
            
            if "errors" in result:
                error_msg = "; ".join([e.get("message", str(e)) for e in result["errors"]])
                raise TableauClientError(f"GraphQL error: {error_msg}")
            
            return result.get("data", {})
    
    def get_datasource_extract_info(self, datasource_name: str) -> Dict[str, Any]:
        """Get extract refresh information for a datasource."""
        query = """
        query GetDatasourceExtractInfo($name: String) {
            publishedDatasources(filter: { name: $name }) {
                id
                name
                hasExtracts
                extractLastRefreshTime
                extractLastUpdateTime
                extractLastIncrementalUpdateTime
                projectName
                owner { name }
                upstreamDatabases { name connectionType }
                downstreamWorkbooks { name projectName }
            }
        }
        """
        
        result = self._execute_metadata_query(query, {"name": datasource_name})
        datasources = result.get("publishedDatasources", [])
        
        if not datasources:
            return {"found": False, "name": datasource_name}
        
        ds = datasources[0]
        return {
            "found": True,
            "id": ds.get("id"),
            "name": ds.get("name"),
            "has_extracts": ds.get("hasExtracts", False),
            "extract_last_refresh_time": ds.get("extractLastRefreshTime"),
            "extract_last_update_time": ds.get("extractLastUpdateTime"),
            "extract_last_incremental_update_time": ds.get("extractLastIncrementalUpdateTime"),
            "project_name": ds.get("projectName"),
            "owner": ds.get("owner", {}).get("name") if ds.get("owner") else None,
            "upstream_databases": ds.get("upstreamDatabases", []),
            "downstream_workbooks": ds.get("downstreamWorkbooks", [])
        }
    
    def get_workbook_datasources_extract_info(self, workbook_name: str) -> Dict[str, Any]:
        """Get extract refresh information for all datasources used by a workbook."""
        query = """
        query GetWorkbookDatasourcesInfo($name: String) {
            workbooks(filter: { name: $name }) {
                id
                name
                projectName
                owner { name }
                updatedAt
                upstreamDatasources {
                    id name hasExtracts
                    extractLastRefreshTime extractLastUpdateTime
                    extractLastIncrementalUpdateTime projectName
                }
            }
        }
        """
        
        result = self._execute_metadata_query(query, {"name": workbook_name})
        workbooks = result.get("workbooks", [])
        
        if not workbooks:
            return {"found": False, "name": workbook_name}
        
        wb = workbooks[0]
        datasources = []
        for ds in wb.get("upstreamDatasources", []):
            datasources.append({
                "id": ds.get("id"),
                "name": ds.get("name"),
                "has_extracts": ds.get("hasExtracts", False),
                "extract_last_refresh_time": ds.get("extractLastRefreshTime"),
                "extract_last_update_time": ds.get("extractLastUpdateTime"),
                "extract_last_incremental_update_time": ds.get("extractLastIncrementalUpdateTime"),
                "project_name": ds.get("projectName")
            })
        
        return {
            "found": True,
            "id": wb.get("id"),
            "name": wb.get("name"),
            "project_name": wb.get("projectName"),
            "owner": wb.get("owner", {}).get("name") if wb.get("owner") else None,
            "updated_at": wb.get("updatedAt"),
            "datasources": datasources
        }
    
    def search_datasources_by_extract_time(self, hours_since_refresh: int = 24) -> List[Dict[str, Any]]:
        """Find datasources that haven't been refreshed within the specified hours."""
        query = """
        query GetAllDatasourcesExtractInfo {
            publishedDatasources {
                id name hasExtracts extractLastRefreshTime
                extractLastUpdateTime projectName
                owner { name }
            }
        }
        """
        
        result = self._execute_metadata_query(query)
        datasources = result.get("publishedDatasources", [])
        
        stale_datasources = []
        now = datetime.utcnow()
        
        for ds in datasources:
            if not ds.get("hasExtracts"):
                continue
                
            last_refresh = ds.get("extractLastRefreshTime")
            if not last_refresh:
                stale_datasources.append({
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "project_name": ds.get("projectName"),
                    "owner": ds.get("owner", {}).get("name") if ds.get("owner") else None,
                    "extract_last_refresh_time": None,
                    "hours_since_refresh": None,
                    "status": "never_refreshed"
                })
                continue
            
            try:
                refresh_time = datetime.fromisoformat(last_refresh.replace('Z', '+00:00'))
                refresh_time = refresh_time.replace(tzinfo=None)
                hours_diff = (now - refresh_time).total_seconds() / 3600
                
                if hours_diff > hours_since_refresh:
                    stale_datasources.append({
                        "id": ds.get("id"),
                        "name": ds.get("name"),
                        "project_name": ds.get("projectName"),
                        "owner": ds.get("owner", {}).get("name") if ds.get("owner") else None,
                        "extract_last_refresh_time": last_refresh,
                        "hours_since_refresh": round(hours_diff, 1),
                        "status": "stale"
                    })
            except (ValueError, TypeError):
                pass
        
        return stale_datasources

    def get_datasource_upstream_tables(self, datasource_name: str) -> Dict[str, Any]:
        """Get the actual upstream tables used by a datasource."""
        query = """
        query GetDatasourceUpstreamTables($name: String) {
            publishedDatasources(filter: { name: $name }) {
                id name hasExtracts projectName
                owner { name }
                upstreamTables {
                    id name fullName schema
                    database { name connectionType }
                }
                upstreamDatabases { name connectionType }
                fields { id name description isHidden fullyQualifiedName }
            }
        }
        """
        
        result = self._execute_metadata_query(query, {"name": datasource_name})
        datasources = result.get("publishedDatasources", [])
        
        if not datasources:
            return {"found": False, "name": datasource_name}
        
        ds = datasources[0]
        
        upstream_tables = []
        for table in ds.get("upstreamTables", []):
            db = table.get("database", {})
            upstream_tables.append({
                "id": table.get("id"),
                "name": table.get("name"),
                "full_name": table.get("fullName"),
                "schema": table.get("schema"),
                "database_name": db.get("name") if db else None,
                "connection_type": db.get("connectionType") if db else None
            })
        
        fields = []
        for field in ds.get("fields", []):
            if not field.get("isHidden", False):
                fields.append({
                    "name": field.get("name"),
                    "description": field.get("description"),
                    "fully_qualified_name": field.get("fullyQualifiedName")
                })
        fields = fields[:50]
        
        return {
            "found": True,
            "id": ds.get("id"),
            "name": ds.get("name"),
            "has_extracts": ds.get("hasExtracts", False),
            "project_name": ds.get("projectName"),
            "owner": ds.get("owner", {}).get("name") if ds.get("owner") else None,
            "upstream_tables": upstream_tables,
            "upstream_databases": ds.get("upstreamDatabases", []),
            "fields": fields,
            "field_count": len(ds.get("fields", []))
        }
    
    def get_workbook_upstream_tables(self, workbook_name: str) -> Dict[str, Any]:
        """Get all upstream tables used by a workbook/dashboard."""
        query = """
        query GetWorkbookUpstreamTables($name: String) {
            workbooks(filter: { name: $name }) {
                id name projectName
                owner { name }
                updatedAt
                upstreamDatasources {
                    id name hasExtracts projectName
                    upstreamTables {
                        id name fullName schema
                        database { name connectionType }
                    }
                }
                upstreamTables {
                    id name fullName schema
                    database { name connectionType }
                }
            }
        }
        """
        
        result = self._execute_metadata_query(query, {"name": workbook_name})
        workbooks = result.get("workbooks", [])
        
        if not workbooks:
            return {"found": False, "name": workbook_name}
        
        wb = workbooks[0]
        
        all_tables = {}
        
        for table in wb.get("upstreamTables", []):
            db = table.get("database", {})
            full_name = table.get("fullName") or f"{table.get('schema', '')}.{table.get('name', '')}"
            all_tables[full_name] = {
                "name": table.get("name"),
                "full_name": full_name,
                "schema": table.get("schema"),
                "database_name": db.get("name") if db else None,
                "connection_type": db.get("connectionType") if db else None,
                "source": "direct"
            }
        
        datasources = []
        for ds in wb.get("upstreamDatasources", []):
            ds_tables = []
            for table in ds.get("upstreamTables", []):
                db = table.get("database", {})
                full_name = table.get("fullName") or f"{table.get('schema', '')}.{table.get('name', '')}"
                table_info = {
                    "name": table.get("name"),
                    "full_name": full_name,
                    "schema": table.get("schema"),
                    "database_name": db.get("name") if db else None,
                    "connection_type": db.get("connectionType") if db else None,
                    "source": f"datasource:{ds.get('name')}"
                }
                ds_tables.append(table_info)
                all_tables[full_name] = table_info
            
            datasources.append({
                "id": ds.get("id"),
                "name": ds.get("name"),
                "has_extracts": ds.get("hasExtracts", False),
                "project_name": ds.get("projectName"),
                "tables": ds_tables
            })
        
        return {
            "found": True,
            "id": wb.get("id"),
            "name": wb.get("name"),
            "project_name": wb.get("projectName"),
            "owner": wb.get("owner", {}).get("name") if wb.get("owner") else None,
            "updated_at": wb.get("updatedAt"),
            "datasources": datasources,
            "all_upstream_tables": list(all_tables.values()),
            "table_count": len(all_tables)
        }

    def get_dashboard_custom_sql_from_url(self, url: str) -> Dict[str, Any]:
        """Get all custom SQL queries for a dashboard from its URL."""
        
        patterns = [
            r'/authoring/([^/]+)/([^#?]+)',
            r'/#/views/([^/]+)/([^#?]+)',
            r'/views/([^/]+)/([^#?]+)',
        ]
        
        workbook_slug = None
        view_slug = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                workbook_slug = match.group(1)
                view_slug = match.group(2)
                break
        
        if not workbook_slug or not view_slug:
            return {"found": False, "error": f"Could not parse URL: {url}"}
        
        with self.connection() as server:
            target_view = None
            target_workbook = None
            
            for view in TSC.Pager(server.views):
                if view.content_url and workbook_slug in view.content_url:
                    if view_slug.lower().replace("-", "") in view.content_url.lower().replace("-", ""):
                        target_view = view
                        target_workbook = server.workbooks.get_by_id(view.workbook_id)
                        break
            
            if not target_view or not target_workbook:
                return {
                    "found": False, 
                    "error": f"View not found for URL slug: {workbook_slug}/{view_slug}"
                }
            
            workbook_name = target_workbook.name
            view_name = target_view.name
            auth_token = server.auth_token
            
            dashboard_query = """
            query GetDashboards {
                dashboards {
                    id name luid
                    sheets { name }
                    workbook { name luid }
                    upstreamDatasources { name }
                }
            }
            """
            
            headers = {
                "Content-Type": "application/json",
                "X-Tableau-Auth": auth_token
            }
            
            response = requests.post(
                self._get_metadata_api_url(),
                json={"query": dashboard_query},
                headers=headers,
                verify=self.config.verify_ssl
            )
            
            if response.status_code != 200:
                return {"found": False, "error": f"Metadata API error: {response.status_code}"}
            
            dashboard_result = response.json().get("data", {})
            
            target_dashboard = None
            dashboard_sheets = []
            dashboard_datasources = []
            
            for dash in dashboard_result.get("dashboards", []):
                wb = dash.get("workbook") or {}
                if wb.get("name") == workbook_name:
                    dash_name = dash.get("name", "")
                    if (view_name.lower().replace(" ", "") in dash_name.lower().replace(" ", "") or
                        dash_name.lower().replace(" ", "") in view_name.lower().replace(" ", "")):
                        target_dashboard = dash
                        dashboard_sheets = [s.get("name") for s in (dash.get("sheets") or [])]
                        dashboard_datasources = [ds.get("name") for ds in (dash.get("upstreamDatasources") or [])]
                        break
            
            custom_sql_query = """
            query GetCustomSQLTables {
                customSQLTables {
                    id name query
                    columns { name }
                    downstreamSheets { name }
                    downstreamDashboards { name }
                    downstreamWorkbooks { name }
                }
            }
            """
            
            response = requests.post(
                self._get_metadata_api_url(),
                json={"query": custom_sql_query},
                headers=headers,
                verify=self.config.verify_ssl
            )
            
            if response.status_code != 200:
                return {"found": False, "error": f"CustomSQL query error: {response.status_code}"}
            
            custom_sql_result = response.json().get("data", {})
            
            relevant_sql = []
            for table in custom_sql_result.get("customSQLTables", []):
                downstream_wbs = [wb.get("name", "") for wb in (table.get("downstreamWorkbooks") or [])]
                downstream_sheets = [s.get("name", "") for s in (table.get("downstreamSheets") or [])]
                downstream_dashes = [d.get("name", "") for d in (table.get("downstreamDashboards") or [])]
                
                if workbook_name in downstream_wbs:
                    all_names = downstream_sheets + downstream_dashes
                    
                    is_relevant = False
                    if target_dashboard:
                        dash_name = target_dashboard.get("name", "")
                        if dash_name in downstream_dashes:
                            is_relevant = True
                        for sheet in dashboard_sheets:
                            if sheet in downstream_sheets:
                                is_relevant = True
                                break
                    
                    if not is_relevant:
                        for name in all_names:
                            if (view_name.lower().replace(" ", "") in name.lower().replace(" ", "") or
                                name.lower().replace(" ", "") in view_name.lower().replace(" ", "")):
                                is_relevant = True
                                break
                    
                    if is_relevant:
                        query_text = table.get("query", "")
                        source_tables = []
                        table_patterns = [
                            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)',
                            r'join\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)',
                        ]
                        for pattern in table_patterns:
                            matches = re.findall(pattern, query_text, re.IGNORECASE)
                            source_tables.extend(matches)
                        
                        relevant_sql.append({
                            "sheets": downstream_sheets,
                            "dashboards": downstream_dashes,
                            "columns": [c.get("name") for c in (table.get("columns") or [])],
                            "query": query_text,
                            "source_tables": list(set(source_tables))
                        })
            
            return {
                "found": True,
                "url": url,
                "workbook_name": workbook_name,
                "workbook_content_url": target_workbook.content_url,
                "view_name": view_name,
                "project": target_workbook.project_name,
                "dashboard_name": target_dashboard.get("name") if target_dashboard else view_name,
                "sheets": dashboard_sheets,
                "datasources": dashboard_datasources,
                "custom_sql": relevant_sql,
                "sql_count": len(relevant_sql)
            }


# Global client instance
_client: Optional[TableauClient] = None


def get_client() -> TableauClient:
    """Get or create the global client instance."""
    global _client
    if _client is None:
        _client = TableauClient()
    return _client
