"""
Entity layer for redemption summary database operations.
"""

import logging
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class RedemptionSummary(BaseDataLayer):
    """
    Data layer for redemption summary database operations.
    """
    
    def create_redemption_summary_cancellation(
        self,
        lender_id: int,
        investment_id: int,
        redemption_id: int,
        cancelled_amount: float,
        investment_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create redemption summary record for loan cancellation.
        
        Args:
            lender_id: Lender ID
            investment_id: Investment ID
            redemption_id: Lender redemption ID
            cancelled_amount: Cancelled amount
            investment_type: Investment type (from redemption_summary_types enum)
            
        Returns:
            Dict with redemption summary ID or None
        """
        sql = """
            INSERT INTO t_redemption_summary (
                lender_id,
                investment_id,
                total_amount_redeemed,
                total_amount_received,
                total_principal,
                total_interest,
                total_fee_levied,
                type,
                redemption_status,
                redemption_id,
                redemption_type,
                created_dtm,
                updated_dtm
            )
            VALUES (
                %(lender_id)s,
                %(investment_id)s,
                0.00,
                %(cancelled_amount)s,
                %(cancelled_amount)s,
                0.00,
                0.00,
                %(investment_type)s::investment_repayment_transaction_type,
                'PENDING',
                %(redemption_id)s,
                'LOAN_CANCELLATION',
                NOW(),
                NOW()
            )
            RETURNING id
        """
        
        params = {
            'lender_id': lender_id,
            'investment_id': investment_id,
            'redemption_id': redemption_id,
            'cancelled_amount': cancelled_amount,
            'investment_type': investment_type
        }
        return self.execute_fetch_one(sql, params)

