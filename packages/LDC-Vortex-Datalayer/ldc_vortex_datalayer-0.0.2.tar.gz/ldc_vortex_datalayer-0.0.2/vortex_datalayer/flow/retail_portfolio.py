"""
Retail portfolio flow layer for portfolio summary operations.
Handles portfolio calculation and retrieval operations using lender_user_id.
"""

import logging
from typing import List, Optional, Dict, Any
from ..base_layer import BaseDataLayer
from ..constants import LoanStatus, TransactionStatus
from ..entity.investment_product_config import InvestmentProductConfig

logger = logging.getLogger(__name__)


class RetailPortfolioFlow(BaseDataLayer):
    """
    Flow layer for retail portfolio operations.
    Uses lender_user_id instead of lender_id.
    """

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        self.db_alias = db_alias
    
    def get_principal_outstanding(self, investor_id):
        sql = """
                SELECT COALESCE(SUM(total_principal_outstanding), 0) as pos
                FROM t_portfolio_summary tps
                WHERE tps.lender_user_id = %(investor_id)s
                AND tps.deleted IS NULL
            """

        params = {
            'investor_id': investor_id
        }

        return self.execute_fetch_one(sql, params)

    def get_blocked_balance(self, investor_id):
        sql = """
                SELECT COALESCE(SUM(amount_lent), 0) as blocked_balance
                FROM t_lender_investment_order tlio
                JOIN t_lender tl on tlio.lender_id = tl.id
                WHERE tl.user_id = %(investor_id)s and tlio.status = %(status)s
                AND tlio.deleted IS NULL
                AND tl.deleted IS NULL;
            """

        params = {
            'investor_id': investor_id,
            'status': TransactionStatus.PENDING
        }

        return self.execute_fetch_one(sql, params)
    
    def calculate_portfolio_summary(
        self,
        lender_user_ids: List[str],
        product_types: Optional[List[str]] = None,
        loan_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate portfolio summary for given lenders using stored procedure.
        
        Args:
            lender_user_ids: List of lender user IDs (VARCHAR) to calculate portfolio for
            product_types: Optional list of product types ('ML', 'OTL'). If None, calculates for all
            loan_types: Optional list of loan types ('OPEN', 'CLOSED'). If None, calculates for all
            
        Returns:
            List of dictionaries with calculation results
        """
        if not lender_user_ids:
            logger.warning("No lender user IDs provided for portfolio calculation")
            return []
        
        # Call stored procedure
        # Build parameters for procedure call
        # psycopg2 handles Python lists to PostgreSQL arrays automatically
        # For enum arrays, we pass the string values and PostgreSQL will cast them
        params = [lender_user_ids, None, None, None]  # lender_user_ids, product_types, loan_types, inout_response
        
        # Set product_types if provided (pass as list of strings, PostgreSQL will cast)
        if product_types:
            params[1] = product_types
        else:
            params[1] = None
        
        # Set loan_types if provided (pass as list of strings, PostgreSQL will cast)
        if loan_types:
            params[2] = loan_types
        else:
            params[2] = None
        
        try:
            # Call stored procedure
            result = self.execute_procedure(
                procedure_name='prc_calculate_portfolio_summary',
                params=params,
                fetch_one=False,
                to_dict=False
            )
            
            # Get response from INOUT parameter (last parameter)
            # INOUT parameters modify the params list
            response_value = params[3] if len(params) > 3 and params[3] is not None else None
            
            if response_value == 0:
                logger.info(
                    f"Portfolio calculation completed successfully for {len(lender_user_ids)} lender(s)"
                )
                return [{'status': 'SUCCESS', 'lenders_processed': len(lender_user_ids)}]
            else:
                error_msg = f"Portfolio calculation failed with response code: {response_value}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error calculating portfolio summary: {str(e)}", exc_info=True)
            raise
    
    def fetch_portfolio_by_loan_types(
        self,
        lender_user_id: str,
        product_type: str,
        loan_type: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get portfolio summary for a specific lender, product type, and loan type.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_type: Product type ('ML' or 'OTL')
            loan_type: Loan type list (['OPEN'], ['CLOSED'], or ['OPEN', 'CLOSED'])
            
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
              AND loan_type = ANY(%(loan_type)s::loan_portfolio_enum[])
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'product_type': product_type,
            'loan_type': loan_type
        }
        
        return self.execute_fetch_one(sql, params)

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
        if loan_type == 'BOTH':
            loan_type_list = ['OPEN', 'CLOSED']
        else:
            loan_type_list = [loan_type]
            
        return self.fetch_portfolio_by_loan_types(
            lender_user_id, product_type, loan_type_list
        )
    
    def fetch_active_loan_records(
        self,
        lender_user_id: str,
        product_config_ids: List[int],
        loan_statuses: List[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get portfolio loan details for open loans.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_config_ids: List of product config IDs
            loan_statuses: List of loan statuses
            limit: Number of records to return
            offset: Offset for pagination
            
        Returns:
            List of loan detail dictionaries
        """
        sql = """
            SELECT
                ROUND(COALESCE(tilrs.total_fee_levied, 0), 2) as fee,
                0 as npa,
                ROUND(COALESCE(tilrs.principal_outstanding, 0), 2) as pos,
                ROUND(COALESCE(tilrs.total_amount_redeemed, 0), 2) as total_received_amount,
                ROUND(COALESCE(tl.expected_repayment_sum * tild.allocation_percentage / 100, 0), 2) as expected_returns,
                ROUND(COALESCE(tild.investment_amount, 0), 2) as lent_amount,
                NULL as total_earned,
                NULL as portfolio_health,
                CONCAT(tl.tenure, ' Month(s)') as loan_tenure,
                NULL as scheme_id,
                tl.loan_ref_id as loan_id,
                tl.borrower_name,
                tb.source,
                NULL as loan_type,
                NULL as principal_due,
                ROUND(COALESCE(tilrs.total_principal_redeemed, 0), 2) as principal_received,
                ROUND(COALESCE(tilrs.total_principal_redeemed, 0), 2) as principle_received,
                ROUND(GREATEST(COALESCE(tilrs.total_interest_redeemed, 0) - COALESCE(tilrs.total_fee_levied, 0), 0), 2) as net_interest_received
            FROM t_lender_investment tli
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
            JOIN t_investment_loan_redemption_summary tilrs ON tild.id = tilrs.investment_loan_id
            JOIN t_loan tl ON tl.id = tild.loan_id
            JOIN t_lender tlender ON tli.lender_id = tlender.id
            JOIN t_borrowers tb ON tb.id = tl.borrower_id
            WHERE tlender.user_id = %(lender_user_id)s
              AND tl.status = ANY(%(loan_statuses)s::loan_status[])
              AND tli.product_config_id = ANY(%(product_config_ids)s)
              AND tli.deleted IS NULL
              AND tild.deleted IS NULL
            ORDER BY tild.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'product_config_ids': product_config_ids,
            'loan_statuses': loan_statuses,
            'limit': limit,
            'offset': offset
        }
        
        return self.execute_fetch_all(sql, params) or []

    def fetch_settled_loan_records(
        self,
        lender_user_id: str,
        product_config_ids: List[int],
        loan_statuses: List[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get portfolio loan details for closed loans.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_config_ids: List of product config IDs
            loan_statuses: List of loan statuses
            limit: Number of records to return
            offset: Offset for pagination
            
        Returns:
            List of loan detail dictionaries
        """
        sql = """
            WITH loan_details AS (
                SELECT
                    tild.id,
                    tl.loan_ref_id as loan_id,
                    tl.borrower_name,
                    tb.source,
                    CONCAT(tl.tenure, ' Month(s)') as loan_tenure,
                    tl.tenure,
                    ROUND(COALESCE(tild.investment_amount, 0), 2) as lent_amount,
                    ROUND(COALESCE(tilrs.total_amount_redeemed, 0), 2) as received_amount,
                    ROUND(COALESCE(tilrs.total_principal_redeemed, 0), 2) as principal_received,
                    ROUND(COALESCE(tilrs.total_principal_redeemed, 0), 2) as principle_received,
                    ROUND(COALESCE(tilrs.total_interest_redeemed, 0), 2) as interest_received,
                    ROUND(COALESCE(tilrs.total_fee_levied, 0), 2) as fee,
                    ROUND(GREATEST(COALESCE(tilrs.total_interest_redeemed, 0) - COALESCE(tilrs.total_fee_levied, 0), 0), 2) as net_interest_received,
                    ROUND(COALESCE(tilrs.total_npa_amount, 0), 2) as npa,
                    ROUND(COALESCE(tilrs.total_amount_redeemed, 0) - COALESCE(tild.investment_amount, 0), 2) as "p_&_l",
                    ROUND(
                        CASE 
                            WHEN COALESCE(tild.investment_amount, 0) = 0 THEN 0
                            ELSE ((COALESCE(tilrs.total_amount_redeemed, 0) - COALESCE(tild.investment_amount, 0)) / tild.investment_amount) * 100
                        END, 
                        2
                    ) as absolute_return
                FROM t_lender_investment tli
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_investment_loan_redemption_summary tilrs ON tild.id = tilrs.investment_loan_id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_lender tlender ON tli.lender_id = tlender.id
                JOIN t_borrowers tb ON tb.id = tl.borrower_id
                WHERE tlender.user_id = %(lender_user_id)s
                  AND tl.status = ANY(%(loan_statuses)s::loan_status[])
                  AND tli.product_config_id = ANY(%(product_config_ids)s)
                  AND tli.deleted IS NULL
                  AND tild.deleted IS NULL
            )
            SELECT
                NULL as scheme_id,
                ld.loan_id,
                ld.borrower_name,
                ld.source,
                NULL as portfolio_health,
                ld.loan_tenure,
                ld.lent_amount,
                ld.received_amount,
                ld.principal_received,
                ld.principle_received,
                ld.interest_received,
                ld.fee,
                ld.net_interest_received,
                ld.absolute_return,
                ld."p_&_l",
                ld.npa,
                CASE 
                    WHEN ld.absolute_return < 0 THEN 0
                    ELSE ROUND((ld.absolute_return * 12) / ld.tenure, 2)
                END as annualized_net_return
            FROM loan_details ld
            ORDER BY ld.absolute_return DESC, ld.id
            LIMIT %(limit)s OFFSET %(offset)s
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'product_config_ids': product_config_ids,
            'loan_statuses': loan_statuses,
            'limit': limit,
            'offset': offset
        }
        
        return self.execute_fetch_all(sql, params) or []

    def get_portfolio_loan_details(
        self,
        lender_user_id: str,
        product_type: str,
        loan_type: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get portfolio loan details list with pagination.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_type: Product type ('ML' or 'OTL')
            loan_type: Loan type ('OPEN' or 'CLOSED')
            limit: Number of records to return
            offset: Offset for pagination
            
        Returns:
            List of loan detail dictionaries
        """
        # Get product_config_ids from database based on product_type
        product_config_entity = InvestmentProductConfig()
        product_config_ids = product_config_entity.get_product_config_ids_by_investment_type(product_type)
        if not product_config_ids:
            logger.warning(f"No product configs found for product_type: {product_type}")
            return []
        
        # Determine loan statuses based on loan_type
        if loan_type == 'OPEN':
            loan_statuses = ['DISBURSED', 'LIVE']
            return self.fetch_active_loan_records(
                lender_user_id, product_config_ids, loan_statuses, limit, offset
            )
        else:  # CLOSED
            loan_statuses = ['CLOSED', 'NPA']
            return self.fetch_settled_loan_records(
                lender_user_id, product_config_ids, loan_statuses, limit, offset
            )

    def fetch_loan_status_counts(
        self,
        lender_user_id: str,
        product_config_ids: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Get loan counts for open and closed loans.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_config_ids: List of product config IDs
            
        Returns:
            Dict with open_count, closed_count, and total_count or None
        """
        sql = """
            SELECT
                COUNT(*) FILTER (WHERE tl.status = ANY (%(disbursed_and_live_loan_status)s)) as open_count,
                COUNT(*) FILTER (WHERE tl.status = ANY (%(closed_and_npa_loan_status)s)) as closed_count,
                COUNT(*) as total_count
            FROM t_lender_investment tli
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
            JOIN t_loan tl ON tl.id = tild.loan_id
            JOIN t_lender tlender ON tli.lender_id = tlender.id
            WHERE tlender.user_id = %(lender_user_id)s
              AND tli.product_config_id = ANY(%(product_config_ids)s)
              AND tli.deleted IS NULL
              AND tild.deleted IS NULL
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'product_config_ids': product_config_ids,
            'disbursed_and_live_loan_status': [LoanStatus.DISBURSED, LoanStatus.LIVE],
            'closed_and_npa_loan_status': [LoanStatus.CLOSED, LoanStatus.NPA]
        }
        
        return self.execute_fetch_one(sql, params)

    def get_portfolio_loan_counts(
        self,
        lender_user_id: str,
        product_type: str
    ) -> Dict[str, int]:
        """
        Get loan counts for open and closed loans.
        
        Args:
            lender_user_id: Lender user ID (VARCHAR)
            product_type: Product type ('MANUAL_LENDING' or 'ONE_TIME_LENDING')
            
        Returns:
            Dictionary with open_count, closed_count, and total_count
        """
        # Get product_config_ids from database based on product_type
        product_config_entity = InvestmentProductConfig()
        product_config_ids = product_config_entity.get_product_config_ids_by_investment_type(product_type)
        if not product_config_ids:
            logger.warning(f"No product configs found for product_type: {product_type}")
            return {'open_count': 0, 'closed_count': 0, 'total_count': 0}
        
        result = self.fetch_loan_status_counts(
            lender_user_id, product_config_ids
        )
        if result:
            return {
                'open_count': int(result.get('open_count') or 0),
                'closed_count': int(result.get('closed_count') or 0),
                'total_count': int(result.get('total_count') or 0)
            }
        return {'open_count': 0, 'closed_count': 0, 'total_count': 0}

    def get_stl_cashflow_data(
        self,
        lender_user_id: str,
        investment_type_id: int,
        is_matured: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get STL cashflow data for a lender (retail) using lender_user_id.

        Args:
            lender_user_id: Lender user ID (VARCHAR)
            investment_type_id: Investment type ID from mst_parameter
            is_matured: Optional filter for matured schemes (True for closed, False for active)

        Returns:
            List of dictionaries with cashflow data
        """
        sql = """
            SELECT
                tli.created_dtm,
                tli.investment_id AS urn_id,
                COALESCE(tli.actual_closure_date IS NOT NULL, FALSE) AS is_matured,
                COALESCE(ROUND(
                    SUM(tilrs.total_amount_redeemed) - COALESCE(mliprad.pending_repayment_amount, 0),
                    2
                ), 0) AS redeemed_amount,
                COALESCE(mliprad.pending_repayment_amount, 0) AS pending_repayment_transfer,
                tipc.tenure,
                COALESCE(ROUND(tli.amount_lent_on_investment, 2), 0) AS investment_amount,
                COALESCE(ROUND(SUM(tilrs.total_principal_redeemed), 2), 0) AS actual_principal_sum,
                COALESCE(ROUND(SUM(tilrs.total_interest_redeemed - tilrs.total_fee_levied), 2), 0) AS actual_interest_sum,
                COALESCE(ROUND(SUM(tilrs.total_fee_levied), 2), 0) AS total_facilitation_fee,
                COALESCE(ROUND(SUM(tilrs.principal_outstanding), 2), 0) AS pos,
                COALESCE(ROUND(SUM(tilrs.total_npa_amount), 2), 0) AS total_npa_amount,
                COALESCE(ROUND(tli.cancelled_loan_amount, 2), 0) AS loan_cancellation_amount
            FROM
                t_lender_investment tli
            JOIN
                t_lender tl_lender ON tli.lender_id = tl_lender.id
            JOIN
                t_investment_loan_detail tild ON tli.id = tild.investment_id
            JOIN
                t_loan tl ON tl.id = tild.loan_id
            JOIN
                t_investment_loan_redemption_summary tilrs ON tilrs.investment_loan_id = tild.id
            JOIN
                t_investment_product_config tipc ON tipc.id = tli.product_config_id
            LEFT JOIN
                mv_lender_investment_pending_repayment_amount_details mliprad ON tli.id = mliprad.investment_id
            WHERE
                tl_lender.user_id = %(lender_user_id)s
                AND tli.investment_type_id = %(investment_type_id)s
                AND (%(is_matured)s IS NULL OR (%(is_matured)s IS NOT NULL AND (
                    (%(is_matured)s = TRUE)
                )))
                AND tli.deleted IS NULL
                AND tild.deleted IS NULL
                AND tilrs.deleted IS NULL
                AND tl.deleted IS NULL
                AND tl_lender.deleted IS NULL
            GROUP BY
                tli.id, tli.amount_lent_on_investment, tli.cancelled_loan_amount, 
                tli.investment_id, mliprad.pending_repayment_amount, tipc.tenure, 
                tli.investment_type_id, tli.created_dtm, tli.actual_closure_date
            ORDER BY
                tli.created_dtm
        """

        params = {
            'lender_user_id': lender_user_id,
            'investment_type_id': investment_type_id,
            'is_matured': is_matured
        }

        return self.execute_fetch_all(sql, params, to_dict=True) or []

