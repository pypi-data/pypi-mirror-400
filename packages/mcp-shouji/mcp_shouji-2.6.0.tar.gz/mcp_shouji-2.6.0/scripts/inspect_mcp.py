
import asyncio
import inspect
from mcp_shouji.server import mcp

async def main():
    print(f"MCP object type: {type(mcp)}")
    print(f"Dir mcp: {dir(mcp)}")
    
    # Try to find tools
    if hasattr(mcp, "_tools"):
        print(f"Tools dict keys: {mcp._tools.keys()}")
    elif hasattr(mcp, "tools"):
        print(f"Tools attribute: {mcp.tools}")
    
    # Check if we can call list_tools directly (maybe it's not async?)
    try:
        if hasattr(mcp, "list_tools"):
            print("Found list_tools method")
            if inspect.iscoroutinefunction(mcp.list_tools):
                tools = await mcp.list_tools()
                print(f"list_tools() result: {tools}")
            else:
                tools = mcp.list_tools()
                print(f"list_tools() result: {tools}")
    except Exception as e:
        print(f"Error calling list_tools: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
