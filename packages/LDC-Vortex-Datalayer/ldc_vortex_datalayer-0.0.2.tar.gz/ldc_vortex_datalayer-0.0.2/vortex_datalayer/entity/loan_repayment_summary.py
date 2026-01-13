"""
Entity layer for loan repayment summary database operations.
"""

import logging
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer
from ..constants import DpdThreshold

logger = logging.getLogger(__name__)


class LoanRepaymentSummary(BaseDataLayer):
    """
    Data layer for loan repayment summary database operations.
    """
    
    def get_loan_repayment_summary_by_loan_id(self, loan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get loan repayment summary by loan ID.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            Dict with repayment summary data or None
        """
        sql = """
            SELECT 
                loan_id,
                principal_outstanding
            FROM t_loan_repayment_summary
            WHERE loan_id = %(loan_id)s
              AND deleted IS NULL
        """
        
        params = {'loan_id': loan_id}
        return self.execute_fetch_one(sql, params)
    
    def update_loan_repayment_summary_cancellation(self, loan_id: int) -> bool:
        """
        Mark loan repayment summary as deleted and reset principal_outstanding.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_loan_repayment_summary
            SET deleted = NOW(),
                principal_outstanding = 0,
                updated_dtm = NOW()
            WHERE loan_id = %(loan_id)s
        """
        
        params = {'loan_id': loan_id}
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def update_loan_repayment_summary_dpd(
        self,
        loan_id: int,
        days_past_due: int,
        npa_as_on_date: Optional[str]
    ) -> bool:
        """
        Update loan repayment summary with DPD data.
        Updates principal_outstanding (pos) and npa_amount based on DPD.
        If DPD > 120, moves principal_outstanding to npa_amount. 
        If DPD <= 120 and was NPA, moves npa_amount back to principal_outstanding.
        
        Args:
            loan_id: Loan ID
            days_past_due: Days past due
            npa_as_on_date: NPA as on date (YYYY-MM-DD format) or None
            
        Returns:
            bool: True if update successful
        """
        # If DPD > 120, move principal_outstanding to npa_amount
        # If DPD <= 120, move npa_amount back to principal_outstanding (if it was NPA)
        if days_past_due > DpdThreshold.DPD:
            sql = """
                UPDATE t_loan_repayment_summary
                SET npa_amount = principal_outstanding,
                    principal_outstanding = 0,
                    npa_as_on_date = %(npa_as_on_date)s::DATE,
                    days_past_due = %(days_past_due)s,
                    updated_dtm = NOW()
                WHERE loan_id = %(loan_id)s
                  AND deleted IS NULL
            """
        else:
            # DPD <= 120, move npa_amount back to principal_outstanding if it exists
            sql = """
                UPDATE t_loan_repayment_summary
                SET principal_outstanding = principal_outstanding + npa_amount,
                    npa_amount = 0,
                    npa_as_on_date = NULL,
                    days_past_due = %(days_past_due)s,
                    updated_dtm = NOW()
                WHERE loan_id = %(loan_id)s
                  AND deleted IS NULL
            """
        
        params = {
            'loan_id': loan_id,
            'days_past_due': days_past_due,
            'npa_as_on_date': npa_as_on_date
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0

