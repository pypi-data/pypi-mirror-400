"""
Flow layer for repayment migration business logic.
This layer handles complex multi-step business processes and database operations for repayment migration.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import json

from ..base_layer import BaseDataLayer
from ..constants import (
    RepaymentMigrationSource,
    RepaymentMigrationStatus
)

logger = logging.getLogger('normal')


class RepaymentMigrationFlow(BaseDataLayer):
    """
    Flow for handling repayment migration business logic and database operations.
    Orchestrates complex multi-step processes for migrating repayment data.
    """

    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        self.batch_size = 5000
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def execute_lms_migration_procedure(self, batch_size: int = 5000) -> Any:
        """
        Execute the LMS to common table repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Result from stored procedure
        """
        params = [None, batch_size]  # inout_response, batch_size
        
        result = self.execute_procedure(
            procedure_name='prc_repayments_lms_to_vortex_common_table_migration',
            params=params,
            fetch_one=True,
            to_dict=False
        )
        
        return result

    def execute_lms_to_common_table_migration(self, batch_size: int = 5000) -> Dict[str, Any]:
        """
        Execute the LMS to common table repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Dict containing migration results
        """
        result = self.execute_lms_migration_procedure(batch_size)
        
        # Parse the JSON response
        if result and len(result) > 0:
            response_text = result[0] if isinstance(result, tuple) else result
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response_text}")
                return {
                    'status': 'ERROR',
                    'message': 'Failed to parse response',
                    'rows_processed': 0,
                    'conflicts_logged': 0
                }
        
        return {
            'status': 'ERROR',
            'message': 'No response from stored procedure',
            'rows_processed': 0,
            'conflicts_logged': 0
        }

    def execute_pp_migration_procedure(self, batch_size: int = 5000) -> Any:
        """
        Execute the PP to common table repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Result from stored procedure
        """
        params = [None, batch_size]  # inout_response, batch_size
        
        result = self.execute_procedure(
            procedure_name='prc_repayments_pp_to_vortex_common_table_migration',
            params=params,
            fetch_one=True,
            to_dict=False
        )
        
        return result

    def execute_pp_to_common_table_migration(self, batch_size: int = 5000) -> Dict[str, Any]:
        """
        Execute the PP to common table repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Dict containing migration results
        """
        result = self.execute_pp_migration_procedure(batch_size)
        
        # Parse the JSON response
        if result and len(result) > 0:
            response_text = result[0] if isinstance(result, tuple) else result
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response_text}")
                return {
                    'status': 'ERROR',
                    'message': 'Failed to parse response',
                    'rows_processed': 0,
                    'conflicts_logged': 0
                }
        
        return {
            'status': 'ERROR',
            'message': 'No response from stored procedure',
            'rows_processed': 0,
            'conflicts_logged': 0
        }
    
    def execute_vortex_migration_procedure(self, batch_size: int = 5000) -> Any:
        """
        Execute the common table to Vortex repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Result from stored procedure
        """
        params = [None, batch_size]  # inout_response, batch_size
        
        result = self.execute_procedure(
            procedure_name='prc_repayments_common_table_to_vortex_migration',
            params=params,
            fetch_one=True,
            to_dict=False
        )
        
        return result

    def execute_common_table_to_vortex_migration(self, batch_size: int = 5000) -> Dict[str, Any]:
        """
        Execute the common table to Vortex repayment migration stored procedure.
        
        Args:
            batch_size: Number of records to process in each batch (default: 5000)
            
        Returns:
            Dict containing migration results
        """
        result = self.execute_vortex_migration_procedure(batch_size)
        
        # Parse the JSON response
        if result and len(result) > 0:
            response_text = result[0] if isinstance(result, tuple) else result
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response_text}")
                return {
                    'status': RepaymentMigrationStatus.ERROR,
                    'message': 'Failed to parse response',
                    'rows_processed': 0,
                    'fee_records_inserted': 0
                }
        
        return {
            'status': RepaymentMigrationStatus.ERROR,
            'message': 'No response from stored procedure',
            'rows_processed': 0,
            'fee_records_inserted': 0
        }

    def get_repayment_details_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Get repayment details for a specific batch.
        
        Args:
            batch_id: Batch ID to fetch details for
            
        Returns:
            List of repayment detail records
        """
        sql = """
            SELECT 
                id, loan_id, loan_ref_id, purpose, purpose_amount, total_fees,
                is_processed, days_past_due, src_txn_id, sys_txn_id, batch_id,
                ammort_id, transaction_date, settlement_date, src_created_dtm,
                sys_created_dtm, updated_dtm
            FROM t_loan_repayment_detail
            WHERE batch_id = %(batch_id)s
            ORDER BY id
        """
        
        params = {'batch_id': batch_id}
        return self.execute_fetch_all(sql, params)

    def get_fee_details_by_repayment_id(self, repayment_detail_id: int) -> List[Dict[str, Any]]:
        """
        Get fee details for a specific repayment transaction.
        
        Args:
            repayment_detail_id: ID of the repayment detail record
            
        Returns:
            List of fee detail records
        """
        sql = """
            SELECT 
                id, fee_source_id, fee_source, fee_type, fee_amount, fee_levy_date,
                created_dtm, updated_dtm
            FROM t_fee_details
            WHERE fee_source_id = %(repayment_detail_id)s
            ORDER BY id
        """
        
        params = {'repayment_detail_id': repayment_detail_id}
        return self.execute_fetch_all(sql, params)

    def get_processing_logs_by_event(self, event_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get processing logs for a specific event.
        
        Args:
            event_name: Name of the event to fetch logs for
            limit: Maximum number of records to return
            
        Returns:
            List of processing log records
        """
        sql = """
            SELECT 
                id, created_dtm, updated_dtm, event_name, batch_id, msg,
                is_final, execution_time, rows_processed
            FROM repayment_processing_logs
            WHERE event_name = %(event_name)s
            ORDER BY created_dtm DESC
            LIMIT %(limit)s
        """
        
        params = {'event_name': event_name, 'limit': limit}
        return self.execute_fetch_all(sql, params)

    def get_lms_pending_repayment_count(self) -> int:
        """
        Get count of pending repayment records in LMS.
        
        Returns:
            Number of pending records
        """
        sql = """
            SELECT COUNT(*) as pending_count
            FROM ldclmsprod.ims_repayment_transfer imt
            WHERE imt.is_processed = false
              AND imt.settlement_date IS NOT NULL
              AND imt.emi_amount > 0
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['pending_count'] if result else 0

    def get_pp_pending_repayment_count(self) -> int:
        """
        Get count of pending repayment records in PP.
        
        Returns:
            Number of pending records
        """
        sql = """
            SELECT COUNT(*) as pending_count
            FROM ldcpp.loan_ims_repayment_transfer imt
            WHERE imt.is_processed = false
              AND imt.settlement_date IS NOT NULL
              AND imt.emi_amount > 0
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['pending_count'] if result else 0

    def get_lms_max_processed_id(self) -> Optional[int]:
        """
        Get the maximum ID of processed records in LMS for pagination.
        
        Returns:
            Maximum processed ID or None
        """
        sql = """
            SELECT MAX(id) as max_id
            FROM ldclmsprod.ims_repayment_transfer
            WHERE is_processed = true
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['max_id'] if result and result['max_id'] else None

    def get_pp_max_processed_id(self) -> Optional[int]:
        """
        Get the maximum ID of processed records in PP for pagination.
        
        Returns:
            Maximum processed ID or None
        """
        sql = """
            SELECT MAX(id) as max_id
            FROM ldcpp.loan_ims_repayment_transfer
            WHERE is_processed = true
        """
        
        result = self.execute_fetch_one(sql, to_dict=True)
        return result['max_id'] if result and result['max_id'] else None

    def execute_lms_migration_batch(self) -> Dict[str, Any]:
        """
        Execute a single LMS to common table migration batch.        
        Returns:
            Dict containing batch execution results
        """
        try:
            return self.execute_lms_to_common_table_migration(
                batch_size=self.batch_size
            )
        except Exception as e:
            logger.error(f"Error executing LMS migration batch: {str(e)}")
            return {
                'status': RepaymentMigrationStatus.ERROR,
                'message': str(e),
                'rows_processed': 0,
                'conflicts_logged': 0
            }

    def execute_pp_migration_batch(self) -> Dict[str, Any]:
        """
        Execute a single PP to common table migration batch.
        Returns:
            Dict containing batch execution results
        """
        try:
            return self.execute_pp_to_common_table_migration(
                batch_size=self.batch_size
            )
        except Exception as e:
            logger.error(f"Error executing PP migration batch: {str(e)}")
            return {
                'status': RepaymentMigrationStatus.ERROR,
                'message': str(e),
                'rows_processed': 0,
                'conflicts_logged': 0
            }
    
    def execute_common_table_to_vortex_batch(self) -> Dict[str, Any]:
        """
        Execute a single common table to Vortex migration batch.
        Returns:
            Dict containing batch execution results
        """
        try:
            return self.execute_common_table_to_vortex_migration(
                batch_size=self.batch_size
            )
        except Exception as e:
            logger.error(f"Error executing common table to Vortex migration batch: {str(e)}")
            return {
                'status': RepaymentMigrationStatus.ERROR,
                'message': str(e),
                'rows_processed': 0,
                'fee_records_inserted': 0
            }

    def should_retry(self, batch_count: int) -> bool:
        """
        Determine if a batch should be retried.
        
        Args:
            batch_count: Current batch number
            
        Returns:
            True if should retry, False otherwise
        """
        return batch_count <= self.max_retries

    def validate_migration_data(self, batch_id: str) -> Dict[str, Any]:
        """
        Validate migration data for a specific batch.
        
        Args:
            batch_id: Batch ID to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            # Get repayment details for the batch
            repayment_details = self.get_repayment_details_by_batch(batch_id)
            
            validation_results = {
                'batch_id': batch_id,
                'repayment_records_count': len(repayment_details),
                'validation_errors': [],
                'fee_validation': {}
            }
            
            # Validate each repayment record
            for record in repayment_details:
                repayment_id = record['id']
                
                # Get fee details for this repayment
                fee_details = self.get_fee_details_by_repayment_id(repayment_id)
                
                # Calculate total fees from fee details
                calculated_total_fees = sum(fee['fee_amount'] for fee in fee_details)
                recorded_total_fees = record['total_fees']
                
                # Validate fee totals match
                if abs(calculated_total_fees - recorded_total_fees) > 0.01:  # Allow for small rounding differences
                    validation_results['validation_errors'].append(
                        f"Repayment ID {repayment_id}: Fee mismatch - "
                        f"Calculated: {calculated_total_fees}, Recorded: {recorded_total_fees}"
                    )
                
                validation_results['fee_validation'][repayment_id] = {
                    'fee_records_count': len(fee_details),
                    'calculated_total': calculated_total_fees,
                    'recorded_total': recorded_total_fees,
                    'match': abs(calculated_total_fees - recorded_total_fees) <= 0.01
                }
            
            validation_results['status'] = RepaymentMigrationStatus.SUCCESS if not validation_results['validation_errors'] else RepaymentMigrationStatus.ERROR
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating migration data for batch {batch_id}: {str(e)}")
            return {
                'status': RepaymentMigrationStatus.ERROR,
                'message': str(e),
                'batch_id': batch_id
            }

    def get_migration_status(self, system: str = RepaymentMigrationSource.LMS) -> Dict[str, Any]:
        """
        Get current migration status and statistics for a specific system.
        
        Args:
            system: System to get status for (RepaymentMigrationSource.LMS or RepaymentMigrationSource.PP)
            
        Returns:
            Dict containing migration status information
        """
        try:
            if system.upper() == RepaymentMigrationSource.LMS:
                pending_count = self.get_lms_pending_repayment_count()
                max_processed_id = self.get_lms_max_processed_id()
            elif system.upper() == RepaymentMigrationSource.PP:
                pending_count = self.get_pp_pending_repayment_count()
                max_processed_id = self.get_pp_max_processed_id()
            else:
                return {
                    'status': RepaymentMigrationStatus.ERROR,
                    'message': f'Invalid system: {system}. Must be {RepaymentMigrationSource.LMS} or {RepaymentMigrationSource.PP}'
                }
            
            # Get recent processing logs
            migration_logs = self.get_processing_logs_by_event(
                f'{system.upper()}_TO_VORTEX_MIGRATION', limit=10
            )
            
            return {
                'status': RepaymentMigrationStatus.READY,
                'system': system.upper(),
                'pending_repayment_count': pending_count,
                'max_processed_id': max_processed_id,
                'recent_migration_logs': migration_logs,
                'batch_size': self.batch_size,
                'max_retries': self.max_retries
            }
            
        except Exception as e:
            logger.error(f"Error getting migration status for {system}: {str(e)}")
            return {
                'status': RepaymentMigrationStatus.ERROR,
                'message': str(e),
                'system': system.upper()
            }
