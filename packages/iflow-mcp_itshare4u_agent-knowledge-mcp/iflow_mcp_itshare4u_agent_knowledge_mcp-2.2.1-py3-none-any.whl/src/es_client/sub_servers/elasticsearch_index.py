"""
Elasticsearch Index FastMCP Server
Index management operations extracted from main elasticsearch server.
Handles index creation, deletion, and listing operations.
"""
import json
from typing import Dict, Any, Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field

from ..elasticsearch_client import get_es_client

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Index",
    version="1.0.0",
    instructions="Elasticsearch index management tools"
)


@app.tool(
    description="Create a new Elasticsearch index with optional mapping and settings configuration",
    tags={"elasticsearch", "create", "index", "mapping"}
)
async def create_index(
        index: Annotated[str, Field(description="Name of the new Elasticsearch index to create")],
        mapping: Annotated[
            Dict[str, Any], Field(description="Index mapping configuration defining field types and properties")],
        settings: Annotated[Optional[Dict[str, Any]], Field(
            description="Optional index settings for shards, replicas, analysis, etc.")] = None
) -> str:
    """Create a new Elasticsearch index with mapping and optional settings."""
    try:
        es = get_es_client()

        # Special case: Allow creating index_metadata without validation
        if index == "index_metadata":
            body = {"mappings": mapping}
            if settings:
                body["settings"] = settings

            result = es.indices.create(index=index, body=body)

            return (f"✅ Index metadata system initialized successfully!\n\n" +
                    f"📋 **Metadata Index Created**: {index}\n" +
                    f"🔧 **System Status**: Index metadata management now active\n" +
                    f"✅ **Next Steps**:\n" +
                    f"   1. Use 'create_index_metadata' to document your indices\n" +
                    f"   2. Then use 'create_index' to create actual indices\n" +
                    f"   3. Use 'list_indices' to see metadata integration\n\n" +
                    f"🎯 **Benefits Unlocked**:\n" +
                    f"   • Index governance and documentation enforcement\n" +
                    f"   • Enhanced index listing with descriptions\n" +
                    f"   • Proper cleanup workflows for index deletion\n" +
                    f"   • Team collaboration through shared index understanding\n\n" +
                    f"📋 **Technical Details**:\n{json.dumps(result, indent=2, ensure_ascii=False)}")

        # Check if metadata document exists for this index
        metadata_index = "index_metadata"
        try:
            # Search for existing metadata document
            search_body = {
                "query": {
                    "term": {
                        "index_name": index
                    }
                },
                "size": 1
            }

            metadata_result = es.search(index=metadata_index, body=search_body)

            if metadata_result['hits']['total']['value'] == 0:
                return (f"❌ Index creation blocked - Missing metadata documentation!\n\n" +
                        f"🚨 **MANDATORY: Create Index Metadata First**:\n" +
                        f"   📋 **Required Action**: Before creating index '{index}', you must document it\n" +
                        f"   🔧 **Use This Tool**: Call 'create_index_metadata' tool first\n" +
                        f"   📝 **Required Information**:\n" +
                        f"      • Index purpose and description\n" +
                        f"      • Data types and content it will store\n" +
                        f"      • Usage patterns and access frequency\n" +
                        f"      • Retention policies and lifecycle\n" +
                        f"      • Related indices and dependencies\n\n" +
                        f"💡 **Workflow**:\n" +
                        f"   1. Call 'create_index_metadata' with index name and description\n" +
                        f"   2. Then call 'create_index' again to create the actual index\n" +
                        f"   3. This ensures proper documentation and governance\n\n" +
                        f"🎯 **Why This Matters**:\n" +
                        f"   • Prevents orphaned indices without documentation\n" +
                        f"   • Ensures team understands index purpose\n" +
                        f"   • Facilitates better index management and cleanup\n" +
                        f"   • Provides context for future maintenance")

        except Exception as metadata_error:
            # If metadata index doesn't exist, that's also a problem
            if "index_not_found" in str(metadata_error).lower():
                return (f"❌ Index creation blocked - Metadata system not initialized!\n\n" +
                        f"🚨 **SETUP REQUIRED**: Index metadata system needs initialization\n" +
                        f"   📋 **Step 1**: Create metadata index first using 'create_index' with name 'index_metadata'\n" +
                        f"   📝 **Step 2**: Use this mapping for metadata index:\n" +
                        f"```json\n" +
                        f"{{\n" +
                        f"  \"properties\": {{\n" +
                        f"    \"index_name\": {{\"type\": \"keyword\"}},\n" +
                        f"    \"description\": {{\"type\": \"text\"}},\n" +
                        f"    \"purpose\": {{\"type\": \"text\"}},\n" +
                        f"    \"data_types\": {{\"type\": \"keyword\"}},\n" +
                        f"    \"created_by\": {{\"type\": \"keyword\"}},\n" +
                        f"    \"created_date\": {{\"type\": \"date\"}},\n" +
                        f"    \"usage_pattern\": {{\"type\": \"keyword\"}},\n" +
                        f"    \"retention_policy\": {{\"type\": \"text\"}},\n" +
                        f"    \"related_indices\": {{\"type\": \"keyword\"}},\n" +
                        f"    \"tags\": {{\"type\": \"keyword\"}}\n" +
                        f"  }}\n" +
                        f"}}\n" +
                        f"```\n" +
                        f"   🔧 **Step 3**: Then use 'create_index_metadata' to document your index\n" +
                        f"   ✅ **Step 4**: Finally create your actual index\n\n" +
                        f"💡 **This is a one-time setup** - once metadata index exists, normal workflow applies")

        # If we get here, metadata exists - proceed with index creation
        body = {"mappings": mapping}
        if settings:
            body["settings"] = settings

        result = es.indices.create(index=index, body=body)

        return f"✅ Index '{index}' created successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to create index:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "already exists" in error_str or "resource_already_exists" in error_str:
            error_message += f"📁 **Index Exists**: Index '{index}' already exists\n"
            error_message += f"📍 Cannot create an index that already exists\n"
            error_message += f"💡 Try: Use 'delete_index' first, or choose a different name\n\n"
        elif "mapping" in error_str or "invalid" in error_str:
            error_message += f"📝 **Mapping Error**: Invalid index mapping or settings\n"
            error_message += f"📍 The provided mapping/settings are not valid\n"
            error_message += f"💡 Try: Check mapping syntax and field types\n\n"
        elif "permission" in error_str or "forbidden" in error_str:
            error_message += "🔒 **Permission Error**: Not allowed to create index\n"
            error_message += f"📍 Insufficient permissions for index creation\n"
            error_message += f"💡 Try: Check Elasticsearch security settings\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


@app.tool(
    description="Delete an Elasticsearch index and all its documents permanently",
    tags={"elasticsearch", "delete", "index", "destructive"}
)
async def delete_index(
        index: Annotated[str, Field(description="Name of the Elasticsearch index to delete")]
) -> str:
    """Delete an Elasticsearch index permanently."""
    try:
        es = get_es_client()

        # Check if metadata document exists for this index
        metadata_index = "index_metadata"
        try:
            # Search for existing metadata document
            search_body = {
                "query": {
                    "term": {
                        "index_name.keyword": index
                    }
                },
                "size": 1
            }

            metadata_result = es.search(index=metadata_index, body=search_body)

            if metadata_result['hits']['total']['value'] > 0:
                metadata_doc = metadata_result['hits']['hits'][0]
                metadata_id = metadata_doc['_id']
                metadata_source = metadata_doc['_source']

                return (f"❌ Index deletion blocked - Metadata cleanup required!\n\n" +
                        f"🚨 **MANDATORY: Remove Index Metadata First**:\n" +
                        f"   📋 **Found Metadata Document**: {metadata_id}\n" +
                        f"   📝 **Index Description**: {metadata_source.get('description', 'No description')}\n" +
                        f"   🔧 **Required Action**: Delete metadata document before removing index\n\n" +
                        f"💡 **Cleanup Workflow**:\n" +
                        f"   1. Call 'delete_index_metadata' with index name '{index}'\n" +
                        f"   2. Then call 'delete_index' again to remove the actual index\n" +
                        f"   3. This ensures proper cleanup and audit trail\n\n" +
                        f"📊 **Metadata Details**:\n" +
                        f"   • Purpose: {metadata_source.get('purpose', 'Not specified')}\n" +
                        f"   • Data Types: {', '.join(metadata_source.get('data_types', []))}\n" +
                        f"   • Created: {metadata_source.get('created_date', 'Unknown')}\n" +
                        f"   • Usage: {metadata_source.get('usage_pattern', 'Not specified')}\n\n" +
                        f"🎯 **Why This Matters**:\n" +
                        f"   • Maintains clean metadata registry\n" +
                        f"   • Prevents orphaned documentation\n" +
                        f"   • Ensures proper audit trail for deletions\n" +
                        f"   • Confirms intentional removal with full context")

        except Exception as metadata_error:
            # If metadata index doesn't exist, warn but allow deletion
            if "index_not_found" in str(metadata_error).lower():
                # Proceed with deletion but warn about missing metadata system
                result = es.indices.delete(index=index)

                return (f"⚠️ Index '{index}' deleted but metadata system is missing:\n\n" +
                        f"{json.dumps(result, indent=2, ensure_ascii=False)}\n\n" +
                        f"🚨 **Warning**: No metadata tracking system found\n" +
                        f"   📋 Consider setting up 'index_metadata' index for better governance\n" +
                        f"   💡 Use 'create_index_metadata' tool for future index documentation")

        # If we get here, no metadata found - proceed with deletion
        result = es.indices.delete(index=index)

        return f"✅ Index '{index}' deleted successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete index:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif (
                "not_found" in error_str or "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 Cannot delete an index that doesn't exist\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "permission" in error_str or "forbidden" in error_str:
            error_message += "🔒 **Permission Error**: Not allowed to delete index\n"
            error_message += f"📍 Insufficient permissions for index deletion\n"
            error_message += f"💡 Try: Check Elasticsearch security settings\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


@app.tool(
    description="List all available Elasticsearch indices with document count and size statistics",
    tags={"elasticsearch", "list", "indices", "stats"}
)
async def list_indices() -> str:
    """List all available Elasticsearch indices with basic statistics."""
    try:
        es = get_es_client()

        indices = es.indices.get_alias(index="*")

        # Get stats for each index
        indices_info = []
        for index_name in indices.keys():
            if not index_name.startswith('.'):  # Skip system indices
                try:
                    stats = es.indices.stats(index=index_name)
                    doc_count = stats['indices'][index_name]['total']['docs']['count']
                    size = stats['indices'][index_name]['total']['store']['size_in_bytes']

                    # Initialize basic index info
                    index_info = {
                        "name": index_name,
                        "docs": doc_count,
                        "size_bytes": size,
                        "description": "No description available",
                        "purpose": "Not documented",
                        "data_types": [],
                        "usage_pattern": "Unknown",
                        "created_date": "Unknown"
                    }

                    # Try to get metadata for this index
                    try:
                        metadata_search = {
                            "query": {
                                "term": {
                                    "index_name": index_name
                                }
                            },
                            "size": 1
                        }

                        metadata_result = es.search(index="index_metadata", body=metadata_search)

                        if metadata_result['hits']['total']['value'] > 0:
                            metadata = metadata_result['hits']['hits'][0]['_source']
                            # Merge metadata into index info
                            index_info.update({
                                "description": metadata.get('description', 'No description available'),
                                "purpose": metadata.get('purpose', 'Not documented'),
                                "data_types": metadata.get('data_types', []),
                                "usage_pattern": metadata.get('usage_pattern', 'Unknown'),
                                "created_date": metadata.get('created_date', 'Unknown'),
                                "retention_policy": metadata.get('retention_policy', 'Not specified'),
                                "related_indices": metadata.get('related_indices', []),
                                "tags": metadata.get('tags', []),
                                "created_by": metadata.get('created_by', 'Unknown'),
                                "has_metadata": True
                            })
                        else:
                            index_info["has_metadata"] = False

                    except Exception:
                        # If metadata index doesn't exist or search fails, keep basic info
                        index_info["has_metadata"] = False

                    indices_info.append(index_info)

                except:
                    indices_info.append({
                        "name": index_name,
                        "docs": "unknown",
                        "size_bytes": "unknown",
                        "description": "Statistics unavailable",
                        "has_metadata": False
                    })

        # Sort indices: metadata-documented first, then by name
        indices_info.sort(key=lambda x: (not x.get('has_metadata', False), x['name']))

        # Format the output with metadata information
        result = "✅ Available indices with metadata:\n\n"

        # Count documented vs undocumented
        documented = sum(1 for idx in indices_info if idx.get('has_metadata', False))
        undocumented = len(indices_info) - documented

        result += f"📊 **Index Overview**:\n"
        result += f"   📋 Total indices: {len(indices_info)}\n"
        result += f"   ✅ Documented: {documented}\n"
        result += f"   ❌ Undocumented: {undocumented}\n\n"

        if undocumented > 0:
            result += f"🚨 **Governance Alert**: {undocumented} indices lack metadata documentation\n"
            result += f"   💡 Use 'create_index_metadata' tool to document missing indices\n"
            result += f"   🎯 Proper documentation improves index management and team collaboration\n\n"

        # Group indices by documentation status
        documented_indices = [idx for idx in indices_info if idx.get('has_metadata', False)]
        undocumented_indices = [idx for idx in indices_info if not idx.get('has_metadata', False)]

        if documented_indices:
            result += f"📋 **Documented Indices** ({len(documented_indices)}):\n\n"
            for idx in documented_indices:
                size_mb = idx['size_bytes'] / 1048576 if isinstance(idx['size_bytes'], (int, float)) else 0
                result += f"🟢 **{idx['name']}**\n"
                result += f"   📝 Description: {idx['description']}\n"
                result += f"   🎯 Purpose: {idx['purpose']}\n"
                result += f"   📊 Documents: {idx['docs']}, Size: {size_mb:.1f} MB\n"
                result += f"   📂 Data Types: {', '.join(idx.get('data_types', [])) or 'Not specified'}\n"
                result += f"   🔄 Usage: {idx.get('usage_pattern', 'Unknown')}\n"
                result += f"   📅 Created: {idx.get('created_date', 'Unknown')}\n"
                if idx.get('tags'):
                    result += f"   🏷️ Tags: {', '.join(idx['tags'])}\n"
                if idx.get('related_indices'):
                    result += f"   🔗 Related: {', '.join(idx['related_indices'])}\n"
                result += "\n"

        if undocumented_indices:
            result += f"❌ **Undocumented Indices** ({len(undocumented_indices)}) - Need Metadata:\n\n"
            for idx in undocumented_indices:
                size_mb = idx['size_bytes'] / 1048576 if isinstance(idx['size_bytes'], (int, float)) else 0
                result += f"🔴 **{idx['name']}**\n"
                result += f"   📊 Documents: {idx['docs']}, Size: {size_mb:.1f} MB\n"
                result += f"   ⚠️ Status: No metadata documentation found\n"
                result += f"   🔧 Action: Use 'create_index_metadata' to document this index\n\n"

        # Add metadata improvement suggestions
        if undocumented > 0:
            result += f"💡 **Metadata Improvement Suggestions**:\n"
            result += f"   📋 Document each index's purpose and data types\n"
            result += f"   🎯 Define usage patterns and access frequencies\n"
            result += f"   📅 Record creation dates and retention policies\n"
            result += f"   🔗 Link related indices for better organization\n"
            result += f"   🏷️ Add relevant tags for categorization\n"
            result += f"   👤 Track ownership and responsibility\n\n"

        return result

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to list indices:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Elasticsearch server is not responding\n"
            error_message += f"📍 Server may be overloaded or slow to respond\n"
            error_message += f"💡 Try: Wait and retry, or check server status\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# CLI Entry Point
def main():
    """Main entry point for elasticsearch index server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-index 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Index Server - FastMCP Implementation")
            print("Handles index management operations.")
            print("\nTools provided:")
            print("  - [TO BE COPIED FROM BAK FILE]")
            return

    print("🚀 Starting Elasticsearch Index Server...")
    print("🔍 Tools: [TO BE COPIED FROM BAK FILE]")
    app.run()


if __name__ == "__main__":
    main()
