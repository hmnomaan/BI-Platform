"""
Search service provider implementations.
"""
import requests
from typing import Dict, Any, Optional, List

from ..core.abstract_providers import SearchProvider
from ..utils.logging import get_logger


class ElasticsearchProvider(SearchProvider):
    """Elasticsearch provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Elasticsearch provider.
        
        Args:
            config: Configuration dictionary with 'host', 'port' (optional),
                   'username', 'password' (optional), 'use_ssl' (optional)
        """
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 9200)
        self.username = config.get("username")
        self.password = config.get("password")
        self.use_ssl = config.get("use_ssl", False)
        
        protocol = "https" if self.use_ssl else "http"
        self.base_url = f"{protocol}://{self.host}:{self.port}"
        
        self.logger = get_logger("ElasticsearchProvider")
    
    def _get_auth(self) -> Optional[tuple]:
        """Get authentication tuple if credentials provided."""
        if self.username and self.password:
            return (self.username, self.password)
        return None
    
    def search(self, query: str, index: str,
              filters: Optional[Dict[str, Any]] = None,
              limit: int = 10) -> List[Dict[str, Any]]:
        """Perform a search query in Elasticsearch."""
        url = f"{self.base_url}/{index}/_search"
        
        # Build query
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["*"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            },
            "size": limit
        }
        
        # Add filters
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                filter_clauses.append({"term": {key: value}})
            
            if filter_clauses:
                search_query["query"]["bool"]["filter"] = filter_clauses
        
        try:
            response = requests.post(
                url,
                json=search_query,
                auth=self._get_auth()
            )
            response.raise_for_status()
            
            result = response.json()
            hits = result.get("hits", {}).get("hits", [])
            
            # Extract source documents
            documents = [hit.get("_source", {}) for hit in hits]
            
            self.logger.info(f"Search returned {len(documents)} results")
            return documents
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def index_document(self, document_id: str, document: Dict[str, Any],
                      index: str) -> bool:
        """Index a document in Elasticsearch."""
        url = f"{self.base_url}/{index}/_doc/{document_id}"
        
        try:
            response = requests.put(
                url,
                json=document,
                auth=self._get_auth()
            )
            response.raise_for_status()
            
            self.logger.info(f"Document indexed successfully: {document_id}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to index document: {e}")
            return False

