"""
Job Master Mapper for handling operations on t_job_master table.
This class provides operations for checking job status and configuration.
"""

import logging

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class JobMaster(BaseDataLayer):
    """
    Operations for t_job_master table.
    
    Table Schema:
    - job_name: varchar
    - is_job_enabled: boolean
    - is_batch_enabled: boolean
    """

    def is_job_enabled(self, job_name):
        """
        Check if a job is enabled in t_job_master table.
        
        Args:
            job_name: Name of the job to check
            
        Returns:
            bool: True if job exists and is enabled, False otherwise
        """
        sql = """
            SELECT EXISTS (
                SELECT 1
                FROM t_job_master
                WHERE job_name=%(job_name)s AND is_job_enabled
            )
        """
        try:
            params = {'job_name': job_name}
            result = self.execute_fetch_one(
                sql=sql,
                params=params,
            )
            return result['exists']
        except Exception as e:
            logger.error(f"Error checking job status for {job_name}: {str(e)}")
            return False

    def is_batch_enabled(self, job_name):
        """
        Check if batch processing is enabled for a job in t_job_master table.
        
        Args:
            job_name: Name of the job to check
            
        Returns:
            bool: True if job exists and batch is enabled, False otherwise
        """
        sql = """
            SELECT EXISTS (
                SELECT 1
                FROM t_job_master
                WHERE job_name=%(job_name)s AND is_batch_enabled
            )
        """
        try:
            params = {'job_name': job_name}
            result = self.execute_fetch_one(
                sql=sql,
                params=params
            )
            return result['exists']
        except Exception as e:
            logger.error(f"Error checking batch status for {job_name}: {str(e)}")
            return False

