from ..base_layer import BaseDataLayer
from ..constants import LoanStatus, PartnerCode, FmppInvestmentType


class FetchLoans(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """

    def get_loans(
            self, investor_id, filter_conditions, sort_by_conditions, limit, offset,
            lending_amount, buffer_remaining_amount, funding_dtm
    ):
        order_by_clause = f"ORDER BY {sort_by_conditions}" if sort_by_conditions else ""

        sql = f"""
                SELECT
                    COALESCE(t_loan.borrower_name, '_') AS borrower_name,
                    COALESCE(t_loan.loan_ref_id, '-') AS loan_id,
                    ROUND(t_loan.amount::NUMERIC, 2)::TEXT AS loan_amount,
                    ROUND(t_loan.investment_amount_sum::NUMERIC, 2)::TEXT AS funded_amount,
                    ROUND(COALESCE(t_loan.remaining_amount, 0)::NUMERIC, 2)::TEXT AS remaining_amount,
                    t_loan.tenure::TEXT AS loan_tenure,
                    'Month(s)' AS loan_tenure_type,
                    ROUND(t_loan.interest_rate::NUMERIC, 2)::TEXT AS loan_roi,
                    COALESCE(t_loan.ldc_score::TEXT, '-') AS ldc_score,
                    COALESCE(t_loan.risk_type::TEXT, '-') AS risk_type,
                    %(lending_amount)s AS lending_amount,
                    ARRAY[
                        ROUND(t_loan.interest_rate::NUMERIC, 2)::TEXT,
                        ROUND((t_loan.interest_rate + %(loan_roi_1)s)::NUMERIC, 2)::TEXT,
                        ROUND((t_loan.interest_rate + %(loan_roi_2)s)::NUMERIC, 2)::TEXT
                    ] AS roi_list,
                    t_loan.is_modified_roi AS is_modified,
                    CASE
                        WHEN tlpc.partner_code = 'PP' THEN 'Daily'
                        ELSE 'Monthly'
                    END AS repayment_frequency,
                    ROUND(COALESCE((t_loan.remaining_amount * 100.0 / t_loan.amount), 0)::NUMERIC, 2) AS remaining_amount_percentage
                FROM t_loan
                JOIN t_loan_product_config tlpc ON t_loan.loan_product_config_id = tlpc.id
                WHERE
                    t_loan.status = %(loan_status)s
                    AND t_loan.amount >= t_loan.investment_amount_sum + %(buffer_remaining_amount)s
                    AND t_loan.created_dtm <= %(funding_dtm)s
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_lender_investment tli
                        JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                        JOIN t_lender tl ON tli.lender_id = tl.id
                        WHERE tl.user_id = %(investor_id)s
                          AND tild.loan_id = t_loan.id
                          AND tild.deleted IS NULL
                          AND tli.deleted IS NULL
                    )
                    {filter_conditions}
                {order_by_clause}
                LIMIT %(limit)s OFFSET %(offset)s
            """

        params = {
            'investor_id': investor_id,
            'lending_amount': lending_amount,
            'buffer_remaining_amount': buffer_remaining_amount,
            'funding_dtm': funding_dtm,
            'loan_status': LoanStatus.LIVE,
            'loan_roi_1': 0.5,
            'loan_roi_2': 1,
            'limit': limit,
            'offset': offset
        }

        return self.execute_fetch_all(sql, params)

    def get_funded_loans_count(self):
        sql = """
                SELECT 
                    count(tl.id) as funded_loans_count
                FROM t_lender_investment tli
                JOIN t_lender tls ON tli.lender_id = tls.id
                JOIN t_mst_parameter tmp ON tli.investment_type_id = tmp.id
                JOIN t_mst_parameter tmp2 ON tls.partner_code_id = tmp2.id
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_loan tl ON tild.loan_id = tl.id
                WHERE 
                    tmp.key_2 = %(otl_inv_type)s 
                    AND tmp2.key_2 = %(lender_partner_code)s
                    AND tl.created_dtm  > NOW() - INTERVAL '30 DAY' 
                    AND tl.status = %(loan_status)s
                    AND tli.deleted IS NULL 
                    AND tild.deleted IS NULL 
                    AND tl.deleted IS NULL;
            """

        params = {
            'loan_status': LoanStatus.DISBURSED,
            'otl_inv_type': FmppInvestmentType.ONE_TIME_LENDING,
            'lender_partner_code': PartnerCode.LENDER
        }

        return self.execute_fetch_one(sql, params)

    def fetch_otl_loan_counts_and_amounts(
            self, funding_time, investor_id, cig_preference_query_condition,
            product_config
    ):
        query = f"""
            WITH sorted_loans AS (
                SELECT
                    t_loan.remaining_amount AS available_amount,
                    {product_config['case_statement']} AS invest_amount
                FROM t_loan
                WHERE
                    t_loan.status = 'LIVE'
                    AND t_loan.created_dtm <= %(funding_dtm)s
                    {product_config['product_filter_query']}
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_lender_investment tli
                        JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                        JOIN t_lender tl ON tli.lender_id = tl.id
                        WHERE tl.user_id = %(user_id)s
                          AND tild.loan_id = t_loan.id
                          AND tild.deleted IS NULL
                          AND tli.deleted IS NULL
                    )
                    {cig_preference_query_condition}
            )
            SELECT
                invest_amount,
                COALESCE(count(invest_amount), 0) AS available_loan_count
            FROM sorted_loans
            WHERE invest_amount > 0
            GROUP BY invest_amount ORDER BY invest_amount
        """
        params = {
            'user_id': investor_id,
            'funding_dtm': funding_time
        }

        return self.execute_fetch_all(query, params)

    def fetch_otl_loan_list(
            self, funding_time, investor_id, limit, cig_preference_query_condition,
            order_by_clause, cig_ordering, product_config
    ):
        query = f"""
            WITH sorted_loans AS (
                SELECT
                    t_loan.id,
                    t_loan.loan_ref_id,
                    t_loan.tenure,
                    t_loan.amount,
                    t_loan.investment_amount_sum,
                    t_loan.interest_rate,
                    t_loan.ldc_score,
                    t_loan.borrower_name,
                    t_loan.remaining_amount AS available_amount,
                    {product_config['case_statement']} AS invest_amount,
                    CASE
                        WHEN t_loan.risk_type = 'LOW' THEN 1
                        WHEN t_loan.risk_type = 'MEDIUM' THEN 2
                        WHEN t_loan.risk_type = 'HIGH' THEN 3
                        ELSE 4
                    END AS risk_type_order,
                    CASE
                        WHEN t_loan.is_modified_roi THEN 1
                        ELSE 0
                    END AS is_modified_roi_order,
                    CASE
                        WHEN tlpc.partner_code = 'RAJ' THEN 0
                        ELSE 1
                    END AS partner_code_order
                FROM t_loan
                JOIN t_loan_product_config tlpc ON t_loan.loan_product_config_id = tlpc.id
                WHERE
                    t_loan.status = 'LIVE'
                    AND t_loan.created_dtm <= %(funding_time)s
                    {product_config['product_filter_query']}
                    AND tlpc.deleted IS NULL
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_lender_investment tli
                        JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                        JOIN t_lender tl ON tli.lender_id = tl.id
                        WHERE tl.user_id = %(user_id)s
                          AND tild.loan_id = t_loan.id
                          AND tild.deleted IS NULL
                          AND tli.deleted IS NULL
                    )
                    {cig_preference_query_condition}
                ORDER BY {order_by_clause}
            )
            SELECT
                id,
                loan_ref_id,
                tenure,
                amount,
                interest_rate,
                ldc_score,
                risk_type_order,
                is_modified_roi_order,
                borrower_name,
                invest_amount
            FROM sorted_loans
            WHERE invest_amount > 0
            ORDER BY {cig_ordering}
            LIMIT %(limit)s
        """

        params = {
            'funding_time': funding_time,
            'user_id': investor_id,
            'limit': limit,
        }
        return self.execute_fetch_all(query, params)

    def insert_otl_log_data(self, otl_log_data):
        sql = """
                INSERT INTO t_otl_loan_tracker_logs (
                    created_dtm, per_loan_amount, available_loan_count, batch_number
                )
                VALUES (
                    NOW(), %(per_loan_amount)s, %(available_loan_count)s, %(batch_number)s
                )
                RETURNING id;
            """

        params = {
            'per_loan_amount': otl_log_data['per_loan_amount'],
            'available_loan_count': otl_log_data['available_loan_count'],
            'batch_number': otl_log_data['batch_number']
        }

        return self.execute_fetch_one(sql, params)
    
    def get_investment_product_configs_for_validation(
        self,
        partner_code_id: int,
        investment_type_id: int = None
    ):
        sql = """
            SELECT
                tipc.id,
                tipc.name,
                tipc.display_name,
                tipc.tenure,
                tipc.min_amount,
                tipc.max_amount,
                tipc.expected_roi,
                tipc.is_default,
                tipc.default_amount,
                tipc.investment_type_id,
                tipc.investment_type
            FROM t_investment_product_config tipc
            WHERE tipc.is_active = TRUE
              AND tipc.deleted IS NULL
              AND tipc.partner_code_id = %(partner_code_id)s
        """
        
        params = {'partner_code_id': partner_code_id}
        
        if investment_type_id:
            sql += " AND tipc.investment_type_id = %(investment_type_id)s"
            params['investment_type_id'] = investment_type_id
        
        sql += " ORDER BY tipc.tenure"
        
        return self.execute_fetch_all(sql, params)