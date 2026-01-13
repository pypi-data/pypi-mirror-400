from ..base_layer import BaseDataLayer
from ..helper.generic_utils import generate_transaction_id
from ..constants import (
    TransactionStatusFilterMap,
    TransactionTypeFilterMap,
    TransactionActionFilterMap,
    TransactionSortBy,
    TimeZone,
    WalletTransactionType,
    TransactionStatus
)
from datetime import datetime
from typing import List, Optional, Dict, Any

class WalletTransaction(BaseDataLayer):

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        
    def insert_lender_wallet_transaction(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert a new transaction.
        """
        sql = """
                INSERT INTO t_lender_wallet_transaction (
                    account_id, amount, source_transaction_id, transaction_type,
                    lender_id, parent_transaction_id, status,
                    transaction_id
                ) VALUES (
                    %(account_id)s, %(amount)s, %(source_transaction_id)s,
                    %(transaction_type)s, %(lender_id)s, %(parent_transaction_id)s,
                    %(status)s, %(transaction_id)s
                ) RETURNING id;
            """

        return self.execute_fetch_one(sql, params)


    def insert(self, transaction_data):
        """
        Insert a new transaction.
        """
        transaction_id = generate_transaction_id()
        
        params = {
            'account_id': transaction_data['account_id'],
            'amount': transaction_data['amount'],
            'source_transaction_id': transaction_data.get('source_transaction_id'),
            'transaction_type': transaction_data['transaction_type'],
            'lender_id': transaction_data['lender_id'],
            'parent_transaction_id': transaction_data.get('parent_transaction_id'),
            'status': transaction_data['status'],
            'transaction_id': transaction_id
        }

        txn_data = self.insert_lender_wallet_transaction(params)
        txn_data['transaction_id'] = transaction_id

        return txn_data

    def bulk_insert(self, transactions_data_list):
        """
        Bulk insert multiple transactions and return their IDs.
        Executes all inserts in a single SQL query.

        Args:
            transactions_data_list: List of dictionaries containing transaction data
                Each dict must have: account_id, amount, source_transaction_id,
                transaction_type, lender_id, parent_transaction_id, status, transaction_id

        Returns:
            List of dictionaries with 'id' and 'transaction_id' for each inserted transaction
        """
        if not transactions_data_list:
            return []

        # Generate transaction_id for each transaction if not provided
        for txn_data in transactions_data_list:
            if 'transaction_id' not in txn_data or not txn_data['transaction_id']:
                txn_data['transaction_id'] = generate_transaction_id()

        # Define columns and values template
        columns = "account_id, amount, source_transaction_id, transaction_type, lender_id, parent_transaction_id, status, transaction_id"
        values_template = "%s, %s, %s, %s, %s, %s, %s, %s"  # 8 placeholders

        # Generate the VALUES part of the SQL query for all data items
        placeholders = ", ".join([f"({values_template})"] * len(transactions_data_list))

        sql = f"""
            INSERT INTO t_lender_wallet_transaction ({columns}) 
            VALUES {placeholders} 
            RETURNING id, transaction_id
        """

        # Flatten the list of dictionaries' values in the correct order
        # (account_id, amount, source_transaction_id, transaction_type, lender_id, parent_transaction_id, status, transaction_id, ..)
        flat_values = []
        for data in transactions_data_list:
            flat_values.append(data['account_id'])
            flat_values.append(data['amount'])
            flat_values.append(data['source_transaction_id'])
            flat_values.append(data['transaction_type'])
            flat_values.append(data['lender_id'])
            flat_values.append(data.get('parent_transaction_id'))
            flat_values.append(data['status'])
            flat_values.append(data['transaction_id'])

        # Execute the bulk insert with RETURNING clause to get all IDs
        results = self.execute_fetch_all(sql, flat_values, to_dict=True)

        return results if results else []

    def update_transaction_status_by_id(self, transaction_id, new_status):
        """Update transaction status."""
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE id = %(transaction_id)s AND deleted IS NULL;
        """

        params = {
            'transaction_id': transaction_id,
            'status': new_status
        }

        return self.execute_query(sql, params,return_row_count=True)

    def get_existing_transaction(self, source_transaction_id, transaction_type):
        """
        Check if a transaction already exists with the given parameters.

        Args:
            source_transaction_id: The source transaction ID
            transaction_type: The transaction type

        Returns:
            dict: Transaction data if found, None if not found
        """
        sql = """
            SELECT id, transaction_id, status, amount, created_dtm, account_id, lender_id
            FROM t_lender_wallet_transaction
            WHERE source_transaction_id = %(source_transaction_id)s
              AND transaction_type = %(transaction_type)s
              AND deleted IS NULL
            ORDER BY created_dtm DESC
            LIMIT 1
        """

        params = {
            'source_transaction_id': source_transaction_id,
            'transaction_type': transaction_type
        }

        return self.execute_fetch_one(sql, params, to_dict=True)


    def update_wallet_transaction_by_id(self, update_data, transaction_id):
        # Creates a list like: ["loan_count = %(loan_count)s"]
        set_clauses = [f"{col} = %({col})s" for col in update_data.keys()]

        set_clauses.append("updated_dtm = now()")
        # Join all the SET clauses with a comma and a space
        set_string = ", ".join(set_clauses)

        # Construct the final SQL query
        sql = f"""
                UPDATE t_lender_wallet_transaction
                SET {set_string}
                WHERE id = %(transaction_id)s
            """

        # Create the parameters dictionary for the query
        # Start with a copy of all the data to be set
        params = update_data.copy()

        # Add the tracker_id for the WHERE clause
        params['transaction_id'] = transaction_id

        # Execute the query
        return self.execute_no_return(sql, params)

    def get_data_by_src_txn_id(self, txn_id):
        sql = """
                SELECT id as transaction_pk, lender_id, transaction_id
                FROM t_lender_wallet_transaction
                WHERE source_transaction_id = %(source_transaction_id)s 
                AND status = %(status)s
            """

        params = {
            'source_transaction_id': txn_id,
            'status': TransactionStatus.PENDING
        }

        return self.execute_fetch_one(sql, params)


    def get_transaction_by_source_transaction_id(self, source_transaction_id):
        """Get transaction by source_transaction_id."""
        sql = """
            SELECT id, account_id, amount, source_transaction_id, transaction_type,
                   lender_id, parent_transaction_id, status, transaction_id
            FROM t_lender_wallet_transaction
            WHERE source_transaction_id = %(source_transaction_id)s 
            AND deleted IS NULL
            ORDER BY created_dtm DESC
            LIMIT 1;
        """

        params = {
            'source_transaction_id': source_transaction_id
        }

        return self.execute_fetch_one(sql, params)

    def update_transaction_status_by_source_transaction_id(self, source_transaction_id, new_status):
        """Update transaction status by source_transaction_id."""
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE source_transaction_id = %(source_transaction_id)s 
            AND deleted IS NULL
            RETURNING id,transaction_id
        """

        params = {
            'source_transaction_id': source_transaction_id,
            'status': new_status
        }

        return self.execute_fetch_one(sql, params)

    def mark_pending_txn_failed_by_source_txn_id(self, source_transaction_id):
        """
        Mark pending transaction as FAILED by source_transaction_id and return the transaction id.
        This combines the get and update operations into a single database call.

        Args:
            source_transaction_id: The source transaction ID to update

        Returns:
            dict: Transaction data with 'id' and 'amount' fields, or None if not found or not in PENDING status
        """
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE source_transaction_id = %(source_transaction_id)s 
            AND status = %(pending_status)s
            AND deleted IS NULL
            RETURNING id, transaction_id, amount, account_id, lender_id, transaction_type
        """

        params = {
            'source_transaction_id': source_transaction_id,
            'status': TransactionStatus.FAILED,
            'pending_status': TransactionStatus.PENDING
        }

        return self.execute_fetch_one(sql, params)

    def mark_pending_txn_failed_by_id(self, transaction_id):
        """
        Mark pending transaction as FAILED by source_transaction_id and return the transaction id.
        This combines the get and update operations into a single database call.

        Args:
            transaction_id: The source transaction ID to update

        Returns:
            dict: Transaction data with 'id' and 'amount' fields, or None if not found or not in PENDING status
        """
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE id = %(transaction_id)s 
            AND status = %(pending_status)s
            AND deleted IS NULL
            RETURNING id, transaction_id, amount, account_id, 
            lender_id, transaction_type, source_transaction_id
        """

        params = {
            'source_transaction_id': transaction_id,
            'status': TransactionStatus.FAILED,
            'pending_status': TransactionStatus.PENDING
        }

        return self.execute_fetch_one(sql, params)

    def mark_processing_txn_failed_by_source_txn_id(self, source_transaction_id):
        """
        Mark processing transaction as FAILED by source_transaction_id and return the transaction id.
        This combines the get and update operations into a single database call.

        Args:
            source_transaction_id: The source transaction ID to update

        Returns:
            dict: Transaction data with 'id' and 'amount' fields, or None if not found or not in PROCESSING status
        """
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE source_transaction_id = %(source_transaction_id)s 
            AND status = %(processing_status)s
            AND deleted IS NULL
            RETURNING id, transaction_id, amount, account_id, lender_id, transaction_type
        """

        params = {
            'source_transaction_id': source_transaction_id,
            'status': TransactionStatus.FAILED,
            'processing_status': TransactionStatus.PROCESSING
        }

        return self.execute_fetch_one(sql, params)

    def bulk_update_status_by_source_transaction_ids(self, source_transaction_ids, new_status):
        """
        Bulk update transaction status for all transactions matching any of the provided source_transaction_ids.

        Args:
            source_transaction_ids: List of source_transaction_ids to update
            new_status: New status to set (e.g., 'SUCCESS')

        Returns:
            int: Number of rows updated
        """
        if not source_transaction_ids:
            return 0

        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE source_transaction_id = ANY(%(source_transaction_ids)s)
            AND deleted IS NULL
        """

        params = {
            'source_transaction_ids': source_transaction_ids,
            'status': new_status
        }

        return self.execute_query(sql, params, return_row_count=True)

    def get_transaction_by_id(self, txn_id):
        """Get transaction by source_transaction_id."""
        sql = """
            SELECT id, account_id, amount, source_transaction_id, transaction_type,
                   lender_id, parent_transaction_id, status, transaction_id
            FROM t_lender_wallet_transaction
            WHERE id = %(txn_id)s 
            AND deleted IS NULL
            ORDER BY created_dtm DESC
            LIMIT 1;
        """

        params = {
            'txn_id': txn_id
        }

        return self.execute_fetch_one(sql, params)

    def update_transaction_status_by_txn_id(self, txn_id, new_status):
        """Update transaction status by source_transaction_id."""
        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE id = %(txn_id)s 
            AND deleted IS NULL
            RETURNING id,transaction_id
        """

        params = {
            'txn_id': txn_id,
            'status': new_status
        }

        return self.execute_fetch_one(sql, params)

    def get_innofin_transfer_txn(self, txn_id_list=None):
        sql = """
                SELECT 
                    tlwt.transaction_type as type, 
                    tigm.mapping_id as gst_mapping_txn_id, 
                    tlwt.amount, tlwt.id, tlwt.transaction_id as vortex_txn_id
                FROM t_lender_wallet_transaction tlwt
                JOIN t_innofin_gst_mapping tigm ON tlwt.id = tigm.wallet_transaction_id
                WHERE tlwt.transaction_type = %(innofin_txn_type)s 
                AND tlwt.status = %(scheduled_status)s 
            """

        params = {
            'innofin_txn_type': WalletTransactionType.INNOFIN_TRANSFER,
            'scheduled_status': TransactionStatus.SCHEDULED
        }

        if txn_id_list:
            sql += """ AND tlwt.transaction_id = ANY(%(txn_id)s) """
            params['txn_id'] = txn_id_list

        return self.execute_fetch_all(sql, params)

    def update_src_txn_id_by_transaction_id(
            self, source_transaction_id, transaction_id, status
    ):
        """Update source_transaction_id by transaction_id."""

        sql = """
            UPDATE t_lender_wallet_transaction
            SET source_transaction_id = %(source_transaction_id)s, status = %(status)s,
            updated_dtm = now()
            WHERE transaction_id = %(transaction_id)s AND status = %(processing_status)s
            RETURNING id, account_id, lender_id
        """

        params = {
            'source_transaction_id': source_transaction_id,
            'transaction_id': transaction_id,
            'status': status,
            'processing_status': TransactionStatus.PROCESSING
        }

        return self.execute_fetch_one(sql, params)

    def bulk_mark_scheduled_as_processing(self, transaction_ids):
        """
        Bulk update scheduled transactions to PROCESSING status.
        Only updates transactions that are currently in SCHEDULED status.

        Args:
            transaction_ids: List of transaction IDs (primary key) to update

        Returns:
            int: Number of rows updated
        """
        if not transaction_ids:
            return 0

        sql = """
            UPDATE t_lender_wallet_transaction
            SET status = %(status)s, updated_dtm = now()
            WHERE id = ANY(%(transaction_ids)s)
            AND status = %(scheduled_status)s
            AND deleted IS NULL
        """

        params = {
            'transaction_ids': transaction_ids,
            'status': TransactionStatus.PROCESSING,
            'scheduled_status': TransactionStatus.SCHEDULED
        }

        return self.execute_query(sql, params, return_row_count=True)

    def lock_and_fetch_scheduled_transactions(self, transaction_ids):
        """
        Lock and fetch scheduled transactions by their IDs using FOR UPDATE SKIP LOCKED.
        This ensures only unlocked rows are processed, preventing race conditions.

        Args:
            transaction_ids: List of transaction IDs to lock and fetch

        Returns:
            list: List of dictionaries containing locked transaction data
        """
        if not transaction_ids:
            return []

        sql = """
            SELECT 
                txn.id,
                txn.amount,
                txn.transaction_type,
                txn.transaction_id,
                tl.user_source_group_id
            FROM t_lender_wallet_transaction txn
            INNER JOIN t_lender tl ON tl.id = txn.lender_id
            WHERE txn.id = ANY(%(transaction_ids)s)
            AND txn.status = 'SCHEDULED'
            AND txn.deleted IS NULL
            AND tl.deleted IS NULL
            FOR UPDATE SKIP LOCKED
        """

        params = {
            'transaction_ids': transaction_ids
        }

        return self.execute_fetch_all(sql, params, to_dict=True) or []

    def get_account_statement_transactions(
        self,
        lender_id,
        from_date,
        to_date,
        transaction_types,
        statuses,
        limit,
        offset,
    ):
        """
        Fetch paginated wallet transactions for lender account statement.

        Joins with lender investment to enrich data with scheme_id where applicable.

        Args:
            lender_id: Lender's ID to filter by
            from_date: Start date (inclusive) for created_dtm::date
            to_date: End date (inclusive) for created_dtm::date
            transaction_types: List of wallet transaction types to include
            statuses: List of transaction statuses to include (e.g., SUCCESS, FAILED)
            limit: Page size
            offset: Offset for pagination

        Returns:
            List[dict]: Transaction rows with fields:
                - created_dtm
                - transaction_id
                - transaction_type
                - amount
                - scheme_id (nullable)
        """
        if not transaction_types:
            return []

        # Ensure limit and offset are integers
        limit = int(limit) if limit is not None else 10
        offset = int(offset) if offset is not None else 0

        sql = """
            SELECT
                txn.created_dtm,
                txn.transaction_id,
                txn.transaction_type,
                txn.amount,
                tli.investment_id AS scheme_id
            FROM t_lender_wallet_transaction txn
            LEFT JOIN t_lender_investment tli
                ON tli.transaction_id = txn.id
                AND tli.deleted IS NULL
            WHERE txn.lender_id = %(lender_id)s
              AND txn.status = ANY(%(statuses)s)
              AND txn.transaction_type = ANY(%(transaction_types)s)
              AND txn.created_dtm::date BETWEEN %(from_date)s AND %(to_date)s
              AND txn.deleted IS NULL
            ORDER BY txn.created_dtm DESC, txn.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        params = {
            "lender_id": lender_id,
            "from_date": from_date,
            "to_date": to_date,
            "transaction_types": transaction_types,
            "statuses": statuses,
            "limit": limit,
            "offset": offset,
        }

        return self.execute_fetch_all(sql, params, to_dict=True) or []

    def get_account_statement_transaction_count(
        self,
        lender_id,
        from_date,
        to_date,
        transaction_types,
        statuses,
    ):
        """
        Get total count of wallet transactions for lender account statement.

        Args:
            lender_id: Lender's ID to filter by
            from_date: Start date (inclusive) for created_dtm::date
            to_date: End date (inclusive) for created_dtm::date
            transaction_types: List of wallet transaction types to include
            statuses: List of transaction statuses to include

        Returns:
            int: Count of matching transactions
        """
        if not transaction_types:
            return 0

        sql = """
            SELECT COUNT(*) AS txn_count
            FROM t_lender_wallet_transaction txn
            WHERE txn.lender_id = %(lender_id)s
              AND txn.status = ANY(%(statuses)s)
              AND txn.transaction_type = ANY(%(transaction_types)s)
              AND txn.created_dtm::date BETWEEN %(from_date)s AND %(to_date)s
              AND txn.deleted IS NULL
        """

        params = {
            "lender_id": lender_id,
            "from_date": from_date,
            "to_date": to_date,
            "transaction_types": transaction_types,
            "statuses": statuses,
        }

        result = self.execute_fetch_one(sql, params, to_dict=True) or {}
        return int(result.get("txn_count") or 0)
    
    def fetch_statement_aggregates(
        self,
        lender_id: int,
        from_date,
        to_date,
        debit_transaction_types: List[str],
        credit_transaction_types: List[str],
        statuses: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Get aggregate added and withdrawn amounts for account statement.
        """
        sql = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN txn.transaction_type = ANY(%(debit_types)s)
                            THEN txn.amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS withdrawn_amount,
                COALESCE(
                    SUM(
                        CASE
                            WHEN txn.transaction_type = ANY(%(credit_types)s)
                            THEN txn.amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS added_amount
            FROM t_lender_wallet_transaction txn
            WHERE txn.lender_id = %(lender_id)s
              AND txn.status = ANY(%(statuses)s)
              AND txn.created_dtm::date BETWEEN %(from_date)s AND %(to_date)s
              AND txn.deleted IS NULL
        """

        params = {
            "lender_id": lender_id,
            "from_date": from_date,
            "to_date": to_date,
            "debit_types": debit_transaction_types,
            "credit_types": credit_transaction_types,
            "statuses": statuses,
        }

        return self.execute_fetch_one(sql, params, to_dict=True)


    def get_account_statement_aggregates(
        self,
        lender_id,
        from_date,
        to_date,
        debit_transaction_types,
        credit_transaction_types,
        statuses,
    ):
        """
        Get aggregate added and withdrawn amounts for account statement.

        Args:
            lender_id: Lender's ID to filter by
            from_date: Start date (inclusive) for created_dtm::date
            to_date: End date (inclusive) for created_dtm::date
            debit_transaction_types: List of debit transaction types
            credit_transaction_types: List of credit transaction types
            statuses: List of transaction statuses to include

        Returns:
            dict: {
                "withdrawn_amount": float,
                "added_amount": float
            }
        """
        if not (debit_transaction_types or credit_transaction_types):
            return {"withdrawn_amount": 0.0, "added_amount": 0.0}

        result = self.fetch_statement_aggregates(
            lender_id, from_date, to_date,
            debit_transaction_types or [], credit_transaction_types or [], statuses
        )
        
        if result:
            return {
                "withdrawn_amount": float(result.get("withdrawn_amount") or 0.0),
                "added_amount": float(result.get("added_amount") or 0.0),
            }
        return {"withdrawn_amount": 0.0, "added_amount": 0.0}

    def get_refund_by_parent_transaction_id(self, parent_transaction_id, transaction_type):
        """
        Check if a refund transaction already exists for the given parent transaction.

        Args:
            parent_transaction_id: The parent transaction ID (primary key)
            transaction_type: The refund transaction type (e.g., 'REFUND ADD MONEY')

        Returns:
            dict: Refund transaction data if found, None if not found
        """
        sql = """
            SELECT id, transaction_id, status, amount, created_dtm, account_id, lender_id
            FROM t_lender_wallet_transaction
            WHERE parent_transaction_id = %(parent_transaction_id)s
              AND transaction_type = %(transaction_type)s
              AND deleted IS NULL
            ORDER BY created_dtm DESC
            LIMIT 1
        """

        params = {
            'parent_transaction_id': parent_transaction_id,
            'transaction_type': transaction_type
        }

        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_transaction_list(self, lender_id, filter_data=None, sort_data=None, limit=10, offset=0):
        """
        Get transaction list for a lender based on filters and sorting.

        Args:
            lender_id: The lender ID
            filter_data: Dictionary containing filter criteria
            sort_data: List of sort options
            limit: Number of records to return
            offset: Number of records to skip

        Returns:
            dict: Dictionary containing transaction_count and transaction_list
        """
        default_config = {
            'status': [
                TransactionStatus.FAILED,
                TransactionStatus.SUCCESS,
                TransactionStatus.SCHEDULED,
                TransactionStatus.PROCESSING,
                TransactionStatus.PENDING
            ],
             'types' : [
                WalletTransactionType.ADD_MONEY,
                WalletTransactionType.WITHDRAW_MONEY,
                WalletTransactionType.MIP_AUTO_WITHDRAWAL,
                WalletTransactionType.MANUAL_LENDING_AUTO_WITHDRAWAL,
                WalletTransactionType.LUMPSUM_AUTO_WITHDRAWAL,
                WalletTransactionType.SHORT_TERM_LENDING_AUTO_WITHDRAWAL,
                WalletTransactionType.IDLE_FUND_WITHDRAWAL,
                WalletTransactionType.REPAYMENT_AUTO_WITHDRAWAL,
                WalletTransactionType.FMPP_REPAYMENT_WITHDRAWAL,
                WalletTransactionType.AUTO_LENDING_REPAYMENT_WITHDRAWAL,
                WalletTransactionType.AUTO_LENDING_REPAYMENT_ADD_MONEY
            ],
            'failed_status': [TransactionStatus.FAILED]
        }

        params = {
            "indian_time": TimeZone.indian_time,
            "lender_id": lender_id,
            "limit": limit
        }

        # Initialize base where conditions
        base_where_conditions = [
            "lt.lender_id = %(lender_id)s",
            "lt.deleted IS NULL"
        ]

        # Handle filters if present
        if filter_data:
            # Status filters
            if filter_data.get('status'):
                status_list = []
                for status in filter_data['status']:
                    status_list.extend(TransactionStatusFilterMap.STATUS_FILTER_MAP.get(status, []))
                if status_list:
                    params['status'] = list(set(status_list))
                    base_where_conditions.append("lt.status = ANY(%(status)s)")
            else:
                params['status'] = default_config['status']
                base_where_conditions.append("lt.status = ANY(%(status)s)")

            # Type and category filters
            type_list = []
            if filter_data.get('type'):
                for category in filter_data['type']:
                    type_list.extend(TransactionTypeFilterMap.TYPE_FILTER_MAP.get(category, []))

            # Action filters
            action_types = []
            if filter_data.get('action'):
                for action in filter_data['action']:
                    action_types.extend(TransactionActionFilterMap.ACTION_FILTER_MAP.get(action, []))

            # Combine type and action filters
            if type_list and action_types:
                # Intersect both filters
                type_set = set(type_list)
                action_set = set(action_types)
                final_types = list(type_set.intersection(action_set))
                if final_types:
                    params['type'] = final_types
                    base_where_conditions.append("lt.transaction_type = ANY(%(type)s)")
            elif type_list:
                params['type'] = list(set(type_list))
                base_where_conditions.append("lt.transaction_type = ANY(%(type)s)")
            elif action_types:
                params['type'] = list(set(action_types))
                base_where_conditions.append("lt.transaction_type = ANY(%(type)s)")
            else:
                params['type'] = default_config['types']
                base_where_conditions.append("lt.transaction_type = ANY(%(type)s)")

            # Date range filter
            if filter_data.get('period'):
                period = filter_data['period']
                if period.get('from_date') and period.get('to_date'):
                    datetime.strptime(str(period['from_date']), '%Y-%m-%d')
                    datetime.strptime(str(period['to_date']), '%Y-%m-%d')
                    params['from_date'] = period['from_date']
                    params['to_date'] = period['to_date']
                    base_where_conditions.append("DATE(lt.created_dtm) BETWEEN %(from_date)s AND %(to_date)s")
        else:
            # Set default values if no filters
            params['status'] = default_config['status']
            params['type'] = default_config['types']
            base_where_conditions.extend([
                "lt.transaction_type = ANY(%(type)s)",
                "lt.status = ANY(%(status)s)"
            ])

        # Add failed status to params
        params['failed_status'] = default_config['failed_status']
        params['failed_status_label'] = TransactionStatus.FAILED

        # Build the base query
        where_clause = " AND ".join(base_where_conditions)
        query = """
            SELECT 
                TO_CHAR(lt.created_dtm AT TIME ZONE %(indian_time)s, 'DD Mon YYYY HH12:MI AM') AS created_date,
                lt.transaction_type::text as type,
                lt.source_transaction_id,
                lt.amount, 
                lt.transaction_id,
                lt.status <> ALL(%(failed_status)s) AS success,
                CASE 
                    WHEN lt.status = ANY(%(failed_status)s) THEN %(failed_status_label)s
                    ELSE lt.status 
                END AS label
            FROM t_lender_wallet_transaction lt
            WHERE """ + where_clause

        # Add sorting
        if sort_data:
            sort_conditions = []
            for sort_option in sort_data:
                sort_condition = TransactionSortBy.SORT_CONDITIONS.get(sort_option)
                if sort_condition:
                    sort_conditions.append(sort_condition)

            if sort_conditions:
                query += " ORDER BY " + ", ".join(sort_conditions)
        else:
            # Default sorting by date descending
            query += " ORDER BY lt.created_dtm DESC, lt.id DESC"

        # Add pagination
        query += " LIMIT %(limit)s"
        if offset is not None and offset >= 0:
            params['offset'] = offset
            query += " OFFSET %(offset)s"

        result = self.execute_fetch_all(query, params)

        if not result:
            return {
                "transaction_count": 0,
                "transaction_list": []
            }

        return {
            "transaction_count": len(result),
            "transaction_list": result
        }
