"""
Sophisticated User Confirmation System for AgentKnowledgeMCP
Provides enterprise-grade permission control with simple yes/no interface.
"""
import time
import uuid
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class OperationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PendingOperation:
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    session_id: Optional[str]
    created_at: float
    expires_at: float
    status: OperationStatus = OperationStatus.PENDING
    retry_count: int = 0
    last_retry_at: Optional[float] = None
    user_message: Optional[str] = None
    audit_trail: List[Dict] = field(default_factory=list)
    rule_name: str = "default"
    timeout_minutes: int = 30

    def is_expired(self) -> bool:
        """Check if operation has expired"""
        return time.time() > self.expires_at

    def time_remaining(self) -> int:
        """Get remaining time in seconds"""
        remaining = self.expires_at - time.time()
        return max(0, int(remaining))

    def add_audit_entry(self, action: str, details: str = ""):
        """Add entry to audit trail"""
        self.audit_trail.append({
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "status": self.status.value
        })

class ConfirmationManager:
    """
    Sophisticated confirmation system with enterprise features:
    - Session management
    - Auto cleanup
    - Operation queuing
    - Audit logging
    - Configurable rules
    - Statistics tracking
    """

    def __init__(self, config: Dict):
        self.config = config.get("", {})
        self.operations: Dict[str, PendingOperation] = {}
        self.session_operations: Dict[str, List[str]] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self.statistics = {
            "total_operations": 0,
            "approved": 0,
            "denied": 0,
            "expired": 0,
            "cancelled": 0,
            "auto_cleanups": 0
        }

        # Default configuration
        self.default_config = {
            "enabled": True,
            "default_timeout_minutes": 30,
            "max_pending_per_session": 10,
            "auto_cleanup_interval_minutes": 5,
            "audit_log_enabled": True,
            "rules": {
                "admin_tools": {
                    "tools": ["update_config", "reset_config", "setup_elasticsearch"],
                    "require_confirmation": True,
                    "timeout_minutes": 60
                },
                "destructive_operations": {
                    "tools": ["delete_file", "delete_directory", "delete_index", "delete_document"],
                    "require_confirmation": True,
                    "timeout_minutes": 30
                },
                "file_write_operations": {
                    "tools": ["write_file", "move_file", "copy_file", "append_file"],
                    "require_confirmation": True,
                    "timeout_minutes": 15
                },
                "elasticsearch_write": {
                    "tools": ["index_document", "create_index"],
                    "require_confirmation": True,
                    "timeout_minutes": 20
                }
            }
        }

        # Merge with provided config
        self._merge_config()
        self._start_cleanup_task()

    def _merge_config(self):
        """Merge default config with provided config"""
        if not self.config:
            self.config = self.default_config.copy()
        else:
            # Merge rules
            default_rules = self.default_config["rules"].copy()
            user_rules = self.config.get("rules", {})
            default_rules.update(user_rules)
            self.config["rules"] = default_rules

            # Set defaults for missing keys
            for key, value in self.default_config.items():
                if key not in self.config and key != "rules":
                    self.config[key] = value

    def _start_cleanup_task(self):
        """Start background cleanup task (only if in async context)"""
        if self.config.get("enabled", True):
            try:
                # Only start cleanup task if we're in an async context
                loop = asyncio.get_running_loop()
                interval = self.config.get("auto_cleanup_interval_minutes", 5) * 60
                self.cleanup_task = asyncio.create_task(self._periodic_cleanup(interval))
            except RuntimeError:
                # No running event loop - cleanup task will be started later
                self.cleanup_task = None
                print("ℹ️ Confirmation cleanup task will start when server runs")

    async def _periodic_cleanup(self, interval_seconds: int):
        """Background task for periodic cleanup"""
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                await self.cleanup_expired_operations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup task error: {e}")

    async def requires_confirmation(self, tool_name: str) -> Tuple[bool, Dict]:
        """
        Check if tool requires confirmation and return rule details

        Returns:
            Tuple of (requires_confirmation: bool, rule_details: dict)
        """
        if not self.config.get("enabled", True):
            return False, {}

        # Check each rule
        for rule_name, rule_config in self.config["rules"].items():
            if tool_name in rule_config.get("tools", []):
                if rule_config.get("require_confirmation", False):
                    return True, {
                        "rule_name": rule_name,
                        "timeout_minutes": rule_config.get("timeout_minutes", 30)
                    }

        return False, {}

    async def store_operation(self, tool_name: str, arguments: Dict,
                            session_id: Optional[str] = None) -> str:
        """
        Store pending operation with sophisticated tracking

        Returns:
            pending_id: Unique identifier for the operation
        """
        # Check session limits
        if session_id:
            session_ops = self.session_operations.get(session_id, [])
            max_pending = self.config.get("max_pending_per_session", 10)
            if len(session_ops) >= max_pending:
                raise ValueError(f"Maximum pending operations ({max_pending}) reached for session")

        # Get rule details
        requires_confirm, rule_details = await self.requires_confirmation(tool_name)
        if not requires_confirm:
            raise ValueError(f"Tool {tool_name} does not require confirmation")

        # Generate unique ID
        pending_id = f"confirm_{uuid.uuid4().hex[:8]}_{int(time.time())}"

        # Calculate expiry
        timeout_minutes = rule_details.get("timeout_minutes", 30)
        expires_at = time.time() + (timeout_minutes * 60)

        # Create operation
        operation = PendingOperation(
            id=pending_id,
            tool_name=tool_name,
            arguments=arguments,
            session_id=session_id,
            created_at=time.time(),
            expires_at=expires_at,
            rule_name=rule_details.get("rule_name", "unknown"),
            timeout_minutes=timeout_minutes
        )

        operation.add_audit_entry("created", f"Tool: {tool_name}, Rule: {operation.rule_name}")

        # Store operation
        self.operations[pending_id] = operation

        # Track by session
        if session_id:
            if session_id not in self.session_operations:
                self.session_operations[session_id] = []
            self.session_operations[session_id].append(pending_id)

        # Update statistics
        self.statistics["total_operations"] += 1

        return pending_id

    async def process_user_response(self, pending_id: str, response: str,
                                  user_message: Optional[str] = None) -> Dict:
        """
        Process user confirmation response

        Args:
            pending_id: Operation identifier
            response: 'yes' or 'no'
            user_message: Optional user message

        Returns:
            Dict with operation result
        """
        # Validate operation exists
        if pending_id not in self.operations:
            return {
                "success": False,
                "error": f"Operation {pending_id} not found",
                "pending_id": pending_id
            }

        operation = self.operations[pending_id]

        # Check if expired
        if operation.is_expired():
            operation.status = OperationStatus.EXPIRED
            operation.add_audit_entry("expired", "Operation expired before user response")
            self.statistics["expired"] += 1
            return {
                "success": False,
                "error": f"Operation {pending_id} has expired",
                "pending_id": pending_id
            }

        # Validate response
        response = response.lower().strip()
        if response not in ["yes", "no"]:
            return {
                "success": False,
                "error": f"Invalid response '{response}'. Use 'yes' or 'no'",
                "pending_id": pending_id
            }

        # Process response
        if response == "yes":
            operation.status = OperationStatus.APPROVED
            operation.add_audit_entry("approved", f"User approved. Message: {user_message or 'None'}")
            self.statistics["approved"] += 1

            # Execute the original operation
            return await self._execute_pending_operation(operation)

        else:  # response == "no"
            operation.status = OperationStatus.DENIED
            operation.add_audit_entry("denied", f"User denied. Message: {user_message or 'None'}")
            self.statistics["denied"] += 1

            # Clean up
            await self._cleanup_operation(pending_id)

            return {
                "success": True,
                "action": "denied",
                "message": f"Operation {operation.tool_name} denied by user",
                "pending_id": pending_id
            }

    async def _execute_pending_operation(self, operation: PendingOperation) -> Dict:
        """
        Execute the stored operation

        Args:
            operation: The pending operation to execute

        Returns:
            Dict with execution result
        """
        try:
            operation.status = OperationStatus.EXECUTING
            operation.add_audit_entry("executing", f"Starting execution of {operation.tool_name}")

            # Import here to avoid circular imports
            import importlib
            server_module = importlib.import_module('.server', package=__package__)

            # Get handler from server module
            TOOL_HANDLERS = getattr(server_module, 'TOOL_HANDLERS', {})
            handler = TOOL_HANDLERS.get(operation.tool_name)

            if not handler:
                raise ValueError(f"Handler not found for tool: {operation.tool_name}")

            # Execute
            result = await handler(operation.arguments)

            operation.status = OperationStatus.COMPLETED
            operation.add_audit_entry("completed", "Operation executed successfully")

            # Clean up
            await self._cleanup_operation(operation.id)

            return {
                "success": True,
                "action": "executed",
                "tool_name": operation.tool_name,
                "result": result,
                "pending_id": operation.id
            }

        except Exception as e:
            operation.status = OperationStatus.FAILED
            operation.add_audit_entry("failed", f"Execution failed: {str(e)}")

            return {
                "success": False,
                "error": f"Failed to execute {operation.tool_name}: {str(e)}",
                "pending_id": operation.id
            }

    async def get_operation(self, pending_id: str) -> Optional[PendingOperation]:
        """Get operation details"""
        return self.operations.get(pending_id)

    async def cancel_operation(self, pending_id: str, reason: str = "user_cancelled") -> bool:
        """Cancel pending operation"""
        if pending_id not in self.operations:
            return False

        operation = self.operations[pending_id]
        operation.status = OperationStatus.CANCELLED
        operation.add_audit_entry("cancelled", reason)
        self.statistics["cancelled"] += 1

        await self._cleanup_operation(pending_id)
        return True

    async def get_session_operations(self, session_id: str) -> List[PendingOperation]:
        """Get all operations for a session"""
        if session_id not in self.session_operations:
            return []

        operations = []
        for pending_id in self.session_operations[session_id]:
            if pending_id in self.operations:
                operations.append(self.operations[pending_id])

        return operations

    async def cleanup_expired_operations(self):
        """Cleanup expired operations with audit logging"""
        expired_count = 0
        expired_ids = []

        for pending_id, operation in list(self.operations.items()):
            if operation.is_expired() and operation.status == OperationStatus.PENDING:
                operation.status = OperationStatus.EXPIRED
                operation.add_audit_entry("auto_expired", "Automatically expired by cleanup task")
                expired_ids.append(pending_id)
                expired_count += 1

        # Clean up expired operations
        for pending_id in expired_ids:
            await self._cleanup_operation(pending_id)

        if expired_count > 0:
            self.statistics["auto_cleanups"] += 1
            self.statistics["expired"] += expired_count
            print(f"🧹 Cleaned up {expired_count} expired confirmation operations")

    async def _cleanup_operation(self, pending_id: str):
        """Remove operation from all tracking structures"""
        if pending_id in self.operations:
            operation = self.operations[pending_id]

            # Remove from session tracking
            if operation.session_id and operation.session_id in self.session_operations:
                if pending_id in self.session_operations[operation.session_id]:
                    self.session_operations[operation.session_id].remove(pending_id)

                # Clean up empty session lists
                if not self.session_operations[operation.session_id]:
                    del self.session_operations[operation.session_id]

            # Remove operation
            del self.operations[pending_id]

    async def get_statistics(self) -> Dict:
        """Get confirmation system statistics"""
        return {
            **self.statistics,
            "active_operations": len(self.operations),
            "active_sessions": len(self.session_operations),
            "config_enabled": self.config.get("enabled", True),
            "cleanup_interval_minutes": self.config.get("auto_cleanup_interval_minutes", 5)
        }

    async def start_cleanup_task(self):
        """Manually start cleanup task when in async context"""
        if self.config.get("enabled", True) and not self.cleanup_task:
            try:
                interval = self.config.get("auto_cleanup_interval_minutes", 5) * 60
                self.cleanup_task = asyncio.create_task(self._periodic_cleanup(interval))
                print(f"✅ Confirmation cleanup task started (interval: {interval//60} minutes)")
            except Exception as e:
                print(f"⚠️ Failed to start cleanup task: {e}")

    async def shutdown(self):
        """Graceful shutdown - cancel cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

# Global confirmation manager (will be initialized in server.py)
confirmation_manager: Optional[ConfirmationManager] = None

def initialize_confirmation_manager(config: Dict) -> ConfirmationManager:
    """Initialize global confirmation manager"""
    global confirmation_manager
    confirmation_manager = ConfirmationManager(config)
    return confirmation_manager

def get_confirmation_manager() -> Optional[ConfirmationManager]:
    """Get global confirmation manager"""
    return confirmation_manager
