# Python MCP Demonstration Project

This project showcases the **Model Context Protocol (MCP)** using Python, AWS Bedrock, LangChain, and Chainlit. It demonstrates how to build an MCP Server that exposes Tools, Resources, and Prompts to an LLM Client.

## 🚀 Overview

The system consists of three main parts:
1. **MCP Server (`server.py`)**: Built with `FastMCP`, it manages a product inventory database (Tools), company policies (Static Resources), and system status (Dynamic Resources).
2. **LLM Client (`client.py`)**: A LangChain-based client using AWS Bedrock and `langchain-mcp-adapters` to connect to the MCP server.
3. **Web Interface (`web_app.py`)**: A user-friendly chat interface powered by `Chainlit`.

---

## 🛠️ Features Demonstrated

### 1. Tools
- `query_inventory`: Allows the LLM to search for product details (price, stock, category) in a real SQLite database.

### 2. Resources
- `file://resources/company_policy.txt`: A static resource containing the company's remote work policy.
- `system://status`: A dynamic resource generating a live system health report.

### 3. Prompts
- `inventory_analysis`: A template for structured analysis, guiding the LLM to provide consistent product reports.

---

## 📦 Prerequisites

- Python 3.10+
- An AWS account with access to **Anthropic Claude 3.5 Sonnet** in Amazon Bedrock.
- AWS Credentials (Access Key and Secret Key) configured.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd mcp-demo
```

### 2. Create a Virtual Environment and Install Dependencies
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the `.env.example` file to `.env` and fill in your AWS credentials:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### 4. Initialize the Database
Run the script to create the `inventory.db` and seed it with sample data:
```bash
python db_utils.py
```

---

## 🏃 Running the Application

### Launch the Web Interface
Start the Chainlit app:
```bash
chainlit run web_app.py
```
This will open a browser window at `http://localhost:8000`.

---

## 🧪 Testing Scenarios

Try these queries in the chat interface:

1. **Tools (Inventory Query)**:
   - "What is the price of the laptop?"
   - "How many mice are in stock?"
   - "Find all accessories."

2. **Resources (Static & Dynamic Content)**:
   - "Tell me about the company remote work policy." (The agent should use the file resource)
   - "What is the current system status?" (The agent should fetch the dynamic resource)

3. **Combined Task**:
   - "Analyze the laptop inventory and compare it with our company policy for new hires."
   - "Is there any office equipment in stock? If so, what is our remote work policy for equipment provision?"

4. **Prompts (Analysis Template)**:
   - "Perform an inventory analysis for the Desk Lamp."

---

## 📘 MCP Concepts Explained

- **Server**: A process that provides context (tools, resources, prompts) to a client. In this project, `FastMCP` simplifies server creation.
- **Client**: An LLM-powered application that consumes the MCP server's capabilities. We use `langchain-mcp-adapters` to bridges the MCP protocol with LangChain's Tool Calling.
- **Tools**: Executable functions that the LLM can call (e.g., querying a database).
- **Resources**: Data sources that the LLM can read from (e.g., files, APIs).
- **Prompts**: Reusable templates that provide pre-defined instructions or context.

---

## ⚠️ Troubleshooting

- **AWS Credentials**: Ensure your AWS user has `AmazonBedrockFullAccess` or a similar policy.
- **Bedrock Model Access**: Ensure **Claude 3.5 Sonnet** is enabled in the model access page of your AWS region's Bedrock console.
- **MCP Initialization**: If you see errors about "initializing MCP server", check that `server.py` runs correctly in standalone mode: `python server.py`.
