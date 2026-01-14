"""
OnCrawl MCP Server
Exposes OnCrawl API as tools for Claude to use in SEO analysis.
"""

import json
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .oncrawl_client import OnCrawlClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oncrawl-mcp")

# Initialize server
server = Server("oncrawl-mcp")

# Client will be initialized on first use
_client: Optional[OnCrawlClient] = None

def get_client() -> OnCrawlClient:
    global _client
    if _client is None:
        _client = OnCrawlClient()
    return _client


# === Tool Definitions ===

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="oncrawl_list_projects",
            description="List all OnCrawl projects in a workspace. Returns project IDs, names, start URLs, and latest crawl info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {
                        "type": "string",
                        "description": "The workspace ID to list projects from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max projects to return (default 100)",
                        "default": 100
                    }
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="oncrawl_get_project",
            description="Get detailed info about a project including all crawl IDs. Use this to find the latest crawl_id for analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="oncrawl_get_schema",
            description="""Get available fields for querying. ALWAYS CALL THIS FIRST before searching or aggregating.
Returns field names, types, available filters, and whether they can be used for aggregation.
This tells you what data is available to explore.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID to get schema for"
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["pages", "links", "clusters", "structured_data"],
                        "description": "Type of data to get schema for (default: pages)",
                        "default": "pages"
                    }
                },
                "required": ["crawl_id"]
            }
        ),
        Tool(
            name="oncrawl_search_pages",
            description="""Search crawled pages with flexible OQL filtering. Use for exploring URL structure, finding anomalies, checking specific page attributes.

OQL Examples:
- All pages: null
- Pages in /blog/: {"field": ["urlpath", "startswith", "/blog/"]}
- 404 errors: {"field": ["status_code", "equals", 404]}
- Orphan pages: {"field": ["depth", "has_no_value", ""]}
- Combined: {"and": [{"field": ["urlpath", "contains", "/product/"]}, {"field": ["follow_inlinks", "lt", "5"]}]}

Filter types: equals, contains, startswith, endswith, gt, gte, lt, lte, between, has_value, has_no_value
Add not_ prefix to negate string filters (not_contains, not_equals, etc.)
Use {"regex": true} as 4th element for regex matching.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID to search"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return (e.g., ['url', 'status_code', 'depth', 'follow_inlinks', 'title'])"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter object (optional, null for all pages)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 100, max 10000)",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset",
                        "default": 0
                    },
                    "sort": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "order": {"type": "string", "enum": ["asc", "desc"]}
                            }
                        },
                        "description": "Sort order (e.g., [{'field': 'follow_inlinks', 'order': 'desc'}])"
                    }
                },
                "required": ["crawl_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_search_links",
            description="""Search the internal link graph. Use for analyzing link distribution, finding broken links, understanding site architecture.

Useful fields: url (source), target_url, anchor, follow, status_code
Use OQL to filter by source or target URL patterns.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID to search"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return (e.g., ['url', 'target_url', 'anchor', 'follow'])"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter object"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 100)",
                        "default": 100
                    }
                },
                "required": ["crawl_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_aggregate",
            description="""Run aggregate queries to group and count pages by dimensions. Essential for understanding site structure at scale.

Examples:
- Count by depth: [{"fields": [{"name": "depth"}]}]
- Count by status code: [{"fields": [{"name": "status_code"}]}]
- Avg inrank by depth: [{"fields": [{"name": "depth"}], "value": "inrank:avg"}]
- Count by inlink ranges: [{"fields": [{"name": "follow_inlinks", "ranges": [{"name": "0", "to": 1}, {"name": "1-10", "from": 1, "to": 11}, {"name": "10+", "from": 11}]}]}]
- With filter: [{"oql": {"field": ["urlpath", "startswith", "/blog/"]}, "fields": [{"name": "depth"}]}]

Aggregation methods: count (default), min, max, avg, sum, value_count, cardinality""",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID"
                    },
                    "aggs": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Array of aggregation objects"
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["pages", "links", "clusters"],
                        "description": "Data type to aggregate (default: pages)",
                        "default": "pages"
                    }
                },
                "required": ["crawl_id", "aggs"]
            }
        ),
        Tool(
            name="oncrawl_export_pages",
            description="""Export pages to JSON or CSV without the 10k limit. Use for larger datasets when you need complete data.
Warning: Can be slow for large sites. Consider filtering with OQL first.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to export"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter (recommended to limit export size)"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["json", "csv"],
                        "description": "Output format (default: json)",
                        "default": "json"
                    }
                },
                "required": ["crawl_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_search_clusters",
            description="Search duplicate content clusters. Use to find near-duplicate pages that might cause cannibalization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 100
                    }
                },
                "required": ["crawl_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_search_structured_data",
            description="Search structured data (JSON-LD, microdata, RDFa). Use to audit schema markup implementation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "crawl_id": {
                        "type": "string",
                        "description": "The crawl ID"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 100
                    }
                },
                "required": ["crawl_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_get_coc_schema",
            description="""Get available fields for crawl-over-crawl comparison.
Call this before querying COC data to understand what change metrics are available.
COC IDs are found in the project details (crawl_over_crawl_ids array).""",
            inputSchema={
                "type": "object",
                "properties": {
                    "coc_id": {
                        "type": "string",
                        "description": "The crawl-over-crawl comparison ID"
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["pages"],
                        "description": "Data type (default: pages)",
                        "default": "pages"
                    }
                },
                "required": ["coc_id"]
            }
        ),
        Tool(
            name="oncrawl_search_coc",
            description="""Search crawl-over-crawl data to find what changed between crawls.
Essential for detecting:
- New pages appearing (where did they come from?)
- Pages that disappeared (were they removed or broken?)
- Status code changes (200→404, 200→301, etc.)
- Depth changes (pages moving deeper/shallower in structure)
- Inlink changes (pages gaining/losing internal links)

Use OQL to filter for specific change patterns.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "coc_id": {
                        "type": "string",
                        "description": "The crawl-over-crawl comparison ID"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return - typically includes 'previous_' and 'current_' variants"
                    },
                    "oql": {
                        "type": "object",
                        "description": "OQL filter for specific changes"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 100)",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset",
                        "default": 0
                    },
                    "sort": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "order": {"type": "string", "enum": ["asc", "desc"]}
                            }
                        },
                        "description": "Sort order"
                    }
                },
                "required": ["coc_id", "fields"]
            }
        ),
        Tool(
            name="oncrawl_aggregate_coc",
            description="""Aggregate crawl-over-crawl data to see change patterns at scale.
Examples:
- Count pages by change type (new, removed, changed, unchanged)
- Group status code changes
- See which URL patterns had the most changes""",
            inputSchema={
                "type": "object",
                "properties": {
                    "coc_id": {
                        "type": "string",
                        "description": "The crawl-over-crawl comparison ID"
                    },
                    "aggs": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Array of aggregation objects"
                    }
                },
                "required": ["coc_id", "aggs"]
            }
        )
    ]


# === Tool Handlers ===

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        client = get_client()
        result = None
        
        if name == "oncrawl_list_projects":
            result = client.list_projects(
                workspace_id=arguments["workspace_id"],
                limit=arguments.get("limit", 100)
            )
        
        elif name == "oncrawl_get_project":
            result = client.get_project(arguments["project_id"])
        
        elif name == "oncrawl_get_schema":
            result = client.get_fields(
                crawl_id=arguments["crawl_id"],
                data_type=arguments.get("data_type", "pages")
            )
            # Simplify output for readability
            if "fields" in result:
                result["fields"] = [
                    {
                        "name": f["name"],
                        "type": f["type"],
                        "filters": f.get("actions", []),
                        "can_aggregate": f.get("agg_dimension", False),
                        "agg_methods": f.get("agg_metric_methods", [])
                    }
                    for f in result["fields"]
                ]
        
        elif name == "oncrawl_search_pages":
            result = client.search_pages(
                crawl_id=arguments["crawl_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                limit=arguments.get("limit", 100),
                offset=arguments.get("offset", 0),
                sort=arguments.get("sort")
            )
        
        elif name == "oncrawl_search_links":
            result = client.search_links(
                crawl_id=arguments["crawl_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                limit=arguments.get("limit", 100)
            )
        
        elif name == "oncrawl_aggregate":
            result = client.aggregate(
                crawl_id=arguments["crawl_id"],
                aggs=arguments["aggs"],
                data_type=arguments.get("data_type", "pages")
            )
        
        elif name == "oncrawl_export_pages":
            raw = client.export_pages(
                crawl_id=arguments["crawl_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                file_type=arguments.get("file_type", "json")
            )
            # Return as-is for JSON/CSV
            return [TextContent(type="text", text=raw)]
        
        elif name == "oncrawl_search_clusters":
            result = client.search_clusters(
                crawl_id=arguments["crawl_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                limit=arguments.get("limit", 100)
            )
        
        elif name == "oncrawl_search_structured_data":
            result = client.search_structured_data(
                crawl_id=arguments["crawl_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                limit=arguments.get("limit", 100)
            )

        elif name == "oncrawl_get_coc_schema":
            result = client.get_crawl_over_crawl_fields(
                coc_id=arguments["coc_id"],
                data_type=arguments.get("data_type", "pages")
            )
            if "fields" in result:
                result["fields"] = [
                    {
                        "name": f["name"],
                        "type": f["type"],
                        "filters": f.get("actions", []),
                        "can_aggregate": f.get("agg_dimension", False),
                        "agg_methods": f.get("agg_metric_methods", [])
                    }
                    for f in result["fields"]
                ]

        elif name == "oncrawl_search_coc":
            result = client.search_crawl_over_crawl(
                coc_id=arguments["coc_id"],
                fields=arguments["fields"],
                oql=arguments.get("oql"),
                limit=arguments.get("limit", 100),
                offset=arguments.get("offset", 0),
                sort=arguments.get("sort")
            )

        elif name == "oncrawl_aggregate_coc":
            result = client.aggregate_crawl_over_crawl(
                coc_id=arguments["coc_id"],
                aggs=arguments["aggs"]
            )

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# === Main Entry Point ===

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
