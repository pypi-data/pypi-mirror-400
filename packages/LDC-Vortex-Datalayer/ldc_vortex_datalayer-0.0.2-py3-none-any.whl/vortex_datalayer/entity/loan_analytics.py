from ..base_layer import BaseDataLayer
from ..constants import LoanAnalyticsKeys


class LoanAnalytics(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """
    def bulk_insert_loan_analytics(self, analytics_data):
        return self._execute_bulk_insert(
            table_name='t_loan_analytics',
            data_list=analytics_data
        )

    def get_count(self):
        sql = """
                SELECT key, value
                FROM (
                    SELECT key, value,
                           ROW_NUMBER() OVER (PARTITION BY key ORDER BY id DESC) AS rn
                    FROM t_loan_analytics
                    WHERE key = ANY(%(keys)s)
                ) t
                WHERE rn = 1;
            """

        params = {
            'keys': [LoanAnalyticsKeys.LIVE_LOAN_COUNT, LoanAnalyticsKeys.FUNDED_LOAN_COUNT]
        }

        return self.execute_fetch_all(sql, params)