"""
Entity layer for retail portfolio calculation queue database operations.
"""

import logging
from typing import List, Dict, Any, Optional
from ..base_layer import BaseDataLayer
from ..constants import QueueStatus
logger = logging.getLogger(__name__)


class RetailPortfolioCalculationQueue(BaseDataLayer):
    """
    Entity layer for retail portfolio calculation queue table operations.
    Handles lender-based events (REDEMPTION) - Implementation deferred
    """
    
    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        
    def enqueue_task(
        self,
        lender_user_id: str,
        source_event: str,
        priority: int = 0
    ) -> Optional[int]:
        """
        Insert a new task into the retail portfolio calculation queue.
        
        Args:
            lender_user_id: Lender user ID for portfolio calculation
            source_event: Event type (e.g., 'REDEMPTION')
            priority: Priority (higher = processed first, default: 0)
            
        Returns:
            Queue task ID or None if failed
        """
        sql = """
            INSERT INTO t_retail_portfolio_calculation_queue (
                lender_user_id,
                status,
                priority,
                source_event,
                created_dtm
            )
            VALUES (
                %(lender_user_id)s,
                'PENDING',
                %(priority)s,
                %(source_event)s,
                NOW()
            )
            RETURNING id
        """
        
        params = {
            'lender_user_id': lender_user_id,
            'priority': priority,
            'source_event': source_event
        }
        
        try:
            result = self.execute_fetch_one(sql, params)
            return result['id'] if result else None
        except Exception as e:
            logger.error(
                f"Error enqueueing retail portfolio calculation task: {str(e)}",
                exc_info=True
            )
            return None
    
    def get_pending_tasks(
        self,
        batch_size: int = 500,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending tasks from queue with row-level locking.
        Uses FOR UPDATE SKIP LOCKED to allow concurrent processing.
        
        Args:
            batch_size: Number of tasks to fetch
            limit: Optional limit (overrides batch_size if provided)
            
        Returns:
            List of task dictionaries
        """
        actual_limit = limit if limit is not None else batch_size
        
        sql = """
            SELECT 
                id,
                lender_user_id,
                status,
                priority,
                source_event,
                created_dtm,
                retry_count,
                max_retries
            FROM t_retail_portfolio_calculation_queue
            WHERE status = 'PENDING'
            ORDER BY priority DESC, created_dtm ASC
            LIMIT %(limit)s
            FOR UPDATE SKIP LOCKED
        """
        
        params = {'limit': actual_limit}
        return self.execute_fetch_all(sql, params) or []
    
    def mark_tasks_processing(self, task_ids: List[int]) -> int:
        """
        Mark tasks as PROCESSING.
        
        Args:
            task_ids: List of task IDs to mark as processing
            
        Returns:
            Number of rows updated
        """
        if not task_ids:
            return 0
        
        sql = """
            UPDATE t_retail_portfolio_calculation_queue
            SET status = 'PROCESSING',
                updated_dtm = NOW()
            WHERE id = ANY(%(task_ids)s)
              AND status = 'PENDING'
        """
        
        params = {'task_ids': task_ids}
        return self.execute_update(sql, params)
    
    def mark_tasks_success(self, lender_user_ids: List[str]) -> int:
        """
        Mark all tasks for given lender_user_ids as SUCCESS.
        This handles deduplication - multiple tasks for same lender are all marked success.
        
        Args:
            lender_user_ids: List of lender user IDs whose tasks should be marked as success
            
        Returns:
            Number of rows updated
        """
        if not lender_user_ids:
            return 0
        
        sql = """
            UPDATE t_retail_portfolio_calculation_queue
            SET status = %(success_queue_status)s,
                processed_dtm = NOW(),
                updated_dtm = NOW()
            WHERE lender_user_id = ANY(%(lender_user_ids)s)
              AND status = ANY (%(pending_and_processing_queue_status)s)
        """
        
        params = {
            'lender_user_ids': lender_user_ids,
            'pending_and_processing_queue_status': [QueueStatus.PENDING, QueueStatus.PROCESSING],
            'success_queue_status': QueueStatus.SUCCESS
        }
        return self.execute_update(sql, params)
    
    def mark_tasks_failed(
        self,
        task_ids: List[int],
        error_message: str,
        increment_retry: bool = True
    ) -> int:
        """
        Mark tasks as FAILED and optionally increment retry count.
        If retry_count < max_retries, task will be reset to PENDING.
        
        Args:
            task_ids: List of task IDs to mark as failed
            error_message: Error message to store
            increment_retry: Whether to increment retry_count
            
        Returns:
            Number of rows updated
        """
        if not task_ids:
            return 0
        
        if increment_retry:
            sql = """
                UPDATE t_retail_portfolio_calculation_queue
                SET status = CASE 
                        WHEN retry_count + 1 < max_retries THEN 'PENDING'
                        ELSE 'FAILED'
                    END,
                    retry_count = retry_count + 1,
                    error_message = %(error_message)s,
                    updated_dtm = NOW()
                WHERE id = ANY(%(task_ids)s)
            """
        else:
            sql = """
                UPDATE t_retail_portfolio_calculation_queue
                SET status = 'FAILED',
                    error_message = %(error_message)s,
                    updated_dtm = NOW()
                WHERE id = ANY(%(task_ids)s)
            """
        
        params = {
            'task_ids': task_ids,
            'error_message': error_message[:1000]  # Limit error message length
        }
        return self.execute_update(sql, params)
    
    def fetch_queue_status_metrics(self) -> List[Dict[str, Any]]:
        """
        Get queue statistics for monitoring.
        
        Returns:
            List of dicts with statistics by status
        """
        sql = """
            SELECT 
                status,
                COUNT(*) as count,
                MIN(created_dtm) as oldest_task,
                MAX(created_dtm) as newest_task
            FROM t_retail_portfolio_calculation_queue
            GROUP BY status
        """
        
        return self.execute_fetch_all(sql, {}) or []

