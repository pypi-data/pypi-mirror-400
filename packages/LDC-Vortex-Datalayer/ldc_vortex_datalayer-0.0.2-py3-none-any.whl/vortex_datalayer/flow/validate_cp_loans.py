from ..base_layer import BaseDataLayer
from ..constants import LoanStatus


class ValidateCpLoans(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """
    def validate_loan_cp_ml(self, loan_ids, user_source_id, batch_number, amount_per_loan):
        sql = """
                WITH inserted AS (
                    INSERT INTO t_scheme_loan_mapping (
                        batch_number, loan_id, user_source_group_id, is_available, 
                        loan_roi, ldc_score, lent_amount, loan_amount, loan_tenure, 
                        borrower_name, is_selected
                    )
                    SELECT
                        %(batch_number)s, tl.loan_ref_id, %(user_source_id)s,
                        CASE
                            WHEN tl.investment_amount_sum + 250 < tl.amount THEN TRUE
                            ELSE FALSE
                        END AS is_available, 
                        tl.interest_rate, 
                        tl.ldc_score,
                        %(amount_per_loan)s,
                        tl.amount,
                        tl.tenure,
                        tl.borrower_name,
                        TRUE
                    FROM t_loan tl 
                    WHERE tl.loan_ref_id = ANY(%(loan_ids)s)
                    AND tl.status = %(loan_status)s
                    RETURNING loan_id, is_available
                )
                SELECT ARRAY_AGG(loan_id) AS available_loan_ids
                FROM inserted
                WHERE is_available = TRUE;
            """

        params = {
            'batch_number': batch_number,
            'user_source_id': user_source_id,
            'loan_status': LoanStatus.LIVE,
            'loan_ids': loan_ids,
            'amount_per_loan': amount_per_loan
        }

        return self.execute_fetch_one(sql, params)
