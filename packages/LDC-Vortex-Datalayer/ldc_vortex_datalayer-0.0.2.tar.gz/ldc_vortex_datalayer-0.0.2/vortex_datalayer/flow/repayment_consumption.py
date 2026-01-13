"""
Flow layer for repayment consumption business logic.
This layer handles complex multi-step business processes and database operations for repayment consumption.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from ..base_layer import BaseDataLayer
from ..entity.repayment_batch_summary import RepaymentBatchSummary

logger = logging.getLogger('normal')


class RepaymentConsumptionFlow(BaseDataLayer):
    """
    Flow for handling repayment consumption business logic and database operations.
    Orchestrates complex multi-step processes for consuming repayments and distributing to investments.
    """

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        self.batch_summary_entity = RepaymentBatchSummary(db_alias)

    def get_unprocessed_loan_ids(self, limit: Optional[int] = None) -> List[int]:
        """
        Get distinct loan IDs that have unprocessed repayments.
        
        Args:
            limit: Maximum number of loan IDs to return (None for all)
            
        Returns:
            List of loan IDs
        """
        sql = """
            SELECT DISTINCT loan_id
            FROM t_loan_repayment_detail
            WHERE is_processed = false
            ORDER BY loan_id
        """
        
        if limit:
            sql += f" LIMIT {limit}"
        
        results = self.execute_fetch_all(sql, to_dict=False)
        return [row[0] for row in results] if results else []

    def get_unprocessed_repayment_count(self) -> int:
        """
        Get count of unprocessed repayments.
        
        Returns:
            int: Number of unprocessed repayments
        """
        sql = """
            SELECT COUNT(*) as count
            FROM t_loan_repayment_detail
            WHERE is_processed = false
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['count'] if result else 0

    def get_loan_ids_with_unprocessed_repayments(self, batch_size: int = 1000) -> List[List[int]]:
        """
        Get loan IDs grouped into batches of specified size.
        
        Args:
            batch_size: Number of loan IDs per batch (default: 1000)
            
        Returns:
            List of lists, each containing up to batch_size loan IDs
        """
        loan_ids = self.get_unprocessed_loan_ids()
        
        # Group into batches
        batches = []
        for i in range(0, len(loan_ids), batch_size):
            batches.append(loan_ids[i:i + batch_size])
        
        return batches

    def fetch_batch_status_metrics(self) -> List[Dict[str, Any]]:
        """
        Execute batch processing statistics query.
        
        Returns:
            List of dicts containing batch statistics
        """
        sql = """
            SELECT 
                status,
                COUNT(*) as batch_count,
                SUM(total_loans) as total_loans,
                SUM(processed_loans) as processed_loans,
                SUM(failed_loans) as failed_loans
            FROM t_repayment_processing_logs
            GROUP BY status
        """
        
        results = self.execute_fetch_all(sql, to_dict=True)
        return results if results else []

    def get_batch_statistics(self) -> Dict[str, Any]:
        """
        Get batch processing statistics grouped by status.
        
        Returns:
            Dict containing batch statistics
        """
        results = self.fetch_batch_status_metrics()
        
        # Format results
        stats = {}
        for row in results:
            stats[row['status']] = {
                'batch_count': row['batch_count'],
                'total_loans': row['total_loans'],
                'processed_loans': row['processed_loans'],
                'failed_loans': row['failed_loans']
            }
        
        return stats

    def execute_repayment_procedure(self, loan_ids: List[int], batch_id_str: str) -> Tuple[Any, List]:
        """
        Execute repayment processing stored procedure for a batch of loan IDs.
        
        Args:
            loan_ids: List of loan IDs to process
            batch_id_str: Batch identifier string (format: YYYYMMDDHHMMSS_XXXX)
            
        Returns:
            Tuple of (result, params) from stored procedure
        """
        # PostgreSQL array parameter - psycopg2 handles Python list to array conversion
        # Procedure signature: prc_process_repayments(loan_ids bigint[], batch_id_str varchar(30), inout_response integer)
        params = [loan_ids, batch_id_str, None]  # loan_ids (array), batch_id_str, inout_response (INOUT)
        
        result = self.execute_procedure(
            procedure_name='prc_process_repayments',
            params=params,
            fetch_one=True,
            to_dict=False
        )
        
        return result, params

    def execute_repayment_processing(self, loan_ids: List[int], batch_id_str: str) -> Dict[str, Any]:
        """
        Execute repayment processing for a batch of loan IDs.
        
        Args:
            loan_ids: List of loan IDs to process
            batch_id_str: Batch identifier string (format: YYYYMMDDHHMMSS_XXXX)
            
        Returns:
            Dict containing processing results
        """
        try:
            result, params = self.execute_repayment_procedure(loan_ids, batch_id_str)
            
            # The INOUT parameter is returned as the last element
            # For INOUT parameters, psycopg2 returns them in the result
            # Check if result is a tuple or if we need to get the INOUT value differently
            if isinstance(result, tuple):
                # The INOUT parameter is typically the last parameter returned
                response_value = result[-1] if len(result) > 0 else None
            else:
                response_value = result
            
            # Also check params array as INOUT parameters modify the params list
            if params[2] is not None:
                response_value = params[2]
            
            if response_value == 0:
                return {
                    'status': 'SUCCESS',
                    'message': 'Repayment processing completed successfully',
                    'loan_ids_count': len(loan_ids)
                }
            else:
                return {
                    'status': 'ERROR',
                    'message': f'Repayment processing failed with code: {response_value}',
                    'loan_ids_count': len(loan_ids)
                }
                
        except Exception as e:
            logger.error(f"Error executing repayment processing: {str(e)}")
            return {
                'status': 'ERROR',
                'message': str(e),
                'loan_ids_count': len(loan_ids)
            }

    def get_batch_by_batch_id_str(self, batch_id_str: str) -> Optional[Dict[str, Any]]:
        """
        Get batch by batch_id string.
        
        Args:
            batch_id_str: Batch identifier string
            
        Returns:
            Dict containing batch information or None
        """
        return self.batch_summary_entity.get_batch_by_batch_id(batch_id_str)
