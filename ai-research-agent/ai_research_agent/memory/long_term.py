"""
File: src/memory/long_term.py
Purpose: Long-term persistent memory management using vector database for semantic storage and retrieval
Functionality: Stores and retrieves research findings, maintains episodic memory, and provides semantic search capabilities
Update Trigger: When vector database integration changes, embedding models are updated, or memory retrieval strategies are modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
import hashlib

try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from ..config import config
from ..models import MemoryEntry, ResearchReport, Citation

class LongTermMemory:
    """
    Manages long-term persistent memory using vector database.
    Handles semantic storage, episodic memory, and knowledge retrieval.
    """
    
    def __init__(self):
        self.index_name = config.PINECONE_INDEX_NAME
        self.pc: Optional[Any] = None
        self.index: Optional[Any] = None
        self.embedding_dimension = 1536  # OpenAI text-embedding-ada-002 dimension
        self.initialized = False
        
        if PINECONE_AVAILABLE and config.PINECONE_API_KEY:
            try:
                self._initialize_pinecone()
            except Exception as e:
                print(f"Warning: Could not initialize Pinecone: {e}")
        else:
            print("Warning: Pinecone not available. Long-term memory will use local storage.")
            self.local_memory: Dict[str, Any] = {}
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone connection and index."""
        try:
            self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            self.initialized = True
            print(f"Pinecone initialized successfully with index: {self.index_name}")
            
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            self.initialized = False
    
    def store_research_finding(self, content: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None) -> str:
        """Store a research finding in long-term memory."""
        # Generate unique ID
        content_hash = hashlib.md5(content.encode()).hexdigest()
        memory_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_hash[:8]}"
        
        # Prepare metadata
        storage_metadata = {
            "content": content,
            "type": "research_finding",
            "timestamp": datetime.now().isoformat(),
            "importance": metadata.get("importance", 0.5),
            **metadata
        }
        
        if self.initialized and embedding:
            try:
                # Store in Pinecone
                self.index.upsert(
                    vectors=[(memory_id, embedding, storage_metadata)]
                )
                print(f"Stored research finding in Pinecone: {memory_id}")
            except Exception as e:
                print(f"Error storing in Pinecone: {e}")
                # Fallback to local storage
                self._store_locally(memory_id, content, storage_metadata)
        else:
            # Store locally
            self._store_locally(memory_id, content, storage_metadata)
        
        return memory_id
    
    def store_citation(self, citation: Citation) -> str:
        """Store a citation in long-term memory."""
        citation_id = f"citation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{citation.title[:20].replace(' ', '_')}"
        
        metadata = {
            "type": "citation",
            "title": citation.title,
            "author": citation.author,
            "source_url": citation.source_url,
            "publication_date": citation.publication_date.isoformat() if citation.publication_date else None,
            "accessed_date": citation.accessed_date.isoformat(),
            "relevance_score": citation.relevance_score,
            "timestamp": datetime.now().isoformat()
        }
        
        content = f"Citation: {citation.title}\nSnippet: {citation.snippet}"
        
        if self.initialized:
            try:
                # For citations, we don't need embeddings as they're primarily metadata
                self._store_locally(citation_id, content, metadata)
            except Exception as e:
                print(f"Error storing citation: {e}")
        else:
            self._store_locally(citation_id, content, metadata)
        
        return citation_id
    
    def store_research_report(self, report: ResearchReport) -> str:
        """Store a complete research report."""
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{report.query[:20].replace(' ', '_')}"
        
        metadata = {
            "type": "research_report",
            "query": report.query,
            "word_count": report.word_count,
            "methodology": report.methodology,
            "generated_at": report.generated_at.isoformat(),
            "timestamp": datetime.now().isoformat(),
            "importance": 0.9  # Research reports are high importance
        }
        
        # Combine all report content
        content = f"""
        Query: {report.query}
        
        Executive Summary:
        {report.executive_summary}
        
        Detailed Findings:
        {report.detailed_findings}
        
        Conclusions:
        {report.conclusions}
        
        Methodology: {report.methodology}
        """
        
        if self.initialized:
            try:
                self._store_locally(report_id, content.strip(), metadata)
                
                # Also store citations from the report
                for citation in report.citations:
                    self.store_citation(citation)
                    
            except Exception as e:
                print(f"Error storing research report: {e}")
        else:
            self._store_locally(report_id, content.strip(), metadata)
        
        return report_id
    
    def search_memories(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search long-term memory for relevant content."""
        if self.initialized:
            try:
                return self._search_pinecone(query, memory_type, limit)
            except Exception as e:
                print(f"Error searching Pinecone: {e}")
                return self._search_locally(query, memory_type, limit)
        else:
            return self._search_locally(query, memory_type, limit)
    
    def get_related_findings(self, topic: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get research findings related to a specific topic."""
        return self.search_memories(topic, memory_type="research_finding", limit=limit)
    
    def get_citation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent citation history."""
        return self.search_memories("", memory_type="citation", limit=limit)
    
    def get_research_reports(self, query_filter: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get stored research reports."""
        if query_filter:
            return self.search_memories(query_filter, memory_type="research_report", limit=limit)
        else:
            return self.search_memories("", memory_type="research_report", limit=limit)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about long-term memory usage."""
        if self.initialized:
            try:
                stats = self.index.describe_index_stats()
                return {
                    "vector_count": stats.total_vector_count,
                    "dimension": stats.dimension,
                    "index_fullness": stats.index_fullness,
                    "namespaces": stats.namespaces,
                    "backend": "pinecone"
                }
            except Exception as e:
                print(f"Error getting Pinecone stats: {e}")
        
        # Local storage stats
        return {
            "local_entries": len(self.local_memory) if hasattr(self, 'local_memory') else 0,
            "backend": "local"
        }
    
    def _store_locally(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Store memory entry locally as fallback."""
        if not hasattr(self, 'local_memory'):
            self.local_memory = {}
        
        self.local_memory[memory_id] = {
            "content": content,
            "metadata": metadata
        }
    
    def _search_locally(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search local memory storage."""
        if not hasattr(self, 'local_memory'):
            return []
        
        results = []
        query_lower = query.lower()
        
        for memory_id, data in self.local_memory.items():
            content = data["content"]
            metadata = data["metadata"]
            
            # Filter by type if specified
            if memory_type and metadata.get("type") != memory_type:
                continue
            
            # Simple text matching
            if not query or query_lower in content.lower():
                score = 1.0 if not query else content.lower().count(query_lower) / len(content)
                
                results.append({
                    "id": memory_id,
                    "content": content,
                    "metadata": metadata,
                    "score": score
                })
        
        # Sort by score and timestamp
        results.sort(key=lambda x: (x["score"], x["metadata"].get("timestamp", "")), reverse=True)
        
        return results[:limit]
    
    def _search_pinecone(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone vector database."""
        # Note: This would require generating embeddings for the query
        # For now, return empty results as we'd need OpenAI integration for embeddings
        print("Pinecone search not fully implemented - requires embedding generation")
        return []
    
    def clear_memory(self, memory_type: Optional[str] = None) -> bool:
        """Clear long-term memory entries."""
        try:
            if self.initialized:
                if memory_type:
                    # Would need to implement filtered deletion in Pinecone
                    print(f"Filtered deletion not implemented for type: {memory_type}")
                    return False
                else:
                    # Delete entire index
                    self.pc.delete_index(self.index_name)
                    self._initialize_pinecone()
                    return True
            else:
                # Clear local memory
                if memory_type:
                    to_delete = [
                        mid for mid, data in self.local_memory.items()
                        if data["metadata"].get("type") == memory_type
                    ]
                    for mid in to_delete:
                        del self.local_memory[mid]
                else:
                    self.local_memory.clear()
                return True
                
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def export_memory(self, file_path: str) -> bool:
        """Export memory to a JSON file."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "backend": "pinecone" if self.initialized else "local",
                "memories": []
            }
            
            if hasattr(self, 'local_memory'):
                for memory_id, data in self.local_memory.items():
                    export_data["memories"].append({
                        "id": memory_id,
                        "content": data["content"],
                        "metadata": data["metadata"]
                    })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting memory: {e}")
            return False
