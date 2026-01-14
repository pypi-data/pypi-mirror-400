"""
Elasticsearch Batch FastMCP Server
Batch operations extracted from main elasticsearch server.
Handles bulk indexing and batch operations.
"""

from fastmcp import Context
from datetime import datetime
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from ..elasticsearch_client import get_es_client
from ..document_schema import validate_document_structure, DocumentValidationError
from ..elasticsearch_helper import generate_smart_metadata

app = FastMCP(
    name="AgentKnowledgeMCP-Batch",
    version="1.0.0",
    instructions="Elasticsearch batch operations tools"
)


@app.tool(
    description="Batch index all documents from a directory into Elasticsearch with AI-enhanced metadata generation and comprehensive file processing",
    tags={"elasticsearch", "batch", "directory", "index", "bulk", "ai-enhanced"}
)
async def batch_index_directory(
        index: Annotated[str, Field(description="Name of the Elasticsearch index to store the documents")],
        directory_path: Annotated[str, Field(description="Path to directory containing documents to index")],
        file_pattern: Annotated[str, Field(description="File pattern to match (e.g., '*.md', '*.txt', '*')")] = "*.md",
        validate_schema: Annotated[
            bool, Field(description="Whether to validate document structure for knowledge base format")] = True,
        recursive: Annotated[bool, Field(description="Whether to search subdirectories recursively")] = True,
        skip_existing: Annotated[
            bool, Field(description="Skip files that already exist in index (check by filename)")] = False,
        max_file_size: Annotated[
            int, Field(description="Maximum file size in bytes to process", ge=1, le=10485760)] = 1048576,
        # 1MB default
        use_ai_enhancement: Annotated[
            bool, Field(description="Use AI to generate intelligent tags and key points for each document")] = True,
        ctx: Context = None
) -> str:
    """Batch index all documents from a directory into Elasticsearch."""
    try:
        from pathlib import Path
        import os

        # Check directory exists and is valid
        directory = Path(directory_path)
        if not directory.exists():
            return f"❌ Directory not found: {directory_path}\n💡 Check the directory path spelling and location"

        if not directory.is_dir():
            return f"❌ Path is not a directory: {directory_path}\n💡 Provide a directory path, not a file path"

        # Get Elasticsearch client
        es = get_es_client()

        # Find all matching files
        if recursive:
            files = list(directory.rglob(file_pattern))
        else:
            files = list(directory.glob(file_pattern))

        if not files:
            return f"❌ No files found matching pattern '{file_pattern}' in directory: {directory_path}\n💡 Try a different file pattern like '*.txt', '*.json', or '*'"

        # Filter out files that are too large
        valid_files = []
        skipped_size = []
        for file_path in files:
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    if file_size <= max_file_size:
                        valid_files.append(file_path)
                    else:
                        skipped_size.append((file_path, file_size))
                except Exception as e:
                    # Skip files we can't stat
                    continue

        if not valid_files:
            return f"❌ No valid files found (all files too large or inaccessible)\n💡 Increase max_file_size or check file permissions"

        # Check for existing documents if skip_existing is True
        existing_docs = set()
        if skip_existing:
            try:
                # Search for existing documents by titles
                search_body = {
                    "query": {"match_all": {}},
                    "size": 10000,  # Get many docs to check
                    "_source": ["title", "id"]
                }
                existing_result = es.search(index=index, body=search_body)
                for hit in existing_result['hits']['hits']:
                    source = hit.get('_source', {})
                    if 'title' in source:
                        existing_docs.add(source['title'])
                    if 'id' in source:
                        existing_docs.add(source['id'])
            except Exception:
                # If we can't check existing docs, proceed anyway
                pass

        # Process files
        successful = []
        failed = []
        skipped_existing = []

        for file_path in valid_files:
            try:
                file_name = file_path.name
                # Handle files with multiple dots properly (e.g., .post.md, .get.md)
                clean_stem = file_path.name
                if file_path.suffix:
                    clean_stem = file_path.name[:-len(file_path.suffix)]
                title = clean_stem.replace('_', ' ').replace('-', ' ').replace('.', ' ').title()

                # Skip if document with same title already exists in index
                if skip_existing and title in existing_docs:
                    skipped_existing.append(file_name)
                    continue

                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try with different encodings
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        failed.append((file_name, f"Encoding error: {str(e)}"))
                        continue
                except Exception as e:
                    failed.append((file_name, f"Read error: {str(e)}"))
                    continue

                # Create document from file
                relative_path = file_path.relative_to(directory)
                # Handle files with multiple dots (e.g., .post.md, .get.md) by using the full name without final extension
                clean_stem = file_path.name
                if file_path.suffix:
                    clean_stem = file_path.name[:-len(file_path.suffix)]
                doc_id = f"{clean_stem.replace('.', '_')}_{hash(str(relative_path)) % 100000}"  # Create unique ID

                # Initialize basic tags and key points
                base_tags = [
                    "batch-indexed",
                    file_path.suffix[1:] if file_path.suffix else "no-extension",
                    directory.name
                ]

                base_key_points = [
                    f"Content length: {len(content)} characters",
                    f"Source directory: {directory.name}"
                ]

                final_tags = base_tags.copy()
                final_key_points = base_key_points.copy()
                final_summary = f"Document from {file_name}"

                # Use AI enhancement if requested and context is available
                if use_ai_enhancement and ctx and content.strip():
                    try:
                        await ctx.info(f"🤖 Generating AI metadata and smart content for: {file_name}")
                        ai_metadata = await generate_smart_metadata(title, content, ctx)

                        # Merge AI-generated tags with base tags
                        ai_tags = ai_metadata.get("tags", [])
                        for tag in ai_tags:
                            if tag not in final_tags:
                                final_tags.append(tag)

                        # Merge AI-generated key points with base points
                        ai_key_points = ai_metadata.get("key_points", [])
                        for point in ai_key_points:
                            if point not in final_key_points:
                                final_key_points.append(point)

                        # Use AI-generated smart summary and enhanced content
                        ai_summary = ai_metadata.get("smart_summary", "")
                        ai_enhanced_content = ai_metadata.get("enhanced_content", "")

                        if ai_summary:
                            final_summary = ai_summary
                        elif len(content) > 100:
                            # Fallback to content preview if no AI summary
                            content_preview = content[:300].strip()
                            if content_preview:
                                final_summary = content_preview + ("..." if len(content) > 300 else "")

                        # Use enhanced content if available and substantially different
                        if ai_enhanced_content and len(ai_enhanced_content) > len(content) * 0.8:
                            content = ai_enhanced_content

                    except Exception as e:
                        await ctx.warning(f"AI enhancement failed for {file_name}: {str(e)}")

                document = {
                    "id": doc_id,
                    "title": title,
                    "summary": final_summary,
                    "content": content,
                    "last_modified": datetime.now().isoformat(),
                    "priority": "medium",
                    "tags": final_tags,
                    "related": [],
                    "source_type": "documentation",
                    "key_points": final_key_points
                }

                # Validate document if requested
                if validate_schema:
                    try:
                        validated_doc = validate_document_structure(document)
                        document = validated_doc
                    except DocumentValidationError as e:
                        failed.append((file_name, f"Validation error: {str(e)}"))
                        continue
                    except Exception as e:
                        failed.append((file_name, f"Validation error: {str(e)}"))
                        continue

                # Index the document
                try:
                    result = es.index(index=index, id=doc_id, body=document)
                    successful.append((file_name, doc_id, result.get('result', 'unknown')))
                except Exception as e:
                    failed.append((file_name, f"Indexing error: {str(e)}"))
                    continue

            except Exception as e:
                failed.append((file_path.name, f"Processing error: {str(e)}"))
                continue

        # Build result summary
        total_processed = len(successful) + len(failed) + len(skipped_existing)
        result_summary = f"✅ Batch indexing completed for directory: {directory_path}\n\n"

        # Summary statistics
        result_summary += f"📊 **Processing Summary**:\n"
        result_summary += f"   📁 Directory: {directory_path}\n"
        result_summary += f"   🔍 Pattern: {file_pattern} (recursive: {recursive})\n"
        result_summary += f"   📄 Files found: {len(files)}\n"
        result_summary += f"   ✅ Successfully indexed: {len(successful)}\n"
        result_summary += f"   ❌ Failed: {len(failed)}\n"

        if skipped_existing:
            result_summary += f"   ⏭️ Skipped (already exist): {len(skipped_existing)}\n"

        if skipped_size:
            result_summary += f"   📏 Skipped (too large): {len(skipped_size)}\n"

        result_summary += f"   🎯 Index: {index}\n"

        # AI Enhancement info
        if use_ai_enhancement and ctx:
            result_summary += f"   🤖 AI Enhancement: Enabled (generated intelligent tags and key points)\n"
        else:
            result_summary += f"   🤖 AI Enhancement: Disabled (using basic metadata)\n"

        result_summary += "\n"

        # Successful indexing details
        if successful:
            result_summary += f"✅ **Successfully Indexed** ({len(successful)} files):\n"
            for file_name, doc_id, index_result in successful[:10]:  # Show first 10
                result_summary += f"   📄 {file_name} → {doc_id} ({index_result})\n"
            if len(successful) > 10:
                result_summary += f"   ... and {len(successful) - 10} more files\n"
            result_summary += "\n"

        # Failed indexing details
        if failed:
            result_summary += f"❌ **Failed to Index** ({len(failed)} files):\n"
            for file_name, error_msg in failed[:5]:  # Show first 5 errors
                result_summary += f"   📄 {file_name}: {error_msg}\n"
            if len(failed) > 5:
                result_summary += f"   ... and {len(failed) - 5} more errors\n"
            result_summary += "\n"

        # Skipped files details
        if skipped_existing:
            result_summary += f"⏭️ **Skipped (Already Exist)** ({len(skipped_existing)} files):\n"
            for file_name in skipped_existing[:5]:
                result_summary += f"   📄 {file_name}\n"
            if len(skipped_existing) > 5:
                result_summary += f"   ... and {len(skipped_existing) - 5} more files\n"
            result_summary += "\n"

        if skipped_size:
            result_summary += f"📏 **Skipped (Too Large)** ({len(skipped_size)} files):\n"
            for file_path, file_size in skipped_size[:3]:
                size_mb = file_size / 1048576
                result_summary += f"   📄 {file_path.name}: {size_mb:.1f} MB\n"
            if len(skipped_size) > 3:
                result_summary += f"   ... and {len(skipped_size) - 3} more large files\n"
            result_summary += f"   💡 Increase max_file_size to include these files\n\n"

        # Performance tips
        if len(successful) > 0:
            result_summary += f"🚀 **Performance Tips for Future Batches**:\n"
            result_summary += f"   🔄 Use skip_existing=True to avoid reindexing\n"
            result_summary += f"   📂 Process subdirectories separately for better control\n"
            result_summary += f"   🔍 Use specific file patterns (*.md, *.txt) for faster processing\n"
            result_summary += f"   📏 Adjust max_file_size based on your content needs\n"
            if use_ai_enhancement:
                result_summary += f"   🤖 AI enhancement adds ~2-3 seconds per file but greatly improves metadata quality\n"
                result_summary += f"   ⚡ Set use_ai_enhancement=False for faster processing with basic metadata\n"
            else:
                result_summary += f"   🤖 Enable use_ai_enhancement=True for intelligent tags and key points\n"
            result_summary += "\n"

        # Knowledge base recommendations
        if len(successful) > 20:
            result_summary += f"🧹 **Knowledge Base Organization Recommendation**:\n"
            result_summary += f"   📊 You've indexed {len(successful)} documents from this batch\n"
            result_summary += f"   💡 Consider organizing them by topics or themes\n"
            result_summary += f"   🔍 Use the 'search' tool to find related documents for consolidation\n"
            result_summary += f"   🎯 Group similar content to improve knowledge base quality\n"

        return result_summary

    except Exception as e:
        error_message = "❌ Batch indexing failed:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 Try: Use 'create_index' tool to create the index first\n\n"
        elif "permission" in error_str or "access denied" in error_str:
            error_message += f"🔒 **Permission Error**: Access denied to directory or files\n"
            error_message += f"📍 Insufficient permissions to read directory or files\n"
            error_message += f"💡 Try: Check directory permissions or verify file access rights\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


def main():
    """Main entry point for elasticsearch batch server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-batch 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Batch Server - FastMCP Implementation")
            print("Handles batch operations for bulk document processing.")
            print("\nTools provided:")
            print("  - batch_index_directory: Batch index documents from directory")
            return

    print("🚀 Starting Elasticsearch Batch Server...")
    print("🔍 Tools: batch_index_directory")
    print("🎯 Purpose: Bulk operations for efficient mass document processing")
    print("✅ Status: 1 Batch tool completed - Ready for production!")
    app.run()


if __name__ == "__main__":
    main()
