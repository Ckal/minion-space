import gradio as gr
import asyncio
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from minion.main import LocalPythonEnv
from minion.main.rpyc_python_env import RpycPythonEnv
from minion.main.brain import Brain
from minion.providers import create_llm_provider

# Import our MCP integration
from mcp_integration import MCPBrainClient, create_final_answer_tool, BrainTool, add_filesystem_tool

# Load .env file
load_dotenv()

class LLMConfig:
    def __init__(self, api_type: str, api_key: str, base_url: str, api_version: str, 
                 model: str, temperature: float = 0.7, max_tokens: int = 4000, 
                 vision_enabled: bool = False):
        self.api_type = api_type
        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.vision_enabled = vision_enabled

def get_preset_configs():
    """Get preset configurations"""
    presets = {
        "gpt-4o": LLMConfig(
            api_type=os.getenv("GPT_4O_API_TYPE", "azure"),
            api_key=os.getenv("GPT_4O_API_KEY", ""),
            base_url=os.getenv("GPT_4O_BASE_URL", ""),
            api_version=os.getenv("GPT_4O_API_VERSION", "2024-06-01"),
            model=os.getenv("GPT_4O_MODEL", "gpt-4o"),
            temperature=float(os.getenv("GPT_4O_TEMPERATURE", "0")),
            max_tokens=int(os.getenv("GPT_4O_MAX_TOKENS", "4000"))
        ),
        "gpt-4o-mini": LLMConfig(
            api_type=os.getenv("GPT_4O_MINI_API_TYPE", "azure"),
            api_key=os.getenv("GPT_4O_MINI_API_KEY", ""),
            base_url=os.getenv("GPT_4O_MINI_BASE_URL", ""),
            api_version=os.getenv("GPT_4O_MINI_API_VERSION", "2024-06-01"),
            model=os.getenv("GPT_4O_MINI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("GPT_4O_MINI_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("GPT_4O_MINI_MAX_TOKENS", "4000"))
        ),
        "gpt-4.1": LLMConfig(
            api_type=os.getenv("GPT_41_API_TYPE", "azure"),
            api_key=os.getenv("GPT_41_API_KEY", ""),
            base_url=os.getenv("GPT_41_BASE_URL", ""),
            api_version=os.getenv("GPT_41_API_VERSION", "2025-03-01-preview"),
            model=os.getenv("GPT_41_MODEL", "gpt-4.1"),
            temperature=float(os.getenv("GPT_41_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GPT_41_MAX_TOKENS", "4000"))
        ),
        "o4-mini": LLMConfig(
            api_type=os.getenv("O4_MINI_API_TYPE", "azure"),
            api_key=os.getenv("O4_MINI_API_KEY", ""),
            base_url=os.getenv("O4_MINI_BASE_URL", ""),
            api_version=os.getenv("O4_MINI_API_VERSION", "2025-03-01-preview"),
            model=os.getenv("O4_MINI_MODEL", "o4-mini"),
            temperature=float(os.getenv("O4_MINI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("O4_MINI_MAX_TOKENS", "4000"))
        )
    }
    return presets

def get_default_config():
    """Get default configuration"""
    return LLMConfig(
        api_type=os.getenv("DEFAULT_API_TYPE", "azure"),
        api_key=os.getenv("DEFAULT_API_KEY", ""),
        base_url=os.getenv("DEFAULT_BASE_URL", ""),
        api_version=os.getenv("DEFAULT_API_VERSION", "2024-06-01"),
        model=os.getenv("DEFAULT_MODEL", "gpt-4o"),
        temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "4000"))
    )

def get_available_routes():
    """Get available route options for current minion system"""
    return [
        "",            # Auto route selection (empty for automatic)
        "raw",         # Raw LLM output without processing
        "native",      # Native minion processing
        "cot",         # Chain of Thought reasoning
        "dcot",        # Dynamic Chain of Thought
        "plan",        # Planning-based approach
        "python"       # Python code execution
    ]

def create_custom_llm_config(api_type: str, api_key: str, base_url: str, 
                           api_version: str, model: str, temperature: float, 
                           max_tokens: int) -> Dict[str, Any]:
    """Create custom LLM configuration"""
    return {
        'api_type': api_type,
        'api_key': api_key,
        'base_url': base_url,
        'api_version': api_version,
        'model': model,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'vision_enabled': False
    }

def build_brain_with_config(llm_config_dict: Dict[str, Any]):
    """Build brain with specified configuration"""
    # Create a config object similar to LLMConfig
    class Config:
        def __init__(self, config_dict):
            for key, value in config_dict.items():
                setattr(self, key, value)
    
    config_obj = Config(llm_config_dict)
    llm = create_llm_provider(config_obj)
    python_env = LocalPythonEnv(verbose=False)
    brain = Brain(
        python_env=python_env,
        llm=llm,
    )
    return brain

# Global MCP client instance
mcp_client: Optional[MCPBrainClient] = None

async def setup_mcp_tools():
    """Setup MCP tools and connections"""
    global mcp_client
    
    if mcp_client is None:
        mcp_client = MCPBrainClient()
        await mcp_client.__aenter__()
        
        # Add filesystem tool (always try to add this)
        try:
            await add_filesystem_tool(mcp_client)
            print("✓ Added filesystem tool")
        except Exception as e:
            print(f"⚠ Failed to add filesystem tool: {e}")
        
        # Add MCP servers from environment variables
        # Example: SSE server
        sse_url = os.getenv("MCP_SSE_URL")
        if sse_url:
            try:
                await mcp_client.add_mcp_server("sse", url=sse_url)
                print(f"✓ Added SSE server: {sse_url}")
            except Exception as e:
                print(f"⚠ Failed to add SSE server: {e}")
        
        # Example: Stdio server
        stdio_command = os.getenv("MCP_STDIO_COMMAND")
        if stdio_command:
            try:
                await mcp_client.add_mcp_server("stdio", command=stdio_command)
                print(f"✓ Added stdio server: {stdio_command}")
            except Exception as e:
                print(f"⚠ Failed to add stdio server: {e}")
    
    return mcp_client

async def get_available_tools() -> List[BrainTool]:
    """Get all available tools including MCP tools and final answer tool"""
    try:
        mcp_client = await setup_mcp_tools()
        mcp_tools = mcp_client.get_tools_for_brain()
    except Exception as e:
        print(f"Warning: Failed to setup MCP tools: {e}")
        mcp_tools = []
    
    # Always add final answer tool
    final_answer_tool = create_final_answer_tool()
    
    return mcp_tools #+ [final_answer_tool]

# Get preset configurations and default configuration
preset_configs = get_preset_configs()
default_config = get_default_config()
available_routes = get_available_routes()

async def minion_respond_async(query: str, 
                             preset_model: str = "gpt-4o", 
                             api_type: str = None, 
                             api_key: str = None, 
                             base_url: str = None, 
                             api_version: str = None, 
                             model: str = None, 
                             temperature: float = None, 
                             max_tokens: int = None,
                             route: str = "", 
                             query_type: str = "calculate", 
                             check_enabled: bool = False,
                             use_tools: bool = True):
    """Respond to query using specified configuration with optional MCP tools"""
    
    # Get default config for None values
    if api_type is None:
        api_type = default_config.api_type
    if api_key is None:
        api_key = default_config.api_key
    if base_url is None:
        base_url = default_config.base_url
    if api_version is None:
        api_version = default_config.api_version
    if model is None:
        model = default_config.model
    if temperature is None:
        temperature = default_config.temperature
    if max_tokens is None:
        max_tokens = default_config.max_tokens
    
    # Always use the current UI values, regardless of preset selection
    # Preset is only used for initializing UI fields, not for actual execution
    llm_config_dict = create_custom_llm_config(
        api_type, api_key, base_url, api_version, model, temperature, max_tokens
    )
    
    if preset_model != "Custom":
        print(f"🔧 Using preset '{preset_model}' base with UI overrides:")
        print(f"   - API Type: {api_type}")
        print(f"   - Model: {model}")
        print(f"   - Base URL: {base_url}")
        print(f"   - API Version: {api_version}")
        print(f"   - Temperature: {temperature}")
        print(f"   - Max tokens: {max_tokens}")
    else:
        print(f"🔧 Using custom configuration:")
        print(f"   - API Type: {api_type}")
        print(f"   - Model: {model}")
        print(f"   - Base URL: {base_url}")
        print(f"   - API Version: {api_version}")
        print(f"   - Temperature: {temperature}")
        print(f"   - Max tokens: {max_tokens}")
    
    # Always rebuild brain with current UI configuration
    print(f"🧠 Building brain with final config:")
    print(f"   - Final API type: {llm_config_dict['api_type']}")
    print(f"   - Final model: {llm_config_dict['model']}")
    print(f"   - Final temperature: {llm_config_dict['temperature']}")
    print(f"   - Final max_tokens: {llm_config_dict['max_tokens']}")
    brain = build_brain_with_config(llm_config_dict)
    
    # Handle empty route selection for auto route
    route_param = route if route else None
    
    # Build kwargs for brain.step
    kwargs = {'query': query, 'route': route_param, 'check': check_enabled}
    
    # Add query_type to kwargs if route is python
    if route == "python" and query_type:
        kwargs['query_type'] = query_type
    
    # Add tools if enabled
    if use_tools:
        try:
            tools = await get_available_tools()
            kwargs['tools'] = tools
            print(f"🔧 Using {len(tools)} tools: {[tool.name for tool in tools]}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to get tools: {e}")
    
    print(f"🚀 Executing brain.step with route='{route_param}', check={check_enabled}")
    obs, score, *_ = await brain.step(**kwargs)
    return obs

def minion_respond(query: str, preset_model: str, api_type: str, api_key: str, 
                  base_url: str, api_version: str, model: str, temperature: float, 
                  max_tokens: int, route: str, query_type: str, check_enabled: bool,
                  use_tools: bool):
    """Gradio sync interface, automatically schedules async"""
    return asyncio.run(minion_respond_async(
        query, preset_model, api_type, api_key, base_url, 
        api_version, model, temperature, max_tokens, route, query_type, check_enabled,
        use_tools
    ))

def update_fields(preset_model: str):
    """Update other fields when preset model is selected"""
    if preset_model == "Custom":
        # Return default values, let user configure themselves
        return (
            default_config.api_type,
            default_config.api_key,  # Show real API key instead of empty
            default_config.base_url,
            default_config.api_version,
            default_config.model,
            default_config.temperature,
            default_config.max_tokens
        )
    else:
        config_obj = preset_configs.get(preset_model, default_config)
        # Ensure API type is from valid choices
        api_type = config_obj.api_type if config_obj.api_type in ["azure", "openai", "groq", "ollama", "anthropic", "gemini"] else "azure"
        return (
            api_type,
            config_obj.api_key,  # Show real API key from preset config
            config_obj.base_url,
            config_obj.api_version,
            config_obj.model,
            config_obj.temperature,
            config_obj.max_tokens
        )

def update_query_type_visibility(route: str):
    """Show query_type dropdown only when route is python"""
    return gr.update(visible=(route == "python"))

async def get_tool_status():
    """Get status of available tools"""
    try:
        tools = await get_available_tools()
        return f"Available tools: {', '.join([tool.name for tool in tools])}"
    except Exception as e:
        return f"Error getting tools: {str(e)}"

def check_tools():
    """Sync wrapper for tool status check"""
    return asyncio.run(get_tool_status())

# Create Gradio interface
with gr.Blocks(title="Minion Brain Chat with MCP Tools") as demo:
    gr.Markdown("# Minion Brain Chat with MCP Tools\nIntelligent Q&A powered by Minion1 Brain with MCP tool support")
    
    with gr.Row():
        with gr.Column(scale=2):
            query_input = gr.Textbox(
                label="Enter your question",
                placeholder="Please enter your question...",
                lines=3
            )
            submit_btn = gr.Button("Submit", variant="primary")
            
            # Tool status
            with gr.Row():
                tool_status_btn = gr.Button("Check Available Tools", size="sm")
                tool_status_output = gr.Textbox(
                    label="Tool Status",
                    lines=2,
                    interactive=False
                )
            
            # Move Answer section to left column, closer to question input
            output = gr.Textbox(
                label="Answer",
                lines=10,
                show_copy_button=True
            )
            
        with gr.Column(scale=1):
            # Tool settings
            use_tools_checkbox = gr.Checkbox(
                label="Enable MCP Tools",
                value=True,
                info="Use Model Context Protocol tools"
            )
            
            # Move route selection to the front
            route_dropdown = gr.Dropdown(
                label="Route",
                choices=available_routes,
                value="",
                info="empty: auto select, raw: direct LLM, native: standard, cot: chain of thought, dcot: dynamic cot, plan: planning, python: code execution"
            )
            
            # Add query_type option, visible only when route="python"
            query_type_dropdown = gr.Dropdown(
                label="Query Type",
                choices=["calculate", "code_solution", "generate"],
                value="calculate",
                visible=False,
                info="Type of query for python route"
            )
            
            # Add check option
            check_checkbox = gr.Checkbox(
                label="Enable Check",
                value=False,
                info="Enable output verification and validation"
            )
            
            preset_dropdown = gr.Dropdown(
                label="Preset Model",
                choices=["Custom"] + list(preset_configs.keys()),
                value="gpt-4o",
                info="Select preset configuration or custom"
            )
            
            api_type_input = gr.Dropdown(
                label="API Type",
                choices=["azure", "openai", "groq", "ollama", "anthropic", "gemini"],
                value=default_config.api_type,
                info="Select API provider type"
            )
            
            api_key_input = gr.Textbox(
                label="API Key",
                value=default_config.api_key,  # Show real API key instead of masked value
                type="password",
                info="Your API key"
            )
            
            base_url_input = gr.Textbox(
                label="Base URL",
                value=default_config.base_url,
                info="API base URL"
            )
            
            api_version_input = gr.Textbox(
                label="API Version",
                value=default_config.api_version,
                info="API version (required for Azure)"
            )
            
            model_input = gr.Textbox(
                label="Model",
                value=default_config.model,
                info="Model name"
            )
            
            temperature_input = gr.Slider(
                label="Temperature",
                minimum=0.0,
                maximum=2.0,
                value=default_config.temperature,
                step=0.1,
                info="Control output randomness"
            )
            
            max_tokens_input = gr.Slider(
                label="Max Tokens",
                minimum=100,
                maximum=8000,
                value=default_config.max_tokens,
                step=100,
                info="Maximum number of tokens to generate"
            )
    
    # Update other fields when preset model changes
    preset_dropdown.change(
        fn=update_fields,
        inputs=[preset_dropdown],
        outputs=[api_type_input, api_key_input, base_url_input, 
                api_version_input, model_input, temperature_input, max_tokens_input]
    )
    
    # Update query_type visibility when route changes
    route_dropdown.change(
        fn=update_query_type_visibility,
        inputs=[route_dropdown],
        outputs=[query_type_dropdown]
    )
    
    # Tool status check
    tool_status_btn.click(
        fn=check_tools,
        outputs=[tool_status_output]
    )
    
    # Submit button event
    submit_btn.click(
        fn=minion_respond_async,
        inputs=[query_input, preset_dropdown, api_type_input, api_key_input, 
               base_url_input, api_version_input, model_input, temperature_input, 
               max_tokens_input, route_dropdown, query_type_dropdown, check_checkbox,
               use_tools_checkbox],
        outputs=[output]
    )
    
    # Enter key submit
    query_input.submit(
        fn=minion_respond_async,
        inputs=[query_input, preset_dropdown, api_type_input, api_key_input, 
               base_url_input, api_version_input, model_input, temperature_input, 
               max_tokens_input, route_dropdown, query_type_dropdown, check_checkbox,
               use_tools_checkbox],
        outputs=[output]
    )

# Cleanup function
async def cleanup_on_exit():
    """Clean up MCP client on exit"""
    global mcp_client
    if mcp_client:
        await mcp_client.cleanup()

if __name__ == "__main__":
    try:
        demo.launch(mcp_server=True)
    finally:
        asyncio.run(cleanup_on_exit()) 