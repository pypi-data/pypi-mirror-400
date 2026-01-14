"""
Confirmation handlers for user response processing.
"""
import mcp.types as types
from typing import List, Dict, Any

from src.confirmation.confirmation import get_confirmation_manager

async def handle_user_response(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle user confirmation response for pending operations.

    Args:
        arguments: Dictionary containing:
            - pending_id (str): The operation ID to respond to
            - response (str): 'yes' or 'no'
            - message (str, optional): User message

    Returns:
        List of TextContent with operation result
    """
    confirmation_manager = get_confirmation_manager()
    if not confirmation_manager:
        return [types.TextContent(
            type="text",
            text="❌ **Confirmation system not initialized**"
        )]

    # Validate required parameters
    pending_id = arguments.get("pending_id")
    if not pending_id:
        return [types.TextContent(
            type="text",
            text="❌ **Error**: Missing required parameter 'pending_id'\n\n"
                 "Usage: user_response(pending_id='xxx', response='yes')"
        )]

    response = arguments.get("response")
    if not response:
        return [types.TextContent(
            type="text",
            text="❌ **Error**: Missing required parameter 'response'\n\n"
                 "Usage: user_response(pending_id='xxx', response='yes' or 'no')"
        )]

    user_message = arguments.get("message", "")

    # Process the response
    result = await confirmation_manager.process_user_response(
        pending_id=pending_id,
        response=response,
        user_message=user_message
    )

    # Format response based on result
    if result["success"]:
        if result["action"] == "executed":
            # Operation was approved and executed
            return [types.TextContent(
                type="text",
                text=f"✅ **Operation Approved & Executed**\n\n"
                     f"**Tool**: {result['tool_name']}\n"
                     f"**Status**: Successfully completed\n"
                     f"**Pending ID**: {result['pending_id']}\n\n"
                     f"**Result**: Operation executed successfully"
            )] + result.get("result", [])

        elif result["action"] == "denied":
            # Operation was denied
            return [types.TextContent(
                type="text",
                text=f"🚫 **Operation Denied**\n\n"
                     f"**Message**: {result['message']}\n"
                     f"**Pending ID**: {result['pending_id']}\n\n"
                     f"Operation cancelled as requested by user."
            )]

    else:
        # Error occurred
        return [types.TextContent(
            type="text",
            text=f"❌ **Error Processing Response**\n\n"
                 f"**Error**: {result['error']}\n"
                 f"**Pending ID**: {result.get('pending_id', 'Unknown')}\n\n"
                 f"Please check the pending ID and try again."
        )]

async def handle_confirmation_status(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Get status of confirmation system and pending operations.

    Args:
        arguments: Dictionary containing:
            - pending_id (str, optional): Specific operation to check
            - session_id (str, optional): All operations for session

    Returns:
        List of TextContent with status information
    """
    confirmation_manager = get_confirmation_manager()
    if not confirmation_manager:
        return [types.TextContent(
            type="text",
            text="❌ **Confirmation system not initialized**"
        )]

    pending_id = arguments.get("pending_id")
    session_id = arguments.get("session_id")

    if pending_id:
        # Get specific operation status
        operation = await confirmation_manager.get_operation(pending_id)
        if not operation:
            return [types.TextContent(
                type="text",
                text=f"❌ **Operation Not Found**\n\n"
                     f"Pending ID '{pending_id}' does not exist or has been completed."
            )]

        time_remaining = operation.time_remaining()
        return [types.TextContent(
            type="text",
            text=f"📊 **Operation Status**\n\n"
                 f"**Pending ID**: {operation.id}\n"
                 f"**Tool**: {operation.tool_name}\n"
                 f"**Status**: {operation.status.value}\n"
                 f"**Rule**: {operation.rule_name}\n"
                 f"**Time Remaining**: {time_remaining // 60}m {time_remaining % 60}s\n"
                 f"**Created**: {operation.created_at}\n"
                 f"**Session**: {operation.session_id or 'None'}"
        )]

    elif session_id:
        # Get all operations for session
        operations = await confirmation_manager.get_session_operations(session_id)
        if not operations:
            return [types.TextContent(
                type="text",
                text=f"📊 **Session Status**\n\n"
                     f"No pending operations for session '{session_id}'"
            )]

        status_lines = [f"📊 **Session Status**: {session_id}\n"]
        for i, op in enumerate(operations, 1):
            time_remaining = op.time_remaining()
            status_lines.append(
                f"{i}. **{op.tool_name}** ({op.id[:12]}...)\n"
                f"   Status: {op.status.value} | "
                f"   Time: {time_remaining // 60}m {time_remaining % 60}s"
            )

        return [types.TextContent(
            type="text",
            text="\n".join(status_lines)
        )]

    else:
        # Get system statistics
        stats = await confirmation_manager.get_statistics()
        return [types.TextContent(
            type="text",
            text=f"📊 **Confirmation System Status**\n\n"
                 f"**Active Operations**: {stats['active_operations']}\n"
                 f"**Active Sessions**: {stats['active_sessions']}\n"
                 f"**Total Processed**: {stats['total_operations']}\n"
                 f"**Approved**: {stats['approved']}\n"
                 f"**Denied**: {stats['denied']}\n"
                 f"**Expired**: {stats['expired']}\n"
                 f"**Cancelled**: {stats['cancelled']}\n"
                 f"**Auto Cleanups**: {stats['auto_cleanups']}\n"
                 f"**System Enabled**: {stats['config_enabled']}\n"
                 f"**Cleanup Interval**: {stats['cleanup_interval_minutes']} minutes"
        )]
