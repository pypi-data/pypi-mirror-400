"""
Common Table Repayment Migration Logs Entity for handling operations on t_common_table_repayment_migration_logs table.
This module provides entity class for common table migration log operations.
"""

import logging
from typing import Dict, Any, Optional, List

from ..base_layer import BaseDataLayer
from ..constants import (
    RepaymentMigrationStatus
)

logger = logging.getLogger('normal')


class CommonTableRepaymentMigrationLogs(BaseDataLayer):
    """
    Entity class for common table repayment migration log operations.
    
    Table Schema (t_common_table_repayment_migration_logs):
    - id: BIGSERIAL (Primary Key)
    - migration_batch_id: VARCHAR(30) UNIQUE
    - source_system: VARCHAR(10) (LMS or PP)
    - status: VARCHAR(20)
    - rows_processed: INTEGER
    - error_message: TEXT
    - created_dtm: TIMESTAMP WITH TIME ZONE
    - updated_dtm: TIMESTAMP WITH TIME ZONE
    """
    
    def create_log_entry(self, source_system: str, batch_size: int = 5000) -> int:
        """
        Create a new migration log entry.
        
        Args:
            source_system: Source system (RepaymentMigrationSource.LMS or RepaymentMigrationSource.PP)
            batch_size: Batch size for this migration
            
        Returns:
            ID of the created log entry
        """
        sql = """
            INSERT INTO t_common_table_repayment_migration_logs (
                migration_batch_id, source_system, status, rows_processed,
                created_dtm, updated_dtm
            )
            VALUES (
                TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '_' || 
                LPAD(EXTRACT(MICROSECONDS FROM NOW())::bigint % 10000::bigint, 4, '0'),
                %(source_system)s,
                %(status)s,
                0,
                NOW(),
                NOW()
            )
            RETURNING id
        """
        
        params = {
            'source_system': source_system,
            'status': RepaymentMigrationStatus.PROCESSING,
            'batch_size': batch_size
        }
        
        result = self.execute_fetch_one(sql, params, to_dict=False, index_result=True)
        return result if result else None
    
    def update_log_entry(self, log_id: int, status: str, rows_processed: int = 0, error_message: Optional[str] = None) -> int:
        """
        Update a migration log entry.
        
        Args:
            log_id: ID of the log entry to update
            status: New status
            rows_processed: Number of rows processed
            error_message: Error message if failed
            
        Returns:
            Number of records updated
        """
        sql = """
            UPDATE t_common_table_repayment_migration_logs
            SET status = %(status)s,
                rows_processed = %(rows_processed)s,
                error_message = %(error_message)s,
                updated_dtm = NOW()
            WHERE id = %(log_id)s
        """
        
        params = {
            'log_id': log_id,
            'status': status,
            'rows_processed': rows_processed,
            'error_message': error_message
        }
        
        return self.execute_update(sql, params)
    
    def get_recent_logs(self, source_system: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent migration logs.
        
        Args:
            source_system: Filter by source system (RepaymentMigrationSource.LMS or RepaymentMigrationSource.PP), None for all
            limit: Maximum number of records to return
            
        Returns:
            List of recent log entries
        """
        if source_system:
            sql = """
                SELECT 
                    id,
                    migration_batch_id,
                    source_system,
                    status,
                    rows_processed,
                    error_message,
                    created_dtm,
                    updated_dtm
                FROM t_common_table_repayment_migration_logs
                WHERE source_system = %(source_system)s
                ORDER BY created_dtm DESC
                LIMIT %(limit)s
            """
            params = {'source_system': source_system, 'limit': limit}
        else:
            sql = """
                SELECT 
                    id,
                    migration_batch_id,
                    source_system,
                    status,
                    rows_processed,
                    error_message,
                    created_dtm,
                    updated_dtm
                FROM t_common_table_repayment_migration_logs
                ORDER BY created_dtm DESC
                LIMIT %(limit)s
            """
            params = {'limit': limit}
        
        return self.execute_fetch_all(sql, params)

