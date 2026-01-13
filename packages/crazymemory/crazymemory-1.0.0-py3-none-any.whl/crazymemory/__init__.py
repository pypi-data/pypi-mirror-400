"""
CrazyMemory (Neural Fabric X) Python SDK
Universal Memory Layer for AI Agents

Make any AI "CrazyMemory-aware" in one line of code.
"""

__version__ = "1.0.0"
__author__ = "DevMubarak"

from .client import (
    CrazyMemory,
    FabricClient,
    quick_sync,
    fabric_aware,
)

from .mcp_client import (
    MCPClient,
    install_mcp_server,
)

__all__ = [
    "CrazyMemory",
    "FabricClient", 
    "MCPClient",
    "quick_sync",
    "fabric_aware",
    "install_mcp_server",
]
