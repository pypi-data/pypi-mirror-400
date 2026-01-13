import logging
from typing import List, Optional, Dict, Any

from ..constants import SchemeStatus, LoanSystemSource, ProductConfig
from ..base_layer import BaseDataLayer
from ..constants import LoanStatus, OrderStatus

logger = logging.getLogger(__name__)


class LenderInvestment(BaseDataLayer):
    """
    Data layer for `t_lender_investment` database operations.
    """

    def get_investment_scheme_id(self, investment_scheme_id):
        sql = """
                SELECT id 
                FROM t_lender_investment 
                WHERE investment_id = %(investment_scheme_id)s
            """

        params = {
            'investment_scheme_id': investment_scheme_id
        }

        return self.execute_fetch_one(sql, params)

    def get_distinct_product_configs_for_partner(self, partner_id: str) -> List[Dict[str, Any]]:
        """
        Get distinct product configurations used by lenders under a given partner.

        This is used during CP-to-MCP conversion to identify all product_config_ids
        that need to be re-associated to MCP-specific configs.

        Args:
            partner_id: Channel / Master partner identifier

        Returns:
            List of dicts with keys: product_config_id, tenure, partner_code_id, investment_type_id
        """
        sql = """
            SELECT DISTINCT
                tli.product_config_id,
                tipc.tenure,
                tipc.partner_code_id,
                tipc.investment_type_id
            FROM t_lender_investment tli
            JOIN t_lender tl
                ON tli.lender_id = tl.id
               AND tl.deleted IS NULL
            JOIN t_investment_product_config tipc
                ON tli.product_config_id = tipc.id
               AND tipc.deleted IS NULL
            WHERE tl.partner_id = %(partner_id)s
              AND tli.deleted IS NULL
        """

        params = {"partner_id": partner_id}
        results = self.execute_fetch_all(sql, params, to_dict=True)
        return results or []

    def update_product_config_for_partner(
        self,
        partner_id: str,
        old_product_config_id: int,
        new_product_config_id: int,
    ) -> int:
        """
        Update `t_lender_investment.product_config_id` for all investments belonging
        to lenders under the given partner from old_product_config_id to new_product_config_id.

        Args:
            partner_id: Channel / Master partner identifier
            old_product_config_id: Existing product_config_id to be replaced
            new_product_config_id: New MCP-specific product_config_id

        Returns:
            int: Number of rows updated
        """
        sql = """
            UPDATE t_lender_investment tli
            SET product_config_id = %(new_product_config_id)s,
                updated_dtm = NOW()
            FROM t_lender tl
            WHERE tli.lender_id = tl.id
              AND tl.partner_id = %(partner_id)s
              AND tli.product_config_id = %(old_product_config_id)s
              AND tli.deleted IS NULL
              AND tl.deleted IS NULL
        """

        params: Dict[str, Any] = {
            "partner_id": partner_id,
            "old_product_config_id": old_product_config_id,
            "new_product_config_id": new_product_config_id,
        }
        return self.execute_update(sql, params)
    
    def get_product_types_for_lender(self, lender_id: int) -> List[str]:
        """
        Get all product types (ML/OTL) that a lender has investments in.
        
        Args:
            lender_id: Lender ID
            
        Returns:
            List of product types (e.g., ['ML', 'OTL'])
        """
        sql = """
            SELECT DISTINCT 
                CASE 
                    WHEN tli.product_config_id = %(ml_product_config_id)s THEN 'ML'
                    WHEN tli.product_config_id = ANY(%(product_config_ids)s) THEN 'OTL'
                    ELSE NULL
                END as product_type
            FROM t_lender_investment tli
            WHERE tli.lender_id = %(lender_id)s
              AND tli.deleted IS NULL
              AND (
                  tli.product_config_id = %(ml_product_config_id)s  
                  OR tli.product_config_id = ANY(%(product_config_ids)s)
              )
        """
        
        params = {
            'lender_id': lender_id,
            'ml_product_config_id': ProductConfig.ML_PRODUCT_CONFIG_ID,
            'product_config_ids': ProductConfig.OTL_PRODUCT_CONFIG_IDS
        }
        results = self.execute_fetch_all(sql, params)
        product_types = [row['product_type'] for row in results if row['product_type']]
        return list(set(product_types))  # Remove duplicates
    
    def update_lender_investment_cancellation(
        self,
        investment_id: int,
        cancelled_amount: float
    ) -> bool:
        """
        Update lender investment for loan cancellation.
        Decreases actual_principal_lent and total_principal_outstanding,
        increases cancelled_loan_amount.
        
        Args:
            investment_id: Investment ID
            cancelled_amount: Amount to cancel
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_lender_investment
            SET actual_principal_lent = actual_principal_lent - %(cancelled_amount)s,
                total_principal_outstanding = total_principal_outstanding - %(cancelled_amount)s,
                cancelled_loan_amount = cancelled_loan_amount + %(cancelled_amount)s,
                updated_dtm = NOW()
            WHERE id = %(investment_id)s
        """
        
        params = {
            'investment_id': investment_id,
            'cancelled_amount': cancelled_amount
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def has_active_scheme(
        self, 
        lender_id: int,
        scheme_id: str = None,
        from_date=None,
        to_date=None
    ) -> bool:
        sql = """
            SELECT EXISTS(
                SELECT 1 
                FROM t_lender_investment 
                WHERE lender_id = %(lender_id)s
                  AND status = %(status)s
                  AND deleted IS NULL
                  
        """
        
        params = {
            'lender_id': lender_id,
            'status': SchemeStatus.ACTIVE
        }

        if scheme_id:
            sql += " AND investment_id = %(scheme_id)s"
            params['scheme_id'] = scheme_id

        if from_date:
            sql += " AND created_dtm >= %(from_date)s"
            params['from_date'] = from_date

        if to_date:
            sql += " AND created_dtm <= %(to_date)s"
            params['to_date'] = to_date

        sql += ") as has_active"

        result = self.execute_fetch_one(sql, params)
        return result['has_active'] if result else False

    def check_redemption_exists(
        self,
        user_source_group_id: str,
        investment_type_id: int = None,
        scheme_id: str = None,
        from_date=None,
        to_date=None
    ) -> bool:
        sql = """
            SELECT EXISTS(
                SELECT 1 
                FROM t_lender_investment tli
                JOIN t_lender tl ON tl.id = tli.lender_id
                JOIN t_lender_redemption tlr ON tlr.lender_id = tli.id
                WHERE tl.user_source_group_id = %(user_source_group_id)s
                  AND tlr.redemption_status = 'SUCCESS'
                  AND tli.deleted IS NULL
                  AND tl.deleted IS NULL
        """
        
        params = {
            'user_source_group_id': user_source_group_id
        }
        
        if investment_type_id is not None:
            sql += " AND tli.investment_type_id = %(investment_type_id)s"
            params['investment_type_id'] = investment_type_id
        
        if scheme_id is not None:
            sql += " AND tli.investment_id = %(scheme_id)s"
            params['scheme_id'] = scheme_id
        
        if from_date is not None and to_date is not None:
            sql += " AND tli.created_dtm BETWEEN %(from_date)s AND %(to_date)s"
            params['from_date'] = from_date
            params['to_date'] = to_date
        
        sql += ") AS has_redemption"
        
        result = self.execute_fetch_one(sql, params)
        return result['has_redemption'] if result else False

    def get_investor_schemes_data(
        self,
        lender_id: int,
        product_config_ids: Optional[List[int]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get investor schemes data for a specific lender with aggregated repayment data.

        Args:
            lender_id: Lender ID
            product_config_ids: Optional list of product_config_ids to filter by investment_type
            limit: Number of results to return
            offset: Number of results to skip

        Returns:
            List of investment dictionaries with all required fields
        """
        product_filter = ""
        params = {"lender_id": lender_id}

        if product_config_ids:
            product_filter = "AND tli.product_config_id = ANY(%(product_config_ids)s)"
            params["product_config_ids"] = product_config_ids

        sql = f"""
            SELECT
                tli.id as investment_pk_id,
                tli.investment_id as scheme_id,
                tli.amount_lent_on_investment as total_investment,
                tli.created_dtm,
                tli.expected_closure_date,
                tli.actual_closure_date,
                tli.cancelled_loan_amount as loan_cancel_amount,
                tli.order_id,
                tipc.tenure,
                tipc.investment_type,
                tlender.partner_id,
                tlender.partner_code_id,
                COALESCE(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 0) as actual_returns,
                COALESCE(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 0) as net_interest_received,
                COALESCE(SUM(tilrs.total_principal_received), 0) as principal_received_amount,
                COALESCE(SUM(tilrs.principal_outstanding), 0) as principal_outstanding,
                COALESCE(SUM(tilrs.total_npa_amount), 0) as npa_amount,
                COALESCE(SUM(tilrs.total_npa_amount), 0) as principal_loss,
                COALESCE(SUM(tilrs.total_fee_levied), 0) as facilitation_fee,
                COALESCE(SUM(tilrs.total_amount_received), 0) as received_amount,
                COALESCE(mliprad.pending_repayment_amount, 0) as pending_repayment_transfer,
                tmp.value_1 as partner_name
            FROM t_lender_investment tli
            JOIN t_lender tlender ON tli.lender_id = tlender.id
                AND tlender.deleted IS NULL
            JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                AND tipc.deleted IS NULL
            LEFT JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                AND tild.deleted IS NULL
            LEFT JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                AND tilrs.deleted IS NULL
            LEFT JOIN mv_lender_investment_pending_repayment_amount_details mliprad
                ON tli.id = mliprad.investment_id
            LEFT JOIN t_mst_parameter tmp ON tlender.partner_code_id = tmp.id
                AND tmp.logical_group = 'partner_code'
                AND tmp.deleted IS NULL
            WHERE tli.lender_id = %(lender_id)s
                AND tli.deleted IS NULL
                {product_filter}
            GROUP BY
                tli.id,
                tli.investment_id,
                tli.amount_lent_on_investment,
                tli.created_dtm,
                tli.expected_closure_date,
                tli.actual_closure_date,
                tli.cancelled_loan_amount,
                tli.order_id,
                tipc.tenure,
                tipc.investment_type,
                tlender.partner_id,
                tlender.partner_code_id,
                mliprad.pending_repayment_amount,
                tmp.value_1
            ORDER BY tli.created_dtm DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        params["limit"] = limit
        params["offset"] = offset

        results = self.execute_fetch_all(sql, params, to_dict=True)
        return results if results else []

    def get_investor_loan_counts(
        self,
        lender_id: int,
        investment_type: str,
        scheme_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Get counts of open, closed and total loans for a lender and investment type.

        Args:
            lender_id: Lender ID
            investment_type: Investment type (e.g., ONE_TIME_LENDING, MEDIUM_TERM_LENDING)
            scheme_id: Optional scheme URN ID (investment_id from t_lender_investment)

        Returns:
            Dict with open_count, closed_count and total_count
        """
        params: Dict[str, Any] = {
            "lender_id": lender_id,
            "investment_type": investment_type,
            "closed_status": [LoanStatus.CLOSED, LoanStatus.NPA],
            "disbursed_status": LoanStatus.DISBURSED
        }
        scheme_filter = ""
        if scheme_id:
            scheme_filter = "AND tli.investment_id = %(scheme_id)s"
            params["scheme_id"] = scheme_id

        sql = f"""
            SELECT
                COUNT(*) FILTER (WHERE tl.status = ANY(%(closed_status)s)) AS closed_count,
                COUNT(*) FILTER (WHERE tl.status = %(disbursed_status)s) AS open_count,
                COUNT(*) AS total_count
            FROM t_loan tl
            JOIN t_investment_loan_detail tild ON tild.loan_id = tl.id
                AND tild.deleted IS NULL
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
                AND tli.deleted IS NULL
            JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                AND tipc.deleted IS NULL
            WHERE tli.lender_id = %(lender_id)s
                AND tipc.investment_type = %(investment_type)s
                AND tl.deleted IS NULL
                {scheme_filter}
        """

        result = self.execute_fetch_one(sql, params, to_dict=True) or {}
        return {
            "open_count": int(result.get("open_count") or 0),
            "closed_count": int(result.get("closed_count") or 0),
            "total_count": int(result.get("total_count") or 0),
        }

    def get_investor_open_loans(
        self,
        lender_id: int,
        investment_type: str,
        scheme_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get open (active, non-NPA) loan exposures for a lender and investment type.

        Args:
            lender_id: Lender ID
            investment_type: Investment type (e.g., ONE_TIME_LENDING, MEDIUM_TERM_LENDING)
            scheme_id: Optional scheme URN ID (investment_id from t_lender_investment)
            limit: Number of rows to return
            offset: Number of rows to skip
        """
        params: Dict[str, Any] = {
            "lender_id": lender_id,
            "investment_type": investment_type,
            "limit": limit,
            "offset": offset,
            "personal_loan_partner_codes": LoanSystemSource.PERSONAL_LOAN_LIST,
            "personal_loan_label": LoanSystemSource.PERSONAL_LOAN,
            "merchant_loan_label": LoanSystemSource.MERCHANT_LOAN,
            "active_loan_status": ['LIVE', 'DISBURSED'],
        }
        scheme_filter = ""
        if scheme_id:
            scheme_filter = "AND tli.investment_id = %(scheme_id)s"
            params["scheme_id"] = scheme_id

        sql = f"""
            SELECT
                ROUND(COALESCE(tilrs.total_fee_levied, 0), 2) AS fee,
                0 AS npa,
                ROUND(COALESCE(tilrs.principal_outstanding, 0), 2) AS pos,
                ROUND(COALESCE(tilrs.total_amount_received, 0), 2) AS total_received_amount,
                ROUND(COALESCE(tl.expected_repayment_sum * tild.allocation_percentage / 100, 0), 2) AS expected_returns,
                ROUND(COALESCE(tild.investment_amount, 0), 2) AS lent_amount,
                NULL AS total_earned,
                NULL AS portfolio_health,
                ROUND(tlpc.tenure)::TEXT || ' Month(s)' AS loan_tenure,
                tli.investment_id AS scheme_id,
                tl.loan_ref_id AS loan_id,
                tl.borrower_name,
                tlpc.source,
                CASE
                    WHEN tlpc.partner_code = ANY(%(personal_loan_partner_codes)s)
                        THEN %(personal_loan_label)s
                    ELSE %(merchant_loan_label)s
                END AS loan_type,
                NULL AS principal_due,
                ROUND(COALESCE(tilrs.total_principal_received, 0), 2) AS principal_received,
                ROUND(COALESCE(tilrs.total_principal_received, 0), 2) AS principle_received,
                ROUND(GREATEST(COALESCE(tilrs.total_interest_received, 0) - COALESCE(tilrs.total_fee_levied, 0), 0), 2) AS net_interest_received
            FROM t_loan tl
            JOIN t_investment_loan_detail tild ON tild.loan_id = tl.id
                AND tild.deleted IS NULL
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
                AND tli.deleted IS NULL
            JOIN t_investment_loan_repayment_summary tilrs
                ON tilrs.investment_loan_id = tild.id
                AND tilrs.deleted IS NULL
            JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
                AND tlpc.deleted IS NULL
            JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                AND tipc.deleted IS NULL
            WHERE tli.lender_id = %(lender_id)s
                AND tipc.investment_type = %(investment_type)s
                AND tl.status = ANY(%(active_loan_status)s)
                AND COALESCE(tilrs.total_npa_amount, 0) = 0
                AND tl.deleted IS NULL
                {scheme_filter}
            ORDER BY tli.id DESC, tl.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        results = self.execute_fetch_all(sql, params, to_dict=True)
        return results if results else []

    def get_investor_closed_loans(
        self,
        lender_id: int,
        investment_type: str,
        scheme_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get closed/NPA loan exposures for a lender and investment type.

        Args:
            lender_id: Lender ID
            investment_type: Investment type (e.g., ONE_TIME_LENDING, MEDIUM_TERM_LENDING)
            scheme_id: Optional scheme URN ID (investment_id from t_lender_investment)
            limit: Number of rows to return
            offset: Number of rows to skip
        """
        params: Dict[str, Any] = {
            "lender_id": lender_id,
            "investment_type": investment_type,
            "limit": limit,
            "offset": offset,
            "status": [LoanStatus.CLOSED, LoanStatus.NPA]
        }
        scheme_filter = ""
        if scheme_id:
            scheme_filter = "AND tli.investment_id = %(scheme_id)s"
            params["scheme_id"] = scheme_id

        sql = f"""
            WITH loan_data AS (
                SELECT
                    tli.investment_id AS scheme_id,
                    tl.loan_ref_id AS loan_id,
                    tl.borrower_name,
                    tlpc.source,
                    tlpc.tenure,
                    ROUND(tlpc.tenure)::TEXT || ' Month(s)' AS loan_tenure,
                    ROUND(COALESCE(tild.investment_amount, 0), 2) AS lent_amount,
                    ROUND(COALESCE(tilrs.total_amount_received, 0), 2) AS received_amount,
                    ROUND(COALESCE(tilrs.total_principal_received, 0), 2) AS principal_received,
                    ROUND(COALESCE(tilrs.total_principal_received, 0), 2) AS principle_received,
                    ROUND(COALESCE(tilrs.total_interest_received, 0), 2) AS interest_received,
                    ROUND(COALESCE(tilrs.total_fee_levied, 0), 2) AS fee,
                    ROUND(GREATEST(COALESCE(tilrs.total_interest_received, 0) - COALESCE(tilrs.total_fee_levied, 0), 0), 2) AS net_interest_received,
                    ROUND(COALESCE(tilrs.total_npa_amount, 0), 2) AS npa,
                    ROUND(COALESCE(tilrs.total_amount_received, 0) - COALESCE(tild.investment_amount, 0), 2) AS "p_&_l",
                    ROUND(
                        CASE 
                            WHEN COALESCE(tild.investment_amount, 0) = 0 THEN 0
                            ELSE ((COALESCE(tilrs.total_amount_received, 0) - COALESCE(tild.investment_amount, 0)) / tild.investment_amount) * 100
                        END, 
                        2
                    ) AS absolute_return,
                    tli.id AS tli_id,
                    tl.id AS tl_id
                FROM t_loan tl
                JOIN t_investment_loan_detail tild ON tild.loan_id = tl.id
                    AND tild.deleted IS NULL
                JOIN t_lender_investment tli ON tli.id = tild.investment_id
                    AND tli.deleted IS NULL
                JOIN t_investment_loan_repayment_summary tilrs
                    ON tilrs.investment_loan_id = tild.id
                    AND tilrs.deleted IS NULL
                JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
                    AND tlpc.deleted IS NULL
                JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                    AND tipc.deleted IS NULL
                WHERE tli.lender_id = %(lender_id)s
                    AND tipc.investment_type = %(investment_type)s
                    AND tl.status = ANY(%(status)s)
                    AND tl.deleted IS NULL
                    {scheme_filter}
            )
            SELECT
                ld.scheme_id,
                ld.loan_id,
                ld.borrower_name,
                ld.source,
                NULL AS portfolio_health,
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
                    WHEN ld.tenure = 0 THEN 0
                    ELSE ROUND((ld.absolute_return * 12) / ld.tenure, 2)
                END AS annualized_net_return
            FROM loan_data ld
            ORDER BY ld.tli_id DESC, ld.tl_id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        results = self.execute_fetch_all(sql, params, to_dict=True)
        return results if results else []

    def get_account_statement_portfolio_metrics(
        self,
        lender_id: int,
    ) -> Dict[str, Any]:
        """
        Get simple portfolio aggregates for account statement.

        Aggregates:
            - total_invested: SUM(tli.amount_lent_on_investment)
            - total_returns: SUM(tilrs.total_interest_received - tilrs.total_fee_levied)
            - overall_investment_amount: SUM(tli.amount_lent_on_investment)

        Filtered by lender_id.
        """
        sql = """
            SELECT
                SUM(T.total_invested_per_scheme) AS total_invested,
                SUM(T.total_returns) AS total_returns
            FROM (
                SELECT
                    MAX(tli.amount_lent_on_investment) AS total_invested_per_scheme,
                    SUM(
                        tilrs.total_interest_received - tilrs.total_fee_levied
                    ) AS total_returns
                FROM t_lender_investment tli
                LEFT JOIN t_investment_loan_detail tild
                    ON tli.id = tild.investment_id
                   AND tild.deleted IS NULL
                LEFT JOIN t_investment_loan_repayment_summary tilrs
                    ON tild.id = tilrs.investment_loan_id
                   AND tilrs.deleted IS NULL
                WHERE tli.lender_id = %(lender_id)s
                  AND tli.status = %(status)s
                  AND tli.deleted IS NULL
                GROUP BY tli.id
            ) AS T;
        """

        params = {
            "lender_id": lender_id,
            "status": SchemeStatus.SUCCESS
        }

        return self.execute_fetch_one(sql, params, to_dict=True) or {}

    def get_lender_schemes(
        self,
        user_source_group_id: str,
        investment_type_id: int,
        is_matured: bool,
        limit: int = 10,
        offset: int = 0
    ) -> list:
        sql = """
            SELECT
                t.scheme_id,
                t.scheme_tenure,
                t.lending_date,
                t.created_dtm,
                t.preference_id,
                t.reinvest,
                t.min_lending_roi,
                t.max_lending_roi,
                t.loan_tenure,
                t.partner_name,
                ROUND(t.cancelled_loan_amount, 2) AS cancelled_loan_amount,
                ROUND(SUM(t.investment_amount), 2) AS lent_amount,
                ROUND(SUM(t.total_received_amount), 2) AS total_received_amount,
                ROUND(SUM(t.expected_repayment_sum), 2) AS expected_returns,
                ROUND(SUM(t.principal_received), 2) AS principal,
                ROUND(SUM(t.interest), 2) AS interest,
                ROUND(SUM(t.fee_deducted), 2) AS platform_fees,
                ROUND(SUM(t.principal_outstanding), 2) AS principal_outstanding,
                ROUND(SUM(t.total_npa_amount), 2) AS npa,
                0 AS principal_receivable,
                t.product_type
            FROM (
                SELECT
                    tli.investment_id AS scheme_id,
                    tipc.tenure AS scheme_tenure,
                    tipc.name AS product_type,
                    TO_CHAR(tli.created_dtm, 'YYYY-MM-DD') AS lending_date,
                    tli.created_dtm,
                    tsp.preference_id,
                    tsp.reinvest,
                    tsp.min_lending_roi,
                    tsp.max_lending_roi,
                    tsp.loan_tenure,
                    tmp.value_1 AS partner_name,
                    TRUNC(tli.cancelled_loan_amount, 4) AS cancelled_loan_amount,
                    TRUNC(tild.investment_amount, 4) AS investment_amount,
                    TRUNC(tilrs.total_amount_redeemed, 4) AS total_received_amount,
                    TRUNC(tl.expected_repayment_sum * tild.allocation_percentage / 100, 4) AS expected_repayment_sum,
                    TRUNC(tilrs.principal_outstanding, 4) AS principal_outstanding,
                    TRUNC(tilrs.total_npa_amount, 4) AS total_npa_amount,
                    TRUNC(tilrs.total_fee_levied, 4) AS fee_deducted,
                    TRUNC(tilrs.total_principal_redeemed, 4) AS principal_received,
                    TRUNC(tilrs.total_interest_redeemed, 4) AS interest
                FROM t_lender_investment tli
                JOIN t_lender tle ON tle.id = tli.lender_id
                JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                JOIN t_investment_loan_redemption_summary tilrs ON tilrs.investment_loan_id = tild.id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_scheme_preference tsp ON tsp.investor_scheme_id = tli.id
                JOIN t_investment_product_config tipc ON tipc.id = tli.product_config_id
                JOIN t_mst_parameter tmp ON tmp.id = tle.partner_code_id
                WHERE tle.user_source_group_id = %(user_source_group_id)s
                  AND tli.investment_type_id = %(investment_type_id)s
                  AND tmp.logical_group = 'partner_code'
                  AND (
                      %(is_matured)s = TRUE AND tli.actual_closure_date IS NOT NULL
                      OR %(is_matured)s = FALSE AND tli.actual_closure_date IS NULL
                  )
                  AND tli.deleted IS NULL
                  AND tild.deleted IS NULL
            ) t
            GROUP BY t.scheme_id, t.cancelled_loan_amount, t.scheme_tenure, t.product_type, 
                     t.lending_date, t.created_dtm, t.preference_id, t.reinvest, t.min_lending_roi, 
                     t.max_lending_roi, t.loan_tenure, t.partner_name
            ORDER BY t.scheme_id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        params = {
            'user_source_group_id': user_source_group_id,
            'investment_type_id': investment_type_id,
            'is_matured': is_matured,
            'limit': limit,
            'offset': offset
        }

        return self.execute_fetch_all(sql, params, to_dict=True) or []

    def get_scheme_count(self, data: dict) -> int:
        sql = """
            select count(tl.id) from t_lender tl
            join t_channel_partner_mapping_table tcpmt on tl.partner_mapping_id =tcpmt.id
            join t_lender_investment_order tlio on tlio.lender_id=tl.id
            where 
            --tlio.status in ('CANCELLED','SUCCESS','FAILED')
            --and product_config_id in ()
            tcpmt.channel_partner_id =%(partner_id)s or tcpmt.master_partner_id =%(partner_id)s
        """
        
        params = {
            'partner_id': data['partner_id']
        }
        return self.execute_fetch_one(sql, params, to_dict=True) or 0
        
    def get_scheme_lending_data(self, data: dict) -> list:
        """
        Get mandate lending data based on investment_type.
        Handles MANUAL_LENDING, ONE_TIME_LENDING, and MEDIUM_TERM_LENDING.
        
        Args:
            data: dict containing partner_id, limit, offset, investment_type, 
                  optional status, from_date, to_date
        
        Returns:
            List of lending data dictionaries
        """
        date_filter = status_filter = ""
        investment_type = data['investment_type']
        params = {
            'partner_id': data['partner_id'],
            'limit': data['limit'],
            'offset': data['offset'],
            'investment_type': investment_type
        }
        
        # Status filter - applies to all investment types
        if data.get('status') and data.get('status') != 'ALL':
            status_filter = "AND tlio.status = %(status)s"
            params['status'] = data['status']
        
        # Date filter
        if data.get('from_date') and data.get('to_date'):
            date_filter = "AND tlio.created_dtm::date BETWEEN %(from_date)s AND %(to_date)s"
            params['from_date'] = data['from_date']
            params['to_date'] = data['to_date']
        
        if investment_type == 'MANUAL_LENDING':
            sql = f"""
                SELECT
                    tl.user_source_group_id,
                    tlio.investment_id,
                    tli.amount_lent_on_investment / NULLIF(count(tild.id), 0) AS amount_per_loan,
                    tipc.investment_type,
                    tli.amount_lent_on_investment AS initial_lending_amount,
                    count(tild.id) AS no_of_selected_loans,
                    date(tli.created_dtm) AS created_date,
                    tlio.created_dtm::date AS txn_date,
                    COALESCE(CASE WHEN tlio.status = 'SUCCESS' THEN COUNT(tild.id) END, NULL) AS no_of_approved_loans,
                    COALESCE(CASE WHEN tlio.status = 'SUCCESS' THEN tlio.amount_lent END, NULL) AS total_lending_amount,
                    CASE WHEN tlio.status = ANY(%(status)s) THEN tlio.status ELSE 'PENDING' END AS status
                FROM t_lender tl
                JOIN t_channel_partner_mapping_table tcpmt ON tl.partner_mapping_id = tcpmt.id
                JOIN t_lender_investment_order tlio ON tl.id = tlio.lender_id
                LEFT JOIN t_lender_investment tli ON tli.investment_id = tlio.investment_id
                JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                LEFT JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                WHERE (tcpmt.channel_partner_id = %(partner_id)s OR tcpmt.master_partner_id = %(partner_id)s)
                AND tipc.investment_type = %(investment_type)s
                {date_filter}
                {status_filter}
                GROUP BY 
                    tl.user_source_group_id,
                    tlio.investment_id,
                    tlio.status,
                    tlio.amount_lent,
                    tli.created_dtm,
                    tlio.created_dtm,
                    tli.amount_lent_on_investment,
                    tipc.investment_type
                ORDER BY tlio.investment_id
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params["status"] = [OrderStatus.SUCCESS, OrderStatus.CANCELLED, OrderStatus.FAILED]
        else:
            # ONE_TIME_LENDING or MEDIUM_TERM_LENDING
            sql = f"""
                SELECT 
                    tipc.investment_type,
                    tl.user_source_group_id,
                    tlio.created_dtm::date AS txn_date,
                    tlio.amount_lent,
                    tlio.investment_id,
                    tipc.tenure,
                    tlio.created_dtm::date AS start_date,
                    tlio.expected_closure_date AS maturity_date,
                    CASE WHEN tlio.status = %(status)s THEN 'PENDING'
                        WHEN tipc.investment_type = 'AUTO_LENDING' THEN 'PENDING'
                        ELSE tlio.status
                    END AS scheme_status
                FROM t_lender_investment_order tlio
                JOIN t_lender tl ON tl.id = tlio.lender_id
                JOIN t_channel_partner_mapping_table tcpmt ON tcpmt.id = tl.partner_mapping_id
                JOIN t_investment_product_config tipc ON tlio.product_config_id = tipc.id
                WHERE (tcpmt.channel_partner_id = %(partner_id)s OR tcpmt.master_partner_id = %(partner_id)s)
                AND tipc.investment_type = %(investment_type)s
                {date_filter}
                {status_filter}
                ORDER BY tlio.created_dtm DESC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            params["status"] = OrderStatus.PENDING
            
        return self.execute_fetch_all(sql, params, to_dict=True) or []