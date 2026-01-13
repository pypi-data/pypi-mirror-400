from ..base_layer import BaseDataLayer
from ..constants import OrderStatus


class LenderInvestmentOrder(BaseDataLayer):
    def insert(self, order_data):
        sql = """
            INSERT INTO t_lender_investment_order (
                investment_id, lender_id, amount_lent, is_active, status, 
                product_config_id, transaction_id
            ) 
            VALUES (
                %(investment_id)s, %(lender_id)s, %(amount_lent)s, %(is_active)s, 
                %(status)s, %(product_config_id)s, %(transaction_id)s
            ) RETURNING id;
        """

        params = {
            'lender_id': order_data['lender_id'],
            'amount_lent': order_data['amount_lent'],
            'is_active': order_data['is_active'],
            'status': order_data['status'],
            'investment_id': order_data['investment_id'],
            'product_config_id': order_data['product_config_id'],
            'transaction_id': order_data['transaction_id']
        }

        return self.execute_fetch_one(sql, params)

    def get_order_data(self, investment_id):
        sql = """                
                SELECT id, status, amount_lent
                FROM t_lender_investment_order 
                WHERE investment_id = %(investment_id)s
            """

        params = {
            "investment_id": investment_id
        }

        return self.execute_fetch_one(sql, params)

    def update_investment_order_by_inv_id(self, update_data, investment_id):
        # Creates a list like: ["loan_count = %(loan_count)s"]
        set_clauses = [f"{col} = %({col})s" for col in update_data.keys()]

        set_clauses.append("updated_dtm = now()")
        # Join all the SET clauses with a comma and a space
        set_string = ", ".join(set_clauses)

        # Construct the final SQL query
        sql = f"""
                UPDATE t_lender_investment_order
                SET {set_string}
                WHERE investment_id = %(investment_id)s
            """

        # Create the parameters dictionary for the query
        # Start with a copy of all the data to be set
        params = update_data.copy()

        # Add the tracker_id for the WHERE clause
        params['investment_id'] = investment_id

        # Execute the query
        return self.execute_no_return(sql, params)


    def lock_and_update_to_cancelled_by_investment_id(self, investment_id):
        """
        Lock and update investment order to CANCELLED status in a single database call.
        Only updates if status is PENDING, ensuring idempotency.
        Uses CTE to lock the row first, then update it.
        
        Args:
            investment_id: The investment ID to lock and update
            
        Returns:
            dict: Investment order data with 'lender_id' and 'id' if update succeeded, None if not found or already processed
        """
        sql = """
            WITH locked_row AS (
                SELECT id, lender_id
                FROM t_lender_investment_order
                WHERE investment_id = %(investment_id)s
                AND status = %(pending_status)s
                AND deleted IS NULL
                FOR UPDATE NOWAIT
            )
            UPDATE t_lender_investment_order
            SET status = %(cancelled_status)s, updated_dtm = now()
            FROM locked_row
            WHERE t_lender_investment_order.id = locked_row.id
            RETURNING t_lender_investment_order.lender_id, t_lender_investment_order.id
        """
        
        params = {
            'investment_id': investment_id,
            'pending_status': OrderStatus.PENDING,
            'cancelled_status': OrderStatus.CANCELLED
        }
        
        return self.execute_fetch_one(sql, params, to_dict=True)
    
    def cancel_order_by_transaction_id(self, transaction_id: int) -> bool:
        """
        Fail investment order(s) associated with a wallet transaction ID.
        
        Args:
            transaction_id: Wallet transaction ID (pk from t_lender_wallet_transaction)
            
        Returns:
            bool: True if any orders were updated, False otherwise
        """
        sql = """
            UPDATE t_lender_investment_order
            SET status = %(cancelled_status)s, updated_dtm = now()
            WHERE status = %(pending_status)s
            AND transaction_id = %(transaction_id)s
            AND deleted IS NULL
        """
        
        params = {
            'transaction_id': transaction_id,
            'pending_status': OrderStatus.PENDING,
            'cancelled_status': OrderStatus.CANCELLED
        }
        
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0