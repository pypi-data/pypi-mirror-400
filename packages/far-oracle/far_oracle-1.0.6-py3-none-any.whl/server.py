"""
FAR MCP Server - Model Context Protocol server for Federal Acquisition Regulations

Bot-First monetization strategy: Exposes the FAR RAG API as an MCP tool,
allowing AI agents like Claude Desktop to query federal acquisition regulations.
Returns raw JSON for maximum agent flexibility.
"""

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from client import query_far_backend

# Load environment variables from .env file (if present)
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("far-oracle")


@mcp.tool()
async def consult_federal_regulations(query: str, top_k: int = 5) -> str:
    """
    Search Federal Acquisition Regulations (FAR) for compliance rules, 
    contract clauses, and procurement requirements.
    
    Use this tool when you need to:
    - Verify government contracting compliance requirements
    - Find specific FAR clauses for contract proposals
    - Understand invoicing rules for federal contracts
    - Research procurement regulations and procedures
    - Check small business set-aside requirements
    
    Args:
        query: Natural language question about federal acquisition regulations.
               Examples: "cybersecurity requirements", "small business set aside",
               "payment terms for government contracts"
        top_k: Number of relevant clauses to return (1-20, default 5)
        
    Returns:
        JSON string with relevant FAR clauses, or error message if quota exceeded
    """
    # Check for direct A2A API key first (preferred)
    far_api_key = os.getenv("FAR_API_KEY")
    if far_api_key:
        return await query_far_backend(
            query=query,
            api_key=far_api_key,
            top_k=top_k,
            use_rapidapi=False
        )
    
    # Fall back to RapidAPI key
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if rapidapi_key:
        return await query_far_backend(
            query=query,
            api_key=rapidapi_key,
            top_k=top_k,
            use_rapidapi=True
        )
    
    # Try auto-registration (like far-search-tool does)
    from client import _load_cached_api_key, _auto_register
    
    cached_key = _load_cached_api_key()
    if cached_key:
        return await query_far_backend(
            query=query,
            api_key=cached_key,
            top_k=top_k,
            use_rapidapi=False
        )
    
    # Auto-register on first use
    new_key = await _auto_register()
    if new_key:
        return await query_far_backend(
            query=query,
            api_key=new_key,
            top_k=top_k,
            use_rapidapi=False
        )
    
    return (
        "Error: Auto-registration failed. Please set FAR_API_KEY:\n"
        "1. Register: curl -X POST https://far-rag-api-production.up.railway.app/v1/register -H 'Content-Type: application/json' -d '{\"agent_id\": \"my-agent\"}'\n"
        "2. Set: export FAR_API_KEY=far_live_...\n"
        "Or get a RapidAPI key: https://rapidapi.com/yschang/api/far-rag"
    )


if __name__ == "__main__":
    # Run the MCP server in stdio mode (for Claude Desktop integration)
    mcp.run()
