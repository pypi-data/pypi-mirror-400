"""
Lender Mapper for handling CRUD operations on lender table.
This class provides production-level operations for lender management with proper validation,
error handling, and connection management.
"""

import logging
from typing import Dict, Optional, Any, List

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class Lender(BaseDataLayer):
    """
    Production-level operations for `t_lender` table.
    
    Table Schema (relevant columns):
    - id: Serial (Primary Key)
    - deleted: TIMESTAMPTZ (soft delete flag)
    - created_dtm: TIMESTAMPTZ
    - updated_dtm: TIMESTAMPTZ
    - user_id: VARCHAR(50)
    - partner_id: VARCHAR(50)          -- Channel / Master partner identifier
    - partner_mapping_id: INTEGER      -- FK to `t_channel_partner_mapping_table.id`
    - partner_code_id: INTEGER         -- FK to `t_mst_parameter.id` (logical_group='partner_code')
    """

    def create(self, lender_data: Dict[str, Any]) -> int:
        """
        Create a new lender record.
        
        Args:
            lender_data: Dictionary containing lender information
                Required fields: user_id, partner_code_id, user_source_group_id
                Optional fields: channel_partner_id, investor_mapping_id
                
        Returns:
            int: The ID of the created lender record
            
        Raises:
            ValidationError: If required fields are missing or invalid
            QueryError: If database operation fails
        """
        
        sql = """
            INSERT INTO t_lender (
                user_id, partner_id, partner_code_id, user_source_group_id,
                partner_mapping_id, created_dtm
            )
            VALUES (
                %(user_id)s, %(channel_partner_id)s, %(partner_code_id)s, %(user_source_group_id)s,
                %(investor_mapping_id)s, NOW()
            )
            RETURNING id
        """
        
        result = self.execute_fetch_one(sql, lender_data)
        logger.info(f"Successfully created lender with ID: {result['id']}")
        return result['id']

    def partner_exists(self, partner_id: str) -> bool:
        """
        Check if any lender exists for the given partner_id.

        Args:
            partner_id: Channel / Master partner identifier

        Returns:
            bool: True if at least one lender exists, False otherwise
        """
        sql = """
            SELECT EXISTS(
                SELECT 1
                FROM t_lender
                WHERE partner_id = %(partner_id)s
                  AND deleted IS NULL
            ) AS exists
        """
        params = {"partner_id": partner_id}
        result = self.execute_fetch_one(sql, params)
        return bool(result and result.get("exists"))

    def is_partner_already_mcp(self, partner_id: str, mcp_partner_code_id: int) -> bool:
        """
        Check if the given partner is already marked as MCP in `t_lender`.

        A partner is considered MCP if any lender row for that partner_id already
        has partner_code_id = mcp_partner_code_id.

        Args:
            partner_id: Channel / Master partner identifier
            mcp_partner_code_id: Partner code ID representing MCP

        Returns:
            bool: True if partner is already MCP, False otherwise
        """
        sql = """
            SELECT EXISTS(
                SELECT 1
                FROM t_lender
                WHERE partner_id = %(partner_id)s
                  AND partner_code_id = %(mcp_partner_code_id)s
                  AND deleted IS NULL
            ) AS exists
        """
        params = {
            "partner_id": partner_id,
            "mcp_partner_code_id": mcp_partner_code_id,
        }
        result = self.execute_fetch_one(sql, params)
        return bool(result and result.get("exists"))

    def update_partner_code_to_mcp(self, partner_id: str, mcp_partner_code_id: int) -> int:
        """
        Update all lender rows for the given partner_id to use the MCP partner_code_id.

        Args:
            partner_id: Channel / Master partner identifier
            mcp_partner_code_id: Partner code ID representing MCP

        Returns:
            int: Number of rows updated
        """
        sql = """
            UPDATE t_lender
            SET partner_code_id = %(mcp_partner_code_id)s,
                updated_dtm = NOW()
            WHERE partner_id = %(partner_id)s
              AND deleted IS NULL
        """
        params = {
            "partner_id": partner_id,
            "mcp_partner_code_id": mcp_partner_code_id,
        }
        return self.execute_update(sql, params)


    def get_id_from_source_id(self, source_id: int) -> Optional[int]:
        """
        Get lender ID from source_id.
        
        Args:
            source_id: The source_id to search for
            
        Returns:
            int: The lender ID if found, None if not found
            
        Raises:
            ValidationError: If source_id is invalid
            QueryError: If database operation fails
        """

        sql = """
            SELECT id FROM t_lender 
            WHERE user_source_group_id = %(source_id)s 
            AND deleted IS NULL;
        """
        params = {"source_id": source_id}
        
        result = self.execute_fetch_one(sql, params)
        if result:
            return result['id']
        return None

    def get_user_source_group_id_by_id(self, lender_id: int) -> Optional[int]:
        """
        Get user_source_group_id from lender_id.
        
        Args:
            lender_id: The lender ID to search for
            
        Returns:
            int: The user_source_group_id if found, None if not found
            
        Raises:
            ValidationError: If lender_id is invalid
            QueryError: If database operation fails
        """
        sql = """
            SELECT user_source_group_id 
            FROM t_lender 
            WHERE id = %(lender_id)s 
            AND deleted IS NULL
        """
        params = {"lender_id": lender_id}
        
        result = self.execute_fetch_one(sql, params, to_dict=True)
        if result:
            return result.get('user_source_group_id')
        return None
    
    def get_lender_user_id_by_lender_id(self, lender_id: int) -> Optional[str]:
        """
        Get lender user_id from lender_id.
        
        Args:
            lender_id: Lender ID (integer)
            
        Returns:
            Lender user_id (VARCHAR) or None if not found
        """
        sql = """
            SELECT user_id 
            FROM t_lender 
            WHERE id = %(lender_id)s 
            AND deleted IS NULL
        """
        
        params = {"lender_id": lender_id}
        result = self.execute_fetch_one(sql, params)
        if result:
            return result.get('user_id')
        return None
    
    def get_lender_user_ids_by_loan_id(self, loan_id: int) -> list:
        """
        Get all lender_user_ids (user_id) for a loan.
        Joins through t_investment_loan_detail -> t_lender_investment -> t_lender.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            List of lender user_ids (VARCHAR strings)
        """
        sql = """
            SELECT DISTINCT tl.user_id
            FROM t_investment_loan_detail tild
            JOIN t_lender_investment tli ON tild.investment_id = tli.id
            JOIN t_lender tl ON tli.lender_id = tl.id
            WHERE tild.loan_id = %(loan_id)s
              AND tild.deleted IS NULL
              AND tli.deleted IS NULL
              AND tl.deleted IS NULL
              AND tl.user_id IS NOT NULL
        """
        
        params = {'loan_id': loan_id}
        results = self.execute_fetch_all(sql, params) or []
        return [row['user_id'] for row in results if row.get('user_id')]


    def get_lender_id_user_id_from_source_id(self, source_id: int) -> Optional[int]:
        """
        Get lender ID and user_id from source_id.
        
        Args:
            source_id: The source_id to search for
            
        Returns:
            int: The lender ID if found, None if not found
        """
        sql = """
            SELECT id, user_id FROM t_lender 
            WHERE user_source_group_id = %(source_id)s 
            AND deleted IS NULL;
        """
        params = {"source_id": source_id}
        result = self.execute_fetch_one(sql, params)
        if result:
            return result['id'], result['user_id']
        return None