from ..base_layer import BaseDataLayer


class MstParameter(BaseDataLayer):
    def get_investment_type_id(self, investment_type):
        sql = """
                SELECT id FROM t_mst_parameter
                WHERE 
                    logical_group = 'investment_type'
                    AND key_2 = %(investment_type)s
            """

        params = {
            'investment_type': investment_type
        }

        return self.execute_fetch_one(sql, params)

    def get_partner_code_id(self, partner_code):
        sql = """
                SELECT id FROM t_mst_parameter
                WHERE 
                    logical_group = 'partner_code'
                    AND key_2 = %(partner_code)s
            """

        params = {
            'partner_code': partner_code
        }

        return self.execute_fetch_one(sql, params)

    def get_bulk_partner_code_id(self, partner_codes):
        """
        Get partner code IDs for a list of partner codes.
        
        Args:
            partner_codes: List of partner code strings (e.g., ['LENDER CHANNEL PARTNER', 'MASTER CHANNEL PARTNER', 'CC', 'PTSO'])
            
        Returns:
            list: List of partner code IDs
        """
        sql = """
            SELECT id FROM t_mst_parameter
            WHERE 
                logical_group = 'partner_code'
                AND key_2 = ANY(%(partner_codes)s)
        """
        
        params = {
            'partner_codes': partner_codes
        }
        
        results = self.execute_fetch_all(sql, params, to_dict=True)
        return [result['id'] for result in results] if results else []

    
    def get_partner_code_by_id(self, partner_code_id: int):
        """
        Get partner code (key_2) from t_mst_parameter by partner_code_id.
        
        Args:
            partner_code_id: Partner code ID from t_lender.partner_code_id
            
        Returns:
            str: Partner code (key_2) or None if not found
        """
        sql = """
            SELECT key_2 as partner_code
            FROM t_mst_parameter
            WHERE id = %(partner_code_id)s
              AND logical_group = 'partner_code'
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'partner_code_id': partner_code_id
        }
        
        result = self.execute_fetch_one(sql, params)
        return result['partner_code'] if result else None