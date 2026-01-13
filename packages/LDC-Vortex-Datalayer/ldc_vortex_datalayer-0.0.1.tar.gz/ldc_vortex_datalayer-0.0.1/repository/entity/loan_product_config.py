"""
Entity layer for loan product configuration database operations.
"""

from typing import Optional
from ..base_layer import BaseDataLayer


class LoanProductConfig(BaseDataLayer):
    """
    Data layer for loan product configuration database operations.
    """
    
    def get_product_config(self, source: str, partner_code: str, tenure: int) -> Optional[dict]:
        """
        Get loan product configuration by source, partner_code, and tenure.
        
        Args:
            source: Source system (MONO, MICRO, PP, LMS)
            partner_code: Partner code
            tenure: Loan tenure in months
            
        Returns:
            Dict with id, tenure, and is_live_enabled if exists, None otherwise
        """
        sql = """
            SELECT id, tenure, is_live_enabled
            FROM t_loan_product_config
            WHERE source = %(source)s
              AND partner_code = %(partner_code)s
              AND tenure = %(tenure)s
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {
            'source': source,
            'partner_code': partner_code,
            'tenure': tenure
        }
        result = self.execute_fetch_one(sql, params)
        return result if result else None

    def get_product_config_ids_by_partner_tenure_pairs(self, partner_tenure_pairs):
        """
        Get loan product configuration IDs for multiple partner_code and tenure combinations.

        Args:
            partner_tenure_pairs: List of tuples [(partner_code, tenure), ..]
                                 e.g., [('EPF', 3), ('IM', 4), ('RAJ', 3)]

        Returns:
            List of loan_product_config IDs
        """
        if not partner_tenure_pairs:
            return []

        # Separate partner_codes and tenures
        partner_codes = [pair[0] for pair in partner_tenure_pairs]
        tenures = [pair[1] for pair in partner_tenure_pairs]

        sql = """
            SELECT DISTINCT tlpc.id
            FROM t_loan_product_config tlpc
            INNER JOIN UNNEST(%(partner_codes)s::text[], %(tenures)s::integer[]) AS t(partner_code, tenure)
                ON tlpc.partner_code = t.partner_code::partner_code_enum AND tlpc.tenure = t.tenure
            WHERE tlpc.deleted IS NULL
        """

        params = {
            'partner_codes': partner_codes,
            'tenures': tenures
        }

        return self.execute_fetch_all(sql, params)
