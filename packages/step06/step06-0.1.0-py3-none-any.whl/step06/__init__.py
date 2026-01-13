from mcp.server.fastmcp  import FastMCP
mcp = FastMCP('demo')


@mcp.tool()
def add(a:int, b: int)-> int:
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str)-> str:
    """Get a personalized greeting."""
    return f"Hello, {name}"





def main() -> None:
    mcp.run(transport='stdio')
    
