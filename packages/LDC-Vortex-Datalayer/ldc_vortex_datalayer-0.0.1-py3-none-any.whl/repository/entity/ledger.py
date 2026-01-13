from ..base_layer import BaseDataLayer


class Ledger(BaseDataLayer):
    def create_lender_escrow(self, data):
        sql = """
                INSERT INTO t_ledger_lender_escrow (
                    account_id, event_type, amount, transaction_dtm, 
                    source_transaction_id, event_id, created_by, previous_balance, 
                    current_balance, transaction_id, value_dtm, narration
                ) VALUES (
                    %(account_id)s, 
                    %(event_type)s, %(amount)s, %(transaction_dtm)s, 
                    %(source_transaction_id)s, %(event_id)s, %(created_by)s, 
                    %(previous_balance)s, %(current_balance)s, %(transaction_id)s, 
                    %(value_dtm)s, %(narration)s
                ) RETURNING id;
            """

        params = {
            "account_id": data['account_id'],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "source_transaction_id": data.get("source_transaction_id"),
            "transaction_id": data["transaction_id"],
            "event_id": 1,
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"],
            "value_dtm": data.get("value_dtm"),
            "transaction_dtm": data.get("transaction_dtm"),
            "narration": data.get("narration")
        }

        return self.execute_fetch_one(sql, params)

    def create_lender_wallet_ledger(self, data):
        sql = """
                INSERT INTO t_ledger_lender_wallet (
                    account_id, event_type, amount, transaction_dtm, 
                    source_transaction_id, event_id, created_by, previous_balance, 
                    current_balance, transaction_id, narration
                ) VALUES (
                    %(account_id)s, %(event_type)s, %(amount)s, %(transaction_dtm)s, 
                    %(source_transaction_id)s, %(event_id)s, %(created_by)s, 
                    %(previous_balance)s, %(current_balance)s, %(transaction_id)s,
                    %(narration)s
                ) RETURNING id;
            """

        params = {
            "account_id": data["account_id"],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "source_transaction_id": data["source_transaction_id"],
            "transaction_id": data["transaction_id"],
            "event_id": 1,
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"],
            "transaction_dtm": data.get("transaction_dtm"),
            "narration": data.get("narration")
        }

        return self.execute_fetch_one(sql, params)

    def create_pg(self, data):
        sql = """
                INSERT INTO t_ledger_pg (
                    account_id, event_type, amount, value_dtm, 
                    source_transaction_id, event_id, created_by, previous_balance, 
                    current_balance, transaction_id, narration
                ) VALUES (
                    %(account_id)s, 
                    %(event_type)s, %(amount)s, %(value_dtm)s, 
                    %(source_transaction_id)s, %(event_id)s, %(created_by)s, 
                    %(previous_balance)s, %(current_balance)s, %(transaction_id)s, 
                    %(narration)s
                ) RETURNING id;
            """

        params = {
            "account_id": data["account_id"],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "source_transaction_id": data.get("source_transaction_id"),
            "transaction_id": data["transaction_id"],
            "event_id": 1,
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"],
            "value_dtm": data["value_dtm"],
            "narration": data.get("narration")
        }

        return self.execute_fetch_one(sql, params)

    def create_investment_wallet(self, data):
        sql = """
                INSERT INTO t_ledger_investment_wallet (
                    account_id, event_type, amount, transaction_dtm, 
                    source_transaction_id, event_id, created_by, previous_balance, 
                    current_balance, transaction_id, narration
                ) VALUES (
                    %(account_id)s, 
                    %(event_type)s, %(amount)s, %(transaction_dtm)s, 
                    %(source_transaction_id)s, %(event_id)s, %(created_by)s, 
                    %(previous_balance)s, %(current_balance)s,  %(transaction_id)s, 
                    %(narration)s
                ) RETURNING id;
            """

        params = {
            "account_id": data["account_id"],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "source_transaction_id": data["source_transaction_id"],
            "transaction_id": data["transaction_id"],
            "event_id": 1,
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"],
            "transaction_dtm": data.get("transaction_dtm"),
            "narration": data.get("narration")
        }

        return self.execute_fetch_one(sql, params)

    def create_loan_account(self, data):
        sql = """
                INSERT INTO t_ledger_loan_account (
                    account_id, event_type, amount, transaction_dtm, transaction_id, 
                    source_transaction_id, narration, created_by, previous_balance, 
                    current_balance
                ) VALUES (
                    %(account_id)s, %(event_type)s, %(amount)s, %(transaction_dtm)s, 
                    %(transaction_id)s, %(source_transaction_id)s, %(narration)s, 
                    %(created_by)s, %(previous_balance)s, %(current_balance)s
                ) RETURNING id;
            """

        params = {
            "account_id": data["account_id"],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "transaction_dtm": data.get("transaction_dtm"),
            "transaction_id": data["transaction_id"],
            "source_transaction_id": data.get("source_transaction_id"),
            "narration": data.get("narration"),
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"]
        }

        return self.execute_fetch_one(sql, params)

    def create_borrower_escrow(self, data):
        sql = """
                INSERT INTO t_ledger_borrower_escrow (
                    account_id, event_type, amount, transaction_dtm, transaction_id, 
                    source_transaction_id, narration, created_by, previous_balance, 
                    current_balance
                ) VALUES (
                    %(account_id)s, %(event_type)s, %(amount)s, %(transaction_dtm)s, 
                    %(transaction_id)s, %(source_transaction_id)s, %(narration)s, 
                    %(created_by)s, %(previous_balance)s, %(current_balance)s
                ) RETURNING id;
            """

        params = {
            "account_id": data["account_id"],
            "event_type": data["event_type"],
            "amount": data["amount"],
            "transaction_dtm": data.get("transaction_dtm"),
            "transaction_id": data["transaction_id"],
            "source_transaction_id": data.get("source_transaction_id"),
            "narration": data.get("narration"),
            "created_by": data["created_by"],
            "previous_balance": data["previous_balance"],
            "current_balance": data["current_balance"]
        }

        return self.execute_fetch_one(sql, params)
