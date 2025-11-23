import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/mcp_server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("Connected to server. Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # We can't easily call tools without a device, but we can check if they are listed.
            required_tools = {"get_screenshot", "click", "type_text", "scroll", "navigate"}
            available_tool_names = {t.name for t in tools.tools}

            missing = required_tools - available_tool_names
            if missing:
                print(f"ERROR: Missing tools: {missing}")
                sys.exit(1)
            else:
                print("All required tools are present.")

if __name__ == "__main__":
    asyncio.run(run())
