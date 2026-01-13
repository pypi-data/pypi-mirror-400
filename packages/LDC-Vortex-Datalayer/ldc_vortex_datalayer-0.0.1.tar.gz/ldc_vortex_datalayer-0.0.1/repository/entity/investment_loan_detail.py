"""
Entity layer for investment loan detail database operations.
"""

import logging
from typing import List, Dict, Any
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class InvestmentLoanDetail(BaseDataLayer):
    """
    Data layer for investment loan detail database operations.
    """
    
    def get_impacted_lenders_by_loan_id(self, loan_id: int) -> List[int]:
        """
        Get all lender IDs impacted by a loan (for disbursal/closure/DPD updates).
        
        Args:
            loan_id: Loan ID to find impacted lenders for
            
        Returns:
            List of unique lender IDs
        """
        sql = """
            SELECT DISTINCT tli.lender_id
            FROM t_investment_loan_detail tild
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
            WHERE tild.loan_id = %(loan_id)s
              AND tild.deleted IS NULL
              AND tli.deleted IS NULL
        """
        
        params = {'loan_id': loan_id}
        results = self.execute_fetch_all(sql, params)
        return [row['lender_id'] for row in results] if results else []
    
    def get_investment_loan_details_by_loan_id(self, loan_id: int) -> List[Dict[str, Any]]:
        """
        Get all investment loan details for a loan.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            List of investment loan detail records with id, investment_id, investment_amount
        """
        sql = """
            SELECT 
                tild.id,
                tild.investment_id,
                tild.investment_amount,
                tli.lender_id,
                tli.product_config_id
            FROM t_investment_loan_detail tild
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
            WHERE tild.loan_id = %(loan_id)s
              AND tild.deleted IS NULL
              AND tli.deleted IS NULL
        """
        
        params = {'loan_id': loan_id}
        return self.execute_fetch_all(sql, params) or []
    
    def update_investment_loan_detail_cancelled(self, investment_loan_detail_id: int) -> bool:
        """
        Mark investment loan detail as cancelled.
        
        Args:
            investment_loan_detail_id: Investment loan detail ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_investment_loan_detail
            SET is_cancelled = TRUE,
                updated_dtm = NOW()
            WHERE id = %(investment_loan_detail_id)s
        """
        
        params = {'investment_loan_detail_id': investment_loan_detail_id}
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0

