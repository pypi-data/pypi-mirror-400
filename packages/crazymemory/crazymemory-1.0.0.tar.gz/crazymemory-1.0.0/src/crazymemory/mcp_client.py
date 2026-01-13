"""
CrazyMemory MCP Client
Native Model Context Protocol integration for Claude Desktop, Cursor, Windsurf, etc.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class MCPClient:
    """
    MCP-native client for CrazyMemory.
    Automatically integrates with Claude Desktop and other MCP-compatible apps.
    """
    
    def __init__(self, server_path: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_path: Path to MCP server (auto-detected if None)
        """
        self.server_path = server_path or self._find_server()
    
    def _find_server(self) -> str:
        """Auto-detect MCP server location"""
        # Try common locations
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "backend" / "mcp_server" / "server.py",
            Path.cwd() / "backend" / "mcp_server" / "server.py",
            Path.home() / ".crazymemory" / "mcp_server" / "server.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            "CrazyMemory MCP server not found. "
            "Please install with: crazymemory.install_mcp_server()"
        )
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get MCP configuration for Claude Desktop / other MCP clients.
        
        Returns:
            Config dict to add to claude_desktop_config.json or similar
        """
        python_path = sys.executable
        
        return {
            "mcpServers": {
                "crazymemory": {
                    "command": python_path,
                    "args": [self.server_path],
                    "description": "CrazyMemory - Universal Memory Layer",
                    "schema": {
                        "type": "mcp",
                        "version": "1.0"
                    }
                }
            }
        }
    
    def install_to_claude(self, force: bool = False) -> bool:
        """
        Automatically install to Claude Desktop.
        
        Args:
            force: Overwrite existing config
        
        Returns:
            True if successful
        """
        # Find Claude config
        if sys.platform == "win32":
            config_path = Path(os.getenv('APPDATA')) / "Claude" / "claude_desktop_config.json"
        elif sys.platform == "darwin":
            config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:
            config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        
        if not config_path.parent.exists():
            print(f"❌ Claude Desktop config not found at: {config_path}")
            return False
        
        # Read existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Check if already installed
        if not force and 'mcpServers' in config and 'crazymemory' in config['mcpServers']:
            print("✅ CrazyMemory already installed in Claude Desktop")
            return True
        
        # Add CrazyMemory server
        our_config = self.get_config()
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        config['mcpServers']['crazymemory'] = our_config['mcpServers']['crazymemory']
        
        # Write config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ CrazyMemory installed to Claude Desktop!")
        print(f"📍 Config: {config_path}")
        print(f"\n⚠️  RESTART Claude Desktop to activate")
        
        return True
    
    def install_to_cursor(self) -> bool:
        """Install to Cursor IDE"""
        # Cursor uses similar MCP config
        if sys.platform == "win32":
            config_path = Path(os.getenv('APPDATA')) / "Cursor" / "User" / "mcp_config.json"
        elif sys.platform == "darwin":
            config_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "mcp_config.json"
        else:
            config_path = Path.home() / ".config" / "Cursor" / "User" / "mcp_config.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read or create config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add CrazyMemory
        our_config = self.get_config()
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        config['mcpServers']['crazymemory'] = our_config['mcpServers']['crazymemory']
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ CrazyMemory installed to Cursor!")
        print(f"📍 Config: {config_path}")
        print(f"\n⚠️  RESTART Cursor to activate")
        
        return True
    
    def install_to_windsurf(self) -> bool:
        """Install to Windsurf IDE"""
        # Windsurf config location
        if sys.platform == "win32":
            config_path = Path(os.getenv('APPDATA')) / "Windsurf" / "mcp_servers.json"
        else:
            config_path = Path.home() / ".windsurf" / "mcp_servers.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {"servers": {}}
        
        our_config = self.get_config()
        config['servers']['crazymemory'] = our_config['mcpServers']['crazymemory']
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ CrazyMemory installed to Windsurf!")
        print(f"📍 Config: {config_path}")
        
        return True
    
    def install_to_copilot(self) -> bool:
        """Install to Microsoft Copilot (if it supports MCP)"""
        print("⚠️  Microsoft Copilot MCP integration coming soon")
        return False
    
    def install_all(self) -> Dict[str, bool]:
        """Install to all detected MCP clients"""
        results = {
            "claude": False,
            "cursor": False,
            "windsurf": False,
            "copilot": False
        }
        
        print("🚀 Installing CrazyMemory to all MCP clients...\n")
        
        try:
            results["claude"] = self.install_to_claude()
        except Exception as e:
            print(f"❌ Claude: {e}")
        
        try:
            results["cursor"] = self.install_to_cursor()
        except Exception as e:
            print(f"❌ Cursor: {e}")
        
        try:
            results["windsurf"] = self.install_to_windsurf()
        except Exception as e:
            print(f"❌ Windsurf: {e}")
        
        print(f"\n✅ Installed to {sum(results.values())} clients")
        
        return results


def install_mcp_server(target: str = "all") -> bool:
    """
    Quick installer for MCP integration.
    
    Usage:
        from crazymemory import install_mcp_server
        
        install_mcp_server("claude")  # Install to Claude Desktop
        install_mcp_server("all")     # Install everywhere
    
    Args:
        target: "claude", "cursor", "windsurf", "copilot", or "all"
    
    Returns:
        True if successful
    """
    client = MCPClient()
    
    if target == "all":
        results = client.install_all()
        return any(results.values())
    elif target == "claude":
        return client.install_to_claude()
    elif target == "cursor":
        return client.install_to_cursor()
    elif target == "windsurf":
        return client.install_to_windsurf()
    elif target == "copilot":
        return client.install_to_copilot()
    else:
        print(f"❌ Unknown target: {target}")
        print("Valid targets: claude, cursor, windsurf, copilot, all")
        return False
