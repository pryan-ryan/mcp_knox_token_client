#!/usr/bin/env python3
import asyncio
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

app = Server("knox-client")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="knox_client",
            description="Client to interact with Knox REST endpoint with optional bearer token authentication",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The Knox cdp-proxy-token REST endpoint URL "
                    },
                    "bearer_token": {
                        "type": "string",
                        "description": "Bearer token for cdp-proxy-token authentication (optional)"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method to use (default: GET)"
                    }
                },
                "required": ["url"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "knox_client":
        raise ValueError(f"Unknown tool: {name}")

    url = arguments["url"]
    bearer_token = arguments.get("bearer_token")
    method = arguments.get("method", "GET")

    headers = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers)
        response.raise_for_status()

        return [TextContent(
            type="text",
            text=response.text
        )]

async def main():
    # Your existing async main code
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

def run():
    """Entry point that properly runs the async main function"""
    asyncio.run(main())