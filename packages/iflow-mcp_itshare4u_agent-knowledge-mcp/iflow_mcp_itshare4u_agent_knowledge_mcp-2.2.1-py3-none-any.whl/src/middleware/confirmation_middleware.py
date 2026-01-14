"""
Confirmation Middleware for AgentKnowledgeMCP
Provides confirmation for destructive operations based on configuration rules.
"""
from typing import Tuple

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from src.config.config import load_config


class ConfirmationMiddleware(Middleware):
    """Middleware that provides confirmation for destructive operations based on configuration rules."""

    def __init__(self):
        super().__init__()
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load confirmation configuration from config.json."""
        try:
            self.config = load_config()
        except Exception as e:
            print(f"Warning: Could not load config for confirmation middleware: {e}")
            self.config = {}

    def _get_confirmation_rules(self) -> dict:
        """Get confirmation rules from configuration."""
        if not self.config:
            self._load_config()
        
        confirmation_config = self.config.get("confirmation", {})
        if not confirmation_config.get("enabled", False):
            return {}
        
        return confirmation_config.get("rules", {})

    def _requires_confirmation(self, tool_name: str) -> Tuple[bool, dict]:
        """Check if tool requires confirmation based on configuration rules."""
        rules = self._get_confirmation_rules()
        
        for rule_name, rule_config in rules.items():
            if not rule_config.get("require_confirmation", False):
                continue
                
            tools_list = rule_config.get("tools", [])
            if tool_name in tools_list:
                return True, rule_config
        
        return False, {}

    async def _collect_user_feedback(self, ctx, feedback_context: str) -> str:
        """Helper method to collect optional user feedback with consistent messaging."""
        feedback_message = f"""💬 **Do you want to say something to the agent?**

{feedback_context}

✍️ **Your message (optional):**"""
        
        feedback_result = await ctx.elicit(
            message=feedback_message,
            response_type=str  # Allow text input for user feedback
        )
        
        # Return feedback text if provided, empty string otherwise
        if feedback_result.action == "accept" and feedback_result.data and feedback_result.data.strip():
            return feedback_result.data.strip()
        return ""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Hook called when tools are being executed - check for confirmation requirements."""
        tool_name = context.message.name
        
        # Check if this tool requires confirmation
        requires_confirmation, rule_config = self._requires_confirmation(tool_name)
        
        if not requires_confirmation:
            # No confirmation needed, proceed with tool execution
            return await call_next(context)
        
        # Get FastMCP context to access elicitation
        if not context.fastmcp_context:
            # No FastMCP context available, skip confirmation
            return await call_next(context)
        
        confirmation_message = f"""📋 **Tool:** {tool_name}

⚠️ **This operation requires confirmation before proceeding.**

🤔 **Do you want to continue with this operation?**"""

        # Request confirmation from user
        ctx = context.fastmcp_context
        result = await ctx.elicit(
            message=confirmation_message,
            response_type=None  # Simple accept/decline confirmation
        )
        
        # Always ask for feedback after user makes a decision (accept or decline)
        if result.action == "accept":
            await ctx.info(f"✅ User confirmed execution of {tool_name}")
            return await call_next(context)
            
        elif result.action == "decline":
            # User declined - ask for additional feedback
            await ctx.info(f"❌ User declined execution of {tool_name}")
            
            # Request feedback using helper function
            feedback_context = "Since you declined the operation, you can provide additional context or instructions to help the agent understand what you'd like to do instead."
            user_feedback = await self._collect_user_feedback(ctx, feedback_context)
            
            # Prepare the cancellation message with user feedback
            error_message = f"Operation cancelled: User declined to confirm {tool_name} execution."
            if user_feedback:
                error_message += f" User feedback: \"{user_feedback}\""
            
            await ctx.warning(error_message)
            raise ToolError(error_message)
        else:  # cancel
            # User cancelled
            await ctx.warning(f"🚫 User cancelled execution of {tool_name}")
            raise ToolError(f"Operation cancelled: User cancelled {tool_name} execution")
