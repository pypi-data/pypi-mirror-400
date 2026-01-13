"""
Entity layer for transaction ID generation.
"""

import logging
from typing import Optional
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class TransactionId(BaseDataLayer):
    """
    Data layer for transaction ID generation operations.
    """
    
    def generate_transaction_id(self, prefix: Optional[str] = None) -> str:
        """
        Generate a transaction ID using the database function.
        
        Args:
            prefix: Optional prefix for the transaction ID (e.g., 'INVW')
            
        Returns:
            Generated transaction ID string
            
        Raises:
            Exception: If transaction ID generation fails or returns None
        """
        sql = "SELECT fn_generate_txn_id(%s)"
        result = self.execute_query(sql, [prefix], fetch_single_column=True)
        
        if not result:
            raise Exception("Failed to generate transaction ID: function returned None")
        
        transaction_id = str(result).strip()
        if not transaction_id:
            raise Exception("Failed to generate transaction ID: empty result")
        
        return transaction_id

