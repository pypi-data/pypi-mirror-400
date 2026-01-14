"""
AgentKnowledgeMCP Prompt Server
FastMCP server for prompts providing comprehensive MCP usage guide content for LLM assistance.

Modular Architecture:
- Mounts specialized sub-servers for specific functionality
- Smart prompting capabilities via dedicated sub-server
- Unified interface for all prompt-related tools

Sub-servers:
- smart_prompting_server.py: 1 tool (ask_mcp_advice) for AI-filtered project guidance
- instructions_server.py: 2 prompts (mcp_usage_guide, copilot_instructions) for guidance documentation
"""

from fastmcp import FastMCP

# Import sub-server applications for mounting
from .sub_servers.smart_prompting_server import app as smart_prompting_app
from .sub_servers.instructions_server import app as instructions_app

# Create FastMCP app for prompt guidance and resource access
app = FastMCP(
    name="AgentKnowledgeMCP-Prompts",
    version="2.0.0",
    instructions="Unified prompt server with comprehensive MCP usage guides and modular smart prompting capabilities"
)

# ================================
# SERVER MOUNTING - MODULAR ARCHITECTURE
# ================================

print("🏗️ Mounting Prompt sub-servers...")

# Mount smart prompting sub-server
app.mount(smart_prompting_app)     # 1 tool: ask_mcp_advice for AI-filtered guidance

# Mount instructions sub-server  
app.mount(instructions_app)        # 2 prompts: mcp_usage_guide, copilot_instructions

print("✅ Smart prompting sub-server mounted successfully")
print("✅ Instructions sub-server mounted successfully")

# ================================
# CLI ENTRY POINT
# ================================
def cli_main():
    """CLI entry point for Prompt FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Prompt FastMCP server...")
    print("📝 Available prompts (via sub-servers):")
    print("  • mcp_usage_guide - Comprehensive usage guide with scenarios and tutorials")
    print("  • copilot_instructions - AI assistant behavioral guidelines and protocols")
    print("🛠️ Available tools (via sub-servers):")
    print("  • ask_mcp_advice - Smart prompting with AI-filtered project knowledge")
    print("✨ Provides complete guidance and modular smart prompting capabilities")

    app.run()

if __name__ == "__main__":
    cli_main()
