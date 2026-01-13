"""
Entity layer for investment loan repayment summary database operations.
"""

import logging
from typing import Optional
from ..base_layer import BaseDataLayer
from ..constants import DpdThreshold

logger = logging.getLogger(__name__)


class InvestmentLoanRepaymentSummary(BaseDataLayer):
    """
    Data layer for investment loan repayment summary database operations.
    """
    
    def update_investment_loan_repayment_summary_cancellation(
        self,
        investment_loan_id: int
    ) -> bool:
        """
        Mark investment loan repayment summary as deleted and reset principal_outstanding.
        
        Args:
            investment_loan_id: Investment loan detail ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_investment_loan_repayment_summary
            SET deleted = NOW(),
                principal_outstanding = 0,
                updated_dtm = NOW()
            WHERE investment_loan_id = %(investment_loan_id)s
        """
        
        params = {'investment_loan_id': investment_loan_id}
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def update_investment_loan_repayment_summary_dpd(
        self,
        investment_loan_id: int,
        days_past_due: int,
        npa_as_on_date: Optional[str]
    ) -> bool:
        """
        Update investment loan repayment summary with DPD data.
        Updates principal_outstanding and total_npa_amount based on DPD.
        If DPD > 120, moves principal_outstanding to total_npa_amount.
        If DPD <= 120 and was NPA, moves total_npa_amount back to principal_outstanding.
        
        Args:
            investment_loan_id: Investment loan detail ID
            days_past_due: Days past due
            npa_as_on_date: NPA as on date (YYYY-MM-DD format) or None
            
        Returns:
            bool: True if update successful
        """
        # If DPD > 120, move principal_outstanding to total_npa_amount
        # If DPD <= 120, move total_npa_amount back to principal_outstanding (if it was NPA)
        if days_past_due > DpdThreshold.DPD:
            sql = """
                UPDATE t_investment_loan_repayment_summary
                SET total_npa_amount = principal_outstanding,
                    principal_outstanding = 0,
                    updated_dtm = NOW()
                WHERE investment_loan_id = %(investment_loan_id)s
                  AND deleted IS NULL
            """
        else:
            # DPD <= 120, move total_npa_amount back to principal_outstanding if it exists
            sql = """
                UPDATE t_investment_loan_repayment_summary
                SET principal_outstanding = principal_outstanding + total_npa_amount,
                    total_npa_amount = 0,
                    updated_dtm = NOW()
                WHERE investment_loan_id = %(investment_loan_id)s
                  AND deleted IS NULL
            """
        
        params = {
            'investment_loan_id': investment_loan_id,
            'days_past_due': days_past_due,
            'npa_as_on_date': npa_as_on_date
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0

