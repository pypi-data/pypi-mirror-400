from ..base_layer import BaseDataLayer
from ..constants import TransactionStatus


class NetWorthLayer(BaseDataLayer):
    def get_principal_outstanding(self, investor_id):
        sql = """
                SELECT COALESCE(SUM(total_principal_outstanding), 0) as pos
                FROM lendenapp_portfolio_summary lps
                JOIN t_lender tl on lps.lender_id = tl.id
                WHERE tl.user_id = %(investor_id)s
                AND lps.deleted IS NULL
                AND tl.deleted IS NULL
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
    
    def get_total_balance(self, source_id: int):
        sql = """
                select round(sum(balance), 2) as total_balance from t_account 
                where lender_id in (
                    select id from t_lender 
                    where user_id in (
                        select user_id from t_lender 
                        where user_source_group_id = %(source_id)s
                        ));
            """
        params = {
            'source_id': source_id
        }
        return self.execute_fetch_one(sql, params)