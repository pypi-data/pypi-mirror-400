from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch


def create_custom_tools(es_client: Elasticsearch, index: str) -> List[Any]:
    """
    Create custom Elasticsearch tools.
    
    Args:
        es_client: The Elasticsearch client instance
        index: The default index to operate on
        
    Returns:
        List of tool functions
    """
    
    def advanced_search(
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Perform an advanced search with optional filters.
        
        Args:
            query: The search query string
            filters: Optional dictionary of filters (term, range, etc.)
            size: Number of results to return (default: 10)
            
        Returns:
            Search results
        """
        # Build the Elasticsearch query
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}}
                    ]
                }
            }
        }
        
        # Add filters if provided
        if filters:
            filter_clauses = []
            for field, value in filters.items():
                if isinstance(value, list):
                    filter_clauses.append({"terms": {field: value}})
                else:
                    filter_clauses.append({"term": {field: value}})
            
            es_query["query"]["bool"]["filter"] = filter_clauses
            
        # Use the Elasticsearch client's search method
        response = es_client.search(
            index=index,
            body=es_query,
            size=size
        )
        return response
        
    # Return the tool functions
    return [advanced_search]
