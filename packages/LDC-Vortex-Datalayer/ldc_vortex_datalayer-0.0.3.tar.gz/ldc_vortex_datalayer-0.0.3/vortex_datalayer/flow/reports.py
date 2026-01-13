"""
Reports Flow Layer
Handles complex reporting queries and data aggregation.
"""
from typing import List, Dict, Any, Tuple
from ..base_layer import BaseDataLayer
from ..constants import LoanStatus

class ReportsFlow(BaseDataLayer):

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)

    def _build_datetime_filter(
        self,
        from_datetime,
        to_datetime,
        table_alias: str,
        column_name: str
    ) -> Tuple[str, Dict[str, Any]]:
        filter_parts = []
        params = {}
        
        if from_datetime:
            filter_parts.append(f"AND {table_alias}.{column_name} >= %(from_datetime)s")
            params['from_datetime'] = from_datetime
            
        if to_datetime:
            filter_parts.append(f"AND {table_alias}.{column_name} <= %(to_datetime)s")
            params['to_datetime'] = to_datetime
            
        return ' '.join(filter_parts), params

    def retail_manual_lending_report_data(
        self,
        user_source_group_id: str,
        from_datetime,
        to_datetime,
        loan_status: str,
    ) -> List[Dict[str, Any]]:
        date_filter, date_params = self._build_datetime_filter(
            from_datetime, to_datetime, 'tli', 'created_dtm'
        )
        
        # Define closed statuses list
        closed_statuses = [LoanStatus.CLOSED, LoanStatus.NPA]

        # Build status filter
        status_filter = ""
        if loan_status == 'OPEN':
            status_filter = "WHERE status = 'ACTIVE'"
        elif loan_status == 'CLOSED':
            status_filter = "WHERE status = 'CLOSED'"
        # For 'ALL', no filter needed
        
        sql = f"""
            SELECT * FROM (
                SELECT
                    tli.investment_id AS scheme_id,
                    tli.lender_id as investor_pk,
                    TO_CHAR(tli.created_dtm, 'DD/MM/YYYY') AS created_date,
                    TO_CHAR((tl.liquidation_date AT TIME ZONE 'Asia/Kolkata')::date, 'DD/MM/YYYY') as disbursement_date,
                    tli.created_dtm,
                    tl.interest_rate,
                    tl.tenure AS loan_tenure,
                    tl.loan_ref_id as loan_id,
                    tlrs.days_past_due as dpd,
                    ROUND(tild.investment_amount, 2) AS investment_amount,
                    CASE
                        WHEN tlpc.partner_code = 'PP' AND tl.liquidation_date IS NOT NULL THEN TO_CHAR(tl.liquidation_date, 'DD/MM/YYYY')
                        WHEN tlpc.partner_code = 'PP' THEN '-'
                        ELSE TO_CHAR(tl.first_repayment_date, 'DD/MM/YYYY')
                    END AS repayment_start_date,
                    ROUND(tilrs.total_amount_redeemed, 2) AS total_amount_received,
                    ROUND((tl.expected_repayment_sum * tild.allocation_percentage) / 100, 2) AS total_receivable,
                    CASE
                        WHEN tild.is_cancelled = TRUE THEN ROUND(tild.investment_amount, 2)
                        ELSE 0
                    END AS refunded_amount,
                    CASE
                        WHEN tl.status = ANY(%(closed_statuses)s) THEN '{LoanStatus.CLOSED}'
                        WHEN tl.status = '{LoanStatus.CANCELLED}' THEN '{LoanStatus.CANCELLED}'
                        ELSE 'ACTIVE'
                    END AS status,
                    ROUND(tilrs.total_principal_redeemed, 2) as principal_received,
                    ROUND(tilrs.total_interest_redeemed, 2) as interest_received,
                    ROUND(tilrs.total_fee_levied, 2) as fees,
                    CASE
                        WHEN tl.status = '{LoanStatus.NPA}' OR tilrs.total_npa_amount > 0 THEN
                            ROUND(tilrs.total_npa_amount, 2)
                        ELSE 0
                    END as npa,
                    CASE
                        WHEN tlpc.partner_code = 'PP' THEN 'Daily'
                        ELSE 'Monthly'
                    END as repayment_type,
                    CASE
                        WHEN tl.status = ANY(%(closed_statuses)s)
                        THEN ROUND(tilrs.total_amount_redeemed - tild.investment_amount, 2)
                        ELSE 0
                    END as profit_loss
                FROM t_lender_investment tli
                JOIN t_lender tle ON tle.user_source_group_id = %(user_source_group_id)s
                    AND tli.lender_id = tle.id
                    AND tle.deleted IS NULL
                JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                    AND tild.deleted IS NULL
                JOIN t_loan tl ON tl.id = tild.loan_id
                    AND tl.deleted IS NULL
                LEFT JOIN t_loan_repayment_summary tlrs ON tlrs.loan_id = tl.id
                LEFT JOIN t_investment_loan_redemption_summary tilrs ON tilrs.investment_loan_id = tild.id
                    AND tilrs.deleted IS NULL
                JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
                WHERE tli.deleted IS NULL
                    AND NOT tild.is_negotiated
                    {date_filter}
                
                UNION ALL
                
                SELECT
                    tli.investment_id AS scheme_id,
                    tli.lender_id as investor_pk,
                    TO_CHAR(tli.created_dtm, 'DD/MM/YYYY') AS created_date,
                    '-' as disbursement_date,
                    tli.created_dtm,
                    tlmo.actual_interest_rate AS interest_rate,
                    tl.tenure AS loan_tenure,
                    tl.loan_ref_id as loan_id,
                    0 as dpd,
                    ROUND(tli.amount_lent_on_investment, 2) AS investment_amount,
                    '-' AS repayment_start_date,
                    0 AS total_amount_received,
                    0 AS total_receivable,
                    CASE
                        WHEN tli.status = 'REJECTED' THEN ROUND(tli.cancelled_loan_amount, 2)
                        ELSE 0
                    END AS refunded_amount,
                    CASE
                        WHEN tli.status = 'REJECTED' THEN 'REJECTED'
                        ELSE 'PROCESSING'
                    END AS status,
                    0 as principal_received,
                    0 as interest_received,
                    0 as fees,
                    0 as npa,
                    CASE
                        WHEN tlpc.partner_code = 'PP' THEN 'Daily'
                        ELSE 'Monthly'
                    END as repayment_type,
                    0 as profit_loss
                FROM t_lender_investment tli
                JOIN t_lender tle ON tle.user_source_group_id = %(user_source_group_id)s
                    AND tli.lender_id = tle.id
                    AND tle.deleted IS NULL
                JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_loan_modified_offer tlmo ON tlmo.loan_id = tl.id
                JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
                WHERE tli.deleted IS NULL
                    AND tild.is_negotiated = true
                    {date_filter}
            ) combined_data
            {status_filter}
            ORDER BY scheme_id DESC
        """
        
        
        params = {
            'user_source_group_id': user_source_group_id,
            'closed_statuses': closed_statuses,
        }
        params.update(date_params)
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def cp_manual_lending_report_data(
        self,
        investment_type_id: int,
        investor_id: str,
        partner_id: str,
        partner_code_id: int,
        from_datetime,
        to_datetime,
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        
        date_filter, date_params = self._build_datetime_filter(
            from_datetime, to_datetime, 'tli', 'created_dtm'
        )
        
        sql = f"""
            SELECT
                tli.investment_id AS scheme_id,
                tli.lender_id as investor_pk,
                TO_CHAR(tli.created_dtm, 'DD/MM/YYYY') AS created_date,
                TO_CHAR((tl.liquidation_date AT TIME ZONE 'Asia/Kolkata')::date, 'DD/MM/YYYY') as disbursement_date,
                tli.created_dtm,
                tl.interest_rate,
                tl.tenure AS loan_tenure,
                tl.loan_ref_id as loan_id,
                tlrs.days_past_due as dpd,
                ROUND(tild.investment_amount, 2) AS investment_amount,
                CASE
                    WHEN tlpc.partner_code = 'PP' AND tl.liquidation_date IS NOT NULL THEN TO_CHAR(tl.liquidation_date, 'DD/MM/YYYY')
                    WHEN tlpc.partner_code = 'PP' THEN '-'
                    ELSE TO_CHAR(tl.first_repayment_date, 'DD/MM/YYYY')
                END AS repayment_start_date,
                ROUND(tilrs.total_amount_received, 2) AS total_amount_received,
                ROUND((tl.expected_repayment_sum * tild.allocation_percentage) / 100, 2) AS total_receivable,
                CASE
                    WHEN tild.is_cancelled = TRUE THEN ROUND(tild.investment_amount, 2)
                    ELSE 0
                END AS refunded_amount,
                CASE
                    WHEN tl.status = '{LoanStatus.CLOSED}' OR tl.status = '{LoanStatus.NPA}' THEN '{LoanStatus.CLOSED}'
                    WHEN tl.status = '{LoanStatus.CANCELLED}' THEN '{LoanStatus.CANCELLED}'
                    ELSE 'ACTIVE'
                END AS status,
                ROUND(tilrs.total_principal_received, 2) as principal_received,
                ROUND(tilrs.total_interest_received, 2) as interest_received,
                ROUND(tilrs.total_fee_levied, 2) as fees,
                CASE
                    WHEN tl.status = '{LoanStatus.NPA}' OR tilrs.total_npa_amount > 0 THEN
                        ROUND(tilrs.total_npa_amount, 2)
                    ELSE 0
                END as npa,
                CASE
                    WHEN tlpc.partner_code = 'PP' THEN 'Daily'
                    ELSE 'Monthly'
                END as repayment_type,
                CASE
                    WHEN tl.status = '{LoanStatus.NPA}' OR tl.status = '{LoanStatus.CLOSED}'
                    THEN ROUND(tilrs.total_amount_received - tild.investment_amount, 2)
                    ELSE 0
                END as profit_loss
            FROM t_lender_investment tli
            JOIN t_lender tle ON tli.lender_id = tle.id
                AND tle.deleted IS NULL
                AND tle.user_id = %(investor_id)s
                AND tle.partner_id = %(partner_id)s
                AND tle.partner_code_id = %(partner_code_id)s
            JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                AND tild.deleted IS NULL
            JOIN t_loan tl ON tl.id = tild.loan_id
                AND tl.deleted IS NULL
            LEFT JOIN t_loan_repayment_summary tlrs ON tlrs.loan_id = tl.id
            LEFT JOIN t_investment_loan_repayment_summary tilrs ON tilrs.investment_loan_id = tild.id
                AND tilrs.deleted IS NULL
            JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
            WHERE tli.investment_type_id = %(investment_type_id)s
                AND tli.deleted IS NULL
                AND NOT tild.is_negotiated
                {date_filter}
            
            UNION ALL
            
            SELECT
                tli.investment_id AS scheme_id,
                tli.lender_id as investor_pk,
                TO_CHAR(tli.created_dtm, 'DD/MM/YYYY') AS created_date,
                '-' as disbursement_date,
                tli.created_dtm,
                tlmo.actual_interest_rate AS interest_rate,
                tl.tenure AS loan_tenure,
                tl.loan_ref_id as loan_id,
                0 as dpd,
                ROUND(tli.amount_lent_on_investment, 2) AS investment_amount,
                '-' AS repayment_start_date,
                0 AS total_amount_received,
                0 AS total_receivable,
                CASE
                    WHEN tli.status = 'REJECTED' THEN ROUND(tli.cancelled_loan_amount, 2)
                    ELSE 0
                END AS refunded_amount,
                CASE
                    WHEN tli.status = 'REJECTED' THEN 'REJECTED'
                    ELSE 'PROCESSING'
                END AS status,
                0 as principal_received,
                0 as interest_received,
                0 as fees,
                0 as npa,
                CASE
                    WHEN tlpc.partner_code = 'PP' THEN 'Daily'
                    ELSE 'Monthly'
                END as repayment_type,
                0 as profit_loss
            FROM t_lender_investment tli
            JOIN t_lender tle ON tli.lender_id = tle.id
                AND tle.deleted IS NULL
                AND tle.user_id = %(investor_id)s
                AND tle.partner_id = %(partner_id)s
                AND tle.partner_code_id = %(partner_code_id)s
            JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
            JOIN t_loan tl ON tl.id = tild.loan_id
            JOIN t_loan_modified_offer tlmo ON tlmo.loan_id = tl.id
            JOIN t_loan_product_config tlpc ON tlpc.id = tl.loan_product_config_id
            WHERE tli.investment_type_id = %(investment_type_id)s
                AND tli.deleted IS NULL
                AND tild.is_negotiated = true
                {date_filter}
            
            ORDER BY scheme_id DESC
        """
        
        if not download:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
        
        params = {
            'investment_type_id': investment_type_id,
            'investor_id': investor_id,
            'partner_id': partner_id,
            'partner_code_id': partner_code_id,
            'limit': limit,
            'offset': offset
        }
        params.update(date_params)
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

