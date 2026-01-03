# Minion Brain Chat - LLM Configuration Guide

This application now supports flexible LLM configuration, allowing you to configure language models in multiple ways.

## Features

### 1. Preset Configurations
The application has built-in preset configurations loaded from `.env` file:
- **gpt-4o**: GPT-4o Azure configuration
- **gpt-4o-mini**: GPT-4o-mini Azure configuration  
- **gpt-4.1**: GPT-4.1 Azure configuration
- **o4-mini**: O4-mini Azure configuration

### 2. Custom Configuration
Select "Custom" option to fully customize all LLM parameters:
- API Type (openai, azure, ollama, groq, etc.)
- API Key
- Base URL
- API Version  
- Model Name
- Temperature (0.0-2.0)
- Max Tokens (100-8000)

### 3. Environment Variable Support
The application automatically loads configurations from `.env` file. Environment variable format:

```bash
# GPT-4o Azure Configuration
GPT_4O_API_TYPE=azure
GPT_4O_API_KEY=your_api_key_here
GPT_4O_BASE_URL=https://your-endpoint.openai.azure.com/
GPT_4O_API_VERSION=2024-06-01
GPT_4O_TEMPERATURE=0
GPT_4O_MAX_TOKENS=4000
GPT_4O_MODEL=gpt-4o
```

## Usage

### Method 1: Using Preset Configurations
1. Select a preset configuration from "Preset Model" dropdown (e.g., gpt-4o)
2. Other fields will automatically populate with corresponding configuration values
3. Enter your question and submit

### Method 2: Custom Configuration
1. Select "Custom" from "Preset Model" dropdown
2. Manually fill in all configuration fields:
   - API Type: Choose provider type
   - API Key: Enter your API key
   - Base URL: Enter API base URL
   - API Version: Enter API version (required for Azure)
   - Model: Enter model name
   - Temperature: Adjust generation randomness
   - Max Tokens: Set maximum generation length
3. Enter your question and submit

## Security

- API keys are displayed as `***hidden***` in the interface
- `.env` file is added to `.gitignore` and won't be committed to version control

## Configuration Examples

### OpenAI Configuration
```
API Type: openai
API Key: sk-your-openai-api-key
Base URL: https://api.openai.com/v1
API Version: (leave empty)
Model: gpt-4
Temperature: 0.7
Max Tokens: 4000
```

### Azure OpenAI Configuration
```
API Type: azure
API Key: your-azure-api-key  
Base URL: https://your-resource.openai.azure.com/
API Version: 2024-06-01
Model: gpt-4
Temperature: 0.7
Max Tokens: 4000
```

### Ollama Local Configuration
```
API Type: ollama
API Key: (leave empty)
Base URL: http://localhost:11434
API Version: (leave empty)
Model: llama2
Temperature: 0.7
Max Tokens: 4000
```

## Troubleshooting

1. **API Key Error**: Check if API key is correct and valid
2. **Connection Error**: Verify if Base URL is correct
3. **Permission Error**: Ensure API key has access to the specified model
4. **Version Error**: For Azure, ensure API Version is correct

## Updating Configuration

To update preset configurations:
1. Edit the `.env` file
2. Restart the application to load new configurations

To add new preset configurations:
1. Add new environment variables in `.env` file
2. Add new configuration in `get_preset_configs()` function in `app1.py`
3. Restart the application 