import logging
from typing import Optional, List, Dict, Any

from ..base_layer import BaseDataLayer
from ..constants import InvestmentType

logger = logging.getLogger('normal')


class InvestmentProductConfig(BaseDataLayer):
    
    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
    
    def get_investment_product_config(self, partner_code, investment_type, tenure=None):
        sql = """
                SELECT tipc.id
                FROM t_investment_product_config tipc
                JOIN t_mst_parameter tmp  ON tipc.investment_type_id = tmp.id
                JOIN t_mst_parameter tmp2 ON tipc.partner_code_id = tmp2.id
                WHERE tmp.key_2 = %(investment_type)s
                    AND tmp2.key_2 = %(partner_code)s
                    AND tipc.is_active = TRUE
                    AND tipc.deleted IS NULL
            """

        params = {
            'partner_code': partner_code,
            'investment_type': investment_type
        }

        if tenure:
            sql += """ AND tenure = %(tenure)s """
            params['tenure'] = tenure

        return self.execute_fetch_one(sql, params)

    def get_partner_code_id(self, partner_code):
        sql = """
                SELECT id
                FROM t_mst_parameter
                WHERE logical_group = 'partner_code'
                  AND key_2 = %(partner_code)s
                  AND deleted IS NULL
            """

        params = {
            'partner_code': partner_code
        }

        return self.execute_fetch_one(sql, params)

    def get_config_by_tenure_partner_and_investment_type(
        self,
        tenure: int,
        partner_code_id: int,
        investment_type_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing investment product configuration for a given
        (tenure, partner_code_id, investment_type_id) combination.

        Args:
            tenure: Tenure in months
            partner_code_id: MCP partner_code_id from `t_mst_parameter`
            investment_type_id: Investment type ID from `t_mst_parameter`

        Returns:
            Dict with config data (at minimum `id`) or None if not found
        """
        sql = """
            SELECT id
            FROM t_investment_product_config
            WHERE tenure = %(tenure)s
              AND partner_code_id = %(partner_code_id)s
              AND investment_type_id = %(investment_type_id)s
              AND deleted IS NULL
            LIMIT 1
        """

        params = {
            "tenure": tenure,
            "partner_code_id": partner_code_id,
            "investment_type_id": investment_type_id,
        }

        return self.execute_fetch_one(sql, params, to_dict=True)


    def get_product_details(self, partner_code, investment_type):
        sql = """
                SELECT tipc.name, tipc.tenure, tipc.min_amount, tipc.max_amount, 
                tipc.expected_roi, tipc.is_default, tipc.default_amount, tipc.is_active
                FROM t_investment_product_config tipc
                JOIN t_mst_parameter tmp ON tipc.partner_code_id = tmp.id
                JOIN t_mst_parameter tmp2 ON tipc.investment_type_id = tmp2.id
                WHERE 
                    tmp.key_2 = %(partner_code)s 
                    AND tmp2.key_2 = %(investment_type)s
                    AND tipc.is_active = true;
            """

        params = {
            'partner_code': partner_code,
            'investment_type': investment_type
        }

        return self.execute_fetch_all(sql, params)

    def get_expected_roi(self, investment_type, tenure, partner_code):
        sql = """
            SELECT 
                sm.expected_roi,
                sm.id
            FROM t_investment_product_config sm
            JOIN t_mst_parameter mp_inv ON sm.investment_type_id = mp_inv.id
            JOIN t_mst_parameter mp_partner ON sm.partner_code_id = mp_partner.id
            WHERE
              mp_inv.key_2 = %(investment_type)s
              AND mp_partner.key_2 = %(partner_code)s
              AND sm.tenure = %(tenure)s
              AND sm.is_active = TRUE
              AND sm.deleted IS NULL
            ORDER BY id DESC;
        """

        params = {
            'investment_type': investment_type,
            'partner_code': partner_code,
            'tenure': tenure
        }

        result = self.execute_fetch_one(sql, params)
        if result:
            return float(result['expected_roi']), result
        return None, None

    def check_config_exists(self, tenure, partner_code_id, investment_type_id):
        sql = """
                SELECT EXISTS(
                    SELECT 1 
                        FROM t_investment_product_config
                        WHERE 
                            is_active = TRUE
                            AND partner_code_id = %(partner_code_id)s
                            AND investment_type_id = %(investment_type_id)s
                            AND tenure = %(tenure)s
                            AND deleted IS NULL
                    ) as exists
                """

        params = {
            'partner_code_id': partner_code_id,
            'investment_type_id': investment_type_id,
            'tenure': tenure
        }

        result = self.execute_fetch_one(sql, params)
        return result['exists'] if result else False
    
    def get_investment_type_by_product_config_id(self, product_config_id: int) -> Optional[str]:
        """
        Get investment_type from product_config_id by joining with t_mst_parameter.
        
        Args:
            product_config_id: Product configuration ID
            
        Returns:
            Investment type string (MANUAL_LENDING, ONE_TIME_LENDING, MEDIUM_TERM_LENDING) or None
        """
        sql = """
            SELECT tmp.key_2 as investment_type
            FROM t_investment_product_config tipc
            JOIN t_mst_parameter tmp ON tipc.investment_type_id = tmp.id
            WHERE tipc.id = %(product_config_id)s
              AND tmp.logical_group = 'investment_type'
              AND tipc.deleted IS NULL
              AND tmp.deleted IS NULL
            LIMIT 1
        """
        
        params = {'product_config_id': product_config_id}
        result = self.execute_fetch_one(sql, params)
        return result['investment_type'] if result else None
    
    def get_product_config_ids_by_investment_type(self, investment_type: str) -> List[int]:
        """
        Get all product_config_ids for a given investment_type.
        
        Args:
            investment_type: Investment type (MANUAL_LENDING, ONE_TIME_LENDING, MEDIUM_TERM_LENDING)
            
        Returns:
            List of product_config_ids
        """
        sql = """
            SELECT DISTINCT tipc.id as product_config_id
            FROM t_investment_product_config tipc
            JOIN t_mst_parameter tmp ON tipc.investment_type_id = tmp.id
            WHERE tmp.key_2 = %(investment_type)s
              AND tmp.logical_group = 'investment_type'
              AND tipc.is_active = TRUE
              AND tipc.deleted IS NULL
              AND tmp.deleted IS NULL
        """
        
        params = {'investment_type': investment_type}
        results = self.execute_fetch_all(sql, params)
        return [row['product_config_id'] for row in results] if results else []
    
    def get_bulk_new_amount(self) -> Optional[Dict[str, Any]]:
        """
        Get bulk_new_amount from t_mst_parameter.
        """
        sql = """
            SELECT value_1::DOUBLE PRECISION AS bulk_new_amount
            FROM t_mst_parameter 
            WHERE logical_group = 'bulk_investment_new_amount'
        """
        return self.execute_fetch_one(sql, {})
    
    def fetch_cp_product_config_list(
        self, 
        partner_code_id: int, 
        custom_order_partner_ids: List[int],
        medium_term: str,
        one_time: str,
        manual: str
    ) -> List[Dict[str, Any]]:
        """
        Get CP product details.
        """
        sql = """
            SELECT
                tmp.id AS investment_type_id,
                tmp.value_1 AS investment_type_name,
                tmp.value_2 AS payout,
                tmp.value_3 AS descriptions,
                tmp.value_4 AS image_link,
                tmp.value_5 AS icon_link,
                tmp.key_2 AS investment_type,
                COALESCE(MAX(tipc.tenure), 0) AS max_tenure,
                COALESCE(MIN(tipc.tenure), 0) AS min_tenure,
                MAX(tipc.max_amount) AS max_investment,
                MIN(tipc.min_amount) AS min_investment,
                COALESCE(MAX(tipc.expected_roi), 0) AS max_roi,
                tipc.partner_code_id,
                CASE
                    WHEN tipc.partner_code_id = ANY(%(partner_ids)s) THEN
                        CASE
                            WHEN UPPER(tmp.key_2) = %(medium_term)s THEN 2
                            WHEN UPPER(tmp.key_2) = %(one_time)s THEN 1
                            WHEN UPPER(tmp.key_2) = %(manual)s THEN 0
                            ELSE tmp.id
                        END
                    ELSE tmp.id
                END AS order_id
            FROM t_mst_parameter tmp
            JOIN t_investment_product_config tipc ON tipc.investment_type_id = tmp.id
            WHERE
                tmp.logical_group = 'investment_type'
                AND tipc.partner_code_id = %(partner_code_id)s
                AND tipc.is_active = true
                AND tipc.deleted IS NULL
            GROUP BY
                tmp.id,
                tmp.value_1,
                tmp.value_2,
                tmp.value_3,
                tmp.value_4,
                tmp.value_5,
                tmp.key_2,
                tipc.partner_code_id
            ORDER BY order_id DESC
        """
        
        params = {
            'partner_code_id': partner_code_id,
            'partner_ids': custom_order_partner_ids,
            'medium_term': medium_term,
            'one_time': one_time,
            'manual': manual
        }
        return self.execute_fetch_all(sql, params)

        
    
    def get_cp_product_details(self, source: str, custom_order_partner_ids: List[int] = None) -> List:
        partner_result = self.get_partner_code_id(source)
        if not partner_result:
            return []
        
        partner_code_id = partner_result['id']
        
        # Get bulk_new_amount (matches line 27 of SP)
        bulk_result = self.get_bulk_new_amount()
        bulk_new_amount = bulk_result['bulk_new_amount'] if bulk_result else 0
        
        # Default to empty list if not provided
        if custom_order_partner_ids is None:
            custom_order_partner_ids = []
        
        results = self.fetch_cp_product_config_list(
            partner_code_id,
            custom_order_partner_ids,
            InvestmentType.MEDIUM_TERM_LENDING,
            InvestmentType.ONE_TIME_LENDING,
            InvestmentType.MANUAL_LENDING
        )
        
        # Add bulk_new_amount to each row (matches SP logic at line 140)
        for row in results:
            row['bulk_new_amount'] = bulk_new_amount
        
        return results

    def get_investment_product_config_by_source_and_investment_type(self, source, investment_type):
        """
        Get investment product config IDs by source (partner code) and investment type.
        
        Args:
            source: Partner code (e.g., 'LENDER CHANNEL PARTNER')
            investment_type: Investment type (e.g., 'ONE_TIME_LENDING')
            
        Returns:
            List of product config IDs
        """
        sql = """
            SELECT tipc.id
            FROM t_investment_product_config tipc
            JOIN t_mst_parameter tmp ON tipc.investment_type_id = tmp.id
            JOIN t_mst_parameter tmp2 ON tipc.partner_code_id = tmp2.id
            WHERE tmp.key_2 = %(investment_type)s
                AND tmp2.key_2 = %(source)s
                AND tipc.is_active = TRUE
                AND tipc.deleted IS NULL
        """

        params = {
            'source': source,
            'investment_type': investment_type
        }

        results = self.execute_fetch_all(sql, params)
        return [row['id'] for row in results] if results else []
    
    def get_investment_product_config_data(self, investment_type_id, tenure, name, partner_code_id):
        """
        Get investment product config data for a given combination.
        """
        sql = """
            SELECT 
                tipc.min_amount::INTEGER,
                tipc.max_amount::INTEGER
            FROM t_investment_product_config tipc
            WHERE tipc.tenure = %(tenure)s
              AND tipc.name = %(name)s
              AND tipc.investment_type_id = %(investment_type_id)s
              AND tipc.partner_code_id = %(partner_code_id)s
              AND tipc.deleted IS NULL
        """
        
        params = {
            'investment_type_id': investment_type_id,
            'tenure': tenure,
            'name': name,
            'partner_code_id': partner_code_id
        }
        
        return self.execute_fetch_all(sql, params)

    def update_investment_product_config_min_max(
            self, investment_type_id, tenure, name, partner_code_id, 
            min_amount, max_amount, is_default
    ):
        """
        Update investment product config min and max amount.
        """
        sql = """
            UPDATE t_investment_product_config
            SET min_amount = %(min_amount)s,
                max_amount = %(max_amount)s,
                is_default = %(is_default)s,
                updated_dtm = now()
            WHERE investment_type_id = %(investment_type_id)s
              AND tenure = %(tenure)s
              AND name = %(name)s
              AND partner_code_id = %(partner_code_id)s
              AND deleted IS NULL
              AND is_active = true
        """
        
        params = {
            'investment_type_id': investment_type_id,
            'tenure': tenure,
            'name': name,
            'partner_code_id': partner_code_id,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'is_default': is_default
        }
        
        return self.execute_update(sql, params)
