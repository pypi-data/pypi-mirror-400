"""
Entity layer for loan portfolio details temp table operations.
This table contains loan portfolio details from LMS/PP system.
"""

import logging
from typing import Optional, Dict, Any
from datetime import date
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class LoanPortfolioDetailsTemp(BaseDataLayer):
    """
    Entity layer for t_loan_portfolio_details_temp table operations.
    This temporary table is populated by prc_move_loan_portfolio_details_lms_to_fmpp_temp() procedure.
    """
    
    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
    
    def execute_dpd_calculation_procedure(
        self,
        loan_ref_id: str,
        transaction_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate DPD (Days Past Due) for a loan using next_due_date from temp table.
        
        Args:
            loan_ref_id: Loan reference ID (alphanumeric)
            transaction_date: Transaction date
            
        Returns:
            Dict with days_past_due or None if not found
        """
        sql = """
            SELECT 
                CASE
                    WHEN (next_due_date > CURRENT_DATE OR next_due_date IS NULL) THEN 0
                    ELSE CURRENT_DATE - next_due_date
                END as days_past_due
            FROM t_loan_portfolio_details_temp
            WHERE loan_id = %(loan_ref_id)s
              AND transaction_date = %(transaction_date)s
            LIMIT 1
        """
        
        params = {
            'loan_ref_id': loan_ref_id,
            'transaction_date': transaction_date
        }
        
        return self.execute_fetch_one(sql, params)

    def calculate_dpd_for_loan(
        self,
        loan_ref_id: str,
        transaction_date: Optional[date] = None
    ) -> Optional[int]:
        """
        Calculate DPD (Days Past Due) for a loan using next_due_date from temp table.
        
        DPD calculation formula (as per prc_dpd_update_automation.sql):
        CASE
            WHEN (next_due_date > current_date OR next_due_date IS NULL) THEN 0
            ELSE current_date - next_due_date
        END as days_past_due
        
        Args:
            loan_ref_id: Loan reference ID (alphanumeric)
            transaction_date: Transaction date (defaults to CURRENT_DATE)
            
        Returns:
            Days past due (integer) or None if loan not found in temp table
        """
        if transaction_date is None:
            transaction_date = date.today()
        
        result = self.execute_dpd_calculation_procedure(
            loan_ref_id, transaction_date
        )
        
        if result and result.get('days_past_due') is not None:
            days_past_due = int(result['days_past_due'])
            logger.debug(
                f"Calculated DPD for loan_ref_id: {loan_ref_id}, "
                f"transaction_date: {transaction_date}, days_past_due: {days_past_due}"
            )
            return days_past_due
        else:
            logger.warning(
                f"Loan not found in t_loan_portfolio_details_temp for loan_ref_id: {loan_ref_id}, "
                f"transaction_date: {transaction_date}. Returning None."
            )
            return None

