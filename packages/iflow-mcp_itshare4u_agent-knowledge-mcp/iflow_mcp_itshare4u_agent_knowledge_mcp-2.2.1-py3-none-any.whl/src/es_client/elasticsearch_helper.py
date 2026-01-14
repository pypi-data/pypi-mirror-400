"""
Elasticsearch Helper Functions
Utility functions for AI-enhanced metadata generation and content processing.
"""

import json
import re
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastmcp import Context


async def generate_smart_metadata(title: str, content: str, ctx: Context) -> Dict[str, Any]:
    """Generate intelligent tags, key_points, smart_summary and enhanced_content using LLM sampling."""
    try:
        # Create prompt for generating metadata and smart content
        prompt = f"""Analyze the following document and provide comprehensive smart metadata and content:

Title: {title}

Content: {content[:2000]}{"..." if len(content) > 2000 else ""}

Please provide:
1. Relevant tags (3-8 tags, lowercase, hyphen-separated)
2. Key points (3-6 important points from the content)
3. Smart summary (2-3 sentences capturing the essence)
4. Enhanced content (improved/structured version if content is brief or unclear)

Respond in JSON format:
{{
  "tags": ["tag1", "tag2", "tag3"],
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "smart_summary": "Brief 2-3 sentence summary of the document",
  "enhanced_content": "Improved/structured content if original is brief, otherwise keep original"
}}

Focus on:
- Technical concepts and technologies mentioned
- Main topics and themes
- Document type and purpose
- Key features or functionalities discussed
- Clear, professional language for summary and content
- Maintain accuracy while improving clarity"""

        # Request LLM analysis with controlled parameters and model preferences
        response = await ctx.sample(
            messages=prompt,
            system_prompt="You are an expert document analyzer and content enhancer. Generate accurate, relevant metadata and improve content quality while maintaining original meaning. Always respond with valid JSON.",
            model_preferences=["claude-3-opus", "claude-3-sonnet", "gpt-4"],  # Prefer reasoning models for analysis
            temperature=0.3,  # Low randomness for consistency
            max_tokens=600   # Increased for smart content generation
        )
        
        # Parse the JSON response
        try:
            metadata = json.loads(response.text.strip())
            
            # Validate and clean the response
            tags = metadata.get("tags", [])
            key_points = metadata.get("key_points", [])
            smart_summary = metadata.get("smart_summary", "")
            enhanced_content = metadata.get("enhanced_content", "")
            
            # Ensure we have reasonable limits and clean data
            tags = [tag.lower().strip() for tag in tags[:8] if tag and isinstance(tag, str)]
            key_points = [point.strip() for point in key_points[:6] if point and isinstance(point, str)]
            
            # Clean and validate smart content
            smart_summary = smart_summary.strip() if isinstance(smart_summary, str) else ""
            enhanced_content = enhanced_content.strip() if isinstance(enhanced_content, str) else ""
            
            return {
                "tags": tags,
                "key_points": key_points,
                "smart_summary": smart_summary,
                "enhanced_content": enhanced_content
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            await ctx.warning("LLM response was not valid JSON, using fallback metadata generation")
            return generate_fallback_metadata(title, content)
            
    except Exception as e:
        # Fallback for any sampling errors
        await ctx.warning(f"LLM sampling failed ({str(e)}), using fallback metadata generation")
        return generate_fallback_metadata(title, content)


def generate_fallback_metadata(title: str, content: str) -> Dict[str, Any]:
    """Generate basic metadata when LLM sampling is not available."""
    # Basic tags based on title and content analysis
    title_lower = title.lower()
    content_lower = content.lower()[:1000]  # First 1000 chars for analysis
    
    tags = ["document"]
    
    # Add file type tags
    if any(word in title_lower for word in ["readme", "documentation", "docs"]):
        tags.append("documentation")
    if any(word in title_lower for word in ["config", "configuration", "settings"]):
        tags.append("configuration")
    if any(word in title_lower for word in ["test", "testing", "spec"]):
        tags.append("testing")
    if any(word in content_lower for word in ["python", "def ", "class ", "import "]):
        tags.append("python")
    if any(word in content_lower for word in ["javascript", "function", "const ", "let "]):
        tags.append("javascript")
    if any(word in content_lower for word in ["api", "endpoint", "request", "response"]):
        tags.append("api")
    
    # Basic key points
    key_points = [
        f"Document title: {title}",
        f"Content length: {len(content)} characters"
    ]
    
    # Add content-based points
    if "implementation" in content_lower:
        key_points.append("Contains implementation details")
    if "example" in content_lower or "demo" in content_lower:
        key_points.append("Includes examples or demonstrations")
    if "error" in content_lower or "exception" in content_lower:
        key_points.append("Discusses error handling")
    
    return {
        "tags": tags[:6],  # Limit to 6 tags
        "key_points": key_points[:4],  # Limit to 4 points
        "smart_summary": f"Fallback document: {title}",
        "enhanced_content": content[:500] + "..." if len(content) > 500 else content
    }


def parse_time_parameters(date_from: Optional[str] = None, date_to: Optional[str] = None,
                          time_period: Optional[str] = None) -> Dict[str, Any]:
    """Parse time-based search parameters and return Elasticsearch date range filter."""

    def parse_relative_date(date_str: str) -> datetime:
        """Parse relative date strings like '7d', '1w', '1m' to datetime."""
        if not date_str:
            return None

        match = re.match(r'(\d+)([dwmy])', date_str.lower())
        if match:
            amount, unit = match.groups()
            amount = int(amount)

            if unit == 'd':
                return datetime.now() - timedelta(days=amount)
            elif unit == 'w':
                return datetime.now() - timedelta(weeks=amount)
            elif unit == 'm':
                return datetime.now() - timedelta(days=amount * 30)
            elif unit == 'y':
                return datetime.now() - timedelta(days=amount * 365)

        return None

    def parse_date_string(date_str: str) -> str:
        """Parse various date formats to Elasticsearch compatible format."""
        if not date_str:
            return None

        if date_str.lower() == 'now':
            return 'now'

        # Try relative dates first
        relative_date = parse_relative_date(date_str)
        if relative_date:
            return relative_date.isoformat()

        # Try parsing standard formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ'
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue

        return None

    # Handle time_period shortcuts
    if time_period:
        now = datetime.now()
        if time_period == 'today':
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return {
                "range": {
                    "last_modified": {
                        "gte": start_of_day.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            return {
                "range": {
                    "last_modified": {
                        "gte": start_of_yesterday.isoformat(),
                        "lte": end_of_yesterday.isoformat()
                    }
                }
            }
        elif time_period == 'week':
            week_ago = now - timedelta(weeks=1)
            return {
                "range": {
                    "last_modified": {
                        "gte": week_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'month':
            month_ago = now - timedelta(days=30)
            return {
                "range": {
                    "last_modified": {
                        "gte": month_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'year':
            year_ago = now - timedelta(days=365)
            return {
                "range": {
                    "last_modified": {
                        "gte": year_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }

    # Handle explicit date range
    if date_from or date_to:
        range_filter = {"range": {"last_modified": {}}}

        if date_from:
            parsed_from = parse_date_string(date_from)
            if parsed_from:
                range_filter["range"]["last_modified"]["gte"] = parsed_from

        if date_to:
            parsed_to = parse_date_string(date_to)
            if parsed_to:
                range_filter["range"]["last_modified"]["lte"] = parsed_to

        if range_filter["range"]["last_modified"]:
            return range_filter

    return None


def analyze_search_results_for_reorganization(results: List[Dict], query_text: str, total_results: int) -> str:
    """Analyze search results and provide specific reorganization suggestions."""
    if total_results <= 15:
        return ""

    # Extract topics and themes from search results
    topics = set()
    sources = set()
    priorities = {"high": 0, "medium": 0, "low": 0}
    dates = []

    for result in results[:10]:  # Analyze first 10 results
        source_data = result.get("source", {})

        # Extract tags as topics
        tags = source_data.get("tags", [])
        topics.update(tags)

        # Extract source types
        source_type = source_data.get("source_type", "unknown")
        sources.add(source_type)

        # Count priorities
        priority = source_data.get("priority", "medium")
        priorities[priority] = priorities.get(priority, 0) + 1

        # Extract dates for timeline analysis
        last_modified = source_data.get("last_modified", "")
        if last_modified:
            dates.append(last_modified)

    # Generate reorganization suggestions
    suggestion = f"\n\n🔍 **Knowledge Base Analysis for '{query_text}'** ({total_results} documents):\n\n"

    # Topic analysis
    if topics:
        suggestion += f"📋 **Topics Found**: {', '.join(sorted(list(topics))[:8])}\n"
        suggestion += f"💡 **Reorganization Suggestion**: Group documents by these topics\n\n"

    # Source type analysis
    if sources:
        suggestion += f"📁 **Content Types**: {', '.join(sorted(sources))}\n"
        suggestion += f"💡 **Organization Tip**: Separate by content type for better structure\n\n"

    # Priority distribution
    total_priority_docs = sum(priorities.values())
    if total_priority_docs > 0:
        high_pct = (priorities["high"] / total_priority_docs) * 100
        suggestion += f"⭐ **Priority Distribution**: {priorities['high']} high, {priorities['medium']} medium, {priorities['low']} low\n"
        if priorities["low"] > 5:
            suggestion += f"💡 **Cleanup Suggestion**: Consider archiving {priorities['low']} low-priority documents\n\n"

    # User collaboration template
    suggestion += f"🤝 **Ask User These Questions**:\n"
    suggestion += f"   1. 'I found {total_results} documents about {query_text}. Would you like to organize them better?'\n"
    suggestion += f"   2. 'Should we group them by: {', '.join(sorted(list(topics))[:3]) if topics else 'topic areas'}?'\n"
    suggestion += f"   3. 'Which documents can we merge or archive to reduce redundancy?'\n"
    suggestion += f"   4. 'Do you want to keep all {priorities.get('low', 0)} low-priority items?'\n\n"

    suggestion += f"✅ **Reorganization Goals**:\n"
    suggestion += f"   • Reduce from {total_results} to ~{max(5, total_results // 3)} well-organized documents\n"
    suggestion += f"   • Create comprehensive topic-based documents\n"
    suggestion += f"   • Archive or delete outdated/redundant content\n"
    suggestion += f"   • Improve searchability and knowledge quality"

    return suggestion


# ================================
# DUPLICATE PREVENTION HELPERS
# ================================

def generate_smart_doc_id(title: str, content: str = "", existing_ids: set = None) -> str:
    """Generate a smart document ID with collision detection."""
    if existing_ids is None:
        existing_ids = set()
    
    # Step 1: Generate base ID from title
    base_id = re.sub(r'[^a-zA-Z0-9\-_]', '_', title.lower())
    base_id = re.sub(r'_+', '_', base_id).strip('_')
    
    # Truncate if too long
    if len(base_id) > 50:
        base_id = base_id[:50].rstrip('_')
    
    # Step 2: Check if base ID is unique
    if base_id not in existing_ids:
        return base_id
    
    # Step 3: Add content hash if duplicate title
    if content:
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{base_id}_{content_hash}"
    
    # Step 4: Add timestamp hash as fallback
    timestamp_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    return f"{base_id}_{timestamp_hash}"


def check_title_duplicates(es, index: str, title: str) -> dict:
    """Check for existing documents with similar titles."""
    try:
        # Check exact title match
        exact_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"title": title}},
                        {"term": {"title.keyword": title}} if hasattr(es.indices.get_mapping(index=index), 'keyword') else {"match": {"title": title}}
                    ]
                }
            },
            "size": 5,
            "_source": ["title", "id", "summary", "last_modified"]
        }
        
        result = es.search(index=index, body=exact_query)
        
        duplicates = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            duplicates.append({
                "id": hit['_id'],
                "title": source.get('title', ''),
                "summary": source.get('summary', '')[:100] + "..." if len(source.get('summary', '')) > 100 else source.get('summary', ''),
                "last_modified": source.get('last_modified', ''),
                "score": hit['_score']
            })
        
        return {
            "found": len(duplicates) > 0,
            "count": len(duplicates),
            "duplicates": duplicates
        }
    except Exception:
        return {"found": False, "count": 0, "duplicates": []}


def get_existing_document_ids(es, index: str) -> set:
    """Get all existing document IDs from the index."""
    try:
        result = es.search(
            index=index,
            body={
                "query": {"match_all": {}},
                "size": 10000,
                "_source": False
            }
        )
        return {hit['_id'] for hit in result['hits']['hits']}
    except Exception:
        return set()


async def check_content_similarity_with_ai(es, index: str, title: str, content: str, ctx: Context, similarity_threshold: float = 0.7) -> dict:
    """
    Advanced content similarity checking using AI analysis.
    Returns recommendations for UPDATE, DELETE, CREATE, or MERGE actions.
    """
    try:
        # First, find potentially similar documents using Elasticsearch
        similar_docs = []
        
        # Search for documents with similar titles or content
        if len(content) > 100:
            search_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"title": {"query": title, "boost": 3.0}}},
                            {"match": {"content": {"query": content[:500], "boost": 1.0}}},
                            {"more_like_this": {
                                "fields": ["content", "title"],
                                "like": content[:1000],
                                "min_term_freq": 1,
                                "max_query_terms": 8,
                                "minimum_should_match": "30%"
                            }}
                        ]
                    }
                },
                "size": 5,
                "_source": ["title", "summary", "content", "last_modified", "id"]
            }
            
            result = es.search(index=index, body=search_query)
            
            # Collect similar documents
            for hit in result['hits']['hits']:
                source = hit['_source']
                similar_docs.append({
                    "id": hit['_id'],
                    "title": source.get('title', ''),
                    "summary": source.get('summary', '')[:200] + "..." if len(source.get('summary', '')) > 200 else source.get('summary', ''),
                    "content_preview": source.get('content', '')[:300] + "..." if len(source.get('content', '')) > 300 else source.get('content', ''),
                    "last_modified": source.get('last_modified', ''),
                    "elasticsearch_score": hit['_score']
                })
        
        # If no similar documents found, recommend CREATE
        if not similar_docs:
            return {
                "action": "CREATE",
                "confidence": 0.95,
                "reason": "No similar content found in knowledge base",
                "similar_docs": [],
                "ai_analysis": "Content appears to be unique and should be created as new document"
            }
        
        # Use AI to analyze content similarity and recommend action
        ai_prompt = f"""You are an intelligent duplicate detection system. Analyze the new document against existing similar documents and recommend the best action.

NEW DOCUMENT:
Title: {title}
Content: {content[:1500]}{"..." if len(content) > 1500 else ""}

EXISTING SIMILAR DOCUMENTS:
"""
        
        for i, doc in enumerate(similar_docs[:3], 1):
            ai_prompt += f"""
Document {i}: {doc['title']} (ID: {doc['id']})
Summary: {doc['summary']}
Content Preview: {doc['content_preview']}
Last Modified: {doc['last_modified']}
---"""
        
        ai_prompt += f"""

Please analyze and provide:
1. Content similarity percentage (0-100%) for each existing document
2. Recommended action: UPDATE, DELETE, CREATE, or MERGE
3. Detailed reasoning for your recommendation
4. Which specific document to update/merge with (if applicable)

Guidelines:
- UPDATE: If new content is an improved version of existing content (>70% similar)
- DELETE: If existing content is clearly superior and new content adds no value (>85% similar)  
- MERGE: If both contents have valuable unique information (40-70% similar)
- CREATE: If content is sufficiently different and valuable (<40% similar)

Respond in JSON format:
{{
  "similarity_scores": [85, 60, 20],
  "recommended_action": "UPDATE|DELETE|CREATE|MERGE",
  "confidence": 0.85,
  "target_document_id": "doc-id-if-update-or-merge",
  "reasoning": "Detailed explanation of why this action is recommended",
  "merge_strategy": "How to combine documents if MERGE is recommended"
}}

Consider:
- Content quality and completeness
- Information uniqueness and value
- Documentation freshness and accuracy
- Knowledge base organization"""

        # Get AI analysis
        response = await ctx.sample(
            messages=ai_prompt,
            system_prompt="You are an expert knowledge management AI. Analyze content similarity and recommend the optimal action to maintain a high-quality, organized knowledge base. Always respond with valid JSON.",
            model_preferences=["claude-3-opus", "claude-3-sonnet", "gpt-4"],
            temperature=0.3,
            max_tokens=600
        )
        
        # Parse AI response
        ai_analysis = json.loads(response.text.strip())
        
        # Add similar documents to response
        ai_analysis["similar_docs"] = similar_docs
        ai_analysis["ai_analysis"] = response.text
        
        return ai_analysis
        
    except Exception as e:
        # Fallback to simple duplicate check if AI analysis fails
        return {
            "action": "CREATE",
            "confidence": 0.6,
            "reason": f"AI analysis failed ({str(e)}), defaulting to CREATE",
            "similar_docs": similar_docs if 'similar_docs' in locals() else [],
            "ai_analysis": f"Error during AI analysis: {str(e)}"
        }
