"""
Lendenapp Transaction File Logs Entity for handling operations on investors.lendenapp_transaction_file_logs table.
This module provides entity class for transaction file log operations.
"""

import logging
from typing import List, Dict, Any

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class LendenappTransactionFileLogs(BaseDataLayer):
    """
    Entity class for lendenapp transaction file log operations.
    
    Table Schema (investors.lendenapp_transaction_file_logs):
    - source_transaction_id: VARCHAR(255) NOT NULL
    - user_source_group_id: INT4 NULL
    - transaction_type: VARCHAR(50) NULL
    - status: VARCHAR(50) NULL
    - created_dtm: TIMESTAMPTZ NULL
    - updated_dtm: TIMESTAMPTZ NULL
    - is_processed: BOOL NULL
    - amount: NUMERIC(18, 4) NOT NULL
    """
    
    def bulk_insert(self, transactions_data_list: List[Dict[str, Any]]) -> int:
        """
        Bulk insert transaction logs into investors.lendenapp_transaction_file_logs.
        
        Args:
            transactions_data_list: List of dictionaries containing transaction log data
                Each dict must have:
                - source_transaction_id: Transaction ID (required)
                - user_source_group_id: User source group ID (optional)
                - transaction_type: Transaction type (optional)
                - status: Status (optional)
                - amount: Amount (required)
                - is_processed: Whether processed (optional, defaults to False)
        
        Returns:
            int: Number of rows inserted
        """
        if not transactions_data_list:
            logger.warning("No transaction data provided for bulk insert")
            return 0
        
        # Prepare data for bulk insert
        insert_data = []
        for txn_data in transactions_data_list:
            insert_record = {
                'source_transaction_id': txn_data.get('transaction_id') or txn_data.get('source_transaction_id'),
                'user_source_group_id': txn_data.get('user_source_group_id'),
                'transaction_type': txn_data.get('transaction_type'),
                'status': txn_data.get('status', 'SCHEDULED'),
                'amount': txn_data.get('amount'),
                'is_processed': txn_data.get('is_processed', False)
            }
            insert_data.append(insert_record)
        
        # Build SQL for bulk insert
        sql = """
            INSERT INTO investors.lendenapp_transaction_file_logs (
                source_transaction_id,
                user_source_group_id,
                transaction_type,
                status,
                amount,
                is_processed,
                created_dtm,
                updated_dtm
            )
            VALUES (
                %(source_transaction_id)s,
                %(user_source_group_id)s,
                %(transaction_type)s,
                %(status)s,
                %(amount)s,
                %(is_processed)s,
                NOW(),
                NOW()
            )
        """
        
        try:
            # Use executemany for bulk insert
            from django.db import connections
            with connections[self.db_alias].cursor() as cursor:
                cursor.executemany(sql, insert_data)
                rows_inserted = cursor.rowcount
                logger.info(f"Successfully inserted {rows_inserted} records into investors.lendenapp_transaction_file_logs")
                return rows_inserted
        except Exception as e:
            logger.error(f"Failed to bulk insert into investors.lendenapp_transaction_file_logs: {str(e)}")
            raise

