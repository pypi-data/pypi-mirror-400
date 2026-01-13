"""
Repayment Processing Logs Entity for handling CRUD operations on t_repayment_processing_logs table.
"""

import logging
from typing import Dict, Any, Optional

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class RepaymentBatchSummary(BaseDataLayer):
    """
    Production-level operations for t_repayment_processing_logs table.
    
    Table Schema:
    - id: BIGSERIAL (Primary Key) - used as batch_id in t_loan_repayment_detail
    - batch_id: VARCHAR(30) (Unique batch identifier)
    - status: VARCHAR(20) (PENDING, PROCESSING, COMPLETED, FAILED)
    - total_loans: INTEGER
    - processed_loans: INTEGER
    - failed_loans: INTEGER
    - created_dtm: TIMESTAMP WITH TIME ZONE
    - updated_dtm: TIMESTAMP WITH TIME ZONE
    - error_message: TEXT (optional)
    """

    def create_batch(self, batch_id: str, total_loans: int = 0) -> int:
        """
        Create a new repayment batch summary record.
        
        Args:
            batch_id: Unique batch identifier (max 30 chars, format: YYYYMMDDHHMMSS_XXXX)
            total_loans: Total number of loans in this batch
            
        Returns:
            int: The ID of the created batch record
        """
        sql = """
            INSERT INTO t_repayment_processing_logs (
                batch_id, status, total_loans, processed_loans, failed_loans,
                created_dtm, updated_dtm
            )
            VALUES (
                %(batch_id)s, 'PENDING', %(total_loans)s, 0, 0,
                NOW(), NOW()
            )
            RETURNING id
        """
        
        params = {
            'batch_id': batch_id,
            'total_loans': total_loans
        }
        
        result = self.execute_fetch_one(sql, params, index_result=True)
        logger.info(f"Created repayment batch with ID: {result}, batch_id: {batch_id}")
        return result

    def update_batch_status(self, batch_id: int, status: str, 
                           processed_loans: Optional[int] = None,
                           failed_loans: Optional[int] = None,
                           error_message: Optional[str] = None) -> bool:
        """
        Update batch status and metrics.
        
        Args:
            batch_id: Batch record ID
            status: New status (PENDING, PROCESSING, COMPLETED, FAILED)
            processed_loans: Number of processed loans (optional)
            failed_loans: Number of failed loans (optional)
            error_message: Error message if failed (optional)
            
        Returns:
            bool: True if update successful
        """
        updates = ['status = %(status)s', 'updated_dtm = NOW()']
        params = {'batch_id': batch_id, 'status': status}
        
        if processed_loans is not None:
            updates.append('processed_loans = %(processed_loans)s')
            params['processed_loans'] = processed_loans
            
        if failed_loans is not None:
            updates.append('failed_loans = %(failed_loans)s')
            params['failed_loans'] = failed_loans
            
        if error_message is not None:
            updates.append('error_message = %(error_message)s')
            params['error_message'] = error_message
        
        sql = f"""
            UPDATE t_repayment_processing_logs
            SET {', '.join(updates)}
            WHERE id = %(batch_id)s
        """
        
        self.execute_query(sql, params)
        logger.info(f"Updated batch {batch_id} to status: {status}")
        return True

    def get_batch_by_id(self, batch_id: int) -> Optional[Dict[str, Any]]:
        """
        Get batch summary by ID.
        
        Args:
            batch_id: Batch record ID
            
        Returns:
            Dict containing batch information or None
        """
        sql = """
            SELECT 
                id, batch_id, status, total_loans, processed_loans, failed_loans,
                created_dtm, updated_dtm, error_message
            FROM t_repayment_processing_logs
            WHERE id = %(batch_id)s
        """
        
        params = {'batch_id': batch_id}
        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_batch_by_batch_id(self, batch_id_str: str) -> Optional[Dict[str, Any]]:
        """
        Get batch summary by batch_id string.
        
        Args:
            batch_id_str: Batch identifier string
            
        Returns:
            Dict containing batch information or None
        """
        sql = """
            SELECT 
                id, batch_id, status, total_loans, processed_loans, failed_loans,
                created_dtm, updated_dtm, error_message
            FROM t_repayment_processing_logs
            WHERE batch_id = %(batch_id)s
        """
        
        params = {'batch_id': batch_id_str}
        return self.execute_fetch_one(sql, params, to_dict=True)
