"""
Entity layer for investment loan redemption summary database operations.
"""

import logging
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class InvestmentLoanRedemptionSummary(BaseDataLayer):
    """
    Data layer for investment loan redemption summary database operations.
    """
    
    def update_investment_loan_redemption_summary_cancellation(
        self,
        investment_loan_id: int
    ) -> bool:
        """
        Mark investment loan redemption summary as deleted and reset principal_outstanding.
        
        Args:
            investment_loan_id: Investment loan detail ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_investment_loan_redemption_summary
            SET deleted = NOW(),
                principal_outstanding = 0,
                updated_dtm = NOW()
            WHERE investment_loan_id = %(investment_loan_id)s
        """
        
        params = {'investment_loan_id': investment_loan_id}
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0

