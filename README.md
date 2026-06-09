# MCP-Intro: MCP-Langgraph Integration Tutorial

## Project Overview

MCP-Intro demonstrates the integration of Model Context Protocol (MCP) servers with Langgraph agents to build a powerful, tool-enabled conversational AI assistant named Scout. Scout uses GPT-4.1 as the base LLM and orchestrates communication across multiple MCP servers to perform specialized tasks.

## Key Features

- Conversational AI agent leveraging GPT-4.1-mini
- Dynamic integration with multiple MCP servers providing tools for filesystem operations, data manipulation, version control, and more
- Orchestration of conversation and tool usage using Langgraph's state graph
- Real-time streaming of responses with tool call support
- Autonomous engineering reflection system for analyzing execution results and improving assistant behavior

## Project Structure

```
scout/
├── graph.py           # Langgraph agent graph and prompt definition
├── client.py          # MCP client for connecting to MCP servers and running conversation
├── reflection.py      # Engineering reflection system for analyzing execution
├── my_mcp/            # MCP server configs and custom implementations
│   ├── config.py      # MCP server config loader
│   └── mcp_config.json # MCP server definitions
└── ...                # Other project files and directories
```

## Prerequisites

- Python 3.13+
- Node.js (for filesystem MCP server)
- Docker (for GitHub MCP server)
- UV package manager
- OpenAI API key (configured in environment)

## Usage

1. Configure MCP servers in `my_mcp/mcp_config.json`.
2. Run the client:

```bash
python scout/client.py
```

3. Interact with Scout via the command line.
4. Type `quit` or `exit` to terminate the session.

## Extending the Project

- Add new MCP servers by implementing them under `my_mcp/local_servers/` and updating the config.
- Modify or extend the prompt and tools in `scout/graph.py`.
- Customize conversation flow using Langgraph state graph nodes and edges.
- Enhance reflection capabilities in `scout/reflection.py`.

## Contributing

Contributions and improvements are welcome! Please create pull requests.

## License

Specify your project license here.
