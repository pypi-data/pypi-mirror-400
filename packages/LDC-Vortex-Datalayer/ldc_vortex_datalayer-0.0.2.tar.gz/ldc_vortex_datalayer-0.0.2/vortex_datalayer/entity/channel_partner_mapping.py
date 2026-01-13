"""
Channel Partner Mapping Entity

Data layer for channel partner mapping table operations.
Handles CRUD operations for t_channel_partner_mapping_table.
"""

import logging
from typing import Dict, Optional, Any

from ..base_layer import BaseDataLayer

logger = logging.getLogger('normal')


class ChannelPartnerMapping(BaseDataLayer):
    """
    Production-level operations for t_channel_partner_mapping_table.

    Table Schema:
    - id: Serial (Primary Key)
    - deleted: Timestampz
    - created_dtm: Timestampz
    - updated_dtm: Timestampz
    - channel_partner_id: varchar(20)
    - master_partner_id: varchar(20)
    """

    def get_mapping_by_channel_partner_id(self, channel_partner_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel partner mapping by channel_partner_id.

        Args:
            channel_partner_id: Channel Partner ID to search for

        Returns:
            Dictionary with mapping data or None if not found
        """
        sql = """
            SELECT 
                id,
                channel_partner_id,
                master_partner_id
            FROM t_channel_partner_mapping_table
            WHERE channel_partner_id = %(channel_partner_id)s
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'channel_partner_id': channel_partner_id
        }
        
        return self.execute_fetch_one(sql, params, to_dict=True)

    def update_master_partner_id(
        self,
        channel_partner_id: str,
        master_partner_id: str
    ) -> bool:
        """
        Update master_partner_id for a channel partner mapping.

        Args:
            channel_partner_id: Channel Partner ID
            master_partner_id: Master Channel Partner ID to set

        Returns:
            bool: True if update successful, False otherwise
        """
        sql = """
            UPDATE t_channel_partner_mapping_table
            SET master_partner_id = %(master_partner_id)s,
                updated_dtm = NOW()
            WHERE channel_partner_id = %(channel_partner_id)s
              AND deleted IS NULL
        """
        
        params = {
            'channel_partner_id': channel_partner_id,
            'master_partner_id': master_partner_id
        }
        
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0

    def promote_cp_to_mcp(self, partner_id: str) -> int:
        """
        Promote a Channel Partner (CP) to Master Channel Partner (MCP) in mapping table.

        This method updates mapping rows where:
          - channel_partner_id = partner_id
          - master_partner_id IS NULL

        And sets:
          - master_partner_id = partner_id
          - channel_partner_id = NULL

        This effectively establishes the partner as its own MCP for associated lenders.

        Args:
            partner_id: Channel / Master partner identifier

        Returns:
            int: Number of rows updated
        """
        sql = """
            UPDATE t_channel_partner_mapping_table
            SET master_partner_id = %(partner_id)s,
                channel_partner_id = NULL,
                updated_dtm = NOW()
            WHERE channel_partner_id = %(partner_id)s
              AND master_partner_id IS NULL
              AND deleted IS NULL
        """

        params = {"partner_id": partner_id}
        return self.execute_update(sql, params)

    def get_id(
            self,
            channel_partner_id: Optional[str],
            master_partner_id: Optional[str]
    ) -> Optional[int]:
        """
        Get mapping ID based on channel_partner_id and master_partner_id.

        Args:
            channel_partner_id: Channel partner ID (optional)
            master_partner_id: Master channel partner ID (optional)

        Returns:
            int: The mapping ID if found, None otherwise
        """
        sql = """
            SELECT id 
            FROM t_channel_partner_mapping_table 
            WHERE 
                (channel_partner_id = %(channel_partner_id)s OR 
                 (channel_partner_id IS NULL AND %(channel_partner_id)s IS NULL))
                AND 
                (master_partner_id = %(master_partner_id)s OR 
                 (master_partner_id IS NULL AND %(master_partner_id)s IS NULL))
                AND deleted IS NULL
            LIMIT 1
        """

        params = {
            "channel_partner_id": channel_partner_id,
            "master_partner_id": master_partner_id
        }

        result = self.execute_fetch_one(sql, params)
        if result:
            return result['id']
        return None

    def create(
            self,
            channel_partner_id: Optional[str],
            master_partner_id: Optional[str]
    ) -> int:
        """
        Create a new channel partner mapping record.

        Args:
            channel_partner_id: Channel partner ID (optional)
            master_partner_id: Master channel partner ID (optional)

        Returns:
            int: The ID of the created mapping record
        """
        sql = """
            INSERT INTO t_channel_partner_mapping_table (
                channel_partner_id, master_partner_id, created_dtm, updated_dtm
            )
            VALUES (
                %(channel_partner_id)s, %(master_partner_id)s, NOW(), NOW()
            )
            RETURNING id
        """

        params = {
            "channel_partner_id": channel_partner_id,
            "master_partner_id": master_partner_id
        }

        result = self.execute_fetch_one(sql, params)
        logger.info(f"Successfully created channel partner mapping with ID: {result['id']}")
        return result['id']

