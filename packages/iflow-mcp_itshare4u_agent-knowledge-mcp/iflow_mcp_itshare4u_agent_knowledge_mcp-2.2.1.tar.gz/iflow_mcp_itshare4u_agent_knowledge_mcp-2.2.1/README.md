# Agent Knowledge MCP 🔍

**Complete knowledge management for AI assistants**  
MCP server with Elasticsearch search and document management.

<a href="https://glama.ai/mcp/servers/@itshare4u/AgentKnowledgeMCP">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@itshare4u/AgentKnowledgeMCP/badge" alt="Agent Knowledge MCP server" />
</a>

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

**🔑 All-in-One Solution:**
- 🔍 **Elasticsearch**: Search, index, and manage documents
- 📊 **Document Validation**: Schema-enforced structure
- ⚙️ **Configuration**: Complete config management
- 🛡️ **Security**: Sandboxed operations

**✨ Benefits:**
- 🎯 **20 Tools** for knowledge management
- 🤖 **Works with any MCP-compatible AI** (Claude, ChatGPT, VS Code, etc.)
- 📚 **Smart document management** with validation
- ⚡ **Elasticsearch integration** for powerful search

## ⚡ Quick Start

### Installation
```bash
# Install with uvx (recommended)
uvx agent-knowledge-mcp
```

### Setup for Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agent-knowledge": {
      "command": "uvx",
      "args": ["agent-knowledge-mcp"]
    }
  }
}
```

### Setup for VS Code
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=agent-knowledge&inputs=%5B%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22agent-knowledge-mcp%22%5D%7D)

## 🛠️ What You Can Do

**Try these with your AI assistant:**

- *"Search documents for API authentication info"*
- *"Index this document with proper tags"*  
- *"Create API documentation template"*
- *"Find related documents on specific topics"*
- *"Update configuration settings"*
- *"Validate document structure"*

## 🔧 Tools Overview

**Tools for knowledge management:**

| Category | Tools | Description |
|----------|-------|-------------|
| **🔍 Elasticsearch** | 9 | Search, index, manage documents |
| **⚙️ Administration** | 11 | Config, security, monitoring |

## 🔒 Security & Configuration

**Enterprise-grade security:**
- ✅ **Sandboxed operations** - Configurable access controls
- ✅ **Strict schema validation** - Enforce document structure
- ✅ **Audit trails** - Full operation logging
- ✅ **No cloud dependencies** - Everything runs locally

**Configuration example:**
```json
{
  "security": {
    "log_all_operations": true
  },
  "document_validation": {
    "strict_schema_validation": true,
    "allow_extra_fields": false
  }
}
```

## 🤝 Contributing & Support

### Development
```bash
git clone https://github.com/itshare4u/AgentKnowledgeMCP.git
cd AgentKnowledgeMCP
pip install -r requirements.txt
python3 src/main_server.py
```

### Support the Project
[![Buy Me Coffee](https://img.shields.io/badge/Buy%20Me%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://coff.ee/itshare4u)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-EA4AAA?style=flat&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/itshare4u)

---

**Transform your AI into a powerful knowledge management system! 🚀**

*MIT License - Complete knowledge management solution for AI assistants*