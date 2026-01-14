"""
Elasticsearch Document FastMCP Server
Document operations extracted from main elasticsearch server.
Handles document indexing, retrieval, and deletion operations.
"""
import json
from typing import List, Dict, Any, Optional, Annotated

from fastmcp import FastMCP, Context
from pydantic import Field

from ..document_schema import (
    validate_document_structure,
    DocumentValidationError,
    format_validation_error, create_document_template as create_doc_template_base
)
from ..elasticsearch_client import get_es_client
from ..elasticsearch_helper import (
    generate_smart_metadata,
    generate_smart_doc_id,
    check_title_duplicates,
    get_existing_document_ids,
    check_content_similarity_with_ai
)

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Document",
    version="1.0.0",
    instructions="Elasticsearch document management tools"
)


@app.tool(
    description="Delete a document from Elasticsearch index by document ID",
    tags={"elasticsearch", "delete", "document"}
)
async def delete_document(
        index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
        doc_id: Annotated[str, Field(description="Document ID to delete from the index")]
) -> str:
    """Delete a document from Elasticsearch index."""
    try:
        es = get_es_client()

        result = es.delete(index=index, id=doc_id)

        return f"✅ Document deleted successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete document:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif (
                "not_found" in error_str or "not found" in error_str or "does not exist" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            # Check if it's specifically an index not found error
            if ("index" in error_str and (
                    "not found" in error_str or "not_found" in error_str or "does not exist" in error_str)) or "index_not_found_exception" in error_str or "no such index" in error_str:
                error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
                error_message += f"📍 The target index has not been created yet\n"
                error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
            else:
                error_message += f"📄 **Document Not Found**: Document ID '{doc_id}' does not exist\n"
                error_message += f"📍 Cannot delete a document that doesn't exist\n"
                error_message += f"💡 Try: Check document ID or use 'search' to find documents\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


@app.tool(
    description="Retrieve a specific document from Elasticsearch index by document ID",
    tags={"elasticsearch", "get", "document", "retrieve"}
)
async def get_document(
        index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
        doc_id: Annotated[str, Field(description="Document ID to retrieve from the index")]
) -> str:
    """Retrieve a specific document from Elasticsearch index."""
    try:
        es = get_es_client()

        result = es.get(index=index, id=doc_id)

        return f"✅ Document retrieved successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to get document:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif (
                "not_found" in error_str or "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            if "index" in error_str or "index_not_found_exception" in error_str or "no such index" in error_str:
                error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
                error_message += f"📍 The target index has not been created yet\n"
                error_message += f"💡 **Suggestions for agents**:\n"
                error_message += f"   1. Use 'list_indices' tool to see all available indices\n"
                error_message += f"   2. Check which indices contain your target data\n"
                error_message += f"   3. Use the correct index name from the list\n"
                error_message += f"   4. If no suitable index exists, create one with 'create_index' tool\n\n"
            else:
                error_message += f"📄 **Document Not Found**: Document ID '{doc_id}' does not exist\n"
                error_message += f"📍 The requested document was not found in index '{index}'\n"
                error_message += f"💡 Try: Check document ID or use 'search' to find documents\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


@app.tool(
    description="Index a document into Elasticsearch with smart duplicate prevention and intelligent document ID generation. 💡 RECOMMENDED: Use 'create_document_template' tool first to generate a proper document structure and avoid validation errors.",
    tags={"elasticsearch", "index", "document", "validation", "duplicate-prevention"}
)
async def index_document(
        index: Annotated[str, Field(description="Name of the Elasticsearch index to store the document")],
        document: Annotated[Dict[str, Any], Field(description="Document data to index as JSON object. 💡 RECOMMENDED: Use 'create_document_template' tool first to generate proper document format.")],
        doc_id: Annotated[Optional[str], Field(
            description="Optional document ID - if not provided, smart ID will be generated")] = None,
        validate_schema: Annotated[
            bool, Field(description="Whether to validate document structure for knowledge base format")] = True,
        check_duplicates: Annotated[
            bool, Field(description="Check for existing documents with similar title before indexing")] = True,
        force_index: Annotated[
            bool, Field(description="Force indexing even if potential duplicates are found. 💡 TIP: Set to True if content is genuinely new and not in knowledge base to avoid multiple tool calls")] = False,
        use_ai_similarity: Annotated[bool, Field(
            description="Use AI to analyze content similarity and provide intelligent recommendations")] = True,
        ctx: Context = None
) -> str:
    """Index a document into Elasticsearch with smart duplicate prevention."""
    try:
        es = get_es_client()

        # Smart duplicate checking if enabled
        if check_duplicates and not force_index:
            title = document.get('title', '')
            content = document.get('content', '')

            if title:
                # First check simple title duplicates
                dup_check = check_title_duplicates(es, index, title)
                if dup_check['found']:
                    duplicates_info = "\n".join([
                        f"   📄 {dup['title']} (ID: {dup['id']})\n      📝 {dup['summary']}\n      📅 {dup['last_modified']}"
                        for dup in dup_check['duplicates'][:3]
                    ])

                    # Use AI similarity analysis if enabled and content is substantial
                    if use_ai_similarity and content and len(content) > 200 and ctx:
                        try:
                            ai_analysis = await check_content_similarity_with_ai(es, index, title, content, ctx)

                            action = ai_analysis.get('action', 'CREATE')
                            confidence = ai_analysis.get('confidence', 0.5)
                            reasoning = ai_analysis.get('reasoning', 'AI analysis completed')
                            target_doc = ai_analysis.get('target_document_id', '')

                            ai_message = f"\n\n🤖 **AI Content Analysis** (Confidence: {confidence:.0%}):\n"
                            ai_message += f"   🎯 **Recommended Action**: {action}\n"
                            ai_message += f"   💭 **AI Reasoning**: {reasoning}\n"

                            if action == "UPDATE" and target_doc:
                                ai_message += f"   📄 **Target Document**: {target_doc}\n"
                                ai_message += f"   💡 **Suggestion**: Update existing document instead of creating new one\n"

                            elif action == "DELETE":
                                ai_message += f"   🗑️ **AI Recommendation**: Existing content is superior, consider not creating this document\n"

                            elif action == "MERGE" and target_doc:
                                ai_message += f"   🔄 **Merge Target**: {target_doc}\n"
                                ai_message += f"   📝 **Strategy**: {ai_analysis.get('merge_strategy', 'Combine unique information from both documents')}\n"

                            elif action == "CREATE":
                                ai_message += f"   ✅ **AI Approval**: Content is sufficiently unique to create new document\n"
                                # If AI says CREATE, allow automatic indexing
                                pass

                            # Show similar documents found by AI
                            similar_docs = ai_analysis.get('similar_docs', [])
                            if similar_docs:
                                ai_message += f"\n   📋 **Similar Documents Analyzed**:\n"
                                for i, doc in enumerate(similar_docs[:2], 1):
                                    ai_message += f"      {i}. {doc['title']} (Score: {doc.get('elasticsearch_score', 0):.1f})\n"

                            # If AI recommends CREATE with high confidence, proceed automatically
                            if action == "CREATE" and confidence > 0.8:
                                # Continue with indexing - don't return early
                                pass
                            else:
                                # Return AI analysis for user review
                                return (
                                        f"⚠️ **Potential Duplicates Found** - {dup_check['count']} similar document(s):\n\n" +
                                        f"{duplicates_info}\n" +
                                        f"{ai_message}\n\n" +
                                        f"🤔 **What would you like to do?**\n" +
                                        f"   1️⃣ **FOLLOW AI RECOMMENDATION**: {action} as suggested by AI\n" +
                                        f"   2️⃣ **UPDATE existing document**: Modify one of the above instead\n" +
                                        f"   3️⃣ **SEARCH for more**: Use search tool to find all related content\n" +
                                        f"   4️⃣ **FORCE CREATE anyway**: Set force_index=True if this is truly unique\n\n" +
                                        f"💡 **AI Recommendation**: {reasoning}\n" +
                                        f"🔍 **Next Step**: Search for '{title}' to see all related documents\n\n" +
                                        f"⚡ **To force indexing**: Call again with force_index=True")

                        except Exception as ai_error:
                            # Fallback to simple duplicate check if AI fails
                            return (
                                    f"⚠️ **Potential Duplicates Found** - {dup_check['count']} similar document(s):\n\n" +
                                    f"{duplicates_info}\n\n" +
                                    f"⚠️ **AI Analysis Failed**: {str(ai_error)}\n\n" +
                                    f"🤔 **What would you like to do?**\n" +
                                    f"   1️⃣ **UPDATE existing document**: Modify one of the above instead\n" +
                                    f"   2️⃣ **SEARCH for more**: Use search tool to find all related content\n" +
                                    f"   3️⃣ **FORCE CREATE anyway**: Set force_index=True if this is truly unique\n\n" +
                                    f"💡 **Recommendation**: Update existing documents to prevent knowledge base bloat\n" +
                                    f"🔍 **Next Step**: Search for '{title}' to see all related documents\n\n" +
                                    f"⚡ **To force indexing**: Call again with force_index=True")

                    else:
                        # Simple duplicate check without AI
                        return (f"⚠️ **Potential Duplicates Found** - {dup_check['count']} similar document(s):\n\n" +
                                f"{duplicates_info}\n\n" +
                                f"🤔 **What would you like to do?**\n" +
                                f"   1️⃣ **UPDATE existing document**: Modify one of the above instead\n" +
                                f"   2️⃣ **SEARCH for more**: Use search tool to find all related content\n" +
                                f"   3️⃣ **FORCE CREATE anyway**: Set force_index=True if this is truly unique\n\n" +
                                f"💡 **Recommendation**: Update existing documents to prevent knowledge base bloat\n" +
                                f"🔍 **Next Step**: Search for '{title}' to see all related documents\n\n" +
                                f"⚡ **To force indexing**: Call again with force_index=True")

        # Generate smart document ID if not provided
        if not doc_id:
            existing_ids = get_existing_document_ids(es, index)
            doc_id = generate_smart_doc_id(
                document.get('title', 'untitled'),
                document.get('content', ''),
                existing_ids
            )
            document['id'] = doc_id  # Ensure document has the ID

        # Validate document structure if requested
        if validate_schema:
            try:
                # Check if this looks like a knowledge base document
                if isinstance(document, dict) and "id" in document and "title" in document:
                    validated_doc = validate_document_structure(document)
                    document = validated_doc

                    # Use the document ID from the validated document if not provided earlier
                    if not doc_id:
                        doc_id = document.get("id")

                else:
                    # For non-knowledge base documents, still validate with strict mode if enabled
                    validated_doc = validate_document_structure(document, is_knowledge_doc=False)
                    document = validated_doc
            except DocumentValidationError as e:
                return f"❌ Validation failed:\n\n{format_validation_error(e)}"
            except Exception as e:
                return f"❌ Validation error: {str(e)}"

        # Index the document
        result = es.index(index=index, id=doc_id, body=document)

        success_message = f"✅ Document indexed successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

        # Add smart guidance based on indexing result
        if result.get('result') == 'created':
            success_message += f"\n\n🎉 **New Document Created**:\n"
            success_message += f"   📄 **Document ID**: {doc_id}\n"
            success_message += f"   🆔 **ID Strategy**: {'User-provided' if 'doc_id' in locals() and doc_id else 'Smart-generated'}\n"
            if check_duplicates:
                success_message += f"   ✅ **Duplicate Check**: Passed - no similar titles found\n"
        else:
            success_message += f"\n\n🔄 **Document Updated**:\n"
            success_message += f"   📄 **Document ID**: {doc_id}\n"
            success_message += f"   ⚡ **Action**: Replaced existing document with same ID\n"

        success_message += (f"\n\n💡 **Smart Duplicate Prevention Active**:\n" +
                            f"   🔍 **Auto-Check**: {'Enabled' if check_duplicates else 'Disabled'} - searches for similar titles\n" +
                            f"   🤖 **AI Analysis**: {'Enabled' if use_ai_similarity else 'Disabled'} - intelligent content similarity detection\n" +
                            f"   🆔 **Smart IDs**: Auto-generated from title with collision detection\n" +
                            f"   ⚡ **Force Option**: Use force_index=True to bypass duplicate warnings\n" +
                            f"   🔄 **Update Recommended**: Modify existing documents instead of creating duplicates\n\n" +
                            f"🤝 **Best Practices**:\n" +
                            f"   • Search before creating: 'search(index=\"{index}\", query=\"your topic\")'\n" +
                            f"   • Update existing documents when possible\n" +
                            f"   • Use descriptive titles for better smart ID generation\n" +
                            f"   • AI will analyze content similarity for intelligent recommendations\n" +
                            f"   • Set force_index=True only when content is truly unique")

        return success_message

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Document indexing failed:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 **Suggestions for agents**:\n"
            error_message += f"   1. Use 'create_index' tool to create the index first\n"
            error_message += f"   2. Use 'list_indices' to see available indices\n"
            error_message += f"   3. Check the correct index name for your data type\n\n"
        elif "mapping" in error_str or "field" in error_str:
            error_message += f"🗂️ **Mapping Error**: Document structure conflicts with index mapping\n"
            error_message += f"📍 Document fields don't match the expected index schema\n"
            error_message += f"💡 Try: Adjust document structure or update index mapping\n\n"
        elif "version" in error_str or "conflict" in error_str:
            error_message += f"⚡ **Version Conflict**: Document already exists with different version\n"
            error_message += f"📍 Another process modified this document simultaneously\n"
            error_message += f"💡 Try: Use 'get_document' first, then update with latest version\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Indexing operation timed out\n"
            error_message += f"📍 Document may be too large or index overloaded\n"
            error_message += f"💡 Try: Reduce document size or retry later\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# CLI Entry Point


@app.tool(
    description="Validate document structure against knowledge base schema and provide formatting guidance",
    tags={"elasticsearch", "validation", "document", "schema"}
)
async def validate_document_schema(
        document: Annotated[
            Dict[str, Any], Field(description="Document object to validate against knowledge base schema format")]
) -> str:
    """Validate document structure against knowledge base schema standards."""
    try:
        validated_doc = validate_document_structure(document)

        return (f"✅ Document validation successful!\n\n" +
                f"Validated document:\n{json.dumps(validated_doc, indent=2, ensure_ascii=False)}\n\n" +
                f"Document is ready to be indexed.\n\n" +
                f"🚨 **RECOMMENDED: Check for Duplicates First**:\n" +
                f"   🔍 **Use index_document**: Built-in AI-powered duplicate detection\n" +
                f"   🔄 **Update instead of duplicate**: Modify existing documents when possible\n" +
                f"   📏 **Content length check**: If < 1000 chars, store in 'content' field directly\n" +
                f"   📁 **File creation**: Only for truly long content that needs separate storage\n" +
                f"   🎯 **Quality over quantity**: Prevent knowledge base bloat through smart reuse")

    except DocumentValidationError as e:
        return format_validation_error(e)
    except Exception as e:
        return f"❌ Validation error: {str(e)}"


@app.tool(
    description="Create a properly structured document template for knowledge base with AI-generated metadata and formatting",
    tags={"elasticsearch", "document", "template", "knowledge-base", "ai-enhanced"}
)
async def create_document_template(
        title: Annotated[str, Field(description="Document title for the knowledge base entry")],
        content: Annotated[str, Field(description="Document content for AI analysis and metadata generation")] = "",
        priority: Annotated[
            str, Field(description="Priority level for the document", pattern="^(high|medium|low)$")] = "medium",
        source_type: Annotated[str, Field(description="Type of source content",
                                          pattern="^(markdown|code|config|documentation|tutorial)$")] = "markdown",
        tags: Annotated[
            List[str], Field(description="Additional manual tags (will be merged with AI-generated tags)")] = [],
        summary: Annotated[str, Field(description="Brief summary description of the document content")] = "",
        key_points: Annotated[List[str], Field(
            description="Additional manual key points (will be merged with AI-generated points)")] = [],
        related: Annotated[List[str], Field(description="List of related document IDs or references")] = [],
        use_ai_enhancement: Annotated[
            bool, Field(description="Use AI to generate intelligent tags and key points")] = True,
        ctx: Context = None
) -> str:
    """Create a properly structured document template for knowledge base indexing with AI-generated metadata."""
    try:
        # Initialize metadata
        final_tags = list(tags)  # Copy manual tags
        final_key_points = list(key_points)  # Copy manual key points

        # Use AI enhancement if requested and content is provided
        if use_ai_enhancement and content.strip() and ctx:
            try:
                await ctx.info("🤖 Generating intelligent metadata and smart content using AI...")
                ai_metadata = await generate_smart_metadata(title, content, ctx)

                # Merge AI-generated tags with manual tags
                ai_tags = ai_metadata.get("tags", [])
                for tag in ai_tags:
                    if tag not in final_tags:
                        final_tags.append(tag)

                # Merge AI-generated key points with manual points
                ai_key_points = ai_metadata.get("key_points", [])
                for point in ai_key_points:
                    if point not in final_key_points:
                        final_key_points.append(point)

                # Use AI-generated smart summary if available
                ai_summary = ai_metadata.get("smart_summary", "")
                if ai_summary and not summary:
                    summary = ai_summary

                # Use AI-enhanced content if available and better
                ai_enhanced_content = ai_metadata.get("enhanced_content", "")
                if ai_enhanced_content and len(ai_enhanced_content) > len(content) * 0.8:
                    content = ai_enhanced_content

                await ctx.info(
                    f"✅ AI generated {len(ai_tags)} tags, {len(ai_key_points)} key points, smart summary, and enhanced content")

            except Exception as e:
                await ctx.warning(f"AI enhancement failed: {str(e)}, using manual metadata only")

        # Generate auto-summary if not provided and content is available
        if not summary and content.strip():
            if len(content) > 200:
                summary = content[:200].strip() + "..."
            else:
                summary = content.strip()

        template = create_doc_template_base(
            title=title,
            priority=priority,
            source_type=source_type,
            tags=final_tags,
            summary=summary,
            key_points=final_key_points,
            related=related
        )

        ai_info = ""
        if use_ai_enhancement and ctx:
            ai_info = f"\n🤖 **AI Enhancement Used**: Generated {len(final_tags)} total tags and {len(final_key_points)} total key points\n"

        return (f"✅ Document template created successfully with AI-enhanced metadata!\n\n" +
                f"{json.dumps(template, indent=2, ensure_ascii=False)}\n" +
                ai_info +
                f"\nThis template can be used with the 'index_document' tool.\n\n" +
                f"⚠️ **CRITICAL: Search Before Creating - Avoid Duplicates**:\n" +
                f"   🔍 **STEP 1**: Use 'search' tool to check if similar content already exists\n" +
                f"   🔄 **STEP 2**: If found, UPDATE existing document instead of creating new one\n" +
                f"   📝 **STEP 3**: For SHORT content (< 1000 chars): Add directly to 'content' field\n" +
                f"   📁 **STEP 4**: For LONG content: Create file only when truly necessary\n" +
                f"   🧹 **STEP 5**: Clean up outdated documents regularly to maintain quality\n" +
                f"   🎯 **Remember**: Knowledge base quality > quantity - avoid bloat!")

    except Exception as e:
        return f"❌ Failed to create document template: {str(e)}"


def main():
    """Main entry point for elasticsearch document server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-document 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Document Server - FastMCP Implementation")
            print("Handles document CRUD operations.")
            print("\nTools provided:")
            print("  - [TO BE COPIED FROM BAK FILE]")
            return

    print("🚀 Starting Elasticsearch Document Server...")
    print("🔍 Tools: [TO BE COPIED FROM BAK FILE]")
    app.run()


if __name__ == "__main__":
    main()
