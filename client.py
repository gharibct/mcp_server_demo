import os
import asyncio
from typing import List, Optional
from dotenv import load_dotenv

from langchain_aws import ChatBedrock
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables (AWS credentials)
load_dotenv()

async def get_agent():
    """Sets up and returns a LangGraph agent connected to the MCP server."""
    
    # --- Server Connection ---
    # We'll spawn the server from our server.py file.
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    # --- LLM Client ---
    # Use Anthropic Claude 3.5 Sonnet on Bedrock
    # By not passing credentials, boto3 uses the default provider chain (SSO, IAM roles, etc.)
    llm = ChatBedrock(
        profile="PDO-PoweruserAccess-348505086581",
        model_id="global.anthropic.claude-opus-4-6-v1",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"max_tokens": 1000}
    )
    
    # --- MCP Integration ---
    # Wrap the MCP stdio client in a session context
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Use the adapter to load MCP tools into LangChain tools
            mcp_tools = await load_mcp_tools(session)
            
            # --- Agent Setup ---
            # Create a ReAct agent using LangGraph
            agent = create_react_agent(llm, tools=mcp_tools)
            
            return agent, session

async def run_query(query: str):
    """Executes a query using the agent."""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await load_mcp_tools(session)
            
            llm = ChatBedrock(
                model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            
            agent = create_react_agent(llm, tools=mcp_tools)
            
            # Using the agent's stream or invoke method
            # For simplicity, we'll use invoke
            response = await agent.ainvoke({"messages": [("user", query)]})
            
            # The response messages contain the final answer from the agent
            return response["messages"][-1].content

if __name__ == "__main__":
    # A simple CLI test
    query = "What is the price and stock of the laptop? Also check the company policy on equipment."
    # response = asyncio.run(run_query(query))
    # print(f"Response:\n{response}")
    pass
