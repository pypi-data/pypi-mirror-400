from ..constants import TransactionAction
from ..base_layer import BaseDataLayer


class LenderWalletTracker(BaseDataLayer):
    """
    Entity class for lender wallet tracker operations.
    
    Table Schema:
    - id: Serial (Primary Key)
    - account_id: BigSerial (FK references t_lender_wallet)
    - wallet_transaction_id: varchar(30) (UK)
    - initial_amount: numeric(10, 2) (Default 0.00)
    - initial_transaction_id: BigSerial (FK references t_transaction)
    - action_amount: numeric(10, 2) (Default 0.00)
    - action_type: enum (DEBIT, CREDIT)
    - action_transaction_id: BigSerial (FK references t_transaction)
    - remaining_amount: numeric(10, 2) (Default 0.00)
    - transaction_type: enum (ADD_MONEY, WITHDRAW_MONEY, INVESTMENT, INVESTMENT_CANCELLATION, REFUND_ADD_MONEY)
    - expiry_dtm: Timestampz
    - lender_id: BigSerial (FK references t_investor)
    - created_dtm: Timestampz (Default now())
    - updated_dtm: Timestampz
    """

    def insert(self, tracker_data):
        """
        Insert a new wallet tracker record.
        
        Args:
            tracker_data: Dictionary containing wallet tracker information
                Required fields: account_id, wallet_transaction_id, initial_amount,
                               initial_transaction_id, action_amount, action_type,
                               action_transaction_id, remaining_amount, transaction_type,
                               lender_id
                
        Returns:
            int: The ID of the created wallet tracker record
        """
        sql = """
            INSERT INTO t_lender_wallet_tracker (
                account_id, initial_amount, initial_transaction_id,
                action_amount, action_type, action_transaction_id, remaining_amount,
                expiry_dtm, lender_id, created_dtm, updated_dtm
            ) VALUES (
                %(account_id)s, %(initial_amount)s,
                %(initial_transaction_id)s, %(action_amount)s, %(action_type)s,
                %(action_transaction_id)s, %(remaining_amount)s,
                %(expiry_dtm)s, %(lender_id)s, NOW(), NOW()
            ) RETURNING id;
        """

        params = {
            'account_id': tracker_data['account_id'],
            'initial_amount': tracker_data['initial_amount'],
            'initial_transaction_id': tracker_data['initial_transaction_id'],
            'action_amount': tracker_data['action_amount'],
            'action_type': tracker_data['action_type'],
            'action_transaction_id': tracker_data['action_transaction_id'],
            'remaining_amount': tracker_data['remaining_amount'],
            'expiry_dtm': tracker_data.get('expiry_dtm'),
            'lender_id': tracker_data['lender_id']
        }

        return self.execute_fetch_one(sql, params, index_result=True)

    def fetch_available_records(self, lender_id, account_id):
        """
        Fetch available wallet tracker records with remaining amount > 0.
        Records are typically CREDIT type (from ADD_MONEY) that haven't been fully consumed.
        
        Args:
            lender_id: The lender ID
            account_id: The account ID
            
        Returns:
            list: List of records with remaining_amount > 0, ordered by created_dtm ASC
        """
        sql = """
            SELECT 
                id, 
                remaining_amount as balance,
                account_id,
                initial_amount,
                initial_transaction_id,
                action_amount,
                action_type,
                action_transaction_id,
                lender_id
            FROM t_lender_wallet_tracker
            WHERE lender_id = %(lender_id)s
              AND account_id = %(account_id)s
              AND remaining_amount > 0
              AND deleted IS NULL
            ORDER BY created_dtm ASC, id ASC
            FOR UPDATE NOWAIT;
        """
        
        params = {
            'lender_id': lender_id,
            'account_id': account_id
        }
        
        return self.execute_fetch_all(sql, params, to_dict=True)

    def get_user_available_balance(self, lender_id, account_id, for_update=False):
        """
        Get the total available balance from tracker records for a user.
        
        Args:
            lender_id: The lender ID
            account_id: The account ID
            for_update: If True, applies FOR UPDATE lock on the rows
            
        Returns:
            Decimal: Total available balance from tracker records
        """
        sub_query = """
            SELECT remaining_amount as balance
            FROM t_lender_wallet_tracker
            WHERE lender_id = %(lender_id)s
              AND remaining_amount > 0
              AND deleted IS NULL
        """
        
        if for_update:
            sub_query += ' FOR UPDATE NOWAIT'
        
        sql = f'SELECT COALESCE(SUM(balance), 0) FROM ({sub_query}) AS subquery'
        
        params = {
            'lender_id': lender_id,
            'account_id': account_id
        }
        
        result = self.execute_fetch_one(sql, params, to_dict=True)
        if result:
            return result['coalesce']
        return 0

    def deduct_full_balance(self, tracker_id, action_transaction_id):
        """
        Fully consume a tracker record by setting remaining_amount to 0.
        
        Args:
            tracker_id: The tracker record ID
            action_transaction_id: Optional transaction ID to set as action_transaction_id

        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_lender_wallet_tracker
            SET action_amount = remaining_amount,
                remaining_amount = 0,
                action_type = %(debit)s,
                action_transaction_id = %(action_transaction_id)s,
                updated_dtm = NOW()
            WHERE id = %(tracker_id)s
              AND deleted IS NULL
              AND remaining_amount > 0;
        """
        
        params = {
            'tracker_id': tracker_id,
            'debit': TransactionAction.DEBIT,
            'action_transaction_id': action_transaction_id
        }
        
        return self.execute_query(sql, params, return_row_count=True)

    def deduct_partial_balance(self, tracker_id, debit_amount, action_transaction_id):
        """
        Partially consume a tracker record by reducing remaining_amount.
        
        Args:
            tracker_id: The tracker record ID
            debit_amount: Amount to debit from remaining_amount
            action_transaction_id: Optional transaction ID to set as action_transaction_id
            
        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_lender_wallet_tracker
            SET remaining_amount = remaining_amount - %(debit_amount)s,
                action_type = %(debit)s,
                action_amount = %(debit_amount)s,
                action_transaction_id = %(action_transaction_id)s,
                updated_dtm = NOW()
            WHERE id = %(tracker_id)s
              AND deleted IS NULL
              AND remaining_amount >= %(debit_amount)s;
        """
        
        params = {
            'tracker_id': tracker_id,
            'debit_amount': debit_amount,
            'debit': TransactionAction.DEBIT,
            'action_transaction_id': action_transaction_id
        }
        
        return self.execute_query(sql, params, return_row_count=True)

    def set_tracker_balance_to_zero_by_ids(self, tracker_ids, action_transaction_id):
        """
        Set remaining_amount to 0 for multiple tracker records by their IDs.
        
        Args:
            tracker_ids: Tuple or list of tracker record IDs
            action_transaction_id: Transaction ID to set as action_transaction_id
            
        Returns:
            int: Number of affected rows
        """
        if not tracker_ids:
            return 0
            
        sql = """
            UPDATE t_lender_wallet_tracker
            SET remaining_amount = 0,
                action_type = %(debit)s,
                action_transaction_id = %(action_transaction_id)s,
                updated_dtm = NOW()
            WHERE id = ANY(%(tracker_ids)s)
              AND deleted IS NULL;
        """
        
        params = {
            'tracker_ids': list(tracker_ids),
            'debit': TransactionAction.DEBIT,
            'action_transaction_id': action_transaction_id
        }
        
        return self.execute_query(sql, params, return_row_count=True)

    def credit_balance_to_tracker(self, tracker_id, credit_amount, action_transaction_id):
        """
        Credit amount to a tracker record by adding to remaining_amount.
        
        Args:
            tracker_id: The tracker record ID
            credit_amount: Amount to credit to remaining_amount
            action_transaction_id: Transaction ID to set as action_transaction_id
            
        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_lender_wallet_tracker
            SET remaining_amount = remaining_amount + %(credit_amount)s,
                action_type = %(credit)s,
                action_transaction_id = %(action_transaction_id)s,
                updated_dtm = NOW()
            WHERE id = %(tracker_id)s
              AND deleted IS NULL;
        """
        
        params = {
            'tracker_id': tracker_id,
            'credit_amount': credit_amount,
            'credit': TransactionAction.CREDIT,
            'action_transaction_id': action_transaction_id
        }
        
        return self.execute_query(sql, params, return_row_count=True)

    def get_tracker_by_id(self, tracker_id, lender_id=None, account_id=None, for_update=False):
        """
        Get a tracker record by its ID.
        
        Args:
            tracker_id: The tracker record ID
            lender_id: Optional lender ID for validation
            account_id: Optional account ID for validation
            for_update: If True, applies FOR UPDATE lock on the row
            
        Returns:
            dict or None: Tracker record if found, None otherwise
        """
        sql = """
            SELECT 
                id, 
                remaining_amount as balance,
                account_id,
                wallet_transaction_id,
                initial_amount,
                initial_transaction_id,
                action_amount,
                action_type,
                action_transaction_id,
                transaction_type,
                lender_id
            FROM t_lender_wallet_tracker
            WHERE id = %(tracker_id)s
              AND deleted IS NULL
        """
        
        params = {
            'tracker_id': tracker_id
        }
        
        if lender_id:
            sql += " AND lender_id = %(lender_id)s"
            params['lender_id'] = lender_id
            
        if account_id:
            sql += " AND account_id = %(account_id)s"
            params['account_id'] = account_id
        
        if for_update:
            sql += " FOR UPDATE NOWAIT"
        
        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_max_id_tracker_with_balance(self, lender_id, account_id):
        """
        Get the maximum ID from tracker records where remaining_amount >= 0.
        
        Args:
            lender_id: The lender ID
            account_id: The account ID
            
        Returns:
            int or None: The maximum tracker ID if found, None otherwise
        """
        sql = """
            SELECT MAX(id) as max_id
            FROM t_lender_wallet_tracker
            WHERE lender_id = %(lender_id)s
              AND account_id = %(account_id)s
              AND remaining_amount >= 0
              AND deleted IS NULL;
        """
        
        params = {
            'lender_id': lender_id,
            'account_id': account_id
        }
        
        result = self.execute_fetch_one(sql, params, to_dict=True)
        if result and result.get('max_id'):
            return result['max_id']
        return None
