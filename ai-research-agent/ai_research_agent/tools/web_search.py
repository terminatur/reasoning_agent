"""
File: src/tools/web_search.py
Purpose: Web search tool using Tavily API for retrieving relevant information from the internet
Functionality: Performs web searches, extracts content, formats results with citations, and handles search optimization
Update Trigger: When Tavily API changes, search parameters need adjustment, or result formatting requirements change
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime

from ..config import config
from ..models import ToolSchema, Citation

class WebSearchTool:
    """
    Web search tool using Tavily API for comprehensive internet research.
    Supports various search modes and result filtering.
    """
    
    def __init__(self):
        self.api_key = config.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"
        self.max_results = config.WEB_SEARCH_MAX_RESULTS
        self.description = "Search the web for information on any topic using Tavily API"
    
    def get_schema(self) -> ToolSchema:
        """Return the tool schema for the agent to understand how to use this tool."""
        return ToolSchema(
            name="web_search",
            description="Search the web for current information on any topic",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant information"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "description": "Depth of search - basic for quick results, advanced for comprehensive research",
                    "default": "basic"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (1-20)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                },
                "include_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to prioritize in search results",
                    "default": []
                },
                "exclude_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to exclude from search results",
                    "default": []
                }
            },
            required_parameters=["query"]
        )
    
    def validate_input(self, query: str, **kwargs) -> None:
        """Validate input parameters."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        max_results = kwargs.get("max_results", 5)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            raise ValueError("max_results must be an integer between 1 and 20")
        
        search_depth = kwargs.get("search_depth", "basic")
        if search_depth not in ["basic", "advanced"]:
            raise ValueError("search_depth must be 'basic' or 'advanced'")
    
    def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute web search and return formatted results."""
        # Validate inputs
        self.validate_input(query, **kwargs)
        
        # Check API key
        if not self.api_key:
            return {
                "error": "Tavily API key not configured. Please set TAVILY_API_KEY environment variable.",
                "results": [],
                "citations": []
            }
        
        try:
            # Prepare search parameters
            search_params = self._prepare_search_params(query, **kwargs)
            
            # Perform search
            response = self._make_api_request(search_params)
            
            # Process and format results
            formatted_results = self._process_results(response, query)
            
            return formatted_results
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "citations": []
            }
    
    def _prepare_search_params(self, query: str, **kwargs) -> Dict[str, Any]:
        """Prepare parameters for Tavily API request."""
        params = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": kwargs.get("search_depth", "basic"),
            "max_results": min(kwargs.get("max_results", 5), self.max_results),
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False
        }
        
        # Add domain filters if provided
        include_domains = kwargs.get("include_domains", [])
        exclude_domains = kwargs.get("exclude_domains", [])
        
        if include_domains:
            params["include_domains"] = include_domains
        
        if exclude_domains:
            params["exclude_domains"] = exclude_domains
        
        return params
    
    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Tavily API."""
        try:
            response = requests.post(
                self.base_url,
                json=params,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def _process_results(self, response: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process API response and format results."""
        results = []
        citations = []
        
        # Extract answer if available
        answer = response.get("answer", "")
        
        # Process search results
        search_results = response.get("results", [])
        
        for idx, result in enumerate(search_results, 1):
            # Format result content
            content = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "published_date": result.get("published_date")
            }
            results.append(content)
            
            # Create citation
            citation = Citation(
                source_url=result.get("url"),
                title=result.get("title", f"Search Result {idx}"),
                author=None,  # Tavily doesn't provide author info
                publication_date=self._parse_date(result.get("published_date")),
                accessed_date=datetime.now(),
                snippet=result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                relevance_score=result.get("score", 0.5)
            )
            citations.append(citation)
        
        return {
            "query": query,
            "answer": answer,
            "results": results,
            "citations": [citation.dict() for citation in citations],
            "total_results": len(results),
            "search_time": datetime.now().isoformat()
        }
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                try:
                    return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Alternative entry point for backward compatibility."""
        query = kwargs.get("query", "")
        return self.execute(query, **kwargs)
