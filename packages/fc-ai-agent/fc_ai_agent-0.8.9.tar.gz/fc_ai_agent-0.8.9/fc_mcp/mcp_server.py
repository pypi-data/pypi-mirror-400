#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
FastMCP Server for FC Agent
Provides tools to interact with fc clusters by calling fc-client.
"""

import importlib
import os

from fastmcp import FastMCP

from fc_mcp.mcp_base import MCPPlugin
from fc_mcp.mcp_plugins.internal.fc_mcp import Plugin


def load_external_plugins():
    """Automatically discover and load all plugins from the external folder"""
    external_dir = os.path.join(os.path.dirname(__file__), "mcp_plugins", "external")

    if not os.path.exists(external_dir):
        MCPPlugin.load_plugins(mcp)
        return

    # Find all *_mcp.py files
    for filename in os.listdir(external_dir):
        if filename.endswith("_mcp.py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                full_module_name = f"fc_mcp.mcp_plugins.external.{module_name}"
                module = importlib.import_module(full_module_name)

                if hasattr(module, "Plugin"):
                    plugin_class = getattr(module, "Plugin")
                    plugin_class(mcp)
                    print(f"Loaded external plugin: {module_name}")
                else:
                    print(f"Warning: No Plugin class found in {module_name}")

            except Exception as exce:  # pylint: disable=broad-except
                print(f"Failed to load plugin {module_name}: {exce}")


# Initialize the FastMCP server
mcp = FastMCP("FC MCP Server")

# Load internal plugins
Plugin(mcp)

# Load external plugins
load_external_plugins()

if __name__ == "__main__":
    mcp.run(show_banner=False)
