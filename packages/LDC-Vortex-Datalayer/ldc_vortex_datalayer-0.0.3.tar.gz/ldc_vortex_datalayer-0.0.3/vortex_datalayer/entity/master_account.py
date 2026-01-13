

import logging
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer


logger = logging.getLogger('normal')


class MasterAccount(BaseDataLayer):
    """
    Data layer for master account database operations.
    """

    def get_account_by_type(self, account_type: str) -> Optional[Dict[str, Any]]:
        """
        Get master account by account type.

        Args:
            account_type: Account type (e.g., 'LENDER_WALLET', 'LENDER_REPAYMENT_WALLET')

        Returns:
            Dict with account_id or None
        """
        sql = """
            SELECT id as account_id
            FROM t_master_account
            WHERE account_type = %(account_type)s
              AND deleted IS NULL
            LIMIT 1
        """

        params = {'account_type': account_type}
        return self.execute_fetch_one(sql, params)

    def get_account_by_name(self, account_name: str) -> Optional[Dict[str, Any]]:
        """
        Get master account by account name.

        Args:
            account_name: Account name (e.g., 'LENDER_WALLET')

        Returns:
            Dict with id and account_id or None
        """
        sql = """
            SELECT id
            FROM t_master_account
            WHERE account_name = %(account_name)s
              AND deleted IS NULL
              AND is_active = TRUE
            LIMIT 1
        """
        
        params = {'account_name': account_name}
        return self.execute_fetch_one(sql, params)


    def get_account_id_by_name(self, account_name: str) -> Optional[int]:
        """
        Get master account ID by account type.

        Args:
            account_type: The account type to search for (e.g., 'LENDER_WALLET')

        Returns:
            int: The master account ID if found, None otherwise
        """
        sql = """
            SELECT id 
            FROM t_master_account 
            WHERE account_name = %(account_name)s 
            AND deleted IS NULL
            LIMIT 1
        """

        params = {"account_name": account_name}

        result = self.execute_fetch_one(sql, params)
        if result:
            return result['id']

        logger.warning(f"Master account not found for account_name: {account_name}")
        return None



