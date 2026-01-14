"""
Document schema validation for knowledge base documents.
"""
import json
import re
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Document schema definition will be loaded from config.json
# This allows backup/restore of schema configuration during server upgrades
# NO FALLBACK: Server requires proper config.json with document_schema section

class DocumentValidationError(Exception):
    """Exception raised when document validation fails."""
    pass

def load_document_schema() -> Dict[str, Any]:
    """
    Load document schema from config.json with fallback to config.default.json.
    STRICT MODE with controlled fallback for server upgrades.
    
    Returns:
        Document schema configuration dict
        
    Raises:
        RuntimeError: If both config.json and config.default.json are missing or invalid
    """
    config_path = Path(__file__).parent.parent / "config.json"
    default_config_path = Path(__file__).parent.parent / "config.default.json"
    
    # Check if config.json exists, fallback to default if missing
    if not config_path.exists():
        if default_config_path.exists():
            print("⚠️  Configuration file config.json not found, using config.default.json")
            config_path = default_config_path
        else:
            raise RuntimeError(
                f"❌ Configuration files not found: {config_path} and {default_config_path}\n"
                f"💡 Server requires config.json or config.default.json with document_schema section.\n"
                f"📝 Use 'get_config' tool to view current configuration or create config.json."
            )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"❌ Invalid JSON in config.json: {e}\n"
            f"💡 Fix JSON syntax errors in {config_path}"
        )
    except Exception as e:
        raise RuntimeError(
            f"❌ Could not read config.json: {e}\n"
            f"💡 Check file permissions for {config_path}"
        )
    
    # Check if document_schema section exists
    if "document_schema" not in config:
        raise RuntimeError(
            f"❌ Missing 'document_schema' section in config.json\n"
            f"💡 Add document_schema section to {config_path}\n"
            f"📋 Required sections: {list(config.keys())} + ['document_schema']\n"
            f"🔧 Use 'update_config' tool to add document_schema configuration."
        )
    
    schema_config = config["document_schema"]
    
    # Validate document_schema structure
    required_schema_fields = ["required_fields", "field_types", "priority_values", "source_types"]
    missing_fields = [field for field in required_schema_fields if field not in schema_config]
    
    if missing_fields:
        raise RuntimeError(
            f"❌ Missing required fields in document_schema: {missing_fields}\n"
            f"💡 document_schema must contain: {required_schema_fields}\n"
            f"🔧 Use 'update_config' tool to fix document_schema configuration."
        )
    
    # Convert string type names to actual types for field_types
    if "field_types" in schema_config:
        converted_types = {}
        type_mapping = {
            "str": str,
            "list": list,
            "int": int,
            "float": float,
            "bool": bool
        }
        
        for field, type_name in schema_config["field_types"].items():
            if isinstance(type_name, str) and type_name in type_mapping:
                converted_types[field] = type_mapping[type_name]
            else:
                # Invalid type name - this is an error
                raise RuntimeError(
                    f"❌ Invalid field type '{type_name}' for field '{field}'\n"
                    f"💡 Valid types: {list(type_mapping.keys())}\n"
                    f"🔧 Fix field_types in document_schema configuration."
                )
        
        schema_config["field_types"] = converted_types
    
    print("✅ Document schema loaded from config.json")
    return schema_config

def load_validation_config() -> Dict[str, Any]:
    """
    Load validation configuration from config.json with fallback to config.default.json.
    STRICT MODE with controlled fallback for server upgrades.
    
    Returns:
        Validation configuration dict
        
    Raises:
        RuntimeError: If both config files are missing or document_validation section is missing
    """
    config_path = Path(__file__).parent.parent / "config.json"
    default_config_path = Path(__file__).parent.parent / "config.default.json"
    
    # Check if config.json exists, fallback to default if missing
    if not config_path.exists():
        if default_config_path.exists():
            print("⚠️  Configuration file config.json not found, using config.default.json")
            config_path = default_config_path
        else:
            raise RuntimeError(
                f"❌ Configuration files not found: {config_path} and {default_config_path}\n"
                f"💡 Server requires config.json or config.default.json with document_validation section."
            )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Could not load config.json: {e}")
    
    if "document_validation" not in config:
        raise RuntimeError(
            f"❌ Missing 'document_validation' section in config.json\n"
            f"💡 Add document_validation section to {config_path}\n"
            f"🔧 Use 'update_config' tool to add document_validation configuration."
        )
    
    validation_config = config["document_validation"]
    
    # Validate boolean fields
    bool_fields = ["strict_schema_validation", "allow_extra_fields", "required_fields_only", "auto_correct_paths"]
    for field in bool_fields:
        if field in validation_config:
            # Handle string boolean values like "false"
            if isinstance(validation_config[field], str):
                if validation_config[field].lower() in ["true", "false"]:
                    validation_config[field] = validation_config[field].lower() == "true"
                else:
                    raise RuntimeError(
                        f"❌ Invalid boolean value '{validation_config[field]}' for {field}\n"
                        f"💡 Use true/false or 'true'/'false' for boolean fields"
                    )
            elif not isinstance(validation_config[field], bool):
                raise RuntimeError(
                    f"❌ Field '{field}' must be boolean, got {type(validation_config[field])}"
                )
    
    return validation_config

def validate_document_structure(document: Dict[str, Any], base_directory: str = None, is_knowledge_doc: bool = True) -> Dict[str, Any]:
    """
    Validate document structure against schema with strict mode support.
    
    Args:
        document: Document to validate
        base_directory: Base directory for relative path conversion
        is_knowledge_doc: Whether this is a knowledge base document (default: True)
        
    Returns:
        Validated and normalized document
        
    Raises:
        DocumentValidationError: If validation fails
    """
    errors = []
    validation_config = load_validation_config()
    document_schema = load_document_schema()
    
    # For knowledge base documents, check the full schema
    if is_knowledge_doc:
        # Check for extra fields if strict validation is enabled
        if validation_config.get("strict_schema_validation", False) and not validation_config.get("allow_extra_fields", True):
            allowed_fields = set(document_schema["required_fields"])
            document_fields = set(document.keys())
            extra_fields = document_fields - allowed_fields
            
            if extra_fields:
                errors.append(f"Extra fields not allowed in strict mode: {', '.join(sorted(extra_fields))}. Allowed fields: {', '.join(sorted(allowed_fields))}")
    else:
        # For non-knowledge documents, only check for extra fields if strict validation is enabled
        if validation_config.get("strict_schema_validation", False) and not validation_config.get("allow_extra_fields", True):
            # For non-knowledge docs, we don't have a predefined schema, so just enforce no extra fields beyond basic ones
            # This is a more lenient check - you might want to customize this based on your needs
            errors.append("Strict schema validation is enabled. Extra fields are not allowed for custom documents.")
    
    # Check required fields only for knowledge base documents
    if is_knowledge_doc:
        required_fields = document_schema["required_fields"]
        if validation_config.get("required_fields_only", False):
            # Only check fields that are actually required
            for field in required_fields:
                if field not in document:
                    errors.append(f"Missing required field: {field}")
        else:
            # Check all fields in schema
            for field in required_fields:
                if field not in document:
                    errors.append(f"Missing required field: {field}")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    # For knowledge base documents, perform detailed validation
    if is_knowledge_doc:
        # Validate field types
        for field, expected_type in document_schema["field_types"].items():
            if field in document:
                if not isinstance(document[field], expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}, got {type(document[field]).__name__}")
        
        # NEW: Validate content length
        if document.get("content"):
            content = document["content"]
            
            # Check for empty content
            if not content.strip():
                errors.append("Content cannot be empty or contain only whitespace")
        
        # Validate priority values
        if document.get("priority") not in document_schema["priority_values"]:
            errors.append(f"Priority must be one of {document_schema['priority_values']}, got '{document.get('priority')}'")
        
        # Validate source_type
        if document.get("source_type") not in document_schema["source_types"]:
            errors.append(f"Source type must be one of {document_schema['source_types']}, got '{document.get('source_type')}'")
        
        # Validate ID format (should be alphanumeric with hyphens)
        if document.get("id") and not re.match(r'^[a-zA-Z0-9-_]+$', document["id"]):
            errors.append("ID must contain only alphanumeric characters, hyphens, and underscores")
        
        # Validate timestamp format
        if document.get("last_modified"):
            try:
                datetime.fromisoformat(document["last_modified"].replace('Z', '+00:00'))
            except ValueError:
                errors.append("last_modified must be in ISO 8601 format (e.g., '2025-01-04T10:30:00Z')")
        
        # Validate tags (must be non-empty strings)
        if document.get("tags"):
            for i, tag in enumerate(document["tags"]):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(f"Tag at index {i} must be a non-empty string")
        
        # Validate related documents (must be strings)
        if document.get("related"):
            for i, related_id in enumerate(document["related"]):
                if not isinstance(related_id, str) or not related_id.strip():
                    errors.append(f"Related document ID at index {i} must be a non-empty string")
        
        # Validate key_points (must be non-empty strings)
        if document.get("key_points"):
            for i, point in enumerate(document["key_points"]):
                if not isinstance(point, str) or not point.strip():
                    errors.append(f"Key point at index {i} must be a non-empty string")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    return document

def generate_document_id(title: str, source_type: str = "markdown") -> str:
    """
    Generate a document ID from title.
    
    Args:
        title: Document title
        source_type: Type of source document
        
    Returns:
        Generated ID
    """
    # Load schema to get valid source types
    document_schema = load_document_schema()
    valid_source_types = document_schema.get("source_types", ["markdown", "code", "config", "documentation", "tutorial"])
    
    # Validate source_type
    if source_type not in valid_source_types:
        source_type = "markdown"  # Default fallback
    
    # Convert title to lowercase, replace spaces with hyphens
    base_id = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    base_id = re.sub(r'\s+', '-', base_id.strip())
    
    # Add source type prefix
    type_prefix = {
        "markdown": "md",
        "code": "code", 
        "config": "cfg",
        "documentation": "doc",
        "tutorial": "tut"
    }.get(source_type, "doc")
    
    return f"{type_prefix}-{base_id}"

def create_document_template(
    title: str,
    priority: str = "medium",
    source_type: str = "markdown",
    tags: Optional[List[str]] = None,
    summary: str = "",
    key_points: Optional[List[str]] = None,
    related: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a document template with proper structure.
    
    Args:
        title: Document title
        priority: Priority level (high/medium/low)
        source_type: Type of source
        tags: List of tags
        summary: Brief description
        key_points: List of key points
        related: List of related document IDs
        
    Returns:
        Properly structured document
    """
    document = {
        "id": generate_document_id(title, source_type),
        "title": title,
        "summary": summary or f"Brief description of {title}",
        "content": "",  # Will be filled with actual content
        "last_modified": datetime.now().isoformat() + "Z",
        "priority": priority,
        "tags": tags or [],
        "related": related or [],
        "source_type": source_type,
        "key_points": key_points or []
    }
    
    return validate_document_structure(document)

def get_example_document(context: str = "general") -> Dict[str, Any]:
    """
    Generate an example document with proper format.
    
    Args:
        context: Context for the example (general, jwt, api, config, etc.)
        
    Returns:
        Example document structure
    """
    examples = {
            "id": "doc-example-document",
            "title": "Example Document",
            "summary": "Brief description of the document content",
            "content": "This is the main content of the document. It can contain detailed information, explanations, code examples, or any relevant text content. Content should be meaningful and well-structured.",
            "last_modified": "2025-07-04T16:00:00Z",
            "priority": "medium",
            "tags": ["example", "template"],
            "related": [],
            "source_type": "markdown",
            "key_points": ["Key point 1", "Key point 2"]
    }

    return examples


def format_validation_error(error: DocumentValidationError, context: str = "general") -> str:
    """
    Format validation error with example and requirements.
    
    Args:
        error: The validation error
        context: Context for example selection
        
    Returns:
        Formatted error message with example
    """
    example_doc = get_example_document(context)
    document_schema = load_document_schema()
    
    error_message = f"❌ Document validation failed!\n\n{str(error)}\n\n"
    error_message += "📋 Required fields and format:\n"
    
    # Show requirements
    error_message += f"• Required fields: {', '.join(document_schema['required_fields'])}\n"
    error_message += f"• Priority values: {', '.join(document_schema['priority_values'])}\n"
    error_message += f"• Source types: {', '.join(document_schema['source_types'])}\n"
    error_message += f"• ID format: alphanumeric, hyphens, underscores only\n"
    error_message += f"• Timestamp format: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)\n\n"
    
    # Show example
    error_message += "📄 Example document format:\n"
    error_message += json.dumps(example_doc, indent=2, ensure_ascii=False)
    
    return error_message
