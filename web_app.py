import os
import chainlit as cl
from dotenv import load_dotenv
import asyncio

from langchain_aws import ChatBedrock
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# We store the MCP connection in the user session
# to keep it alive during the chat session.

@cl.on_chat_start
async def start():
    """Initializes the LLM agent and MCP server connection."""
    
    # Configure MCP Server connection parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    # Start the server and create a session
    # Chainlit's task management can be tricky with long-lived async contexts,
    # so we manage the context carefully.
    
    try:
        # We use a Stack to manage the context managers
        from contextlib import AsyncExitStack
        stack = AsyncExitStack()
        
        # Connect to server
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(read, write))
        
        # Initialize session
        await session.initialize()
        
        # Load MCP Tools as LangChain tools
        mcp_tools = await load_mcp_tools(session)
        
        # Set up the LLM
        # Use the default credential provider chain for SSO support
        # llm = ChatBedrock(
        #     model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        #     region_name=os.getenv("AWS_REGION", "us-east-1"),
        #     model_kwargs={"max_tokens": 1000}
        # )
        llm = ChatBedrock(
            model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={"max_tokens": 1000}
        )

        # Create a ReAct agent
        agent = create_react_agent(llm, tools=mcp_tools)
        
        # Store objects in Chainlit session
        cl.user_session.set("stack", stack)
        cl.user_session.set("session", session)
        cl.user_session.set("agent", agent)
        
        cl.set_chat_profiles([
            cl.ChatProfile(
                name="MCP Assistant", 
                description="A powerful assistant with real-time tool & resource access.",
                markdown_description="This assistant uses **Model Context Protocol** to access your product inventory and company policies."
            )
        ])
        
        await cl.Message(content="Hello! I am your MCP-powered assistant. I have access to our product inventory and company policies. How can I help you today?").send()
        
    except Exception as e:
        await cl.Message(content=f"Error initializing MCP server: {str(e)}").send()

@cl.on_message
async def main(message: cl.Message):
    """Processes incoming chat messages."""
    agent = cl.user_session.get("agent")
    
    if not agent:
        await cl.Message(content="Session not properly initialized. Please restart.").send()
        return

    # Use the agent to respond to the message
    msg = cl.Message(content="")
    
    # We use agent.astream or agent.ainvoke
    # Let's use invoke for simplicity in this example
    try:
        response = await agent.ainvoke({"messages": [("user", message.content)]})
        
        # The last message is the agent's final response
        final_answer = response["messages"][-1].content
        msg.content = final_answer
        await msg.send()
        
    except Exception as e:
        await cl.Message(content=f"An error occurred while processing your request: {str(e)}").send()

@cl.on_chat_end
async def end():
    """Closes the MCP server connection when the chat ends."""
    stack = cl.user_session.get("stack")
    if stack:
        await stack.aclose()
