"""
Configuration management for Elasticsearch MCP Server.
"""
import json
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json with fallback to config.default.json."""
    config_path = Path(__file__).parent.parent / "config.json"
    default_config_path = Path(__file__).parent.parent / "config.default.json"
    
    # Try to load config.json first
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # If config.json not found, try config.default.json
        try:
            print("⚠️  Configuration file config.json not found, using config.default.json")
            with open(default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Both files missing - return minimal default configuration
            print("⚠️  Both config.json and config.default.json not found, using minimal default configuration")
            return {
                "elasticsearch": {"host": "localhost", "port": 9200},
                "security": {"allowed_base_directory": "/tmp/knowledge_base_secure"},
                "server": {"name": "elasticsearch-mcp", "version": "0.1.0"}
            }


def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    return load_config()
