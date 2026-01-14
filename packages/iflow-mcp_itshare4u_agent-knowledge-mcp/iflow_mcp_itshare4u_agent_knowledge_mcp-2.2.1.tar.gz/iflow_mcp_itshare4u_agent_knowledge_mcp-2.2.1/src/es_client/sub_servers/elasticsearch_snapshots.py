"""
Elasticsearch Snapshots FastMCP Server
Snapshot operations extracted from main elasticsearch server.
Handles backup and restore operations.
"""
import json
from datetime import datetime
from typing import Annotated
from typing import Optional

from fastmcp import FastMCP
from pydantic import Field

from src.es_client.elasticsearch_client import get_es_client

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Snapshots",
    version="1.0.0",
    instructions="Elasticsearch snapshot operations tools"
)


@app.tool(
    description="Create a snapshot (backup) of Elasticsearch indices with comprehensive options and repository management",
    tags={"elasticsearch", "snapshot", "backup", "repository"}
)
async def create_snapshot(
        snapshot_name: Annotated[str, Field(description="Name for the snapshot (must be unique)")],
        repository: Annotated[str, Field(description="Repository name to store the snapshot")] = "backup_repository",
        indices: Annotated[Optional[str], Field(
            description="Comma-separated list of indices to backup (default: all indices)")] = None,
        ignore_unavailable: Annotated[bool, Field(description="Whether to ignore unavailable indices")] = True,
        include_global_state: Annotated[bool, Field(description="Whether to include cluster global state")] = True,
        wait_for_completion: Annotated[bool, Field(description="Whether to wait for snapshot completion")] = True,
        description: Annotated[Optional[str], Field(description="Optional description for the snapshot")] = None
) -> str:
    """Create a snapshot (backup) of Elasticsearch indices."""
    try:
        es = get_es_client()

        # Check if repository exists, create if not
        try:
            repo_info = es.snapshot.get_repository(repository=repository)
        except:
            # Repository doesn't exist, create default file system repository
            repo_body = {
                "type": "fs",
                "settings": {
                    "location": f"/usr/share/elasticsearch/snapshots/{repository}",
                    "compress": True
                }
            }
            try:
                es.snapshot.create_repository(repository=repository, body=repo_body)
                repo_created = True
            except Exception as repo_error:
                return (f"❌ Failed to create snapshot repository:\n\n" +
                        f"🔧 **Repository Error**: Cannot create repository '{repository}'\n" +
                        f"📍 **Issue**: {str(repo_error)}\n\n" +
                        f"💡 **Common Solutions**:\n" +
                        f"   1. Ensure Elasticsearch has write permissions to snapshot directory\n" +
                        f"   2. Add 'path.repo: [\"/usr/share/elasticsearch/snapshots\"]' to elasticsearch.yml\n" +
                        f"   3. Restart Elasticsearch after configuration change\n" +
                        f"   4. Or use existing repository name\n\n" +
                        f"🔍 **Technical Details**: {str(repo_error)}")
        else:
            repo_created = False

        # Parse indices parameter
        if indices:
            indices_list = [idx.strip() for idx in indices.split(',')]
            indices_param = ','.join(indices_list)
        else:
            indices_param = "*"  # All indices
            indices_list = ["*"]

        # Create snapshot metadata
        snapshot_body = {
            "indices": indices_param,
            "ignore_unavailable": ignore_unavailable,
            "include_global_state": include_global_state
        }

        if description:
            snapshot_body["metadata"] = {
                "description": description,
                "created_by": "AgentKnowledgeMCP",
                "created_at": datetime.now().isoformat()
            }

        # Create the snapshot
        snapshot_result = es.snapshot.create(
            repository=repository,
            snapshot=snapshot_name,
            body=snapshot_body,
            wait_for_completion=wait_for_completion
        )

        # Format response based on completion
        if wait_for_completion:
            snapshot_info = snapshot_result.get('snapshot', {})
            state = snapshot_info.get('state', 'UNKNOWN')

            if state == 'SUCCESS':
                status_emoji = "✅"
                status_msg = "Successfully completed"
            elif state == 'PARTIAL':
                status_emoji = "⚠️"
                status_msg = "Partially completed with some issues"
            elif state == 'FAILED':
                status_emoji = "❌"
                status_msg = "Failed to complete"
            else:
                status_emoji = "🔄"
                status_msg = f"Status: {state}"

            result_message = (f"{status_emoji} Snapshot '{snapshot_name}' {status_msg}!\n\n" +
                              f"📸 **Snapshot Details**:\n" +
                              f"   📂 Repository: {repository}\n" +
                              f"   📋 Name: {snapshot_name}\n" +
                              f"   📊 State: {state}\n" +
                              f"   📦 Indices: {', '.join(indices_list)}\n" +
                              f"   🌐 Global State: {'Included' if include_global_state else 'Excluded'}\n")

            if snapshot_info.get('shards'):
                shards = snapshot_info['shards']
                result_message += (f"   🔢 Shards: {shards.get('total', 0)} total, " +
                                   f"{shards.get('successful', 0)} successful, " +
                                   f"{shards.get('failed', 0)} failed\n")

            if snapshot_info.get('start_time_in_millis') and snapshot_info.get('end_time_in_millis'):
                duration = (snapshot_info['end_time_in_millis'] - snapshot_info['start_time_in_millis']) / 1000
                result_message += f"   ⏱️ Duration: {duration:.2f} seconds\n"

            if description:
                result_message += f"   📝 Description: {description}\n"

        else:
            result_message = (f"🔄 Snapshot '{snapshot_name}' started!\n\n" +
                              f"📸 **Snapshot Details**:\n" +
                              f"   📂 Repository: {repository}\n" +
                              f"   📋 Name: {snapshot_name}\n" +
                              f"   📊 Status: Running in background\n" +
                              f"   📦 Indices: {', '.join(indices_list)}\n" +
                              f"   🌐 Global State: {'Included' if include_global_state else 'Excluded'}\n")

        if repo_created:
            result_message += f"\n🆕 **Repository Created**: Created new repository '{repository}'\n"

        result_message += (f"\n✅ **Success Actions**:\n" +
                           f"   📸 Snapshot backup is {'completed' if wait_for_completion else 'in progress'}\n" +
                           f"   🔍 Use 'list_snapshots' to view all snapshots\n" +
                           f"   🔄 Use 'restore_snapshot' to restore from this backup\n" +
                           f"   📊 Check snapshot status with repository '{repository}'\n\n" +
                           f"💾 **Backup Strategy**:\n" +
                           f"   🕒 Regular snapshots help protect against data loss\n" +
                           f"   🏷️ Use descriptive snapshot names with dates\n" +
                           f"   📂 Monitor repository storage space\n" +
                           f"   🧹 Clean up old snapshots periodically")

        return result_message

    except Exception as e:
        error_message = "❌ Failed to create snapshot:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "repository" in error_str and ("not found" in error_str or "missing" in error_str):
            error_message += f"📂 **Repository Error**: Repository '{repository}' not found or misconfigured\n"
            error_message += f"📍 Check repository configuration and permissions\n"
            error_message += f"💡 Try: Use different repository name or check path.repo settings\n\n"
        elif "invalid_snapshot_name" in error_str:
            error_message += f"🏷️ **Naming Error**: Invalid snapshot name '{snapshot_name}'\n"
            error_message += f"📍 Snapshot names must be lowercase and cannot contain certain characters\n"
            error_message += f"💡 Try: Use alphanumeric characters and hyphens only\n\n"
        elif "already_exists" in error_str:
            error_message += f"📋 **Conflict Error**: Snapshot '{snapshot_name}' already exists\n"
            error_message += f"📍 Each snapshot must have a unique name within the repository\n"
            error_message += f"💡 Try: Use different snapshot name or delete existing snapshot\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 15: RESTORE_SNAPSHOT
# ================================

@app.tool(
    description="Restore indices from an Elasticsearch snapshot with comprehensive options and conflict resolution",
    tags={"elasticsearch", "snapshot", "restore", "rollback"}
)
async def restore_snapshot(
        snapshot_name: Annotated[str, Field(description="Name of the snapshot to restore from")],
        repository: Annotated[str, Field(description="Repository containing the snapshot")] = "backup_repository",
        indices: Annotated[Optional[str], Field(
            description="Comma-separated list of indices to restore (default: all from snapshot)")] = None,
        ignore_unavailable: Annotated[bool, Field(description="Whether to ignore unavailable indices")] = True,
        include_global_state: Annotated[bool, Field(description="Whether to restore cluster global state")] = False,
        wait_for_completion: Annotated[bool, Field(description="Whether to wait for restore completion")] = True,
        rename_pattern: Annotated[
            Optional[str], Field(description="Pattern to rename restored indices (e.g., 'restored_%s')")] = None,
        index_settings: Annotated[Optional[str], Field(description="JSON string of index settings to override")] = None
) -> str:
    """Restore indices from an Elasticsearch snapshot."""
    try:
        es = get_es_client()

        # Verify repository exists
        try:
            repo_info = es.snapshot.get_repository(repository=repository)
        except:
            return (f"❌ Repository '{repository}' not found!\n\n" +
                    f"📂 **Repository Error**: Cannot access snapshot repository\n" +
                    f"📍 **Available Actions**:\n" +
                    f"   1. Check repository name spelling\n" +
                    f"   2. Use 'create_snapshot' to create repository first\n" +
                    f"   3. Verify Elasticsearch path.repo configuration\n\n" +
                    f"💡 **Tip**: Repositories must be configured before accessing snapshots")

        # Verify snapshot exists
        try:
            snapshot_info = es.snapshot.get(repository=repository, snapshot=snapshot_name)
        except:
            return (f"❌ Snapshot '{snapshot_name}' not found in repository '{repository}'!\n\n" +
                    f"📸 **Snapshot Error**: Cannot find the specified snapshot\n" +
                    f"📍 **Possible Issues**:\n" +
                    f"   1. Snapshot name is incorrect\n" +
                    f"   2. Snapshot was deleted or corrupted\n" +
                    f"   3. Repository path has changed\n\n" +
                    f"🔍 **Next Steps**:\n" +
                    f"   • Use 'list_snapshots' to see available snapshots\n" +
                    f"   • Check repository configuration and permissions\n" +
                    f"   • Verify backup storage accessibility")

        # Parse indices parameter
        if indices:
            indices_list = [idx.strip() for idx in indices.split(',')]
            indices_param = ','.join(indices_list)
        else:
            indices_param = None  # Restore all indices from snapshot
            indices_list = ["all"]

        # Build restore body
        restore_body = {
            "ignore_unavailable": ignore_unavailable,
            "include_global_state": include_global_state
        }

        if indices_param:
            restore_body["indices"] = indices_param

        if rename_pattern:
            restore_body["rename_pattern"] = rename_pattern
            restore_body["rename_replacement"] = rename_pattern

        if index_settings:
            try:
                settings_dict = json.loads(index_settings)
                restore_body["index_settings"] = settings_dict
            except json.JSONDecodeError:
                return (f"❌ Invalid JSON in index_settings parameter!\n\n" +
                        f"📋 **JSON Error**: Cannot parse index settings\n" +
                        f"📍 **Provided**: {index_settings}\n" +
                        f"💡 **Example**: '{{\"number_of_replicas\": 0, \"refresh_interval\": \"30s\"}}'")

        # Check for potential conflicts (existing indices)
        conflicts = []
        if indices_list and indices_list != ["all"]:
            for index_name in indices_list:
                if rename_pattern:
                    # If renaming, check the new name
                    new_name = rename_pattern.replace('%s', index_name)
                    try:
                        es.indices.get(index=new_name)
                        conflicts.append(f"{index_name} -> {new_name}")
                    except:
                        pass  # Index doesn't exist, no conflict
                else:
                    # Direct restore, check original name
                    try:
                        es.indices.get(index=index_name)
                        conflicts.append(index_name)
                    except:
                        pass  # Index doesn't exist, no conflict

        # Warn about conflicts
        conflict_warning = ""
        if conflicts and not rename_pattern:
            conflict_warning = (f"\n⚠️ **Warning - Existing Indices Will Be Overwritten**:\n" +
                                f"   📋 Conflicting indices: {', '.join(conflicts)}\n" +
                                f"   🔄 These indices will be closed and replaced\n" +
                                f"   💡 Consider using rename_pattern to avoid conflicts\n\n")

        # Execute restore
        restore_result = es.snapshot.restore(
            repository=repository,
            snapshot=snapshot_name,
            body=restore_body,
            wait_for_completion=wait_for_completion
        )

        # Get snapshot details for reporting
        snapshot_details = snapshot_info['snapshots'][0] if snapshot_info.get('snapshots') else {}
        snapshot_state = snapshot_details.get('state', 'UNKNOWN')

        # Format response based on completion
        if wait_for_completion:
            restore_info = restore_result.get('snapshot', {})
            shards_info = restore_info.get('shards', {})

            result_message = (f"✅ Snapshot '{snapshot_name}' restored successfully!\n\n" +
                              f"🔄 **Restore Details**:\n" +
                              f"   📂 Repository: {repository}\n" +
                              f"   📸 Snapshot: {snapshot_name}\n" +
                              f"   📊 Snapshot State: {snapshot_state}\n" +
                              f"   📦 Restored Indices: {', '.join(indices_list)}\n" +
                              f"   🌐 Global State: {'Restored' if include_global_state else 'Skipped'}\n")

            if rename_pattern:
                result_message += f"   🏷️ Rename Pattern: {rename_pattern}\n"

            if shards_info:
                result_message += (f"   🔢 Shards: {shards_info.get('total', 0)} total, " +
                                   f"{shards_info.get('successful', 0)} successful, " +
                                   f"{shards_info.get('failed', 0)} failed\n")

        else:
            result_message = (f"🔄 Snapshot restore started!\n\n" +
                              f"🔄 **Restore Details**:\n" +
                              f"   📂 Repository: {repository}\n" +
                              f"   📸 Snapshot: {snapshot_name}\n" +
                              f"   📊 Status: Running in background\n" +
                              f"   📦 Indices: {', '.join(indices_list)}\n" +
                              f"   🌐 Global State: {'Included' if include_global_state else 'Excluded'}\n")

        if conflict_warning:
            result_message += conflict_warning

        result_message += (f"\n✅ **Restore Complete**:\n" +
                           f"   🔄 Data has been {'restored' if wait_for_completion else 'restore started'}\n" +
                           f"   🔍 Use 'list_indices' to verify restored indices\n" +
                           f"   📊 Check cluster health and index status\n" +
                           f"   🧪 Test restored data integrity\n\n" +
                           f"📋 **Post-Restore Checklist**:\n" +
                           f"   ✅ Verify all expected indices are present\n" +
                           f"   ✅ Check document counts match expectations\n" +
                           f"   ✅ Test search functionality on restored data\n" +
                           f"   ✅ Monitor cluster performance after restore")

        return result_message

    except Exception as e:
        error_message = "❌ Failed to restore snapshot:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "repository" in error_str and ("not found" in error_str or "missing" in error_str):
            error_message += f"📂 **Repository Error**: Repository '{repository}' not found\n"
            error_message += f"📍 Check repository configuration and permissions\n"
            error_message += f"💡 Try: Create repository first or check path.repo settings\n\n"
        elif "snapshot" in error_str and ("not found" in error_str or "missing" in error_str):
            error_message += f"📸 **Snapshot Error**: Snapshot '{snapshot_name}' not found\n"
            error_message += f"📍 Check snapshot name and repository\n"
            error_message += f"💡 Try: Use 'list_snapshots' to see available snapshots\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📋 **Index Error**: Some indices from snapshot no longer exist\n"
            error_message += f"📍 Original indices may have been deleted\n"
            error_message += f"💡 Try: Use ignore_unavailable=true or specify different indices\n\n"
        elif "already_exists" in error_str or "conflict" in error_str:
            error_message += f"🔄 **Conflict Error**: Cannot restore over existing indices\n"
            error_message += f"📍 Target indices already exist and are open\n"
            error_message += f"💡 Try: Use rename_pattern or close/delete conflicting indices\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 16: LIST_SNAPSHOTS
# ================================

@app.tool(
    description="List all snapshots in an Elasticsearch repository with detailed information and status",
    tags={"elasticsearch", "snapshot", "list", "repository"}
)
async def list_snapshots(
        repository: Annotated[str, Field(description="Repository name to list snapshots from")] = "backup_repository",
        verbose: Annotated[bool, Field(description="Whether to show detailed information for each snapshot")] = True
) -> str:
    """List all snapshots in an Elasticsearch repository."""
    try:
        es = get_es_client()

        # Check if repository exists
        try:
            repo_info = es.snapshot.get_repository(repository=repository)
        except:
            return (f"❌ Repository '{repository}' not found!\n\n" +
                    f"📂 **Repository Error**: Cannot access snapshot repository\n" +
                    f"📍 **Possible Issues**:\n" +
                    f"   1. Repository name is incorrect\n" +
                    f"   2. Repository was not created yet\n" +
                    f"   3. Elasticsearch path.repo configuration issue\n\n" +
                    f"💡 **Solutions**:\n" +
                    f"   • Use 'create_snapshot' to create repository\n" +
                    f"   • Check Elasticsearch configuration\n" +
                    f"   • Verify repository permissions")

        # Get repository details
        repo_details = repo_info.get(repository, {})
        repo_type = repo_details.get('type', 'unknown')
        repo_settings = repo_details.get('settings', {})

        # List all snapshots
        try:
            snapshots_result = es.snapshot.get(repository=repository, snapshot="_all")
            snapshots = snapshots_result.get('snapshots', [])
        except:
            snapshots = []

        if not snapshots:
            return (f"📋 No snapshots found in repository '{repository}'\n\n" +
                    f"📂 **Repository Information**:\n" +
                    f"   📋 Name: {repository}\n" +
                    f"   📊 Type: {repo_type}\n" +
                    f"   📍 Location: {repo_settings.get('location', 'Not specified')}\n" +
                    f"   📸 Snapshots: 0\n\n" +
                    f"💡 **Next Steps**:\n" +
                    f"   • Use 'create_snapshot' to create your first backup\n" +
                    f"   • Regular snapshots help protect against data loss\n" +
                    f"   • Consider automated snapshot scheduling")

        # Sort snapshots by start time (newest first)
        snapshots.sort(key=lambda x: x.get('start_time_in_millis', 0), reverse=True)

        result_message = f"📸 Found {len(snapshots)} snapshot(s) in repository '{repository}'\n\n"

        # Repository information
        result_message += (f"📂 **Repository Information**:\n" +
                           f"   📋 Name: {repository}\n" +
                           f"   📊 Type: {repo_type}\n" +
                           f"   📍 Location: {repo_settings.get('location', 'Not specified')}\n" +
                           f"   📸 Total Snapshots: {len(snapshots)}\n\n")

        # List snapshots
        result_message += f"📋 **Available Snapshots**:\n\n"

        for i, snapshot in enumerate(snapshots, 1):
            name = snapshot.get('snapshot', 'Unknown')
            state = snapshot.get('state', 'UNKNOWN')

            # Status emoji based on state
            if state == 'SUCCESS':
                status_emoji = "✅"
            elif state == 'PARTIAL':
                status_emoji = "⚠️"
            elif state == 'FAILED':
                status_emoji = "❌"
            elif state == 'IN_PROGRESS':
                status_emoji = "🔄"
            else:
                status_emoji = "❓"

            result_message += f"{status_emoji} **{i}. {name}**\n"
            result_message += f"   📊 State: {state}\n"

            if verbose:
                # Detailed information
                indices = snapshot.get('indices', [])
                result_message += f"   📦 Indices: {len(indices)} ({', '.join(indices[:3])}{'...' if len(indices) > 3 else ''})\n"

                # Timestamps
                if snapshot.get('start_time'):
                    result_message += f"   🕒 Started: {snapshot['start_time']}\n"
                if snapshot.get('end_time'):
                    result_message += f"   🕒 Completed: {snapshot['end_time']}\n"

                # Duration
                if snapshot.get('start_time_in_millis') and snapshot.get('end_time_in_millis'):
                    duration = (snapshot['end_time_in_millis'] - snapshot['start_time_in_millis']) / 1000
                    result_message += f"   ⏱️ Duration: {duration:.2f} seconds\n"

                # Shards info
                if snapshot.get('shards'):
                    shards = snapshot['shards']
                    total = shards.get('total', 0)
                    successful = shards.get('successful', 0)
                    failed = shards.get('failed', 0)
                    result_message += f"   🔢 Shards: {successful}/{total} successful"
                    if failed > 0:
                        result_message += f" ({failed} failed)"
                    result_message += "\n"

                # Metadata
                metadata = snapshot.get('metadata', {})
                if metadata.get('description'):
                    result_message += f"   📝 Description: {metadata['description']}\n"

                # Global state
                include_global_state = snapshot.get('include_global_state', False)
                result_message += f"   🌐 Global State: {'Included' if include_global_state else 'Excluded'}\n"

            result_message += "\n"

        # Usage instructions
        result_message += (f"🔧 **Usage Instructions**:\n" +
                           f"   • Use 'restore_snapshot <name>' to restore from any snapshot\n" +
                           f"   • Use 'create_snapshot <name>' to create new backups\n" +
                           f"   • Monitor storage space in repository location\n" +
                           f"   • Clean up old snapshots periodically\n\n" +
                           f"💾 **Backup Best Practices**:\n" +
                           f"   ✅ Regular automated snapshots (daily/weekly)\n" +
                           f"   ✅ Test restore procedures periodically\n" +
                           f"   ✅ Monitor snapshot success/failure status\n" +
                           f"   ✅ Keep snapshots in multiple locations if possible")

        return result_message

    except Exception as e:
        error_message = "❌ Failed to list snapshots:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "repository" in error_str and ("not found" in error_str or "missing" in error_str):
            error_message += f"📂 **Repository Error**: Repository '{repository}' not found\n"
            error_message += f"📍 Check repository configuration and permissions\n"
            error_message += f"💡 Try: Create repository first or check Elasticsearch configuration\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# CLI Entry Point
def main():
    """Main entry point for elasticsearch snapshots server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-snapshots 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Snapshots Server - FastMCP Implementation")
            print("Handles snapshot operations.")
            print("\nTools provided:")
            print("  - [TO BE COPIED FROM BAK FILE]")
            return

    print("🚀 Starting Elasticsearch Snapshots Server...")
    print("🔍 Tools: [TO BE COPIED FROM BAK FILE]")
    app.run()


if __name__ == "__main__":
    main()
