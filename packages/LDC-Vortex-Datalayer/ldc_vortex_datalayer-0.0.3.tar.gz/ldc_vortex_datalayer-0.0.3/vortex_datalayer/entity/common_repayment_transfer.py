"""
Common Repayment Transfer Entity for handling operations on fmpp_vortex_common_repayment_transfer table.
This module provides entity class for common repayment transfer operations.
"""

import logging
from typing import Dict, Any, Optional, List

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class CommonRepaymentTransfer(BaseDataLayer):
    """
    Entity class for common repayment transfer operations.
    
    Table Schema (fmpp_vortex_common_repayment_transfer):
    - id: BIGSERIAL (Primary Key)
    - is_processed_fmpp: BOOLEAN
    - is_processed_vortex: BOOLEAN
    - transaction_id: VARCHAR(30)
    - loan_id: VARCHAR(21)
    - Unique constraint: (loan_id, transaction_id)
    """
    
    def get_pending_for_vortex(self, batch_size: int = 5000) -> List[Dict[str, Any]]:
        """
        Get pending repayment records for Vortex processing.
        
        Args:
            batch_size: Maximum number of records to return
            
        Returns:
            List of repayment records ready for Vortex processing
        """
        sql = """
            SELECT 
                id,
                loan_id,
                transaction_id,
                emi_amount,
                facilitation_fee,
                collection_fee,
                recovery_fee,
                purpose,
                days_past_due,
                transaction_date,
                settlement_date,
                created_dtm
            FROM fmpp_vortex_common_repayment_transfer
            WHERE is_processed_vortex = false
              AND settlement_date IS NOT NULL
              AND emi_amount > 0
            ORDER BY id
            LIMIT %(batch_size)s
        """
        
        params = {'batch_size': batch_size}
        return self.execute_fetch_all(sql, params)
    
    def mark_as_processed_vortex(self, transaction_ids: List[str]) -> int:
        """
        Mark repayment records as processed by Vortex.
        
        Args:
            transaction_ids: List of transaction IDs to mark as processed
            
        Returns:
            Number of records updated
        """
        if not transaction_ids:
            return 0
            
        sql = """
            UPDATE fmpp_vortex_common_repayment_transfer
            SET is_processed_vortex = true,
                updated_dtm = NOW()
            WHERE transaction_id = ANY(%(transaction_ids)s)
              AND is_processed_vortex = false
        """
        
        params = {'transaction_ids': transaction_ids}
        return self.execute_update(sql, params)
    
    def get_conflict_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get records that had conflicts during insertion (from error log).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of conflict records
        """
        sql = """
            SELECT 
                err_details,
                err_message,
                created_dtm
            FROM t_error_log
            WHERE sp_name IN (
                'prc_repayments_lms_to_vortex_common_table_migration',
                'prc_repayments_pp_to_vortex_common_table_migration'
            )
              AND err_state = '23505'
            ORDER BY created_dtm DESC
            LIMIT %(limit)s
        """
        
        params = {'limit': limit}
        return self.execute_fetch_all(sql, params)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about common repayment transfer table.
        
        Returns:
            Dictionary with statistics
        """
        sql = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(*) FILTER (WHERE is_processed_fmpp = true) as processed_fmpp,
                COUNT(*) FILTER (WHERE is_processed_vortex = true) as processed_vortex,
                COUNT(*) FILTER (WHERE is_processed_fmpp = false AND is_processed_vortex = false) as pending_both,
                COUNT(*) FILTER (WHERE is_processed_fmpp = true AND is_processed_vortex = false) as pending_vortex,
                COUNT(*) FILTER (WHERE is_processed_fmpp = false AND is_processed_vortex = true) as pending_fmpp,
                COUNT(*) FILTER (WHERE settlement_date IS NOT NULL AND is_processed_vortex = false) as pending_vortex_with_settlement
            FROM fmpp_vortex_common_repayment_transfer
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result if result else {}

