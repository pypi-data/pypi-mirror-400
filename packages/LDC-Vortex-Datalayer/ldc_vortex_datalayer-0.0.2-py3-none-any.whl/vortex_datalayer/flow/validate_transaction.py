from ..base_layer import BaseDataLayer


class ValidateTransaction(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """
    def validate_otl_txn_data(self, data):
        sql = """
                SELECT
                    lt.id as txn_pk,  lt.amount as amount, lt.source_transaction_id,
                    lost.tenure as tenure, lost.preference_id as preference_id,
                    amount_per_loan, lost.id tracker_id
                FROM t_lender_wallet_transaction lt
                JOIN t_scheme_tracker lost ON lt.id = lost.transaction_id
                JOIN t_lender_investment_order ls on lt.lender_id = ls.lender_id
                WHERE 
                    lt.user_source_group_id = %(user_source_group_id)s 
                    AND ls.investment_id = %(investment_id)s 
                    AND lt.status = %(txn_status)s 
                    AND ls.status = %(inv_order_status)s 
                    AND lost.batch_number = %(batch_number)s;
            """

        params = {
            "user_source_group_id": data["user_source_group_id"],
            "investment_id": data["investment_id"],
            "batch_number": data["batch_number"],
            "txn_status": data["txn_status"],
            "inv_order_status": data["inv_order_status"]
        }

        return self.execute_fetch_one(sql, params=params)
