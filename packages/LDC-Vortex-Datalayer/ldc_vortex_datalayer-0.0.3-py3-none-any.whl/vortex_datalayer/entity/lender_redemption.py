"""
Entity layer for lender redemption database operations.
"""

import logging
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class LenderRedemption(BaseDataLayer):
    """
    Data layer for lender redemption database operations.
    """
    
    def create_lender_redemption_cancellation(
        self,
        lender_id: int,
        cancelled_amount: float
    ) -> Optional[Dict[str, Any]]:
        """
        Create lender redemption record for loan cancellation.
        
        Args:
            lender_id: Lender ID
            cancelled_amount: Cancelled amount
            
        Returns:
            Dict with redemption_id or None
        """
        sql = """
            INSERT INTO t_lender_redemption (
                lender_id,
                total_amount_redeemed,
                total_amount_received,
                total_principal,
                total_interest,
                total_fee_levied,
                redemption_status,
                redemption_type,
                status_dtm,
                created_dtm,
                updated_dtm
            )
            VALUES (
                %(lender_id)s,
                0.00,
                %(cancelled_amount)s,
                %(cancelled_amount)s,
                0.00,
                0.00,
                'PENDING',
                'LOAN_CANCELLATION',
                NOW(),
                NOW(),
                NOW()
            )
            RETURNING id as redemption_id
        """
        
        params = {
            'lender_id': lender_id,
            'cancelled_amount': cancelled_amount
        }
        return self.execute_fetch_one(sql, params)

