import os
import asyncio
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from langchain_aws import ChatBedrock
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.sessions import StdioConnection
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Load environment variables (AWS credentials)
load_dotenv()

# MCP server connections
INVENTORY_CONNECTION = StdioConnection(
    transport="stdio",
    command="python",
    args=["server.py"],
)

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
FILESYSTEM_CONNECTION = StdioConnection(
    transport="stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", FILES_DIR],
)

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to inventory data and a file system. "
    "When asked about products (price, stock, etc.), ALWAYS use the query_inventory tool to look up the information. "
    "When asked about files or documents, use the filesystem tools (read_file, list_directory, etc.). "
    "Do not ask for clarification on product names — just search with what the user provides.\n\n"
)


def get_llm():
    """Returns the configured LLM instance."""
    return ChatBedrock(
        model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"max_tokens": 1000},
    )


async def load_resources_context() -> str:
    """Loads MCP resources and returns them as context for the system prompt."""
    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        blobs = await load_mcp_resources(session)
    parts = []
    for blob in blobs:
        data = blob.as_string()
        parts.append(f"--- Resource: {blob.path or 'unknown'} ---\n{data}")
    return "\n\n".join(parts)


async def run_query(query: str):
    """Executes a query using the agent with an MCP connection."""
    resources_context = await load_resources_context()
    system = SYSTEM_PROMPT + "Here are the company resources you have access to:\n\n" + resources_context

    inventory_tools = await load_mcp_tools(session=None, connection=INVENTORY_CONNECTION, server_name="inventory")
    filesystem_tools = await load_mcp_tools(session=None, connection=FILESYSTEM_CONNECTION, server_name="filesystem")
    all_tools = inventory_tools + filesystem_tools
    agent = create_agent(get_llm(), tools=all_tools, system_prompt=system)
    response = await agent.ainvoke({"messages": [("user", query)]})
    return response["messages"][-1].content


if __name__ == "__main__":
    query = "What is the price of the laptop? Also list the files in the files directory and read the sales report."
    response = asyncio.run(run_query(query))
    print(f"Response:\n{response}")
