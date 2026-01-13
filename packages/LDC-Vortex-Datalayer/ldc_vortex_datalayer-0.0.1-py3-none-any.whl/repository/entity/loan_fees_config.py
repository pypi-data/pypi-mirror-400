"""
Entity layer for loan fees configuration database operations.
"""

import random
import time
from typing import Optional, Dict, Any
from ..base_layer import BaseDataLayer, UniqueConstraintError
import logging

logger = logging.getLogger(__name__)

class LoanFeesConfig(BaseDataLayer):
    """
    Data layer for loan fees configuration database operations.
    """
    
    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
    
    def get_fees_config(
        self,
        source: str,
        partner_code: str,
        tenure: int,
        repayment_frequency: str,
        facilitation_fee_percentage: float,
        collection_fee_percentage: float,
        recovery_fee_percentage: float
    ) -> Optional[str]:
        """
        Get existing fees config_id by matching all parameters.
        
        Args:
            source: Source system
            partner_code: Partner code
            tenure: Loan tenure
            repayment_frequency: DAILY or MONTHLY
            facilitation_fee_percentage: Facilitation fee percentage
            collection_fee_percentage: Collection fee percentage
            recovery_fee_percentage: Recovery fee percentage
            
        Returns:
            config_id if exists, None otherwise
        """
        sql = """
            SELECT config_id
            FROM t_loan_fees_config
            WHERE source = %(source)s
              AND partner_code = %(partner_code)s
              AND tenure = %(tenure)s
              AND repayment_frequency = %(repayment_frequency)s
              AND facilitation_fee_percentage = %(facilitation_fee_percentage)s
              AND collection_fee_percentage = %(collection_fee_percentage)s
              AND recovery_fee_percentage = %(recovery_fee_percentage)s
            LIMIT 1
        """
        
        params = {
            'source': source,
            'partner_code': partner_code,
            'tenure': tenure,
            'repayment_frequency': repayment_frequency,
            'facilitation_fee_percentage': facilitation_fee_percentage,
            'collection_fee_percentage': collection_fee_percentage,
            'recovery_fee_percentage': recovery_fee_percentage
        }
        result = self.execute_fetch_one(sql, params)
        return result['config_id'] if result else None
    
    def generate_config_id(self) -> Optional[Dict[str, Any]]:
        """
        Generate a new config_id using database function.
        
        Returns:
            Dict with config_id
        """
        sql = "SELECT fn_generate_fees_config_id() as config_id"
        return self.execute_fetch_one(sql, {})
    
    def insert_fees_config(
        self,
        config_id: str,
        source: str,
        partner_code: str,
        tenure: int,
        repayment_frequency: str,
        facilitation_fee_percentage: float,
        collection_fee_percentage: float,
        recovery_fee_percentage: float
    ) -> Optional[Dict[str, Any]]:
        """
        Insert new fees config with ON CONFLICT handling.
        
        Returns:
            Dict with config_id if inserted, None if conflict occurred
        """
        sql = """
            INSERT INTO t_loan_fees_config (
                config_id,
                repayment_frequency,
                source,
                partner_code,
                tenure,
                facilitation_fee_percentage,
                collection_fee_percentage,
                recovery_fee_percentage
            )
            VALUES (
                %(config_id)s,
                %(repayment_frequency)s,
                %(source)s,
                %(partner_code)s,
                %(tenure)s,
                %(facilitation_fee_percentage)s,
                %(collection_fee_percentage)s,
                %(recovery_fee_percentage)s
            )
            ON CONFLICT ON CONSTRAINT unique_cig_config_combination DO NOTHING
            RETURNING config_id
        """
        
        params = {
            'config_id': config_id,
            'repayment_frequency': repayment_frequency,
            'source': source,
            'partner_code': partner_code,
            'tenure': tenure,
            'facilitation_fee_percentage': facilitation_fee_percentage,
            'collection_fee_percentage': collection_fee_percentage,
            'recovery_fee_percentage': recovery_fee_percentage
        }
        
        return self.execute_fetch_one(sql, params)

    
    def create_fees_config(
        self,
        source: str,
        partner_code: str,
        tenure: int,
        repayment_frequency: str,
        facilitation_fee_percentage: float,
        collection_fee_percentage: float,
        recovery_fee_percentage: float,
        max_retries: int = 3
    ) -> str:
        """
        Create a new fees config and return config_id.
        Handles race conditions by retrying on unique constraint violations.
        
        Args:
            source: Source system
            partner_code: Partner code
            tenure: Loan tenure
            repayment_frequency: DAILY or MONTHLY
            facilitation_fee_percentage: Facilitation fee percentage
            collection_fee_percentage: Collection fee percentage
            recovery_fee_percentage: Recovery fee percentage
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            Generated config_id
            
        Raises:
            UniqueConstraintError: If all retries fail
        """
        base_delay = 0.01
        max_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Generate config_id using function
                logger.info(f"Generating config_id for attempt {attempt}")
                config_id_result = self.generate_config_id()
                config_id = config_id_result['config_id']
                
                # Insert new fees config with ON CONFLICT handling
                result = self.insert_fees_config(
                    config_id, source, partner_code, tenure, repayment_frequency,
                    facilitation_fee_percentage, collection_fee_percentage, recovery_fee_percentage
                )
                
                # If INSERT was skipped due to conflict, fetch the existing config_id
                if not result:
                    # Config was inserted by another concurrent request
                    # Fetch the existing config_id based on unique constraint
                    existing_config = self.get_fees_config(
                        source=source,
                        partner_code=partner_code,
                        tenure=tenure,
                        repayment_frequency=repayment_frequency,
                        facilitation_fee_percentage=facilitation_fee_percentage,
                        collection_fee_percentage=collection_fee_percentage,
                        recovery_fee_percentage=recovery_fee_percentage
                    )
                    if existing_config:
                        return existing_config
                    else:
                        # If not found, raise to trigger retry with new config_id
                        raise UniqueConstraintError(
                            "Config not found after ON CONFLICT, retrying with new config_id",
                            constraint_name="unique_cig_config_combination",
                            db_alias=self.db_alias
                        )
                
                return result['config_id']
                
            except Exception as e:
                # Check if it's a unique constraint violation using base layer helper
                if not BaseDataLayer.is_unique_constraint_error(e):
                    # Not a unique constraint error, re-raise immediately
                    raise
                
                # If it's the last attempt, try to get existing config or raise
                if attempt == max_retries - 1:
                    existing_config = self.get_fees_config(
                        source=source,
                        partner_code=partner_code,
                        tenure=tenure,
                        repayment_frequency=repayment_frequency,
                        facilitation_fee_percentage=facilitation_fee_percentage,
                        collection_fee_percentage=collection_fee_percentage,
                        recovery_fee_percentage=recovery_fee_percentage
                    )
                    if existing_config:
                        return existing_config
                    raise UniqueConstraintError(
                        f"Unique constraint violation after {max_retries} retries: {str(e)}",
                        constraint_name=BaseDataLayer.get_constraint_name(e),
                        db_alias=self.db_alias
                    ) from e
                
                # Calculate exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, base_delay), max_delay)
                time.sleep(delay)
        
        # Should not reach here, but just in case
        raise UniqueConstraintError(
            f"Failed to create fees config after {max_retries} attempts",
            constraint_name="unique_cig_config_combination",
            db_alias=self.db_alias
        )
