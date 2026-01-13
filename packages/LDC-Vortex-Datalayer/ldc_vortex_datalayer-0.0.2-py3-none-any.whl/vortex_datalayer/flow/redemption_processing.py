"""
Flow layer for redemption processing business logic.
This layer handles complex multi-step business processes and database operations for redemption processing.
"""

import logging
from typing import Dict, Any, Optional, List

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class RedemptionProcessingFlow(BaseDataLayer):
    """
    Flow for handling redemption processing business logic and database operations.
    Orchestrates complex multi-step processes for processing redemption details and creating summary records.
    """

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)

    def get_unprocessed_lender_ids(self, limit: Optional[int] = None) -> List[int]:
        """
        Get distinct lender IDs that have unprocessed redemption details.
        
        Args:
            limit: Maximum number of lender IDs to return (None for all)
            
        Returns:
            List of lender IDs
        """
        sql = """
            SELECT DISTINCT trd.lender_id
            FROM t_redemption_details trd
            WHERE trd.redemption_status = 'SCHEDULED'
              AND trd.redemption_id IS NULL
              AND trd.redemption_type = 'REPAYMENT'
            ORDER BY trd.lender_id
        """
        
        if limit:
            sql += f" LIMIT {limit}"
        
        results = self.execute_fetch_all(sql, to_dict=False)
        return [row[0] for row in results] if results else []

    def get_unprocessed_redemption_count(self) -> int:
        """
        Get count of unprocessed redemption details.
        
        Returns:
            int: Number of unprocessed redemption details
        """
        sql = """
            SELECT COUNT(*) as count
            FROM t_redemption_details
            WHERE redemption_status = 'SCHEDULED'
              AND redemption_id IS NULL
              AND redemption_type = 'REPAYMENT'
        """
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['count'] if result else 0

    def execute_redemption_procedure(self, lender_ids: List[int]) -> tuple:
        """
        Execute redemption processing stored procedure for a batch of lender IDs.
        
        Args:
            lender_ids: List of lender IDs to process
            
        Returns:
            Tuple of (result, params) from stored procedure
        """
        params = [lender_ids, None]  # lender_ids (array), inout_response (INOUT)
        
        result = self.execute_procedure(
            procedure_name='prc_process_redemption_batch',
            params=params,
            fetch_one=True,
            to_dict=False
        )
        
        return result, params

    def execute_redemption_processing(self, lender_ids: List[int]) -> Dict[str, Any]:
        """
        Execute redemption processing for a batch of lender IDs.
        
        Args:
            lender_ids: List of lender IDs to process
            
        Returns:
            Dict with processing results
        """
        if not lender_ids:
            return {
                'success': False,
                'message': 'No lender IDs provided',
                'processed_lenders': 0
            }
        
        try:
            result, params = self.execute_redemption_procedure(lender_ids)
            
            # Handle INOUT parameter
            response_value = params[1] if params[1] is not None else (
                result[-1] if isinstance(result, tuple) and len(result) > 0 else result
            )
            
            if response_value == 0:
                return {
                    'success': True,
                    'message': 'Redemption processing completed successfully',
                    'processed_lenders': len(lender_ids),
                    'lender_ids': lender_ids
                }
            else:
                return {
                    'success': False,
                    'message': f'Redemption processing failed with code: {response_value}',
                    'processed_lenders': 0,
                    'lender_ids': lender_ids
                }
                
        except Exception as e:
            logger.error(f"Error executing redemption processing: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Error executing redemption processing: {str(e)}',
                'processed_lenders': 0,
                'lender_ids': lender_ids
            }

    def get_redemption_statistics(self) -> Dict[str, Any]:
        """
        Get redemption processing statistics.
        
        Returns:
            Dict with statistics by status
        """
        sql = """
            SELECT 
                redemption_status,
                COUNT(*) as redemption_count,
                COUNT(DISTINCT lender_id) as lender_count,
                SUM(amount_received) as total_amount_received,
                SUM(principal_received) as total_principal,
                SUM(interest_received) as total_interest,
                SUM(fee_levied) as total_fee_levied
            FROM t_redemption_details
            WHERE redemption_id IS NULL
            GROUP BY redemption_status
        """
        results = self.execute_fetch_all(sql, to_dict=True)
        return results if results else []

    def get_lender_redemption_by_lender_id(self, lender_id: int) -> Optional[Dict[str, Any]]:
        """
        Get lender redemption record by lender ID.
        
        Args:
            lender_id: Lender ID
            
        Returns:
            Dict with lender redemption details or None
        """
        sql = """
            SELECT 
                id,
                lender_id,
                total_amount_redeemed,
                total_amount_received,
                total_principal,
                total_interest,
                total_fee_levied,
                redemption_status,
                urn_id,
                status_dtm,
                created_dtm,
                updated_dtm
            FROM t_lender_redemption
            WHERE lender_id = %(lender_id)s
              AND deleted IS NULL
            ORDER BY created_dtm DESC
            LIMIT 1
        """
        params = {'lender_id': lender_id}
        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_redemption_summary_by_lender(self, lender_id: int) -> List[Dict[str, Any]]:
        """
        Get redemption summary records for a lender.
        
        Args:
            lender_id: Lender ID
            
        Returns:
            List of redemption summary records
        """
        sql = """
            SELECT 
                id,
                lender_id,
                investment_id,
                total_amount_redeemed,
                total_amount_received,
                total_principal,
                total_interest,
                total_fee_levied,
                type,
                redemption_status,
                urn_id,
                redemption_id,
                created_dtm,
                updated_dtm
            FROM t_redemption_summary
            WHERE lender_id = %(lender_id)s
              AND deleted IS NULL
            ORDER BY investment_id, created_dtm DESC
        """
        params = {'lender_id': lender_id}
        return self.execute_fetch_all(sql, params, to_dict=True)
