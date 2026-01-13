"""
Entity layer for redemption detail database operations.
"""

import logging
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class RedemptionDetail(BaseDataLayer):
    """
    Data layer for redemption detail database operations.
    """
    
    def create_redemption_detail_cancellation(
        self,
        investment_loan_id: int,
        lender_id: int,
        redemption_id: int,
        cancelled_amount: float,
        batch_id: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Create redemption detail record for loan cancellation.
        
        Args:
            investment_loan_id: Investment loan detail ID
            lender_id: Lender ID
            redemption_id: Lender redemption ID
            cancelled_amount: Cancelled amount
            batch_id: Batch ID (default 0 for cancellation)
            
        Returns:
            Dict with redemption detail ID or None
        """
        sql = """
            INSERT INTO t_redemption_details (
                investment_loan_id,
                lender_id,
                redemption_id,
                amount_redeemed,
                amount_received,
                principal_received,
                interest_received,
                fee_levied,
                batch_id,
                redemption_status,
                redemption_type,
                created_dtm,
                updated_dtm
            )
            VALUES (
                %(investment_loan_id)s,
                %(lender_id)s,
                %(redemption_id)s,
                0.00,
                %(cancelled_amount)s,
                %(cancelled_amount)s,
                0.00,
                0.00,
                %(batch_id)s,
                'PENDING',
                'LOAN_CANCELLATION',
                NOW(),
                NOW()
            )
            RETURNING id
        """
        
        params = {
            'investment_loan_id': investment_loan_id,
            'lender_id': lender_id,
            'redemption_id': redemption_id,
            'cancelled_amount': cancelled_amount,
            'batch_id': batch_id
        }
        return self.execute_fetch_one(sql, params)

