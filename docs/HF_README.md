---
title: Minion Space
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.32.0
app_file: app_with_mcp.py
pinned: false
license: mit
short_description: minion running in space
tags:
  - mcp-server-track
  - agent-demo-track
---

An example chatbot based on minion framework(https://github.com/femto/minion), can handle arbitray type
of queries, task-aware routing(if don't choose route, it will automatically choose proper route)


## Demo Videos

🎥 **[Minion-Space Demo: Solving Game 24 and Listing Files](https://youtu.be/FGjvGHKKxfo)**

Watch this video to see minion-space in action, demonstrating how it can solve mathematical puzzles like the Game of 24 and perform file operations.

🎥 **[Minion-Space List-Files Demo](https://youtu.be/7neYqi_IQ18)**

This video showcases the list-files functionality of minion-space, demonstrating how it can efficiently browse and manage file systems.

🎥 **[Plan Writing Long Novel](https://youtu.be/ULPvwcyhsI4)**

This video demonstrates how to plan writing long novels using minion-space, showcasing its capability for creative writing planning and story structure development.

🎥 **[Plan Trip](https://youtu.be/nFK2PoL1SfE)**

This video demonstrates how to plan trips using minion-space, showcasing its capability for travel planning, itinerary creation, and destination recommendations.

## Configuration Options

### API Type Configuration
- **openai**: For OpenAI-compatible APIs (OpenAI, local models, etc.)
  - Use standard OpenAI API format
  - Set Base URL to your API endpoint
  - API Version is optional
- **azure**: For Azure OpenAI Service
  - **Required**: Must specify API Version (e.g., "2024-06-01")
  - Set Base URL to your Azure endpoint
  - Uses Azure-specific authentication

### Route Selection
- **Auto (empty)**: Automatically selects the most appropriate route based on query type
- **Raw**: Direct LLM output without additional processing
- **Native**: Standard minion processing
- **CoT**: Chain of Thought reasoning for complex problems
- **DCoT**: Dynamic Chain of Thought with adaptive reasoning
- **Plan**: Planning-based approach for multi-step tasks
- **Python**: Code execution environment for computational queries

### Preset Models
- **gpt-4o**: Latest GPT-4 Omni model for general tasks
- **gpt-4o-mini**: Lightweight version for faster responses
- **gpt-4.1**: Advanced reasoning model
- **o4-mini**: Optimized mini model
- **Custom**: Configure your own API settings

### Additional Settings
- **Enable Check**: Activates output verification and validation
- **Query Type** (Python route only): Choose between `calculate`, `code_solution`, or `generate`
- **Temperature**: Controls response creativity (0.0-2.0)
- **Max Tokens**: Maximum response length (100-8000)