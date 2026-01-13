"""
Job Log Entity for handling operations on t_job_log and t_batch_log tables.
This module provides entity classes for job and batch logging operations.
"""

import logging

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class JobLog(BaseDataLayer):
    """
    Entity class for job log operations.
    
    Table Schema (t_job_log):
    - id: Serial (Primary Key)
    - job_run_log_id: bigint (unique, not null)
    - status: varchar(50) (not null)
    - start_time: timestamp with time zone (not null)
    - end_time: timestamp with time zone
    - job_name: text
    - batch_size: integer
    - total_batches: integer
    """
    
    def insert_job_log(self, job_data):
        """
        Insert a new job log record.
        
        Args:
            job_data: Dictionary containing job log information
                Required fields: job_run_log_id, job_name, status, start_time, batch_size, total_batches
                
        Returns:
            int: The ID of the created job log record
        """
        sql = """
            INSERT INTO t_job_log 
            (job_run_log_id, job_name, status, start_time, batch_size, total_batches)
            VALUES (%(job_run_log_id)s, %(job_name)s, %(status)s, %(start_time)s, %(batch_size)s, %(total_batches)s)
            RETURNING id
        """
        
        params = {
            "job_run_log_id": job_data["job_run_log_id"],
            "job_name": job_data["job_name"],
            "status": job_data["status"],
            "start_time": job_data["start_time"],
            "batch_size": job_data["batch_size"],
            "total_batches": job_data["total_batches"]
        }
        
        result = self.execute_fetch_one(sql=sql, params=params, to_dict=False, index_result=True)
        return result
    
    def update_job_log_status(self, job_run_log_id, status, end_time):
        """
        Update the status and end time of a job log record.
        
        Args:
            job_run_log_id: The job run log ID to update
            status: New status value
            end_time: End time value
            
        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_job_log
            SET status = %(status)s, end_time = %(end_time)s
            WHERE job_run_log_id = %(job_run_log_id)s
        """
        
        params = {
            "status": status,
            "end_time": end_time,
            "job_run_log_id": job_run_log_id
        }
        
        return self.execute_query(sql=sql, params=params, return_row_count=True)


class BatchLog(BaseDataLayer):
    """
    Entity class for batch log operations.
    
    Table Schema (t_batch_log):
    - id: Serial (Primary Key)
    - job_run_log_id: bigint
    - status: varchar(50) (not null)
    - start_time: timestamp with time zone (not null)
    - end_time: timestamp with time zone
    - batch_number: integer
    """
    
    def insert_batch_log(self, batch_data):
        """
        Insert a new batch log record.
        
        Args:
            batch_data: Dictionary containing batch log information
                Required fields: job_run_log_id, batch_number, status, start_time
                
        Returns:
            int: The ID of the created batch log record
        """
        sql = """
            INSERT INTO t_batch_log 
            (job_run_log_id, batch_number, status, start_time)
            VALUES (%(job_run_log_id)s, %(batch_number)s, %(status)s, %(start_time)s)
            RETURNING id
        """
        
        params = {
            "job_run_log_id": batch_data["job_run_log_id"],
            "batch_number": batch_data["batch_number"],
            "status": batch_data["status"],
            "start_time": batch_data["start_time"]
        }
        
        result = self.execute_fetch_one(sql=sql, params=params, to_dict=False, index_result=True)
        return result
    
    def update_batch_log_status(self, job_run_log_id, batch_number, status, end_time):
        """
        Update the status and end time of a batch log record.
        
        Args:
            job_run_log_id: The job run log ID
            batch_number: The batch number
            status: New status value
            end_time: End time value
            
        Returns:
            int: Number of affected rows
        """
        sql = """
            UPDATE t_batch_log
            SET status = %(status)s, end_time = %(end_time)s
            WHERE job_run_log_id = %(job_run_log_id)s AND batch_number = %(batch_number)s
        """
        
        params = {
            "status": status,
            "end_time": end_time,
            "job_run_log_id": job_run_log_id,
            "batch_number": batch_number
        }
        
        return self.execute_query(sql=sql, params=params, return_row_count=True)

