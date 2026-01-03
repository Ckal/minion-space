import gradio as gr
import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

from minion import config
from minion.main import LocalPythonEnv
from minion.main.rpyc_python_env import RpycPythonEnv
from minion.main.brain import Brain
from minion.providers import create_llm_provider

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

# Get preset configurations and default configuration
preset_configs = get_preset_configs()
default_config = get_default_config()
available_routes = get_available_routes()

async def minion_respond_async(query: str, preset_model: str, api_type: str, 
                             api_key: str, base_url: str, api_version: str, 
                             model: str, temperature: float, max_tokens: int,
                             route: str, query_type: str, check_enabled: bool):
    """Respond to query using specified configuration"""
    
    # If a preset model is selected, use preset configuration
    if preset_model != "Custom":
        config_obj = preset_configs.get(preset_model, default_config)
        llm_config_dict = {
            'api_type': config_obj.api_type,
            'api_key': config_obj.api_key,
            'base_url': config_obj.base_url,
            'api_version': config_obj.api_version,
            'model': config_obj.model,
            'temperature': config_obj.temperature,
            'max_tokens': config_obj.max_tokens,
            'vision_enabled': config_obj.vision_enabled
        }
    else:
        # Use custom configuration
        llm_config_dict = create_custom_llm_config(
            api_type, api_key, base_url, api_version, model, temperature, max_tokens
        )
    
    brain = build_brain_with_config(llm_config_dict)
    # Handle empty route selection for auto route
    route_param = route if route else None
    
    # Add query_type to kwargs if route is python
    kwargs = {'query': query, 'route': route_param, 'check': check_enabled}
    if route == "python" and query_type:
        kwargs['query_type'] = query_type
    
    obs, score, *_ = await brain.step(**kwargs)
    return obs

def minion_respond(query: str, preset_model: str, api_type: str, api_key: str, 
                  base_url: str, api_version: str, model: str, temperature: float, 
                  max_tokens: int, route: str, query_type: str, check_enabled: bool):
    """Gradio sync interface, automatically schedules async"""
    return asyncio.run(minion_respond_async(
        query, preset_model, api_type, api_key, base_url, 
        api_version, model, temperature, max_tokens, route, query_type, check_enabled
    ))

def update_fields(preset_model: str):
    """Update other fields when preset model is selected"""
    if preset_model == "Custom":
        # Return default values, let user configure themselves
        return (
            default_config.api_type,
            "",  # Don't display API key 
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
            "***hidden***",  # Hide API key display
            config_obj.base_url,
            config_obj.api_version,
            config_obj.model,
            config_obj.temperature,
            config_obj.max_tokens
        )

def update_query_type_visibility(route: str):
    """Show query_type dropdown only when route is python"""
    return gr.update(visible=(route == "python"))

# Create Gradio interface
with gr.Blocks(title="Minion Brain Chat") as demo:
    gr.Markdown("# Minion Brain Chat\nIntelligent Q&A powered by Minion1 Brain")
    
    with gr.Row():
        with gr.Column(scale=2):
            query_input = gr.Textbox(
                label="Enter your question",
                placeholder="Please enter your question...",
                lines=3
            )
            submit_btn = gr.Button("Submit", variant="primary")
            
            # Move Answer section to left column, closer to question input
            output = gr.Textbox(
                label="Answer",
                lines=10,
                show_copy_button=True
            )
            
        with gr.Column(scale=1):
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
                value="***hidden***",
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
    
    # Submit button event
    submit_btn.click(
        fn=minion_respond,
        inputs=[query_input, preset_dropdown, api_type_input, api_key_input, 
               base_url_input, api_version_input, model_input, temperature_input, 
               max_tokens_input, route_dropdown, query_type_dropdown, check_checkbox],
        outputs=[output]
    )
    
    # Enter key submit
    query_input.submit(
        fn=minion_respond,
        inputs=[query_input, preset_dropdown, api_type_input, api_key_input, 
               base_url_input, api_version_input, model_input, temperature_input, 
               max_tokens_input, route_dropdown, query_type_dropdown, check_checkbox],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch(mcp_server=True)
