"""
OnCrawl API Client
Handles authentication and API requests to OnCrawl REST API v2
"""

import os
import httpx
from typing import Any, Optional
from urllib.parse import urljoin

class OnCrawlClient:
    BASE_URL = "https://app.oncrawl.com/api/v2/"
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get("ONCRAWL_API_TOKEN")
        if not self.api_token:
            raise ValueError("ONCRAWL_API_TOKEN environment variable required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = urljoin(self.BASE_URL, endpoint)
        
        with httpx.Client(timeout=120.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code >= 400:
                error_detail = response.text
                try:
                    error_detail = response.json()
                except:
                    pass
                raise Exception(f"OnCrawl API error {response.status_code}: {error_detail}")
            
            return response.json()
    
    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        return self._request("GET", endpoint, params=params)
    
    def _post(self, endpoint: str, json_data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        return self._request("POST", endpoint, json=json_data, params=params)
    
    # === Project Management ===
    
    def list_projects(self, workspace_id: str, limit: int = 100, offset: int = 0) -> dict:
        """List all projects in a workspace"""
        return self._get(
            f"workspaces/{workspace_id}/projects",
            params={"limit": limit, "offset": offset}
        )
    
    def get_project(self, project_id: str) -> dict:
        """Get details for a specific project including crawl IDs"""
        return self._get(f"projects/{project_id}")
    
    # === Data Schema ===
    
    def get_fields(self, crawl_id: str, data_type: str = "pages") -> dict:
        """
        Get available fields for a data type.
        This is critical for exploration - tells Claude what's queryable.
        
        data_type: pages, links, clusters, structured_data
        """
        return self._get(f"data/crawl/{crawl_id}/{data_type}/fields")
    
    # === Search Queries ===
    
    def search_pages(
        self,
        crawl_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        sort: Optional[list[dict]] = None
    ) -> dict:
        """
        Search pages with OQL filtering.
        Max 10k results via pagination - use export for larger sets.
        
        Example OQL:
        {
            "and": [
                {"field": ["urlpath", "startswith", "/blog/"]},
                {"field": ["status_code", "equals", 200]}
            ]
        }
        """
        payload = {
            "fields": fields,
            "limit": limit,
            "offset": offset
        }
        if oql:
            payload["oql"] = oql
        if sort:
            payload["sort"] = sort
        
        return self._post(f"data/crawl/{crawl_id}/pages", json_data=payload)
    
    def search_links(
        self,
        crawl_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """
        Search internal links.
        Useful for finding link graph anomalies.
        """
        payload = {
            "fields": fields,
            "limit": limit,
            "offset": offset
        }
        if oql:
            payload["oql"] = oql
        
        return self._post(f"data/crawl/{crawl_id}/links", json_data=payload)
    
    # === Aggregations ===
    
    def aggregate(
        self,
        crawl_id: str,
        aggs: list[dict],
        data_type: str = "pages"
    ) -> dict:
        """
        Run aggregate queries for grouping/counting.
        
        Example aggs:
        [
            {
                "fields": [{"name": "depth"}],
                "value": "count"
            }
        ]
        
        Or with ranges:
        [
            {
                "fields": [{
                    "name": "follow_inlinks",
                    "ranges": [
                        {"name": "0", "to": 1},
                        {"name": "1-10", "from": 1, "to": 11},
                        {"name": "10+", "from": 11}
                    ]
                }]
            }
        ]
        """
        return self._post(
            f"data/crawl/{crawl_id}/{data_type}/aggs",
            json_data={"aggs": aggs}
        )
    
    # === Export ===
    
    def export_pages(
        self,
        crawl_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        file_type: str = "json"
    ) -> str:
        """
        Export pages as CSV or JSONL (no 10k limit).
        Returns raw response text.
        
        Note: For large exports, this can take a while.
        """
        url = urljoin(self.BASE_URL, f"data/crawl/{crawl_id}/pages")
        
        payload = {"fields": fields}
        if oql:
            payload["oql"] = oql
        
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                url,
                headers=self.headers,
                json=payload,
                params={"export": "true", "file_type": file_type}
            )
            
            if response.status_code >= 400:
                raise Exception(f"Export error {response.status_code}: {response.text}")
            
            return response.text
    
    # === Clusters (Duplicate Detection) ===
    
    def search_clusters(
        self,
        crawl_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        limit: int = 100
    ) -> dict:
        """Search duplicate content clusters"""
        payload = {
            "fields": fields,
            "limit": limit
        }
        if oql:
            payload["oql"] = oql
        
        return self._post(f"data/crawl/{crawl_id}/clusters", json_data=payload)
    
    # === Structured Data ===
    
    def search_structured_data(
        self,
        crawl_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        limit: int = 100
    ) -> dict:
        """Search structured data (JSON-LD, microdata, RDFa)"""
        payload = {
            "fields": fields,
            "limit": limit
        }
        if oql:
            payload["oql"] = oql

        return self._post(f"data/crawl/{crawl_id}/structured_data", json_data=payload)

    # === Crawl Over Crawl ===

    def get_crawl_over_crawl_fields(self, coc_id: str, data_type: str = "pages") -> dict:
        """Get available fields for crawl over crawl comparison"""
        return self._get(f"data/crawl_over_crawl/{coc_id}/{data_type}/fields")

    def search_crawl_over_crawl(
        self,
        coc_id: str,
        fields: list[str],
        oql: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        sort: Optional[list[dict]] = None
    ) -> dict:
        """
        Search crawl over crawl comparison data.
        Shows what changed between crawls - new pages, removed pages, status changes, etc.
        """
        payload = {
            "fields": fields,
            "limit": limit,
            "offset": offset
        }
        if oql:
            payload["oql"] = oql
        if sort:
            payload["sort"] = sort

        return self._post(f"data/crawl_over_crawl/{coc_id}/pages", json_data=payload)

    def aggregate_crawl_over_crawl(
        self,
        coc_id: str,
        aggs: list[dict],
        data_type: str = "pages"
    ) -> dict:
        """Aggregate crawl over crawl data to see change patterns"""
        return self._post(
            f"data/crawl_over_crawl/{coc_id}/{data_type}/aggs",
            json_data={"aggs": aggs}
        )
