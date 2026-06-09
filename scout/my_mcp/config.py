"""
This file loads required secrets from the .env file into the mcp_config.
LangChain-compatible MCP config loader.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()


def resolve_env_vars(config: dict) -> dict:
    """Resolve environment variables in the config."""
    for server_name, server_config in config.items():
        for prop in list(server_config.keys()):

            if prop == "env":
                for key, value in server_config[prop].items():
                    if isinstance(value, str) and value.startswith("${"):
                        env_var = value[2:-1]
                        server_config[prop][key] = os.environ.get(env_var)

            if prop == "args":
                for i, arg in enumerate(server_config[prop]):
                    if isinstance(arg, str) and arg.startswith("${"):
                        env_var = arg[2:-1]
                        server_config[prop][i] = os.environ.get(env_var)

    return config


def convert_to_langchain_format(config: dict) -> dict:
    """
    Convert Claude Desktop MCP config format to LangChain format.

    Changes:
    - Extract servers from "mcpServers" wrapper
    - Rename "type" to "connection_type"
    """
    # Extract the mcpServers content
    servers = config.get("mcpServers", config)

    # Convert "type" to "connection_type" for each server
    for server_name, server_config in servers.items():
        if "type" in server_config:
            server_config["connection_type"] = server_config.pop("type")

    return servers


config_file = Path(__file__).parent / "mcp_config.json"
if not config_file.exists():
    raise FileNotFoundError(f"{config_file} does not exist")

with open(config_file) as f:
    raw_config = json.load(f)

# Convert format and resolve environment variables
mcp_config = convert_to_langchain_format(raw_config)
mcp_config = resolve_env_vars(mcp_config)
