# MCP Integration with Minion Brain (Standalone Version)

This is a **standalone** MCP (Model Context Protocol) integration solution for Minion Brain.step that **does not depend on huggingface_hub** package. It provides a clean, lightweight tool integration approach.

## Features

- **🔗 MCP Server Support**: Connect to stdio, SSE, and HTTP MCP servers
- **🛠 Tool Adaptation**: Automatically converts MCP tools to brain.step compatible format
- **🧠 Brain Integration**: Native support for tools in minion brain.step function
- **🖥 Gradio UI**: Web interface to configure and test MCP tools
- **⚙️ Environment Configuration**: Easy setup via environment variables
- **🔒 Independence**: No dependency on huggingface_hub, completely self-contained

## Architecture

### Core Components

1. **BrainTool**: Adapter class that wraps MCP tools for brain.step compatibility
2. **MCPBrainClient**: Main client for managing MCP server connections
3. **Local Tools**: Built-in local tools (calculator, final answer, etc.)

### Tool Format Conversion

MCP tools are automatically converted to the format expected by brain.step:

```python
# MCP Tool (from server)
{
    "name": "calculator",
    "description": "Perform basic arithmetic operations",
    "inputSchema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        }
    }
}

# Converted to BrainTool (for brain.step)
BrainTool(
    name="calculator",
    description="Perform basic arithmetic operations", 
    parameters={...},
    session=mcp_session
)
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This version **does not require** `huggingface_hub`, fewer dependencies!

### 2. Environment Configuration

Create a `.env` file:

```bash
# LLM Configuration
GPT_4O_API_TYPE=azure
GPT_4O_API_KEY=your_api_key_here
GPT_4O_BASE_URL=https://your-endpoint.openai.azure.com/
GPT_4O_API_VERSION=2024-06-01
GPT_4O_MODEL=gpt-4o

# MCP Server Configuration (optional)
MCP_SSE_URL=http://localhost:8080/sse
MCP_STDIO_COMMAND=python example_mcp_server.py
```

### 3. Quick Test

```bash
# Test local tools and MCP integration
python simple_mcp_test.py
```

## Usage

### Basic Usage

```python
from mcp_integration import MCPBrainClient, create_final_answer_tool, create_calculator_tool

async def example_usage():
    # Create local tools
    local_tools = [
        create_calculator_tool(),
        create_final_answer_tool()
    ]
    
    # Optional: Add MCP tools
    mcp_tools = []
    try:
        async with MCPBrainClient() as mcp_client:
            await mcp_client.add_mcp_server("sse", url="http://localhost:8080/sse")
            mcp_tools = mcp_client.get_tools_for_brain()
    except:
        pass  # It's okay if there's no MCP server
    
    # Combine all tools
    all_tools = local_tools + mcp_tools
    
    # Use in brain.step
    obs, score, *_ = await brain.step(
        query="Calculate 234*568",
        route="raw",
        check=False,
        tools=all_tools
    )
    
    print(f"Result: {obs}")
```

### Using Only Local Tools

If you don't need to connect to external MCP servers:

```python
from mcp_integration import create_calculator_tool, create_final_answer_tool

# Create local tools
tools = [
    create_calculator_tool(),
    create_final_answer_tool()
]

# Use directly in brain.step
obs, score, *_ = await brain.step(
    query="Calculate 234*568",
    tools=tools
)
```

### Connecting to Different MCP Server Types

#### SSE Server
```python
await mcp_client.add_mcp_server(
    "sse", 
    url="http://localhost:8080/sse",
    headers={"Authorization": "Bearer token"},
    timeout=30.0
)
```

#### Stdio Server
```python
await mcp_client.add_mcp_server(
    "stdio",
    command="python",
    args=["example_mcp_server.py"],
    cwd="/path/to/server"
)
```

#### HTTP Server
```python
await mcp_client.add_mcp_server(
    "http",
    url="http://localhost:8080/http",
    timeout=timedelta(seconds=30)
)
```

### Creating Custom Local Tools

```python
def create_custom_tool():
    class CustomSession:
        async def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
            # Your tool logic
            result = f"Processed: {args}"
            return {
                "content": [{"type": "text", "text": result}]
            }
    
    return BrainTool(
        name="custom_tool",
        description="A custom tool",
        parameters={
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        },
        session=CustomSession()
    )
```

## Built-in Tools

### 1. Calculator Tool
```python
calculator_tool = create_calculator_tool()
result = await calculator_tool(expression="234 * 568")
# Output: "Calculation result: 234 * 568 = 132912"
```

### 2. Final Answer Tool
```python
final_tool = create_final_answer_tool()
result = await final_tool(answer="Calculation completed, result is 132912")
# Output: "Calculation completed, result is 132912"
```

### 3. Filesystem Tool (MCP)
```python
from mcp_integration import add_filesystem_tool

async with MCPBrainClient() as mcp_client:
    # Add filesystem tool, specify allowed access paths
    await add_filesystem_tool(mcp_client, workspace_paths=[
        "/Users/femtozheng/workspace",
        "/Users/femtozheng/python-project/minion-agent"
    ])
    
    # Get tools and use
    tools = mcp_client.get_tools_for_brain()
    # Filesystem tools typically include: read_file, write_file, list_directory, etc.
```

**Filesystem Tool Features**:
- 📖 **read_file**: Read file contents
- ✏️ **write_file**: Write to files
- 📂 **list_directory**: List directory contents
- 🔍 **search_files**: Search files
- 🔒 **Security restriction**: Only access pre-configured paths

## Run Complete Application

```bash
python app_with_mcp.py
```

Then open `http://localhost:7860` in your browser and enable the "MCP Tools" option.

## Integration Patterns

### 1. Tool Discovery
The system automatically discovers and registers tools from connected MCP servers:

```python
tools = mcp_client.get_tools_for_brain()
print([tool.name for tool in tools])
```

### 2. Error Handling
Tools include built-in error handling:

```python
result = await tool(invalid_param="value")
# Returns: "Error: <error_description>"
```

### 3. Tool Execution
Tools execute asynchronously and return formatted results:

```python
result = await tool(expression="2+2")
# Result is automatically formatted for brain.step use
```

## Advantages

### Compared to huggingface_hub dependent version:

1. **Lighter**: Reduced large dependency packages
2. **Simpler**: Focus on core MCP integration functionality
3. **More flexible**: Not restricted by huggingface_hub versions
4. **Faster**: Less import and initialization time
5. **More independent**: Can run in any environment

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Check server URL and port
   - Verify server is running
   - Check network connectivity

2. **Tool Not Found**
   - Verify MCP server has tools
   - Check tool name spelling
   - Ensure server initialization completed

3. **Import Errors**
   - Install all required dependencies
   - Check Python version compatibility
   - Verify mcp package installation

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Tool Filtering

Filter tools by name or type:

```python
# Filter specific tools
filtered_tools = [
    tool for tool in tools 
    if tool.name in ["calculator", "final_answer"]
]
```

### Tool Prioritization

Organize tools by priority:

```python
# High-priority tools first
priority_tools = ["final_answer", "calculator"]
other_tools = [t for t in tools if t.name not in priority_tools]
ordered_tools = priority_tools + other_tools
```

## Example Projects

Check `example_mcp_server.py` to learn how to create MCP servers, or run `simple_mcp_test.py` to see complete integration examples.

## Contributing

To extend the MCP integration:

1. Implement new tool adapters in `BrainTool`
2. Add server type support in `MCPBrainClient`
3. Enhance error handling and logging
4. Add new tool creation utilities

## License

MIT License - see LICENSE file for details. 