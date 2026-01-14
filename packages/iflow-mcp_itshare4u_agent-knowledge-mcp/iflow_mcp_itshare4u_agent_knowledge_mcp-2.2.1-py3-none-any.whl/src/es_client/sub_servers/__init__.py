#!/usr/bin/env python3
"""
Elasticsearch Sub-Servers Package

This package contains modular Elasticsearch servers extracted from the monolithic
elasticsearch_server.py for better maintainability and deployment flexibility.

Each server is a specialized FastMCP application handling specific functionality:

- elasticsearch_snapshots.py: Backup and snapshot management (3 tools)
- elasticsearch_index_metadata.py: Index governance and documentation (3 tools)  
- elasticsearch_document.py: Core document operations (3 tools)
- elasticsearch_index.py: Index lifecycle management (3 tools)
- elasticsearch_search.py: Search and validation operations (2 tools)
- elasticsearch_batch.py: Batch operations and templates (2 tools)

Total: 16 tools distributed across 6 specialized servers.

Usage:
    Each server can be run independently as a FastMCP application:
    
    python -m src.elasticsearch.sub_servers.elasticsearch_snapshots
    python -m src.elasticsearch.sub_servers.elasticsearch_document
    # ... etc
    
    Or mounted together using a unified mounting system.
"""

__version__ = "1.0.0"
__author__ = "AgentKnowledgeMCP"

# List of available sub-servers
SUB_SERVERS = [
    "elasticsearch_snapshots",
    "elasticsearch_index_metadata", 
    "elasticsearch_document",
    "elasticsearch_index",
    "elasticsearch_search",
    "elasticsearch_batch"
]

# Tool distribution mapping
TOOL_DISTRIBUTION = {
    "elasticsearch_snapshots": 3,      # create_snapshot, restore_snapshot, list_snapshots
    "elasticsearch_index_metadata": 3, # create_index_metadata, update_index_metadata, delete_index_metadata
    "elasticsearch_document": 3,       # index_document, delete_document, get_document
    "elasticsearch_index": 3,          # list_indices, create_index, delete_index
    "elasticsearch_search": 2,         # search, validate_document_schema
    "elasticsearch_batch": 2           # batch_index_directory, create_document_template
}

def get_total_tools():
    """Get total number of tools across all sub-servers."""
    return sum(TOOL_DISTRIBUTION.values())

def get_server_info():
    """Get information about all sub-servers."""
    return {
        "total_servers": len(SUB_SERVERS),
        "total_tools": get_total_tools(),
        "servers": SUB_SERVERS,
        "tool_distribution": TOOL_DISTRIBUTION
    }

# Export key information
__all__ = [
    "SUB_SERVERS",
    "TOOL_DISTRIBUTION", 
    "get_total_tools",
    "get_server_info"
]
