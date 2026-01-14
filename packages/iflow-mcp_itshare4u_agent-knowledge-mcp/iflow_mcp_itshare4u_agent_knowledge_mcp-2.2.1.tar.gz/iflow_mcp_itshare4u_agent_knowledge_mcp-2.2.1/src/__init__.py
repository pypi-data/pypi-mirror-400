# AgentKnowledgeMCP - Advanced Knowledge Management for AI Agents
import asyncio
from . import main_server

"""AgentKnowledgeMCP - Advanced Knowledge Management for AI Agents."""

__version__ = "2.2.1"

def main():
    """Main entry point for the package."""
    main_server.cli_main()

# Optionally expose other important items at package level
__all__ = ['main', 'main_server', '__version__']