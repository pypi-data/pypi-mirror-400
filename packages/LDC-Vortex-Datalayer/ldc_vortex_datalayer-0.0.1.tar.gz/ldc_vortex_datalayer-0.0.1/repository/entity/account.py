import json
import logging

from ..base_layer import BaseDataLayer
from ..constants import AccountStatus

logger = logging.getLogger('normal')


class Account(BaseDataLayer):
    """
    Production-level CRUD operations for account table.
    
    Table Schema:
    - id: Serial (Primary Key)
    - account_type_id: integer
    - lender_id: integer  
    - investment_id: integer
    - balance: numeric(10, 2)
    - status: enum
    - created_dtm: Timestampz
    - updated_dtm: Timestampz
    """


    def create(self, account_data):
        """
        Create a new account record.
        
        Args:
            account_data: Dictionary containing account information
                Required fields: account_type_id, lender_id, investment_id, balance, status
                
        Returns:
            int: The ID of the created account record

        """

        sql = """
            INSERT INTO t_account (account_type_id, lender_id, balance, status, created_dtm, updated_dtm)
            VALUES (%(account_id)s, %(lender_id)s, %(balance)s, %(status)s, NOW(), NOW())
            RETURNING id
        """
        
        result = self.execute_fetch_one(sql, account_data)
        logger.info(f"Successfully created account with ID: {result['id']}")
        return result['id']


    def fetch_balance_by_lender_id(self, lender_id, lock=False):
        """
        Get account balance by lender ID with optional row locking.
        
        Args:
            lender_id: The primary key ID of the t_lender
            lock: If True, applies FOR UPDATE lock on the row (uses NOWAIT)

        Returns:
            Balance or None if not found
        """
        sql = "SELECT id as account_id, round(balance, 2) as balance FROM t_account WHERE lender_id = %(lender_id)s"
        if lock:
            sql += " FOR UPDATE NOWAIT"

        params = {"lender_id": lender_id}

        result = self.execute_fetch_one(sql, params, to_dict=True)
        return result

    def fetch_balance_by_user_source_group_id	(self, user_source_group_id, lock=False):
        """
        Get account balance by user_source_group_id with optional row locking.
        
        Args:
            user_source_group_id: The user_source_group_id from t_lender
            lock: If True, applies FOR UPDATE lock on the row (uses NOWAIT)

        Returns:
            dict: Dictionary containing account_id and balance, or None if not found
        """
        sql = """
            SELECT ta.balance 
            FROM t_account ta
            INNER JOIN t_lender tl ON ta.lender_id = tl.id
            WHERE tl.user_source_group_id = %(user_source_group_id)s
            AND tl.deleted IS NULL
        """
        if lock:
            sql += " FOR UPDATE NOWAIT"

        params = {"user_source_group_id": user_source_group_id}

        result = self.execute_fetch_one(sql, params, to_dict=True)
        return result

    def fetch_active_account_id_by_lender_id(self, lender_id):
        sql = """
                SELECT id 
                FROM t_account 
                WHERE lender_id = %(lender_id)s 
                AND status = %(status)s 
            """

        params = {
            "lender_id": lender_id,
            "status": AccountStatus.ACTIVE
        }

        result = self.execute_fetch_one(sql, params)
        if result:
            return result['id']
        return None

    def update_balance_by_lender_id(self, lender_id, new_balance, account_type_id):
        """
        Update account balance for a specific lender.

        Args:
            lender_id: The lender ID to update balance for
            new_balance: The new balance amount

        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_account 
            SET balance = %(new_balance)s, updated_dtm = NOW()
            WHERE lender_id = %(lender_id)s and account_type_id = %(account_type_id)s AND deleted IS NULL
        """

        params = {
            "lender_id": lender_id,
            "new_balance": new_balance,
            "account_type_id": account_type_id
        }

        return self.execute_query(sql, params, return_row_count=True)

    def fetch_balance_by_master_account_id(self, account_id, lock=False):
        """
        Get account balance by master account id with optional row locking.

        Args:
            account_id: The primary key ID of the ledger master account
            lock: If True, applies FOR UPDATE lock on the row (uses NOWAIT)

        Returns:
            Balance or None if not found
        """
        sql = """
                SELECT balance, id as account_id 
                FROM t_account 
                WHERE account_type_id = %(account_id)s
            """

        if lock:
            sql += " FOR UPDATE NOWAIT"

        params = {"account_id": account_id}

        result = self.execute_fetch_one(sql, params, to_dict=True)
        return result

    def fetch_master_account_type_id_by_account_name(self, account_name):
        """
        Fetch master account details by account name from database.

        Args:
            account_name: The name of the ledger master account

        Returns:
            Dict with account_type_id and account_id, or None if not found
        """
        sql = """
            SELECT tma.id as account_type_id, ta.id as account_id
            FROM t_master_account tma
            JOIN t_account ta on ta.account_type_id = tma.id
            WHERE account_name = %(account_name)s
        """

        params = {"account_name": account_name}

        return self.execute_fetch_one(sql, params, to_dict=True)

    def set_balance_by_account_type_id(self, account_id, new_balance):
        """
        Update account balance for a specific lender.

        Args:
            account_id: The account ID to update balance for
            new_balance: The new balance amount

        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_account 
            SET balance = %(new_balance)s, updated_dtm = NOW()
            WHERE account_type_id = %(account_id)s AND deleted IS NULL
        """

        params = {
            "account_id": account_id,
            "new_balance": new_balance
        }

        return self.execute_query(sql, params, return_row_count=True)
    
    def update_balance_by_account_id(self, account_id, amount):
        sql = """
            UPDATE t_account 
            SET balance = balance + %(amount)s, updated_dtm = NOW()
            WHERE account_type_id = %(account_id)s AND deleted IS NULL
            RETURNING balance as new_balance"""
        params = {
            "account_id": account_id,
            "amount": amount
        }
        return self.execute_query(sql, params, fetch_one=True)

    def get_balance_by_account_type_id(self, account_type_id):
        sql = """
            SELECT id as account_id, ROUND(balance, 2) as balance
            FROM t_account
            WHERE account_type_id = %(account_type_id)s
                AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'account_type_id': account_type_id
        }
        
        result = self.execute_fetch_one(sql, params, to_dict=True)
        return result