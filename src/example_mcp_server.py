#!/usr/bin/env python3
"""
Example MCP Server for testing with Minion Brain integration

This server provides simple tools for demonstration purposes:
- calculator: Basic arithmetic operations  
- echo: Simple echo/repeat functionality
- timestamp: Get current timestamp
"""

import asyncio
import json
import math
from datetime import datetime
from typing import Any, Dict

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Create server instance
server = Server("example-tools-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="calculator",
            description="Perform basic arithmetic calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="echo",
            description="Echo back the provided text",
            inputSchema={
                "type": "object", 
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="timestamp",
            description="Get current timestamp",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Timestamp format ('iso', 'unix', or 'readable')",
                        "default": "iso"
                    }
                }
            }
        ),
        types.Tool(
            name="math_functions",
            description="Advanced mathematical functions",
            inputSchema={
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string", 
                        "description": "Math function to use",
                        "enum": ["sin", "cos", "tan", "log", "sqrt", "factorial"]
                    },
                    "value": {
                        "type": "number",
                        "description": "Input value for the function"
                    }
                },
                "required": ["function", "value"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool execution."""
    
    if name == "calculator":
        expression = arguments.get("expression", "")
        try:
            # Simple and safe evaluation for basic arithmetic
            # Note: In production, use a proper math parser for security
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")
            
            result = eval(expression)
            return [types.TextContent(
                type="text",
                text=f"Result: {expression} = {result}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"Error: Unable to calculate '{expression}': {str(e)}"
            )]
    
    elif name == "echo":
        text = arguments.get("text", "")
        return [types.TextContent(
            type="text",
            text=f"Echo: {text}"
        )]
    
    elif name == "timestamp":
        format_type = arguments.get("format", "iso")
        now = datetime.now()
        
        if format_type == "unix":
            timestamp = str(int(now.timestamp()))
        elif format_type == "readable":
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        else:  # iso format
            timestamp = now.isoformat()
        
        return [types.TextContent(
            type="text",
            text=f"Current timestamp ({format_type}): {timestamp}"
        )]
    
    elif name == "math_functions":
        function = arguments.get("function")
        value = arguments.get("value")
        
        try:
            if function == "sin":
                result = math.sin(math.radians(value))
            elif function == "cos":
                result = math.cos(math.radians(value))
            elif function == "tan":
                result = math.tan(math.radians(value))
            elif function == "log":
                result = math.log(value)
            elif function == "sqrt":
                result = math.sqrt(value)
            elif function == "factorial":
                result = math.factorial(int(value))
            else:
                raise ValueError(f"Unknown function: {function}")
            
            return [types.TextContent(
                type="text",
                text=f"{function}({value}) = {result}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error: Unable to calculate {function}({value}): {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main function to run the MCP server."""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example-tools-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main()) 