#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2025-2026 NXP
#
# SPDX-License-Identifier: MIT


"""
FC AI Agent CLI Application using Agno Framework
Provides command-line interface for FC operations through MCP integration.
"""

import asyncio
import importlib
import os
import sys
from getpass import getuser
from pathlib import Path
from socket import gethostname

import urllib3
from agno.agent import Agent
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.mcp import MCPTools

from fc_common.config import Config
from fc_common.version import get_runtime_version

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI color codes - Global variables
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_config_to_env():
    """Load all configuration items from user config to environment variables."""
    user_config = Config.load_user_config()

    for key, value in user_config.items():
        if value is not None:
            os.environ[key] = str(value)


def validate_config():
    """Validate all required configuration before launching the agent."""

    # Load all config to environment variables
    load_config_to_env()

    # Validate model configuration
    model_path = os.environ.get("MODEL_PATH", None)
    model_class = os.environ.get("MODEL_CLASS", None)
    model_id = os.environ.get("MODEL_ID", None)

    missing_model_configs = []

    if model_path is None:
        missing_model_configs.append("MODEL_PATH")

    if model_class is None:
        missing_model_configs.append("MODEL_CLASS")

    if model_id is None:
        missing_model_configs.append("MODEL_ID")

    if missing_model_configs:
        print(
            "❌ Model Configuration Error: missing configuration in $HOME/.fc/config.yaml"
        )
        for config in missing_model_configs:
            if config == "MODEL_PATH":
                print("   MODEL_PATH: agno.models.openai")
            elif config == "MODEL_CLASS":
                print("   MODEL_CLASS: OpenAIChat")
            elif config == "MODEL_ID":
                print("   MODEL_ID: gpt-4")
        sys.exit(1)

    # Check if using Cody model (Sourcegraph's model)
    is_cody_model = (
        "cody" in model_path.lower()
        or "cody" in model_class.lower()
        or model_path == "agno.models.cody"
    )

    # Validate Sourcegraph configuration if using Cody
    if is_cody_model:
        sourcegraph_endpoint = os.environ.get("SOURCEGRAPH_ENDPOINT")
        sourcegraph_token = os.environ.get("SOURCEGRAPH_ACCESS_TOKEN")
        sourcegraph_verify_ssl = os.environ.get("SOURCEGRAPH_VERIFY_SSL")

        missing_sourcegraph_configs = []

        if not sourcegraph_endpoint:
            missing_sourcegraph_configs.append("SOURCEGRAPH_ENDPOINT")

        if not sourcegraph_token:
            missing_sourcegraph_configs.append("SOURCEGRAPH_ACCESS_TOKEN")

        if not sourcegraph_verify_ssl:
            missing_sourcegraph_configs.append("SOURCEGRAPH_VERIFY_SSL")

        if missing_sourcegraph_configs:
            print(
                "❌ Sourcegraph Configuration Error: missing configuration in $HOME/.fc/config.yaml"
            )
            for config in missing_sourcegraph_configs:
                if config == "SOURCEGRAPH_ENDPOINT":
                    print(
                        "   SOURCEGRAPH_ENDPOINT: https://your-sourcegraph-instance.com"
                    )
                elif config == "SOURCEGRAPH_ACCESS_TOKEN":
                    print("   SOURCEGRAPH_ACCESS_TOKEN: your-access-token")
                elif config == "SOURCEGRAPH_VERIFY_SSL":
                    print("   SOURCEGRAPH_VERIFY_SSL: false")
            sys.exit(1)


async def create_fc_agent():
    """Create and configure the FC Agent."""

    # Validate all configuration first
    validate_config()

    # Now we know all required config is available
    model_path = os.environ.get("MODEL_PATH")
    model_class = os.environ.get("MODEL_CLASS")
    model_id = os.environ.get("MODEL_ID")

    try:
        module = importlib.import_module(model_path)
        model_class_obj = getattr(module, model_class)
    except ImportError as exce:
        print(f"❌ Configuration Error: Failed to import model module '{model_path}'.")
        print(f"   Exception: '{exce}'.")
        sys.exit(1)
    except AttributeError as exce:
        print(
            f"❌ Configuration Error: Model class '{model_class}' not found in module '{model_path}'."
        )
        print(f"   Exception: '{exce}'.")
        sys.exit(1)

    # Create model instance
    try:
        model = model_class_obj(model_id)
        print(f"{MAGENTA}Include {model_class}({model_id}){RESET}")
    except Exception:
        print(
            f"❌ Configuration Error: Failed to create model instance with ID '{model_id}'."
        )
        sys.exit(1)

    # Set up database path
    db_file = Path.home() / ".fc_agent" / "agno.db"
    db_file.parent.mkdir(exist_ok=True)

    # Get the MCP server path
    mcp_server_path = Path(__file__).parent / "../fc_mcp/mcp_server.py"
    python_executable = sys.executable

    # Create and connect MCP tools
    mcp_tools = MCPTools(
        transport="stdio",
        command=f"{python_executable} {mcp_server_path}",
        env=os.environ.copy(),
        timeout_seconds=120,
    )
    # Connect to the MCP server asynchronously
    await mcp_tools.connect()

    my_name = "/".join((gethostname(), getuser()))

    # Create the Agno agent with MCP tools
    agent = Agent(
        name="FC Agent",
        model=model,
        description="An intelligent agent for managing FC resources and operations",
        instructions=[
            "You are an FC Agent that helps users manage hardware resources and clusters.",
            "Use the available MCP tools to perform lock operations, check status, and manage cluster resources.",
            "Always provide clear and helpful responses about the operations performed.",
            "If an operation fails, explain what went wrong and suggest possible solutions.",
            "For resource names, use the exact format provided by the user (e.g., 'imx95-19x19-evk-sh62').",
            "When users ask for locks, use the lock tool with the resource ID they provide.",
            "When users ask for status, use the status tool with appropriate filters.",
            "When users ask about cluster info, use the cluster_info tool.",
            "When users want to unlock resources, use the unlock tool.",
            "When users ask about all locks, use the all_locks tool.",
            "For FC operations (ssh, console, power, scp, etc.), use the fc_command tool. The tool will automatically:",
            "  - For interactive commands (ssh, console): Provide the exact fc-client command to run manually, and show notes to them",
            "  - For long-running commands (scp, bootstrap): Offer both manual and automatic execution options",
            "  - For regular commands (power, reset): Execute them directly and return results",
            "When a command requires manual execution, clearly format the command and provide step-by-step instructions.",
            "Always explain what each FC operation does and guide users on the best approach.",
            "Be helpful and explain what each operation does and its results.",
            "Show fc-client command to user always",
            "For deploy/burn/flash, always check advanced features to know which operation to use",
            "For deploy/burn/flash, if support predeploy, retrive uboot configuration for nexus from uboot mcp feature",
            "For deploy/burn/flash, if support uuu, use functions from uuu bcu mcp feature",
            "For deploy/burn/flash, if support both predeploy and uuu, ask user to confirm which method to use",
            "For deploy/burn/flash, if support uuu, and if user not specify boot mode, always use usb boot please. If user specify url for local address, don't use nexus plan",
            "For deploy/burn/flash, if support uuu, and if user don't want to use uuu, get the board server ip first, then retrieve uboot configuration for uris",
            "For deploy/burn/flash, clearly tell user what artifacts will be deployed according to mcp function",
            f"I'm {my_name}",
        ],
        storage=SqliteAgentStorage(
            table_name="fc_agent_storage",
            db_file=db_file,
            auto_upgrade_schema=True,
        ),
        tools=[mcp_tools],
        stream=True,
        tool_choice="required",
        show_tool_calls=True,
        markdown=True,
        add_history_to_messages=True,
        num_history_runs=5,
        tool_call_limit=3,
        add_datetime_to_instructions=True,
        debug_mode=os.environ.get("FC_AGENT_DEBUG_MODE", "false").lower() == "true",
    )

    return agent


def print_banner():
    """Print comprehensive banner with all welcome information for FC Agent."""
    version = get_runtime_version("fc-agent")

    banner = f"""
{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}

                ███████╗ ██████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
                ██╔════╝██╔════╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
                █████╗  ██║         ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
                ██╔══╝  ██║         ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
                ██║     ╚██████╗    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
                ╚═╝      ╚═════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝{RESET}

{GREEN}{BOLD}                  🤖 FC AGENT ({version}) -- AI Intelligent Resource Management{RESET}

{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}
{YELLOW}{BOLD}                                    AVAILABLE OPERATIONS{RESET}
{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}
{BLUE}  • Lock resources: {RESET}'lock imx95-19x19-evk-sh62'
{BLUE}  • Unlock resources: {RESET}'unlock imx95-19x19-evk-sh62'
{BLUE}  • Check status: {RESET}'status of all resources'
{BLUE}  • Cluster info: {RESET}'show cluster information'
{BLUE}  • List locks: {RESET}'show all current locks'

{MAGENTA}{BOLD}  FC OPERATIONS:{RESET}
{BLUE}    - SSH access: {RESET}'ssh to imx95-19x19-evk-sh62'
{BLUE}    - Console access: {RESET}'console to imx95-19x19-evk-sh62'
{BLUE}    - Power control: {RESET}'power cycle/on/off imx95-19x19-evk-sh62'
{BLUE}    - File transfer: {RESET}'scp file to imx95-19x19-evk-sh62'

{MAGENTA}{BOLD}  DEPLOY/FLASH OPERATIONS:{RESET}
{BLUE}    - Check flash modes: {RESET}'what flash modes does ... support?'
{BLUE}    - Deploy images: {RESET}'deploy Linux_Factory 668 to ...'

{GREEN}  General questions: {RESET}'what can you do?'

{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}
{YELLOW}{BOLD}                                         💡 TIPS{RESET}
{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}
  • The agent will automatically check supported modes for deploy/flash operations
  • Interactive commands (ssh/console) will provide manual instructions
  • Flash operations will generate script for you to manually run or provide manual instructions
  • Use specific resource IDs like 'imx95-19x19-evk-sh62' for operations

  Type 'exit', 'quit', or 'bye' to end the session.

{CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════{RESET}
    """
    print(banner)


async def amain():
    """Main function to run the FC Agent CLI."""

    print_banner()

    # Create the agent
    agent = await create_fc_agent()

    # Start the CLI loop using Agno's built-in CLI
    try:
        await agent.acli_app(
            input="Hello! I'm your FC Agent ready to help you manage hardware resources and clusters. "
            "What would you like me to help you with today?",
            user=f"{GREEN}User Question{RESET}",
            emoji="👤",
            stream=True,
        )
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Goodbye!{RESET}")
    except Exception as exce:
        print(f"{RED}❌ Error: {str(exce)}{RESET}")
    finally:
        # Clean up MCP connections
        try:
            for tool in agent.tools:
                if hasattr(tool, "disconnect"):
                    await tool.disconnect()
                elif hasattr(tool, "close"):
                    await tool.close()
        except Exception:
            # Suppress cleanup errors to avoid masking the original issue
            pass


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
