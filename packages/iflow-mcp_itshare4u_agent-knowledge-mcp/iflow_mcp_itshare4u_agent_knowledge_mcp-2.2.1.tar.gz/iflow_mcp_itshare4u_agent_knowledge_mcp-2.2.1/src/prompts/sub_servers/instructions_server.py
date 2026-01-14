"""FastMCP server for AI assistant instructions and smart prompting guidance."""

import os
from pathlib import Path
from typing import Literal
from fastmcp import FastMCP

app = FastMCP(name="Instructions Server")

def _load_copilot_instructions() -> str:
    """Load the copilot instructions content for AI assistants."""
    try:
        instructions_path = Path(__file__).parent.parent.parent / "resources" / "copilot-instructions.md"
        
        if not instructions_path.exists():
            return "Copilot instructions not found. Please refer to the GitHub repository: https://github.com/itshare4u/AgentKnowledgeMCP"
        
        with open(instructions_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return "Copilot instructions file is empty. Please check the installation or refer to online documentation."
            
        return content
        
    except UnicodeDecodeError:
        return "Error reading copilot instructions (encoding issue). Please reinstall AgentKnowledgeMCP or check file integrity."
    except PermissionError:
        return "Permission denied reading copilot instructions. Please check file permissions for the AgentKnowledgeMCP installation."
    except Exception as e:
        return f"Error loading copilot instructions: {str(e)}. Please refer to GitHub documentation: https://github.com/itshare4u/AgentKnowledgeMCP"

def _load_prompt_template(template_name: str, user_request: str) -> str:
    """Load a prompt template from markdown file and replace placeholders.
    
    Args:
        template_name: Name of the template file (without .md extension)
        user_request: User's request to replace {{user_request}} placeholder
        
    Returns:
        Processed template content with placeholders replaced
    """
    try:
        template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.md"
        
        if not template_path.exists():
            return f"Template '{template_name}' not found. Please check the template files."
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read().strip()
            
        if not template_content:
            return f"Template '{template_name}' is empty. Please check the template file."
        
        # Replace placeholders
        processed_content = template_content.replace("{{user_request}}", user_request)
        
        return processed_content
        
    except UnicodeDecodeError:
        return f"Error reading template '{template_name}' (encoding issue). Please check file integrity."
    except PermissionError:
        return f"Permission denied reading template '{template_name}'. Please check file permissions."
    except Exception as e:
        return f"Error loading template '{template_name}': {str(e)}. Please check the template file."

@app.prompt(
    name="copilot_instructions",
    description="AI Assistant instructions for optimal AgentKnowledgeMCP usage - Complete behavioral guidelines and mandatory protocols",
    tags={"copilot", "instructions", "ai", "assistant", "guidelines", "protocols", "behavioral"}
)
async def copilot_instructions() -> str:
    """Return the complete copilot instructions content for AI assistants working with AgentKnowledgeMCP."""
    
    # Load the copilot instructions content
    instructions_content = _load_copilot_instructions()
    
    # Return the content with additional context
    return instructions_content
@app.prompt(
    name="smart_prompting_assistant",
    description="Smart prompting assistant for managing project workflows, rules, and memories in .knowledges directory",
    tags={"smart-prompting", "workflows", "rules", "memories", "knowledges", "project-management"}
)
async def smart_prompting_assistant(
    content_type: Literal["workflow", "rules", "memories"],
    user_request: str
) -> str:
    """Smart assistant for managing project knowledge in .knowledges directory.
    
    Args:
        content_type: Type of content to manage (workflow, rules, or memories)
        user_request: What the user wants to add or manage
    """
    
    # Map content types to template names
    template_mapping = {
        "workflow": "workflow_assistant",
        "rules": "rules_assistant", 
        "memories": "memories_assistant"
    }
    
    template_name = template_mapping.get(content_type)
    if not template_name:
        return f"Invalid content type '{content_type}'. Please choose from: workflow, rules, memories"
    
    # Load and process template
    return _load_prompt_template(template_name, user_request)

def cli_main():
    """CLI entry point for Instructions FastMCP server."""
    print("Starting AgentKnowledgeMCP Instructions FastMCP server...")
    print("Available prompts:")
    print("  • mcp_usage_guide - Comprehensive usage guide with scenarios and tutorials")
    print("  • copilot_instructions - AI assistant behavioral guidelines and protocols")
    print("  • smart_prompting_assistant - Smart assistant for managing workflows, rules, and memories")
    print("Returns complete guidance content for optimal MCP server usage")

    app.run()

if __name__ == "__main__":
    cli_main()
