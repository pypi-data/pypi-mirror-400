"""
Elasticsearch Index Metadata FastMCP Server
Index metadata management tools extracted from main elasticsearch server.
Handles documentation, governance, and lifecycle management of index metadata.
"""

from typing import List, Optional, Annotated
from datetime import datetime
from fastmcp import FastMCP
from pydantic import Field
from ..elasticsearch_client import get_es_client

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Index-Metadata",
    version="1.0.0",
    instructions="Elasticsearch index metadata management tools"
)


@app.tool(
    description="Create metadata documentation for an Elasticsearch index to ensure proper governance and documentation",
    tags={"elasticsearch", "metadata", "documentation", "governance"}
)
async def create_index_metadata(
        index_name: Annotated[str, Field(description="Name of the index to document")],
        description: Annotated[str, Field(description="Detailed description of the index purpose and content")],
        purpose: Annotated[str, Field(description="Primary purpose and use case for this index")],
        data_types: Annotated[List[str], Field(
            description="Types of data stored in this index (e.g., 'documents', 'logs', 'metrics')")] = [],
        usage_pattern: Annotated[
            str, Field(description="How the index is accessed (e.g., 'read-heavy', 'write-heavy', 'mixed')")] = "mixed",
        retention_policy: Annotated[
            str, Field(description="Data retention policy and lifecycle management")] = "No specific policy",
        related_indices: Annotated[List[str], Field(description="Names of related or dependent indices")] = [],
        tags: Annotated[List[str], Field(description="Tags for categorizing and organizing indices")] = [],
        created_by: Annotated[str, Field(description="Team or person responsible for this index")] = "Unknown"
) -> str:
    """Create comprehensive metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()

        # Check if metadata index exists
        metadata_index = "index_metadata"
        try:
            es.indices.get(index=metadata_index)
        except Exception:
            # Create metadata index if it doesn't exist
            metadata_mapping = {
                "properties": {
                    "index_name": {"type": "keyword"},
                    "description": {"type": "text"},
                    "purpose": {"type": "text"},
                    "data_types": {"type": "keyword"},
                    "created_by": {"type": "keyword"},
                    "created_date": {"type": "date"},
                    "usage_pattern": {"type": "keyword"},
                    "retention_policy": {"type": "text"},
                    "related_indices": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "last_updated": {"type": "date"},
                    "updated_by": {"type": "keyword"}
                }
            }

            try:
                es.indices.create(index=metadata_index, body={"mappings": metadata_mapping})
            except Exception as create_error:
                if "already exists" not in str(create_error).lower():
                    return f"❌ Failed to create metadata index: {str(create_error)}"

        # Check if metadata already exists for this index
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }

        existing_result = es.search(index=metadata_index, body=search_body)

        if existing_result['hits']['total']['value'] > 0:
            existing_doc = existing_result['hits']['hits'][0]
            existing_id = existing_doc['_id']
            existing_data = existing_doc['_source']

            return (f"⚠️ Index metadata already exists for '{index_name}'!\n\n" +
                    f"📋 **Existing Metadata** (ID: {existing_id}):\n" +
                    f"   📝 Description: {existing_data.get('description', 'No description')}\n" +
                    f"   🎯 Purpose: {existing_data.get('purpose', 'No purpose')}\n" +
                    f"   📂 Data Types: {', '.join(existing_data.get('data_types', []))}\n" +
                    f"   👤 Created By: {existing_data.get('created_by', 'Unknown')}\n" +
                    f"   📅 Created: {existing_data.get('created_date', 'Unknown')}\n\n" +
                    f"💡 **Options**:\n" +
                    f"   🔄 **Update**: Use 'update_index_metadata' to modify existing documentation\n" +
                    f"   🗑️ **Replace**: Use 'delete_index_metadata' then 'create_index_metadata'\n" +
                    f"   ✅ **Keep**: Current metadata is sufficient, proceed with 'create_index'\n\n" +
                    f"🚨 **Note**: You can now create the index '{index_name}' since metadata exists")

        # Create new metadata document
        current_time = datetime.now().isoformat()

        metadata_doc = {
            "index_name": index_name,
            "description": description,
            "purpose": purpose,
            "data_types": data_types,
            "created_by": created_by,
            "created_date": current_time,
            "usage_pattern": usage_pattern,
            "retention_policy": retention_policy,
            "related_indices": related_indices,
            "tags": tags,
            "last_updated": current_time,
            "updated_by": created_by
        }

        # Generate a consistent document ID
        metadata_id = f"metadata_{index_name}"

        result = es.index(index=metadata_index, id=metadata_id, body=metadata_doc)

        return (f"✅ Index metadata created successfully!\n\n" +
                f"📋 **Metadata Details**:\n" +
                f"   🎯 Index: {index_name}\n" +
                f"   📝 Description: {description}\n" +
                f"   🎯 Purpose: {purpose}\n" +
                f"   📂 Data Types: {', '.join(data_types) if data_types else 'None specified'}\n" +
                f"   🔄 Usage Pattern: {usage_pattern}\n" +
                f"   📅 Retention: {retention_policy}\n" +
                f"   🔗 Related Indices: {', '.join(related_indices) if related_indices else 'None'}\n" +
                f"   🏷️ Tags: {', '.join(tags) if tags else 'None'}\n" +
                f"   👤 Created By: {created_by}\n" +
                f"   📅 Created: {current_time}\n\n" +
                f"✅ **Next Steps**:\n" +
                f"   🔧 You can now use 'create_index' to create the actual index '{index_name}'\n" +
                f"   📊 Use 'list_indices' to see this metadata in the index listing\n" +
                f"   🔄 Use 'update_index_metadata' if you need to modify this documentation\n\n" +
                f"🎯 **Benefits Achieved**:\n" +
                f"   • Index purpose is clearly documented\n" +
                f"   • Team collaboration is improved through shared understanding\n" +
                f"   • Future maintenance is simplified with proper context\n" +
                f"   • Index governance and compliance are maintained")

    except Exception as e:
        error_message = "❌ Failed to create index metadata:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


@app.tool(
    description="Update existing metadata documentation for an Elasticsearch index",
    tags={"elasticsearch", "metadata", "update", "documentation"}
)
async def update_index_metadata(
        index_name: Annotated[str, Field(description="Name of the index to update metadata for")],
        description: Annotated[
            Optional[str], Field(description="Updated description of the index purpose and content")] = None,
        purpose: Annotated[Optional[str], Field(description="Updated primary purpose and use case")] = None,
        data_types: Annotated[
            Optional[List[str]], Field(description="Updated types of data stored in this index")] = None,
        usage_pattern: Annotated[Optional[str], Field(description="Updated access pattern")] = None,
        retention_policy: Annotated[Optional[str], Field(description="Updated data retention policy")] = None,
        related_indices: Annotated[
            Optional[List[str]], Field(description="Updated related or dependent indices")] = None,
        tags: Annotated[Optional[List[str]], Field(description="Updated tags for categorization")] = None,
        updated_by: Annotated[str, Field(description="Person or team making this update")] = "Unknown"
) -> str:
    """Update existing metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()
        metadata_index = "index_metadata"

        # Search for existing metadata
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }

        existing_result = es.search(index=metadata_index, body=search_body)

        if existing_result['hits']['total']['value'] == 0:
            return (f"❌ No metadata found for index '{index_name}'!\n\n" +
                    f"🚨 **Missing Metadata**: Cannot update non-existent documentation\n" +
                    f"   💡 **Solution**: Use 'create_index_metadata' to create documentation first\n" +
                    f"   📋 **Required**: Provide description, purpose, and data types\n" +
                    f"   ✅ **Then**: Use this update tool for future modifications\n\n" +
                    f"🔍 **Alternative**: Use 'list_indices' to see all documented indices")

        # Get existing document
        existing_doc = existing_result['hits']['hits'][0]
        existing_id = existing_doc['_id']
        existing_data = existing_doc['_source']

        # Prepare update data - only update provided fields
        update_data = {
            "last_updated": datetime.now().isoformat(),
            "updated_by": updated_by
        }

        if description is not None:
            update_data["description"] = description
        if purpose is not None:
            update_data["purpose"] = purpose
        if data_types is not None:
            update_data["data_types"] = data_types
        if usage_pattern is not None:
            update_data["usage_pattern"] = usage_pattern
        if retention_policy is not None:
            update_data["retention_policy"] = retention_policy
        if related_indices is not None:
            update_data["related_indices"] = related_indices
        if tags is not None:
            update_data["tags"] = tags

        # Update the document
        result = es.update(index=metadata_index, id=existing_id, body={"doc": update_data})

        # Get updated document to show changes
        updated_result = es.get(index=metadata_index, id=existing_id)
        updated_data = updated_result['_source']

        # Build change summary
        changes_made = []
        if description is not None:
            changes_made.append(f"   📝 Description: {existing_data.get('description', 'None')} → {description}")
        if purpose is not None:
            changes_made.append(f"   🎯 Purpose: {existing_data.get('purpose', 'None')} → {purpose}")
        if data_types is not None:
            old_types = ', '.join(existing_data.get('data_types', []))
            new_types = ', '.join(data_types)
            changes_made.append(f"   📂 Data Types: {old_types or 'None'} → {new_types}")
        if usage_pattern is not None:
            changes_made.append(f"   🔄 Usage Pattern: {existing_data.get('usage_pattern', 'None')} → {usage_pattern}")
        if retention_policy is not None:
            changes_made.append(f"   📅 Retention: {existing_data.get('retention_policy', 'None')} → {retention_policy}")
        if related_indices is not None:
            old_related = ', '.join(existing_data.get('related_indices', []))
            new_related = ', '.join(related_indices)
            changes_made.append(f"   🔗 Related: {old_related or 'None'} → {new_related}")
        if tags is not None:
            old_tags = ', '.join(existing_data.get('tags', []))
            new_tags = ', '.join(tags)
            changes_made.append(f"   🏷️ Tags: {old_tags or 'None'} → {new_tags}")

        return (f"✅ Index metadata updated successfully!\n\n" +
                f"📋 **Updated Metadata for '{index_name}'**:\n" +
                (f"🔄 **Changes Made**:\n" + '\n'.join(changes_made) + "\n\n" if changes_made else "") +
                f"📊 **Current Metadata**:\n" +
                f"   📝 Description: {updated_data.get('description', 'No description')}\n" +
                f"   🎯 Purpose: {updated_data.get('purpose', 'No purpose')}\n" +
                f"   📂 Data Types: {', '.join(updated_data.get('data_types', [])) if updated_data.get('data_types') else 'None'}\n" +
                f"   🔄 Usage Pattern: {updated_data.get('usage_pattern', 'Unknown')}\n" +
                f"   📅 Retention: {updated_data.get('retention_policy', 'Not specified')}\n" +
                f"   🔗 Related Indices: {', '.join(updated_data.get('related_indices', [])) if updated_data.get('related_indices') else 'None'}\n" +
                f"   🏷️ Tags: {', '.join(updated_data.get('tags', [])) if updated_data.get('tags') else 'None'}\n" +
                f"   👤 Last Updated By: {updated_by}\n" +
                f"   📅 Last Updated: {update_data['last_updated']}\n\n" +
                f"✅ **Benefits**:\n" +
                f"   • Index documentation stays current and accurate\n" +
                f"   • Team has updated context for index usage\n" +
                f"   • Change history is tracked with timestamps\n" +
                f"   • Governance and compliance are maintained")

    except Exception as e:
        error_message = "❌ Failed to update index metadata:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) and "index" in error_str:
            error_message += f"📁 **Index Error**: Metadata index 'index_metadata' does not exist\n"
            error_message += f"📍 The metadata system has not been initialized\n"
            error_message += f"💡 Try: Use 'create_index_metadata' to set up metadata system\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


@app.tool(
    description="Delete metadata documentation for an Elasticsearch index",
    tags={"elasticsearch", "metadata", "delete", "cleanup"}
)
async def delete_index_metadata(
        index_name: Annotated[str, Field(description="Name of the index to remove metadata for")]
) -> str:
    """Delete metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()
        metadata_index = "index_metadata"

        # Search for existing metadata
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }

        existing_result = es.search(index=metadata_index, body=search_body)

        if existing_result['hits']['total']['value'] == 0:
            return (f"⚠️ No metadata found for index '{index_name}'!\n\n" +
                    f"📋 **Status**: Index metadata does not exist\n" +
                    f"   ✅ **Good**: No cleanup required for metadata\n" +
                    f"   🔧 **Safe**: You can proceed with 'delete_index' if needed\n" +
                    f"   🔍 **Check**: Use 'list_indices' to see all documented indices\n\n" +
                    f"💡 **This is Normal If**:\n" +
                    f"   • Index was created before metadata system was implemented\n" +
                    f"   • Index was created without using 'create_index_metadata' first\n" +
                    f"   • Metadata was already deleted in a previous cleanup")

        # Get existing document details before deletion
        existing_doc = existing_result['hits']['hits'][0]
        existing_id = existing_doc['_id']
        existing_data = existing_doc['_source']

        # Delete the metadata document
        result = es.delete(index=metadata_index, id=existing_id)

        return (f"✅ Index metadata deleted successfully!\n\n" +
                f"🗑️ **Deleted Metadata for '{index_name}'**:\n" +
                f"   📋 Document ID: {existing_id}\n" +
                f"   📝 Description: {existing_data.get('description', 'No description')}\n" +
                f"   🎯 Purpose: {existing_data.get('purpose', 'No purpose')}\n" +
                f"   📂 Data Types: {', '.join(existing_data.get('data_types', [])) if existing_data.get('data_types') else 'None'}\n" +
                f"   👤 Created By: {existing_data.get('created_by', 'Unknown')}\n" +
                f"   📅 Created: {existing_data.get('created_date', 'Unknown')}\n\n" +
                f"✅ **Cleanup Complete**:\n" +
                f"   🗑️ Metadata documentation removed from registry\n" +
                f"   🔧 You can now safely use 'delete_index' to remove the actual index\n" +
                f"   📊 Use 'list_indices' to verify metadata removal\n\n" +
                f"🎯 **Next Steps**:\n" +
                f"   1. Proceed with 'delete_index {index_name}' to remove the actual index\n" +
                f"   2. Or use 'create_index_metadata' if you want to re-document this index\n" +
                f"   3. Clean up any related indices mentioned in metadata\n\n" +
                f"⚠️ **Important**: This only deleted the documentation, not the actual index")

    except Exception as e:
        error_message = "❌ Failed to delete index metadata:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) and "index" in error_str:
            error_message += f"📁 **Index Error**: Metadata index 'index_metadata' does not exist\n"
            error_message += f"📍 The metadata system has not been initialized\n"
            error_message += f"💡 This means no metadata exists to delete - you can proceed safely\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# CLI Entry Point
def main():
    """Main entry point for elasticsearch index metadata server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-index-metadata 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Index Metadata Server - FastMCP Implementation")
            print("Handles index metadata management tools.")
            print("\nTools provided:")
            print("  - [TO BE COPIED FROM BAK FILE]")
            return

    print("🚀 Starting Elasticsearch Index Metadata Server...")
    print("🔍 Tools: [TO BE COPIED FROM BAK FILE]")
    app.run()


if __name__ == "__main__":
    main()
