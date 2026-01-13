"""
Entity layer for borrower-related database operations.
"""

from typing import Optional
from ..base_layer import BaseDataLayer


class Borrower(BaseDataLayer):
    """
    Data layer for borrower related database operations.
    """
    
    def fetch_borrower_by_source(self, source: str, source_id: str) -> Optional[dict]:
        """
        Get borrower by source and source_id.
        
        Args:
            source: Source system
            source_id: Borrower ID in source system
            
        Returns:
            Dict with borrower id if exists, None otherwise
        """
        sql = """
            SELECT id
            FROM t_borrowers
            WHERE source = %(source)s
              AND source_id = %(source_id)s
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'source': source,
            'source_id': source_id
        }
        result = self.execute_fetch_one(sql, params)
        return result if result else None
    
    def create(self, source: str, source_id: str) -> int:
        """
        Create a new borrower.
        
        Args:
            source: Source system
            source_id: Borrower ID in source system
            
        Returns:
            Borrower ID
        """
        sql = """
            INSERT INTO t_borrowers (source, source_id)
            VALUES (%(source)s, %(source_id)s)
            RETURNING id
        """
        
        params = {
            'source': source,
            'source_id': source_id
        }
        result = self.execute_fetch_one(sql, params)
        return result['id']

