"""
Entity layer for retail portfolio summary database operations.
"""

import logging
from typing import Optional, Dict, Any, List
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class RetailPortfolioSummary(BaseDataLayer):
    """
    Data layer for retail portfolio summary database operations.
    Uses lender_user_id instead of lender_id for portfolio identification.
    """
    
    def create_lender_portfolio_profile(self, lender_user_id: str) -> bool:
        """
        Create all 4 portfolio summary records for a new lender.
        Inserts ML-OPEN, ML-CLOSED, OTL-OPEN, OTL-CLOSED records with zero values.
        
        This method should be called when a lender is first created to initialize
        their portfolio profile.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR) to create portfolio profile for
            
        Returns:
            True if all records created successfully, False otherwise
        """
        sql = """
            INSERT INTO t_portfolio_summary (
                lender_user_id,
                product_type,
                loan_type,
                total_principal_lent,
                total_principal_received,
                total_principal_outstanding,
                total_principal_receivable,
                total_interest_received,
                total_amount_received,
                total_fee_levied,
                total_npa_amount,
                absolute_return,
                annualized_net_return,
                loan_count,
                created_dtm,
                updated_dtm
            )
            VALUES
                -- ML OPEN
                (%(lender_user_id)s, 'ML'::product_type_enum, 'OPEN'::loan_portfolio_enum, 
                 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0, NOW(), NOW()),
                -- ML CLOSED
                (%(lender_user_id)s, 'ML'::product_type_enum, 'CLOSED'::loan_portfolio_enum, 
                 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0, NOW(), NOW()),
                -- OTL OPEN
                (%(lender_user_id)s, 'OTL'::product_type_enum, 'OPEN'::loan_portfolio_enum, 
                 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0, NOW(), NOW()),
                -- OTL CLOSED
                (%(lender_user_id)s, 'OTL'::product_type_enum, 'CLOSED'::loan_portfolio_enum, 
                 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0, NOW(), NOW())
            ON CONFLICT (lender_user_id, product_type, loan_type) DO NOTHING
        """
        
        params = {'lender_user_id': lender_user_id}
        
        try:
            rows_affected = self.execute_insert(sql, params)
            logger.info(
                f"Created portfolio profile for lender_user_id: {lender_user_id}, "
                f"rows_affected: {rows_affected}"
            )
            return rows_affected >= 0  # Return True if no error (even if 0 rows due to conflict)
        except Exception as e:
            logger.error(
                f"Error creating portfolio profile for lender_user_id {lender_user_id}: {str(e)}",
                exc_info=True
            )
            return False
    
    def get_portfolio_summary(
        self,
        lender_user_id: str,
        product_type: str,
        loan_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get portfolio summary for a specific lender, product type, and loan type.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_type: Product type ('ML' or 'OTL')
            loan_type: Loan type ('OPEN' or 'CLOSED')
            
        Returns:
            Portfolio summary dictionary or None if not found
        """
        sql = """
            SELECT 
                id,
                lender_user_id,
                product_type,
                loan_type,
                total_principal_lent,
                total_principal_received,
                total_principal_outstanding,
                total_principal_receivable,
                total_interest_received,
                total_amount_received,
                total_fee_levied,
                total_npa_amount,
                absolute_return,
                annualized_net_return,
                loan_count,
                created_dtm,
                updated_dtm
            FROM t_portfolio_summary
            WHERE lender_user_id = %(lender_user_id)s
              AND product_type = %(product_type)s::product_type_enum
              AND loan_type = %(loan_type)s::loan_portfolio_enum
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'product_type': product_type,
            'loan_type': loan_type
        }
        
        return self.execute_fetch_one(sql, params)
    
    def get_all_portfolio_summaries(self, lender_user_id: str) -> List[Dict[str, Any]]:
        """
        Get all portfolio summaries for a lender (all 4 combinations).
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            
        Returns:
            List of portfolio summary dictionaries
        """
        sql = """
            SELECT 
                id,
                lender_user_id,
                product_type,
                loan_type,
                total_principal_lent,
                total_principal_received,
                total_principal_outstanding,
                total_principal_receivable,
                total_interest_received,
                total_amount_received,
                total_fee_levied,
                total_npa_amount,
                absolute_return,
                annualized_net_return,
                loan_count,
                created_dtm,
                updated_dtm
            FROM t_portfolio_summary
            WHERE lender_user_id = %(lender_user_id)s
              AND deleted IS NULL
            ORDER BY product_type, loan_type
        """
        
        params = {'lender_user_id': lender_user_id}
        return self.execute_fetch_all(sql, params) or []

