"""
Entity layer for loan event queue database operations.
One task per loan event (not per lender).
"""

import logging
import json
from typing import List, Dict, Any, Optional
from ..base_layer import BaseDataLayer

logger = logging.getLogger(__name__)


class LoanEventQueue(BaseDataLayer):
    """
    Entity layer for loan event queue table operations.
    Handles loan-based events: DISBURSAL, CLOSURE, DPD_UPDATE.
    One task per loan event (not per lender).
    """
    
    def get_existing_task(
        self,
        loan_ref_id: str,
        task_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing task for a loan event if it exists.
        
        Args:
            loan_ref_id: Loan reference ID
            task_type: Task type ('DISBURSAL', 'CLOSURE', 'DPD_UPDATE')
            
        Returns:
            Task dictionary if exists, None otherwise
        """
        sql = """
            SELECT 
                id,
                loan_ref_id,
                task_type,
                event_metadata,
                status,
                priority,
                created_dtm,
                retry_count,
                max_retries
            FROM t_loan_event_queue
            WHERE loan_ref_id = %(loan_ref_id)s
              AND task_type = %(task_type)s
            LIMIT 1
        """
        
        params = {
            'loan_ref_id': loan_ref_id,
            'task_type': task_type
        }
        
        result = self.execute_fetch_one(sql, params)
        
        # Parse JSONB event_metadata if present
        if result and result.get('event_metadata'):
            try:
                result['event_metadata'] = json.loads(result['event_metadata']) if isinstance(result['event_metadata'], str) else result['event_metadata']
            except (json.JSONDecodeError, TypeError):
                result['event_metadata'] = {}
        
        return result
    
    def enqueue_task(
        self,
        loan_ref_id: str,
        task_type: str,
        event_metadata: Dict[str, Any],
        priority: int = 0
    ) -> Optional[int]:
        """
        Insert a new task into the loan event queue.
        One task per loan event (not per lender).
        
        Args:
            loan_ref_id: Loan reference ID (alphanumeric)
            task_type: Task type ('DISBURSAL', 'CLOSURE', 'DPD_UPDATE')
            event_metadata: Event-specific metadata dict
                - DISBURSAL: {'liquidation_date': 'YYYY-MM-DD'}
                - CLOSURE: {}
                - DPD_UPDATE: {'days_past_due': int, 'npa_as_on_date': 'YYYY-MM-DD' or None}
            priority: Priority (higher = processed first, default: 0)
            
        Returns:
            Queue task ID or None if failed
        """
        sql = """
            INSERT INTO t_loan_event_queue (
                loan_ref_id,
                task_type,
                event_metadata,
                status,
                priority,
                created_dtm
            )
            VALUES (
                %(loan_ref_id)s,
                %(task_type)s,
                %(event_metadata)s,
                'PENDING',
                %(priority)s,
                NOW()
            )
            RETURNING id
        """
        
        params = {
            'loan_ref_id': loan_ref_id,
            'task_type': task_type,
            'event_metadata': json.dumps(event_metadata) if event_metadata else json.dumps({}),
            'priority': priority
        }
        
        try:
            result = self.execute_fetch_one(sql, params)
            return result['id'] if result else None
        except Exception as e:
            # Check if it's a unique constraint violation (duplicate task)
            from ..base_layer import BaseDataLayer
            if BaseDataLayer.is_unique_constraint_error(e):
                logger.warning(
                    f"Task already exists for loan_ref_id: {loan_ref_id}, task_type: {task_type}. "
                    f"Duplicate insert prevented by unique constraint."
                )
                return None
            logger.error(
                f"Error enqueueing loan event task: {str(e)}",
                exc_info=True
            )
            return None
    
    def get_pending_loan_events(
        self,
        batch_size: int = 500,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending loan events from queue with row-level locking.
        Returns unique loan events (one per loan_ref_id + task_type).
        Uses FOR UPDATE SKIP LOCKED to allow concurrent processing.
        
        Args:
            batch_size: Number of loan events to fetch
            limit: Optional limit (overrides batch_size if provided)
            
        Returns:
            List of loan event dictionaries (one per loan event)
        """
        actual_limit = limit if limit is not None else batch_size
        
        sql = """
            SELECT 
                id,
                loan_ref_id,
                task_type,
                event_metadata,
                status,
                priority,
                created_dtm,
                retry_count,
                max_retries
            FROM t_loan_event_queue
            WHERE status = 'PENDING'
            ORDER BY priority DESC, created_dtm ASC
            LIMIT %(limit)s
            FOR UPDATE SKIP LOCKED
        """
        
        params = {'limit': actual_limit}
        tasks = self.execute_fetch_all(sql, params) or []
        
        # Parse JSONB event_metadata if present
        for task in tasks:
            if task.get('event_metadata'):
                try:
                    task['event_metadata'] = json.loads(task['event_metadata']) if isinstance(task['event_metadata'], str) else task['event_metadata']
                except (json.JSONDecodeError, TypeError):
                    task['event_metadata'] = {}
            else:
                task['event_metadata'] = {}
        
        return tasks
    
    def mark_task_processing(self, task_id: int) -> int:
        """
        Mark a task as PROCESSING.
        
        Args:
            task_id: Task ID to mark as processing
            
        Returns:
            Number of rows updated (should be 1)
        """
        sql = """
            UPDATE t_loan_event_queue
            SET status = 'PROCESSING',
                updated_dtm = NOW()
            WHERE id = %(task_id)s
              AND status = 'PENDING'
        """
        
        params = {'task_id': task_id}
        return self.execute_update(sql, params)
    
    def mark_task_success(self, task_id: int) -> int:
        """
        Mark a task as SUCCESS.
        
        Args:
            task_id: Task ID to mark as success
            
        Returns:
            Number of rows updated (should be 1)
        """
        sql = """
            UPDATE t_loan_event_queue
            SET status = 'SUCCESS',
                processed_dtm = NOW(),
                updated_dtm = NOW()
            WHERE id = %(task_id)s
        """
        
        params = {'task_id': task_id}
        return self.execute_update(sql, params)
    
    def mark_task_failed(
        self,
        task_id: int,
        error_message: str,
        increment_retry: bool = True
    ) -> int:
        """
        Mark a task as FAILED and optionally increment retry count.
        If retry_count < max_retries, task will be reset to PENDING.
        
        Args:
            task_id: Task ID to mark as failed
            error_message: Error message to store
            increment_retry: Whether to increment retry_count
            
        Returns:
            Number of rows updated (should be 1)
        """
        if increment_retry:
            sql = """
                UPDATE t_loan_event_queue
                SET status = CASE 
                        WHEN retry_count + 1 < max_retries THEN 'PENDING'
                        ELSE 'FAILED'
                    END,
                    retry_count = retry_count + 1,
                    error_message = %(error_message)s,
                    updated_dtm = NOW()
                WHERE id = %(task_id)s
            """
        else:
            sql = """
                UPDATE t_loan_event_queue
                SET status = 'FAILED',
                    error_message = %(error_message)s,
                    updated_dtm = NOW()
                WHERE id = %(task_id)s
            """
        
        params = {
            'task_id': task_id,
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
            FROM t_loan_event_queue
            GROUP BY status
        """
        
        return self.execute_fetch_all(sql, {}) or []
