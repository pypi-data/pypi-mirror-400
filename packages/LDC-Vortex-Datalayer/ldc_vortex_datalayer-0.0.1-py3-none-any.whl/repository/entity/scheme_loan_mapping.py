from datetime import timedelta

from ..base_layer import BaseDataLayer
from ..constants import OTLInvestment
from ..helper.date_utils import get_current_dtm


class SchemeLoanMapping(BaseDataLayer):
    def insert(self, data_to_insert):
        return self._execute_bulk_insert(
            table_name='t_scheme_loan_mapping',
            data_list=data_to_insert
        )

    def get_loans(self, batch_number, repayment_frequency):
        sql = """
                SELECT loan_id, loan_roi, ldc_score, loan_tenure::integer, borrower_name, 
                    %(repayment_frequency)s as repayment_frequency,
                    loan_amount, lent_amount as lending_amount, 
                    %(loan_tenure_type)s as loan_tenure_type
                FROM t_scheme_loan_mapping
                WHERE batch_number = %(batch_number)s and is_available = TRUE 
                and is_selected = TRUE and created_dtm > %(yesterday)s
                ORDER BY id
                """

        params = {
            'batch_number': batch_number,
            'loan_tenure_type': OTLInvestment.OTL_LOAN_TENURE_TYPE,
            'yesterday': get_current_dtm() - timedelta(days=1),
            'repayment_frequency': repayment_frequency
        }
        return self.execute_fetch_all(sql, params)

    def mark_loans_unavailable(self, failed_loan_ids, batch_number):
        sql = """
                UPDATE t_scheme_loan_mapping
                SET is_available = False
                WHERE loan_id = ANY(%(failed_loan_ids)s)
                and batch_number = %(batch_number)s
                and created_dtm > %(yesterday)s
            """
        params = {
            "failed_loan_ids" : list(failed_loan_ids),
            "batch_number" : batch_number,
            "yesterday" : get_current_dtm() - timedelta(days=1)
        }

        return self.execute_no_return(sql, params=params)