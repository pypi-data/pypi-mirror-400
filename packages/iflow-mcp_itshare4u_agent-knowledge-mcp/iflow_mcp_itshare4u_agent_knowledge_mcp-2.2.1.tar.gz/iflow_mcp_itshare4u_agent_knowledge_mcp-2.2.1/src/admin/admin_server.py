"""
Admin Operations FastMCP Server - Step by step migration
Tool-by-tool conversion from handlers to FastMCP tools.
File 3/4: Admin Server
"""

import json
import subprocess
import time
import shutil
import importlib.metadata
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Annotated

from fastmcp import FastMCP, Context
from pydantic import Field

from src.config.config import load_config
from src.utils.security import get_allowed_base_dir, init_security
from src.es_client.elasticsearch_client import reset_es_client, init_elasticsearch
from src.es_client.elasticsearch_setup import auto_setup_elasticsearch, ElasticsearchSetup

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Admin",
    version="1.0.0",
    instructions="Administrative operations tools for system management"
)

def _format_admin_error(e: Exception, operation: str, context: str = None) -> str:
    """Format admin operation errors with detailed guidance for agents."""
    error_message = f"❌ Failed to {operation}:\n\n"

    error_str = str(e).lower()
    if "permission denied" in error_str or "access denied" in error_str:
        error_message += "🔒 **Permission Error**: Administrative access denied\n"
        error_message += f"📍 Insufficient permissions for {operation}\n"
        error_message += f"💡 **Suggestions for agents**:\n"
        error_message += f"   1. Check if you have admin privileges\n"
        error_message += f"   2. Ask user to run with elevated permissions\n"
        error_message += f"   3. Verify system user has appropriate access\n"
        error_message += f"   4. Check file/directory ownership and permissions\n\n"
    elif "file not found" in error_str or "no such file" in error_str:
        error_message += f"📁 **File Not Found**: Required file or directory missing\n"
        if context:
            error_message += f"📍 Context: {context}\n"
        error_message += f"💡 Try: Check file paths and verify installation integrity\n\n"
    elif "connection" in error_str or "network" in error_str:
        error_message += f"🌐 **Connection Error**: Network or service connectivity issue\n"
        error_message += f"📍 Cannot connect to required service\n"
        error_message += f"💡 Try: Check service status and network connectivity\n\n"
    elif "invalid" in error_str or "malformed" in error_str:
        error_message += f"📝 **Configuration Error**: Invalid configuration or format\n"
        error_message += f"📍 Configuration validation failed\n"
        error_message += f"💡 Try: Check configuration syntax and format\n\n"
    else:
        error_message += f"⚠️ **System Error**: {str(e)}\n\n"

    error_message += f"🔍 **Technical Details**: {str(e)}"

    return error_message


# ================================
# TOOL 1: GET_CONFIG
# ================================

@app.tool(
    description="Get the complete configuration from config.json file with formatted display",
    tags={"admin", "config", "get", "view", "settings"}
)
async def get_config() -> str:
    """Get the complete configuration from config.json file."""
    try:
        config = load_config()
        config_str = json.dumps(config, indent=2, ensure_ascii=False)

        return f"📄 Current configuration:\n\n```json\n{config_str}\n```"

    except Exception as e:
        return _format_admin_error(e, "get configuration", "config.json loading")


# ================================
# TOOL 2: UPDATE_CONFIG
# ================================

@app.tool(
    description="Update configuration with section-specific changes or full configuration replacement",
    tags={"admin", "config", "update", "modify", "settings"}
)
async def update_config(
    config_section: Annotated[Optional[str], Field(description="The top-level section of the config to update (e.g., 'security')")] = None,
    config_key: Annotated[Optional[str], Field(description="The key within the section to update (e.g., 'allowed_base_directory')")] = None,
    config_value: Annotated[Optional[str], Field(description="The new value for the specified key")] = None,
    full_config: Annotated[Optional[Dict[str, Any]], Field(description="Full configuration object to save. Replaces the entire config")] = None
) -> str:
    """Update configuration with comprehensive validation and automatic component reinitialization."""
    try:
        config_path = Path(__file__).parent.parent / "config.json"

        if full_config:
            # Full configuration replacement
            new_config = full_config

            # Validate new config structure
            required_sections = ["elasticsearch", "security", "document_validation", "server"]
            for section in required_sections:
                if section not in new_config:
                    return f"❌ Error: Missing required config section '{section}'\n💡 Required sections: {', '.join(required_sections)}"

            # Write new config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)

            message = "✅ Full configuration updated successfully!"

        elif config_section and config_key is not None:
            # Section-specific key update
            config = load_config()

            if config_section not in config:
                return f"❌ Error: Config section '{config_section}' not found\n💡 Available sections: {', '.join(config.keys())}"

            # Store old value for comparison
            old_value = config[config_section].get(config_key, "<not set>")

            # Update the value
            config[config_section][config_key] = config_value

            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            message = f"✅ Configuration updated successfully!\n\n"
            message += f"📁 Section: {config_section}\n"
            message += f"🔑 Key: {config_key}\n"
            message += f"📤 Old value: {old_value}\n"
            message += f"📥 New value: {config_value}"

        else:
            return "❌ Error: Must provide either 'full_config' or both 'config_section' and 'config_key'\n💡 Choose: Section-specific update (config_section + config_key + config_value) OR Full replacement (full_config)"

        # Reload configuration in current session
        new_config = load_config()

        # Reinitialize security if security section was updated
        if (config_section == "security" and config_key == "allowed_base_directory") or full_config:
            init_security(new_config["security"]["allowed_base_directory"])

        # Reinitialize Elasticsearch if elasticsearch section was updated
        if (config_section == "elasticsearch") or full_config:
            init_elasticsearch(new_config)
            reset_es_client()

        return message + f"\n\n💡 Configuration reloaded automatically - all components reinitialized"

    except json.JSONDecodeError as e:
        return f"❌ JSON Error: Invalid JSON format in full_config\n🔍 Details: {str(e)}\n💡 Check JSON syntax and structure"
    except Exception as e:
        return _format_admin_error(e, "update configuration", f"config_section={config_section}, config_key={config_key}")


# ================================
# TOOL 3: VALIDATE_CONFIG
# ================================

@app.tool(
    description="Validate configuration object structure, types, and values with comprehensive error reporting",
    tags={"admin", "config", "validate", "check", "schema"}
)
async def validate_config(
    config: Annotated[Optional[Dict[str, Any]], Field(description="Configuration object to validate. If not provided, validates current config")] = None
) -> str:
    """Validate configuration with comprehensive structure checking and detailed feedback."""
    try:
        if config is None:
            config = load_config()

        errors = []
        warnings = []

        # Validate structure - required sections
        required_sections = ["elasticsearch", "security", "document_validation", "document_schema", "server"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Validate elasticsearch section
        if "elasticsearch" in config:
            es_config = config["elasticsearch"]
            if "host" not in es_config:
                errors.append("elasticsearch.host is required")
            if "port" not in es_config:
                errors.append("elasticsearch.port is required")
            elif not isinstance(es_config["port"], int):
                errors.append("elasticsearch.port must be an integer")
            elif es_config["port"] <= 0 or es_config["port"] > 65535:
                errors.append("elasticsearch.port must be between 1-65535")

        # Validate security section
        if "security" in config:
            sec_config = config["security"]
            if "allowed_base_directory" not in sec_config:
                errors.append("security.allowed_base_directory is required")
            else:
                base_dir = Path(sec_config["allowed_base_directory"])
                if not base_dir.exists():
                    warnings.append(f"security.allowed_base_directory does not exist: {base_dir}")
                elif not base_dir.is_dir():
                    errors.append(f"security.allowed_base_directory is not a directory: {base_dir}")

        # Validate document_validation section
        if "document_validation" in config:
            doc_config = config["document_validation"]
            bool_fields = ["strict_schema_validation", "allow_extra_fields", "required_fields_only", "auto_correct_paths"]
            for field in bool_fields:
                if field in doc_config and not isinstance(doc_config[field], bool):
                    errors.append(f"document_validation.{field} must be a boolean")

        # Validate document_schema section
        if "document_schema" in config:
            schema_config = config["document_schema"]
            required_schema_fields = ["required_fields", "field_types", "priority_values", "source_types"]
            for field in required_schema_fields:
                if field not in schema_config:
                    errors.append(f"document_schema.{field} is required")

            # Validate specific schema field types
            if "required_fields" in schema_config:
                if not isinstance(schema_config["required_fields"], list):
                    errors.append("document_schema.required_fields must be a list")
                elif not schema_config["required_fields"]:
                    warnings.append("document_schema.required_fields is empty")

            if "field_types" in schema_config:
                if not isinstance(schema_config["field_types"], dict):
                    errors.append("document_schema.field_types must be a dictionary")
                elif not schema_config["field_types"]:
                    warnings.append("document_schema.field_types is empty")

            if "priority_values" in schema_config:
                if not isinstance(schema_config["priority_values"], list):
                    errors.append("document_schema.priority_values must be a list")
                elif not schema_config["priority_values"]:
                    warnings.append("document_schema.priority_values is empty")

            if "source_types" in schema_config:
                if not isinstance(schema_config["source_types"], list):
                    errors.append("document_schema.source_types must be a list")
                elif not schema_config["source_types"]:
                    warnings.append("document_schema.source_types is empty")

        # Validate server section
        if "server" in config:
            server_config = config["server"]
            if "name" in server_config and not isinstance(server_config["name"], str):
                errors.append("server.name must be a string")
            if "version" in server_config and not isinstance(server_config["version"], str):
                errors.append("server.version must be a string")

        # Prepare result message
        if errors:
            message = f"❌ Configuration validation failed!\n\n🚨 **Errors ({len(errors)}):**\n"
            for i, error in enumerate(errors, 1):
                message += f"   {i}. {error}\n"
        else:
            message = "✅ Configuration validation passed!"

        if warnings:
            message += f"\n⚠️ **Warnings ({len(warnings)}):**\n"
            for i, warning in enumerate(warnings, 1):
                message += f"   {i}. {warning}\n"

        # Show current validation settings summary
        if "document_validation" in config:
            doc_val = config["document_validation"]
            message += f"\n📋 **Current Document Validation Settings:**\n"
            message += f"   🔒 Strict schema validation: {doc_val.get('strict_schema_validation', False)}\n"
            message += f"   📝 Allow extra fields: {doc_val.get('allow_extra_fields', True)}\n"
            message += f"   ✅ Required fields only: {doc_val.get('required_fields_only', False)}\n"
            message += f"   🔧 Auto correct paths: {doc_val.get('auto_correct_paths', True)}\n"

        # Show section summary
        sections_found = [s for s in required_sections if s in config]
        message += f"\n📊 **Configuration Summary:**\n"
        message += f"   📁 Sections found: {len(sections_found)}/{len(required_sections)}\n"
        message += f"   ✅ Valid sections: {', '.join(sections_found)}\n"
        if len(sections_found) < len(required_sections):
            missing = [s for s in required_sections if s not in config]
            message += f"   ❌ Missing sections: {', '.join(missing)}\n"

        return message

    except json.JSONDecodeError as e:
        return f"❌ JSON Error: Invalid JSON format in config data\n🔍 Details: {str(e)}\n💡 Check JSON syntax and structure"
    except Exception as e:
        return _format_admin_error(e, "validate configuration", "config structure validation")


# ================================
# TOOL 4: RELOAD_CONFIG
# ================================

@app.tool(
    description="Reload configuration from config.json file and reinitialize all components with updated settings",
    tags={"admin", "config", "reload", "refresh", "reinitialize"}
)
async def reload_config() -> str:
    """Reload configuration and reinitialize all system components with updated settings."""
    try:
        # Reload configuration from file
        config = load_config()

        # Reinitialize security with updated allowed directory
        init_security(config["security"]["allowed_base_directory"])

        # Reinitialize Elasticsearch with updated configuration
        init_elasticsearch(config)
        reset_es_client()

        # Format success message with key configuration details
        message = "✅ Configuration reloaded successfully!\n\n"
        message += "🔄 **Components Reinitialized:**\n"
        message += f"   🔒 Security: {get_allowed_base_dir()}\n"
        message += f"   🔍 Elasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"

        # Show additional configuration summary
        if "server" in config:
            server_config = config["server"]
            message += f"   🚀 Server: {server_config.get('name', 'AgentKnowledgeMCP')} v{server_config.get('version', '1.0.0')}\n"

        message += f"\n💡 All system components now use the updated configuration from config.json"

        return message

    except KeyError as e:
        return f"❌ Configuration Error: Missing required configuration key: {str(e)}\n💡 Check config.json structure and ensure all required sections are present"
    except FileNotFoundError:
        return f"❌ File Error: config.json not found\n💡 Ensure config.json exists in the source directory"
    except json.JSONDecodeError as e:
        return f"❌ JSON Error: Invalid JSON format in config.json\n🔍 Details: {str(e)}\n💡 Check JSON syntax and structure"
    except Exception as e:
        return _format_admin_error(e, "reload configuration", "component reinitialization")


# ================================
# TOOL 5: SETUP_ELASTICSEARCH
# ================================

@app.tool(
    description="Auto-setup Elasticsearch using Docker with optional Kibana and force recreate options",
    tags={"admin", "elasticsearch", "setup", "docker", "auto-install"}
)
async def setup_elasticsearch(
    include_kibana: Annotated[bool, Field(description="Also setup Kibana (default: true)")] = True,
    force_recreate: Annotated[bool, Field(description="Force recreate containers even if they exist")] = False
) -> str:
    """Auto-setup Elasticsearch using Docker with comprehensive Docker container management."""
    try:
        # Get config path for setup
        config_path = Path(__file__).parent.parent / "config.json"
        config = load_config()

        # Handle force recreate - stop existing containers first
        if force_recreate:
            try:
                setup_manager = ElasticsearchSetup(config_path)
                stop_result = setup_manager.stop_containers()

                # Give containers time to stop gracefully
                import time
                time.sleep(5)

                message = "🔄 **Force Recreate Mode:**\n"
                message += f"   🛑 Stopped existing containers\n"
                message += f"   ⏳ Waiting for graceful shutdown...\n\n"
            except Exception as e:
                # Continue with setup even if stop fails
                message = f"⚠️ **Container Stop Warning:** {str(e)}\n"
                message += f"   💡 Continuing with setup anyway...\n\n"
        else:
            message = ""

        # Run comprehensive auto setup
        result = auto_setup_elasticsearch(config_path, config)

        if result["status"] == "already_configured":
            message += "✅ **Elasticsearch Already Configured!**\n\n"
            message += f"📍 **Running at:** http://{result['host']}:{result['port']}\n"
            message += f"🔍 **Status:** Ready and operational\n"
            message += f"💡 **Action:** No setup needed - already working perfectly\n\n"
            message += f"🚀 **Next Steps:**\n"
            message += f"   • Test connection with search tools\n"
            message += f"   • Start indexing your knowledge base\n"
            message += f"   • Use force_recreate=true to rebuild if needed"

        elif result["status"] == "setup_completed":
            es_info = result["elasticsearch"]
            kibana_info = result.get("kibana")

            message += "🎉 **Elasticsearch Setup Completed Successfully!**\n\n"
            message += f"📍 **Elasticsearch:** http://{es_info['host']}:{es_info['port']}\n"

            # Handle Kibana setup results
            if kibana_info:
                if kibana_info.get("status") in ["running", "already_running"]:
                    message += f"📊 **Kibana:** http://{kibana_info['host']}:{kibana_info['port']}\n"
                    message += f"   ✅ Status: {kibana_info['status'].replace('_', ' ').title()}\n"
                elif "error" in kibana_info:
                    message += f"⚠️ **Kibana Warning:** {kibana_info['error']}\n"
                    message += f"   💡 Elasticsearch is ready, Kibana setup had issues\n"
            else:
                message += f"📊 **Kibana:** Skipped (include_kibana=false)\n"

            message += f"\n🔧 **Configuration Updated:**\n"
            message += f"   📝 config.json automatically updated\n"
            message += f"   🔄 Elasticsearch client reinitialized\n"
            message += f"   ✅ All components ready for use\n"

            message += f"\n🚀 **Next Steps:**\n"
            message += f"   • Test search functionality\n"
            message += f"   • Index your first documents\n"
            message += f"   • Explore Kibana dashboard (if enabled)\n"

            # Reload configuration to use new Elasticsearch setup
            new_config = load_config()
            init_elasticsearch(new_config)
            reset_es_client()

        else:
            # Setup failed
            error_msg = result.get("error", "Unknown setup error")
            message += f"❌ **Elasticsearch Setup Failed!**\n\n"
            message += f"🚨 **Error Details:** {error_msg}\n\n"
            message += f"🔧 **Troubleshooting Steps:**\n"
            message += f"   1. Check Docker is running and accessible\n"
            message += f"   2. Verify ports 9200 (ES) and 5601 (Kibana) are available\n"
            message += f"   3. Try force_recreate=true to rebuild containers\n"
            message += f"   4. Check Docker logs for detailed error information\n"
            message += f"   5. Ensure sufficient disk space and memory\n\n"
            message += f"💡 **Need Help?** Check Docker status and container logs for more details"

        return message

    except ImportError as e:
        return f"❌ Module Error: Missing required dependency\n🔍 Details: {str(e)}\n💡 Ensure all Elasticsearch setup modules are properly installed"
    except FileNotFoundError as e:
        return f"❌ File Error: Required configuration or setup file not found\n🔍 Details: {str(e)}\n💡 Check config.json exists and setup modules are in place"
    except Exception as e:
        return _format_admin_error(e, "setup Elasticsearch", f"Docker setup with include_kibana={include_kibana}, force_recreate={force_recreate}")


# ================================
# TOOL 6: ELASTICSEARCH_STATUS
# ================================

@app.tool(
    description="Check status of Elasticsearch and Kibana containers with detailed configuration information",
    tags={"admin", "elasticsearch", "status", "docker", "monitoring"}
)
async def elasticsearch_status() -> str:
    """Check comprehensive status of Elasticsearch and Kibana Docker containers."""
    try:
        # Get config path and setup manager
        config_path = Path(__file__).parent / "config.json"
        setup_manager = ElasticsearchSetup(config_path)

        # Get detailed container status
        status = setup_manager.get_container_status()

        if "error" in status:
            return f"❌ **Container Status Check Failed!**\n\n🚨 **Error:** {status['error']}\n\n💡 **Troubleshooting:**\n   • Check if Docker is running\n   • Verify Docker daemon is accessible\n   • Ensure proper Docker permissions\n   • Try restarting Docker service"

        # Build comprehensive status message
        message = "📊 **Elasticsearch & Kibana Container Status Report**\n\n"

        # Elasticsearch detailed status
        es_status = status["elasticsearch"]
        message += f"🔍 **Elasticsearch Container** (`{es_status['container_name']}`):\n"
        message += f"   📦 Container Exists: {'✅ Yes' if es_status['exists'] else '❌ No'}\n"
        message += f"   🚀 Container Running: {'✅ Yes' if es_status['running'] else '❌ No'}\n"

        if es_status['running']:
            message += f"   🌐 Access URL: http://localhost:9200\n"
            message += f"   💚 Status: Ready for connections\n"
        elif es_status['exists']:
            message += f"   ⚠️ Status: Container exists but not running\n"
            message += f"   💡 Action: Start container or use setup_elasticsearch\n"
        else:
            message += f"   🔧 Status: Container not found\n"
            message += f"   💡 Action: Run setup_elasticsearch to create\n"

        message += f"\n"

        # Kibana detailed status
        kibana_status = status["kibana"]
        message += f"📊 **Kibana Container** (`{kibana_status['container_name']}`):\n"
        message += f"   📦 Container Exists: {'✅ Yes' if kibana_status['exists'] else '❌ No'}\n"
        message += f"   🚀 Container Running: {'✅ Yes' if kibana_status['running'] else '❌ No'}\n"

        if kibana_status['running']:
            message += f"   🌐 Access URL: http://localhost:5601\n"
            message += f"   💚 Status: Dashboard available\n"
        elif kibana_status['exists']:
            message += f"   ⚠️ Status: Container exists but not running\n"
            message += f"   💡 Action: Start container or use setup_elasticsearch\n"
        else:
            message += f"   🔧 Status: Container not found\n"
            message += f"   💡 Action: Run setup_elasticsearch with include_kibana=true\n"

        # Current configuration summary
        config = load_config()
        message += f"\n⚙️ **Current Configuration Settings:**\n"
        message += f"   🏠 Host: {config['elasticsearch']['host']}\n"
        message += f"   🔌 Port: {config['elasticsearch']['port']}\n"
        message += f"   📍 Full URL: http://{config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"

        # Overall system status assessment
        es_ready = es_status['running']
        kibana_ready = kibana_status['running']

        message += f"\n🎯 **Overall System Status:**\n"
        if es_ready and kibana_ready:
            message += f"   ✅ **Fully Operational** - Both Elasticsearch and Kibana running\n"
            message += f"   🚀 **Next Steps:** Start indexing documents and using search\n"
        elif es_ready and not kibana_ready:
            message += f"   🟡 **Partially Ready** - Elasticsearch running, Kibana stopped\n"
            message += f"   💡 **Suggestion:** Elasticsearch is functional, Kibana optional for visualization\n"
        elif not es_ready and kibana_ready:
            message += f"   🔴 **Incomplete Setup** - Kibana running but Elasticsearch stopped\n"
            message += f"   ⚠️ **Action Required:** Start Elasticsearch for system to function\n"
        else:
            message += f"   🔴 **System Down** - Both services stopped\n"
            message += f"   🛠️ **Action Required:** Run setup_elasticsearch to start services\n"

        return message

    except ImportError as e:
        return f"❌ Module Error: Missing Elasticsearch setup dependency\n🔍 Details: {str(e)}\n💡 Ensure ElasticsearchSetup module is properly installed"
    except FileNotFoundError as e:
        return f"❌ Configuration Error: Required config file not found\n🔍 Details: {str(e)}\n💡 Check that config.json exists in the source directory"
    except Exception as e:
        return _format_admin_error(e, "check Elasticsearch status", "Docker container status monitoring")


# ================================
# TOOL 7: SERVER_STATUS
# ================================

@app.tool(
    description="Check current server status, version, and available updates with comprehensive system information",
    tags={"admin", "server", "status", "version", "updates"}
)
async def server_status(
    check_updates: Annotated[bool, Field(description="Check for available updates from PyPI")] = True
) -> str:
    """Check comprehensive server status including version, installation method, and update availability."""
    try:
        # Get current version with multiple fallback methods
        current_version = "unknown"
        version_source = "fallback"

        try:
            # Method 1: Standard package metadata (for uvx installs)
            import importlib.metadata
            current_version = importlib.metadata.version("agent-knowledge-mcp")
            version_source = "importlib.metadata"
        except Exception:
            # Method 2: Local module version (for development)
            try:
                from . import __version__
                current_version = __version__
                version_source = "local module"
            except ImportError:
                try:
                    from src import __version__
                    current_version = __version__
                    version_source = "src module"
                except ImportError:
                    # Keep fallback
                    pass

        # Get current configuration
        config = load_config()
        server_status = "running"

        # Detect installation method with comprehensive checking
        installation_method = "unknown"
        installation_details = ""

        try:
            # Check if installed via uvx (UV tool management)
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "agent-knowledge-mcp" in result.stdout:
                installation_method = "uvx"
                installation_details = "Installed via UV tool management"
            elif result.returncode == 0:
                installation_method = "development"
                installation_details = "Running in development mode"
            else:
                installation_method = "other"
                installation_details = "Non-uvx installation detected"
        except FileNotFoundError:
            installation_method = "no-uv"
            installation_details = "UV not found - likely pip install or development"
        except subprocess.TimeoutExpired:
            installation_method = "timeout"
            installation_details = "UV tool check timed out"
        except Exception as e:
            installation_method = "error"
            installation_details = f"Error checking: {str(e)}"

        # Check for updates with comprehensive PyPI integration
        latest_version = None
        update_available = False
        update_check_status = "not_checked"
        recommendation = ""

        if check_updates:
            try:
                import requests
                response = requests.get(
                    "https://pypi.org/pypi/agent-knowledge-mcp/json",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data["info"]["version"]
                    update_check_status = "success"

                    # Enhanced version comparison
                    if latest_version != current_version and current_version != "unknown":
                        update_available = True
                        if installation_method == "uvx":
                            recommendation = f"🔄 **Update Available!** Version {latest_version} ready\n   💡 Use server_upgrade tool to update automatically"
                        else:
                            recommendation = f"🔄 **Update Available!** Version {latest_version} ready\n   ⚠️ Manual update required (not uvx installation)"
                    elif current_version == "unknown":
                        recommendation = f"📦 Latest version: {latest_version}\n   ⚠️ Cannot compare - current version unknown"
                else:
                    update_check_status = f"http_error_{response.status_code}"
                    latest_version = f"HTTP {response.status_code} error"
            except ImportError:
                update_check_status = "missing_requests"
                latest_version = "requests module not available"
            except requests.exceptions.Timeout:
                update_check_status = "timeout"
                latest_version = "PyPI request timed out"
            except requests.exceptions.ConnectionError:
                update_check_status = "connection_error"
                latest_version = "No internet connection"
            except Exception as e:
                update_check_status = "error"
                latest_version = f"Error: {str(e)}"
        else:
            update_check_status = "skipped"
            latest_version = "Update check disabled"

        # Build comprehensive status message
        message = "🖥️ **Server Status Report**\n\n"

        # Version information
        message += f"📍 **Version Information:**\n"
        message += f"   🏷️ Current Version: {current_version}\n"
        message += f"   📖 Version Source: {version_source}\n"
        if latest_version:
            message += f"   📦 Latest Version: {latest_version}\n"
            message += f"   🔍 Update Check: {update_check_status}\n"

        # Installation details
        message += f"\n🔧 **Installation Information:**\n"
        message += f"   📥 Method: {installation_method}\n"
        message += f"   📝 Details: {installation_details}\n"

        # System status
        message += f"\n⚡ **System Status:**\n"
        message += f"   🚀 Server: {server_status}\n"
        message += f"   🗂️ Elasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"

        # Configuration summary
        if "server" in config:
            server_config = config["server"]
            message += f"   📛 Server Name: {server_config.get('name', 'AgentKnowledgeMCP')}\n"
            message += f"   🏷️ Config Version: {server_config.get('version', '1.0.0')}\n"

        # Update recommendations
        if update_available and recommendation:
            message += f"\n✨ **Update Available:**\n   {recommendation}\n"
        elif check_updates and not update_available and update_check_status == "success":
            message += f"\n✅ **System Up to Date:**\n   You are running the latest version!\n"

        # Installation method guidance
        if installation_method not in ["uvx"]:
            message += f"\n💡 **Management Tools Notice:**\n"
            message += f"   ⚠️ Server management tools (upgrade) require uvx installation\n"
            message += f"   🛠️ Install via: `uvx install agent-knowledge-mcp`\n"
            message += f"   📚 Current method ({installation_method}) has limited management capabilities\n"

        return message

    except ImportError as e:
        return f"❌ Module Error: Missing required dependency\n🔍 Details: {str(e)}\n💡 Some status features require additional modules (requests for update checks)"
    except subprocess.TimeoutExpired:
        return f"❌ Timeout Error: System command timed out\n💡 Installation method detection failed - try again or check system performance"
    except Exception as e:
        return _format_admin_error(e, "check server status", "version detection and update checking")


def intelligent_config_merge(current_config: Dict[str, Any], backup_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligently merge configuration after server upgrade.

    Logic:
    - Some sections use LATEST config (server, schema, version info)
    - Some sections use INTELLIGENT merge (user settings like security, elasticsearch)
    - Ignore deprecated features (keys only in backup - these were removed)

    Args:
        current_config: New configuration from server upgrade
        backup_config: User's previous configuration (backup)

    Returns:
        Merged configuration with appropriate merge strategy per section
    """
    # Sections that should always use the LATEST config (no merge)
    # These contain version info, schema definitions, server settings that must be current
    LATEST_CONFIG_SECTIONS = {
        "server",           # Version info, new server settings
        "schema",           # Schema definitions must be current
        "version",          # Version tracking
        "defaults",         # Default values must be current
        "required_fields",  # Schema requirements must be current
        "field_types"       # Schema field types must be current
    }

    # Sections that should use INTELLIGENT merge (preserve user settings)
    # These contain user customizations that should be preserved
    INTELLIGENT_MERGE_SECTIONS = {
        "security",         # User's paths and security settings
        "elasticsearch",    # User's ES connection settings
        "logging",          # User's logging preferences
        "features",         # User's feature toggles
        "custom"            # Any custom user sections
    }

    def merge_recursive(current: Dict[str, Any], backup: Dict[str, Any], section_name: str = None) -> Dict[str, Any]:
        result = current.copy()  # Start with current config (includes new features)

        for key, backup_value in backup.items():
            if key in current:
                current_value = current[key]

                # Check if this is a top-level section that needs special handling
                if section_name is None and key in LATEST_CONFIG_SECTIONS:
                    # Use latest config for these sections - no merge
                    result[key] = current_value
                    continue
                elif section_name is None and key in INTELLIGENT_MERGE_SECTIONS:
                    # Use intelligent merge for these sections
                    if isinstance(current_value, dict) and isinstance(backup_value, dict):
                        result[key] = merge_recursive(current_value, backup_value, key)
                    else:
                        result[key] = backup_value  # Preserve user setting
                    continue
                elif section_name is None and isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # For unknown top-level sections, default to intelligent merge
                    result[key] = merge_recursive(current_value, backup_value, key)
                    continue

                # For nested values within a section, merge normally
                if isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = merge_recursive(current_value, backup_value, section_name)
                else:
                    # Use backup value (user's setting) for intelligent merge sections
                    if section_name in INTELLIGENT_MERGE_SECTIONS or section_name is None:
                        result[key] = backup_value
                    else:
                        # For latest config sections, keep current value
                        result[key] = current_value
            else:
                # Key only exists in backup
                # For intelligent merge sections, preserve user settings even if not in current config
                # BUT only if they're not clearly deprecated (e.g., "old_", "deprecated_", "legacy_")
                if section_name in INTELLIGENT_MERGE_SECTIONS:
                    # Check if this looks like a deprecated setting
                    is_deprecated = any(key.startswith(prefix) for prefix in ["old_", "deprecated_", "legacy_"])
                    if not is_deprecated:
                        result[key] = backup_value
                # For latest config sections or deprecated keys, ignore (don't include)

        return result

    return merge_recursive(current_config, backup_config)


# ================================
# TOOL 8: SERVER_UPGRADE
# ================================

@app.tool(
    description="Upgrade this MCP server when installed via uvx with automatic configuration backup and restoration",
    tags={"admin", "server", "upgrade", "uvx", "maintenance"}
)
async def server_upgrade() -> str:
    """Upgrade the MCP server when installed via uvx with comprehensive backup and restoration."""
    try:
        # Check if uv is available
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "❌ **UV Tool Required!**\n\n🚨 **Error:** UV is not installed or not available in PATH\n\n🛠️ **Installation Steps:**\n   1. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`\n   2. Restart terminal or reload shell profile\n   3. Verify installation: `uv --version`\n   4. Try server upgrade again\n\n💡 **Alternative:** Manual upgrade via pip/conda if not using uvx"
        except subprocess.TimeoutExpired:
            return "❌ **UV Command Timeout!**\n\n⏱️ **Error:** UV version check timed out\n\n💡 **Troubleshooting:**\n   • Check system performance and UV installation\n   • Try running `uv --version` manually in terminal\n   • Restart terminal and try again\n   • Consider manual upgrade if UV issues persist"

        # Check if this package is installed via uvx
        try:
            list_result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if "agent-knowledge-mcp" not in list_result.stdout:
                message = "⚠️ **UV Tool Installation Required!**\n\n"
                message += "🚨 **Notice:** Agent Knowledge MCP server is not installed via uv tool\n\n"
                message += "📦 **This tool only works when the server was installed using:**\n"
                message += "   ```bash\n   uv tool install agent-knowledge-mcp\n   ```\n\n"
                message += f"🔍 **Current UV tool packages:**\n"
                if list_result.stdout.strip():
                    message += f"   {list_result.stdout.strip()}\n\n"
                else:
                    message += "   None installed\n\n"
                message += "💡 **Installation Options:**\n"
                message += "   • Install via uvx: `uv tool install agent-knowledge-mcp`\n"
                message += "   • Upgrade manually if using pip/conda installation\n"
                message += "   • Contact support for installation guidance"
                return message
        except subprocess.TimeoutExpired:
            return "❌ **UV Tool Check Timeout!**\n\n⏱️ **Error:** UV tool list command timed out\n\n💡 **Troubleshooting:**\n   • System performance issues may be affecting UV\n   • Try running `uv tool list` manually in terminal\n   • Check for disk space and memory availability\n   • Consider system restart if problems persist"
        except Exception as e:
            return f"⚠️ **UV Installation Verification Failed!**\n\n🚨 **Error:** Cannot verify uvx installation\n🔍 **Details:** {str(e)}\n\n💡 **Resolution:**\n   • Ensure agent-knowledge-mcp is installed via uvx\n   • Try: `uv tool install agent-knowledge-mcp`\n   • Verify UV tool is working: `uv tool list`"

        # Step 1: Backup current configuration
        config_path = Path(__file__).parent / "config.json"
        backup_config = None
        backup_status = ""

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
                backup_status = "✅ Configuration backed up for restoration"
            except Exception as e:
                backup_status = f"⚠️ Warning: Could not backup config: {e}"
        else:
            backup_status = "ℹ️ No existing config.json to backup"

        # Get the latest version from PyPI first
        latest_version = None
        version_check_status = ""

        try:
            import requests
            response = requests.get(
                "https://pypi.org/pypi/agent-knowledge-mcp/json",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data["info"]["version"]
                version_check_status = f"📦 Latest version available: {latest_version}"
            else:
                version_check_status = f"⚠️ PyPI check failed: HTTP {response.status_code}"
        except ImportError:
            version_check_status = "⚠️ Warning: requests module not available for version check"
        except Exception as e:
            version_check_status = f"⚠️ Warning: Could not fetch latest version: {e}"

        # Clean UV cache first
        cache_status = ""
        try:
            cache_result = subprocess.run(
                ["uv", "cache", "clean"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if cache_result.returncode == 0:
                cache_status = "🧹 UV cache cleaned successfully"
            else:
                cache_status = f"⚠️ UV cache clean failed: {cache_result.stderr.strip() or 'Unknown error'}"
                # Continue with upgrade even if cache clean fails
        except subprocess.TimeoutExpired:
            cache_status = "⚠️ UV cache clean timed out - continuing with upgrade"
        except Exception as e:
            cache_status = f"⚠️ UV cache clean error: {str(e)} - continuing anyway"

        # Force reinstall with specific version if available
        install_status = ""
        install_output = ""

        try:
            if latest_version:
                install_cmd = ["uv", "tool", "install", f"agent-knowledge-mcp=={latest_version}", "--force"]

                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                # If specific version fails, try without version constraint
                if result.returncode != 0:
                    install_cmd = ["uv", "tool", "install", "agent-knowledge-mcp", "--force"]
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
            else:
                install_cmd = ["uv", "tool", "install", "agent-knowledge-mcp", "--force"]
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

            install_output = result.stdout.strip()

            if result.returncode == 0:
                # Parse installation output to check if upgrade happened
                upgrade_detected = False
                installed_version = "unknown"

                # Look for upgrade indicators in output
                if "+" in install_output and "agent-knowledge-mcp" in install_output:
                    for line in install_output.split('\n'):
                        if line.strip().startswith('+ agent-knowledge-mcp=='):
                            installed_version = line.split('==')[1].strip()
                            upgrade_detected = True
                            break
                        elif line.strip().startswith('- agent-knowledge-mcp==') and '+ agent-knowledge-mcp==' in install_output:
                            upgrade_detected = True

                if upgrade_detected:
                    install_status = f"🎉 Agent Knowledge MCP server upgraded successfully!"
                    if installed_version != "unknown":
                        install_status += f"\n📦 Installed version: {installed_version}"
                else:
                    install_status = f"🔄 Agent Knowledge MCP server reinstalled successfully!"
            else:
                # Installation failed
                error_msg = f"❌ **Installation Failed!**\n\n"
                error_msg += f"🚨 **Return code:** {result.returncode}\n"
                if result.stderr.strip():
                    error_msg += f"📝 **Error output:**\n```\n{result.stderr.strip()}\n```\n"
                if result.stdout.strip():
                    error_msg += f"📄 **Standard output:**\n```\n{result.stdout.strip()}\n```\n"

                error_msg += f"\n🛠️ **Manual Recovery:**\n"
                error_msg += f"   ```bash\n   uv cache clean && uv tool install agent-knowledge-mcp --force\n   ```\n"
                error_msg += f"\n💡 **Additional Help:**\n"
                error_msg += f"   • Check UV tool is properly configured\n"
                error_msg += f"   • Verify network connectivity to PyPI\n"
                error_msg += f"   • Try manual installation if issues persist"

                return error_msg

        except subprocess.TimeoutExpired:
            return "❌ **Installation Timeout!**\n\n⏱️ **Error:** Installation process timed out (120s limit)\n\n🛠️ **Resolution:**\n   • Network connectivity may be slow\n   • Try manual installation: `uv tool install agent-knowledge-mcp --force`\n   • Check system performance and disk space\n   • Consider increasing timeout for large downloads"

        # Step 3: Restore configuration intelligently
        config_restoration_status = ""

        if backup_config:
            try:
                # Check if config.json exists after upgrade (it should)
                if config_path.exists():
                    # Load new config from upgrade
                    with open(config_path, 'r', encoding='utf-8') as f:
                        new_config = json.load(f)

                    # Perform intelligent merge
                    merged_config = intelligent_config_merge(new_config, backup_config)

                    # Write merged config back
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(merged_config, f, indent=2, ensure_ascii=False)

                    # Reload configuration after restore
                    config = load_config()

                    # Reinitialize components with restored config
                    init_security(config["security"]["allowed_base_directory"])
                    init_elasticsearch(config)
                    reset_es_client()

                    config_restoration_status = "🔧 Configuration automatically restored with intelligent merge!\n"
                    config_restoration_status += "   • Your custom settings preserved\n"
                    config_restoration_status += "   • New features from upgrade included\n"
                    config_restoration_status += "   • Deprecated settings removed"
                else:
                    config_restoration_status = "⚠️ New config.json not found after upgrade"

            except Exception as e:
                config_restoration_status = f"⚠️ Warning: Could not restore configuration: {e}\n"
                config_restoration_status += "💡 Use 'get_config' to review and 'update_config' to customize"
        else:
            config_restoration_status = "ℹ️ No previous configuration to restore"

        # Build comprehensive success message
        message = "🎉 **Server Upgrade Completed Successfully!**\n\n"

        # Upgrade summary
        message += f"📋 **Upgrade Summary:**\n"
        message += f"   {backup_status}\n"
        message += f"   {version_check_status}\n"
        message += f"   {cache_status}\n"
        message += f"   {install_status}\n"
        message += f"   {config_restoration_status}\n\n"

        # Client restart instructions
        message += f"🔄 **Important: Restart Your MCP Client**\n\n"
        message += f"To use the updated version, please restart your MCP client:\n"
        message += f"   • **VS Code:** Reload window (Ctrl/Cmd + Shift + P → 'Reload Window')\n"
        message += f"   • **Claude Desktop:** Restart the application\n"
        message += f"   • **Other clients:** Restart/reload the client application\n\n"

        # Installation output details
        if install_output:
            message += f"📄 **Installation Output:**\n```\n{install_output}\n```\n\n"

        # Final success confirmation
        message += f"✅ **Upgrade Complete!** Restart your client to use the latest version."

        return message

    except ImportError as e:
        return f"❌ Module Error: Missing required dependency\n🔍 Details: {str(e)}\n💡 Some upgrade features require additional modules (requests for version checking, json for configuration management)"
    except subprocess.TimeoutExpired:
        return f"❌ Timeout Error: Upgrade process timed out\n💡 Network connectivity or system performance issues - try manual upgrade or check system resources"
    except Exception as e:
        return _format_admin_error(e, "upgrade server", "uvx package management and configuration restoration")


def extract_section_content(full_content: str, section: str) -> str:
    """Extract specific section from full guide content."""
    lines = full_content.split('\n')
    section_lines = []
    in_section = False

    # Section mappings
    section_headers = {
        "quick_start": "## 🚀 **Quick Start",
        "workflows": "## 📚 **Core Workflows",
        "advanced": "## ⚡ **Power Commands",
        "troubleshooting": "## 🔧 **Troubleshooting Guide",
        "best_practices": "## 🎓 **Best Practices"
    }

    target_header = section_headers.get(section)
    if not target_header:
        return full_content  # Return full content if section not found

    # Always include the prompting instructions at the beginning
    prompt_instruction = """# 🚀 AgentKnowledgeMCP - Complete Usage Guide

## ⚡ **Before Getting Started - IMPORTANT!**

> 💡 **Pro Tip for Maximum Effectiveness**: 
> For the most effective experience with this MCP server, you should attach this instructions file to each prompt:
> 
> 📚 **https://github.com/itshare4u/AgentKnowledgeMCP/blob/main/.github/copilot-instructions.md**
> 
> This file contains guidelines that help AI assistants understand and use the MCP server optimally!

---

"""

    # Extract specific section
    for line in lines:
        if target_header in line:
            in_section = True
            section_lines.append(line)
        elif in_section and line.startswith('## ') and target_header not in line:
            break  # Stop when we reach the next section
        elif in_section:
            section_lines.append(line)

    if section_lines:
        return prompt_instruction + '\n'.join(section_lines)
    else:
        return full_content  # Return full content if section extraction fails


# ================================
# TOOL 10: ASK_USER_ADVICE
# ================================

@app.tool(
    description="Ask user for advice when agent encounters uncertainty, problems, or needs guidance. Use this when you're unsure about something or need human input to proceed properly.",
    tags={"admin", "user", "advice", "guidance", "help", "interaction"}
)
async def ask_user_advice(
    problem_description: Annotated[str, Field(description="Clear description of the problem or uncertainty you're facing")] = "",
    context_information: Annotated[Optional[str], Field(description="Additional context or information that might help the user understand the situation")] = None,
    specific_question: Annotated[Optional[str], Field(description="Specific question you want to ask the user")] = None,
    options_considered: Annotated[Optional[str], Field(description="Options or approaches you've already considered")] = None,
    urgency_level: Annotated[str, Field(description="Urgency level of the advice needed")] = "normal",
    ctx: Context = None  # Type-hinted Context for dependency injection
) -> str:
    """
    Ask user for advice when agent encounters uncertainty or problems.
    
    This tool allows agents to interact with users when they need guidance,
    encounter unexpected situations, or are uncertain about the best course of action.
    """
    try:
        # FastMCP automatically injects Context as ctx parameter
        if not ctx:
            return "❌ **Context Error**: Cannot access FastMCP context for user interaction\n💡 This tool requires an active FastMCP context to communicate with user"
        
        # Build the advice request message
        urgency_icon = {
            "low": "💭",
            "normal": "🤔", 
            "high": "⚠️",
            "urgent": "🚨"
        }.get(urgency_level.lower(), "🤔")

        advice_message = f"{urgency_icon} **Agent Advice Request** {urgency_icon}\n\n"

        advice_message = f"{urgency_icon} **Agent Advice Request** {urgency_icon}\n\n"
        
        if problem_description:
            advice_message += f"🔍 **Problem/Uncertainty:**\n{problem_description}\n\n"
        
        if context_information:
            advice_message += f"📋 **Context:**\n{context_information}\n\n"
        
        if specific_question:
            advice_message += f"❓ **Specific Question:**\n{specific_question}\n\n"
        
        if options_considered:
            advice_message += f"⚙️ **Options I've Considered:**\n{options_considered}\n\n"
        
        # Set urgency-based timeout
        timeout_minutes = {
            "low": 30,
            "normal": 15,
            "high": 10,
            "urgent": 5
        }.get(urgency_level.lower(), 15)
        
        advice_message += f"💡 **Your advice would be very helpful!**\n"
        advice_message += f"🕒 Please respond within {timeout_minutes} minutes if possible.\n\n"
        advice_message += f"**What would you recommend I do?**"

        # Request advice from user using FastMCP elicitation
        result = await ctx.elicit(
            message=advice_message,
            response_type=str
        )

        # Format the user's advice response
        if result and hasattr(result, 'data') and result.data:
            user_advice = result.data.strip()
            
            response_message = f"✅ **User Advice Received!**\n\n"
            response_message += f"👤 **User's Response:**\n{user_advice}\n\n"
            response_message += f"💡 **Next Steps:**\n"
            response_message += f"   • Follow the user's guidance\n"
            response_message += f"   • Document any lessons learned\n"
            response_message += f"   • Update knowledge base if applicable\n"
            response_message += f"   • Thank the user for their help!\n\n"
            response_message += f"🎯 **Agent Action:** Proceed according to user's advice above"
            
            return response_message
        
        elif result and hasattr(result, 'action') and result.action == "decline":
            return f"ℹ️ **User Declined to Provide Advice**\n\n" \
                   f"📍 **Status:** User chose not to provide advice at this time\n\n" \
                   f"💡 **Agent Options:**\n" \
                   f"   • Proceed with your best judgment\n" \
                   f"   • Use available documentation/knowledge base\n" \
                   f"   • Try a conservative/safe approach\n" \
                   f"   • Ask again later if the issue persists\n\n" \
                   f"🤝 **Note:** Respect user's choice and proceed independently"
        
        else:
            return f"⚠️ **No Response Received**\n\n" \
                   f"📍 **Status:** User didn't respond within the expected timeframe\n\n" \
                   f"💡 **Agent Guidance:**\n" \
                   f"   • Proceed with your best available knowledge\n" \
                   f"   • Use conservative approach to avoid issues\n" \
                   f"   • Document the situation for future reference\n" \
                   f"   • Consider asking for advice again later if needed\n\n" \
                   f"🎯 **Recommendation:** Make the safest choice available"

    except Exception as e:
        return _format_admin_error(e, "request user advice", f"problem: {problem_description[:100]}...")


# ================================
# TOOL 11: RESET_CONFIG
# ================================

@app.tool(
    description="Reset config.json to defaults from config.default.json (manual reset - overwrites current config)",
    tags={"admin", "config", "reset", "default", "restore"}
)
async def reset_config() -> str:
    """Reset configuration to defaults, creating backup of current config."""
    try:
        import shutil
        import time
        from src.config.config import load_config  # Use the working config loader
        
        # Use same approach as working update_config function  
        script_dir = Path(__file__).parent.parent  # /src directory
        config_path = script_dir / "config.json"
        default_config_path = script_dir / "config.default.json"
        
        # Verify default config exists
        if not default_config_path.exists():
            return f"❌ **Default Configuration File Not Found!**\n\n🚨 **Error:** Cannot find {default_config_path}\n📁 **Absolute Path:** {default_config_path.absolute()}\n\n🛠️ **Resolution Steps:**\n   1. Verify config.default.json exists in src directory\n   2. Check if file was accidentally deleted or moved\n   3. Try reinstalling AgentKnowledgeMCP package\n\n💡 **Manual Reset:** Copy config.default.json to config.json manually"

        # Create backup of current config if it exists
        backup_created = False
        backup_path = None
        backup_status = ""

        if config_path.exists():
            try:
                import time
                timestamp = int(time.time())
                backup_path = config_path.with_name(f"config.backup.{timestamp}.json")

                import shutil
                shutil.copy2(config_path, backup_path)
                backup_created = True
                backup_status = f"✅ Current configuration backed up as: {backup_path.name}"
            except PermissionError:
                return "❌ **Backup Creation Failed!**\n\n🚨 **Error:** Insufficient permissions to create backup file\n📁 **Target:** config.backup.[timestamp].json\n\n🛠️ **Resolution:**\n   • Check file system permissions for src directory\n   • Ensure user has write access to configuration directory\n   • Try running with elevated permissions if necessary\n   • Verify sufficient disk space for backup creation"
            except Exception as e:
                return f"❌ **Backup Creation Error!**\n\n🚨 **Error:** Cannot create backup of current configuration\n🔍 **Details:** {str(e)}\n\n💡 **Options:**\n   • Check file system permissions and disk space\n   • Try manual backup: copy config.json to config.backup.manual.json\n   • Proceed with caution if backup creation fails"
        else:
            backup_status = "ℹ️ No existing config.json to backup"

        # Copy config.default.json to config.json (overwrite)
        try:
            import shutil
            shutil.copy2(default_config_path, config_path)
        except PermissionError:
            return "❌ **Configuration Reset Failed!**\n\n🚨 **Error:** Insufficient permissions to overwrite config.json\n📁 **Target:** config.json\n\n🛠️ **Resolution:**\n   • Check file permissions for config.json\n   • Ensure user has write access to configuration file\n   • Try running with elevated permissions if necessary\n   • Verify config.json is not locked by another process"
        except Exception as e:
            return f"❌ **File Copy Error!**\n\n🚨 **Error:** Cannot copy default configuration\n🔍 **Details:** {str(e)}\n\n🛠️ **Manual Reset Steps:**\n   1. Copy contents of config.default.json\n   2. Paste into config.json (overwrite existing content)\n   3. Save file and try reloading configuration\n   4. Check file permissions and disk space if issues persist"

        # Reload configuration after reset
        try:
            config = load_config()
        except Exception as e:
            return f"❌ **Configuration Reload Failed!**\n\n🚨 **Error:** Reset completed but cannot load new configuration\n🔍 **Details:** {str(e)}\n\n⚠️ **Status:** config.json has been reset but system components not reinitialized\n\n🛠️ **Recovery:**\n   • Use reload_config tool to reinitialize components\n   • Check config.json syntax and structure\n   • Verify all required configuration sections are present"

        # Reinitialize components with reset config
        component_status = []

        try:
            init_security(config["security"]["allowed_base_directory"])
            component_status.append("✅ Security component reinitialized")
        except Exception as e:
            component_status.append(f"⚠️ Security initialization failed: {str(e)}")

        try:
            init_elasticsearch(config)
            reset_es_client()
            component_status.append("✅ Elasticsearch components reinitialized")
        except Exception as e:
            component_status.append(f"⚠️ Elasticsearch initialization failed: {str(e)}")

        # Build comprehensive success message
        message = "🎉 **Configuration Reset Completed Successfully!**\n\n"

        # Reset summary
        message += f"📋 **Reset Summary:**\n"
        message += f"   {backup_status}\n"
        message += f"   ✅ Configuration reset from config.default.json\n"
        message += f"   🔄 All components reinitialized with default settings\n\n"

        # Component reinitialization status
        message += f"🔧 **Component Status:**\n"
        for status in component_status:
            message += f"   {status}\n"
        message += f"\n"

        # Configuration details
        message += f"📄 **Current Configuration:**\n"
        try:
            message += f"   🔒 Security Base Directory: {config['security']['allowed_base_directory']}\n"
            message += f"   🔍 Elasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"
            if "server" in config:
                server_config = config["server"]
                message += f"   🚀 Server: {server_config.get('name', 'AgentKnowledgeMCP')} v{server_config.get('version', '1.0.0')}\n"
        except Exception as e:
            message += f"   ⚠️ Configuration display error: {str(e)}\n"

        # Next steps guidance
        message += f"\n💡 **Next Steps:**\n"
        message += f"   • Review reset configuration with get_config tool\n"
        message += f"   • Customize settings using update_config tool\n"
        message += f"   • Test system functionality after reset\n"
        if backup_created and backup_path:
            message += f"   • Previous settings available in {backup_path.name}\n"

        # Restore instructions if needed
        if backup_created and backup_path:
            message += f"\n🔄 **Restore Previous Configuration (if needed):**\n"
            message += f"   1. Copy {backup_path.name} to config.json\n"
            message += f"   2. Use reload_config tool to apply restored settings\n"
            message += f"   3. Verify components work with restored configuration\n"

        message += f"\n✅ **System Ready:** Configuration reset complete with default settings active!"

        return message

    except ImportError as e:
        return f"❌ Module Error: Missing required module for configuration reset\n🔍 Details: {str(e)}\n💡 Required modules: shutil (for file operations), time (for backup timestamps)"
    except FileNotFoundError as e:
        return f"❌ File System Error: Required file not found during reset operation\n🔍 Details: {str(e)}\n💡 Check that both config.json and config.default.json exist in src directory"
    except Exception as e:
        return _format_admin_error(e, "reset configuration", "default configuration restore and component reinitialization")


# CLI entry point
def cli_main():
    """CLI entry point for Admin FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Admin FastMCP server...")
    print("⚙️ Tools: get_config, update_config, validate_config, reload_config, setup_elasticsearch, elasticsearch_status, server_status, server_upgrade, ask_user_advice, reset_config")
    print("🎯 Admin-only server - Tools for system management and configuration")

    app.run()

if __name__ == "__main__":
    cli_main()
