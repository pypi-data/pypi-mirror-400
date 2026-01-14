#!/usr/bin/env python3
"""
Elasticsearch Server - FastMCP Implementation
Unified interface mounting all modular sub-servers.

Modular Architecture:
- Original monolithic server (2344 lines) → 6 specialized servers
- Each sub-server handles specific functionality with 2-3 tools
- This unified server mounts all sub-servers into one interface

Sub-servers:
- elasticsearch_snapshots.py: 3 tools (create_snapshot, restore_snapshot, list_snapshots)
- elasticsearch_index_metadata.py: 3 tools (create/update/delete index metadata)
- elasticsearch_document.py: 3 tools (index_document, delete_document, get_document)
- elasticsearch_index.py: 3 tools (list_indices, create_index, delete_index)
- elasticsearch_search.py: 2 tools (search, validate_document_schema)  
- elasticsearch_batch.py: 2 tools (batch_index_directory, create_document_template)

Total: 16 tools unified into one interface for backward compatibility.
"""

from fastmcp import FastMCP

# Import sub-server applications for mounting
from .sub_servers.elasticsearch_snapshots import app as snapshots_app
from .sub_servers.elasticsearch_index_metadata import app as index_metadata_app
from .sub_servers.elasticsearch_document import app as document_app
from .sub_servers.elasticsearch_index import app as index_app
from .sub_servers.elasticsearch_search import app as search_app
from .sub_servers.elasticsearch_batch import app as batch_app

# Create unified FastMCP application
app = FastMCP(
    name="AgentKnowledgeMCP-Elasticsearch",
    version="2.0.0",
    instructions="Unified Elasticsearch tools for comprehensive knowledge management via modular server mounting"
)

# ================================
# SERVER MOUNTING - MODULAR ARCHITECTURE
# ================================

print("🏗️ Mounting Elasticsearch sub-servers...")

# Mount all sub-servers into unified interface
app.mount(snapshots_app)           # 3 tools: snapshot management
app.mount(index_metadata_app)      # 3 tools: metadata governance  
app.mount(document_app)            # 3 tools: document operations
app.mount(index_app)               # 3 tools: index management
app.mount(search_app)              # 2 tools: search & validation
app.mount(batch_app)               # 2 tools: batch operations

print("✅ All 6 sub-servers mounted successfully! Total: 16 tools available")

# CLI Entry Point
def main():
    """Main entry point for unified elasticsearch server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("AgentKnowledgeMCP-Elasticsearch 2.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Unified Server - FastMCP Implementation")
            print("Provides all Elasticsearch tools through modular server mounting.")
            print("\nArchitecture: 6 specialized sub-servers mounted into unified interface")
            print("Total Tools: 16 distributed across specialized servers")
            print("\nMounted Sub-servers:")
            print("  • elasticsearch_snapshots: 3 tools (backup/restore)")
            print("  • elasticsearch_index_metadata: 3 tools (governance)")  
            print("  • elasticsearch_document: 3 tools (CRUD with AI)")
            print("  • elasticsearch_index: 3 tools (lifecycle mgmt)")
            print("  • elasticsearch_search: 2 tools (search/validation)")
            print("  • elasticsearch_batch: 2 tools (bulk/templates)")
            return
    
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch server...")
    print("🔗 Architecture: Modular sub-servers with FastMCP mounting")
    print("📊 Sub-servers: 6 mounted | Tools: 16 total")
    print("✅ Status: All Elasticsearch tools available via unified interface - Ready!")
    
    # Run the unified server
    app.run()

if __name__ == "__main__":
    main()
