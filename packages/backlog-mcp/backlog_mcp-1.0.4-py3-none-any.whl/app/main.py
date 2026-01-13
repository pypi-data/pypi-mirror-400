from mcp.server import FastMCP
from app.tools import *

app = FastMCP(
    name="Backlog MCP Server",
    instructions="A simplified Backlog MCP server with API key authentication",
    debug=True,
    json_response=True,
)

# Add tool for Backlog MCP
app.add_tool(get_issue_details)
app.add_tool(get_user_issue_list)


def main() -> int:
    """Run the Backlog MCP server."""
    mcp_server = app
    mcp_server.run(transport="stdio")
    return 0

if __name__ == "__main__":
    main()
