import datetime
import os
from fastmcp import FastMCP
from db_utils import query_product

# Create the MCP Server
mcp = FastMCP("MCP-Demo-Server")

# --- TOOLS ---

@mcp.tool()
def query_inventory(product_name: str) -> str:
    """
    Search for product details in the inventory database.
    
    :param product_name: The name or partial name of the product to search for.
    :return: A string containing product details or a 'not found' message.
    """
    try:
        return query_product(product_name)
    except Exception as e:
        return f"Error querying inventory: {str(e)}"

# --- RESOURCES ---

@mcp.resource("file://resources/company_policy.txt")
def get_company_policy() -> str:
    """
    Retrieves the company remote work policy.
    """
    policy_path = os.path.join(os.getcwd(), "resources", "company_policy.txt")
    if not os.path.exists(policy_path):
        return "Company policy file not found."
    
    with open(policy_path, "r") as f:
        return f.read()

@mcp.resource("system://status")
def get_system_status() -> str:
    """
    Returns the current dynamic system status report.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"System Status Report (Generated at {now})\n- API Gateway: Healthy\n- Database: Online\n- Message Queue: Idle\n- CPU Load: 15%\n- Memory Usage: 45%"

# --- PROMPTS ---

@mcp.prompt()
def inventory_analysis(product_name: str) -> str:
    """
    A template for performing a comprehensive analysis on a specific product.
    
    :param product_name: The product to analyze.
    :return: A prompt message for the LLM.
    """
    return f"""Please provide a detailed inventory analysis for the product: {product_name}.
    Include the current stock level, price, and recommend if re-ordering is necessary based on its current status. 
    Then, check if there are any company policy considerations related to storing or shipping this category of product.
    """

if __name__ == "__main__":
    # Start the server (stdio by default)
    mcp.run()
