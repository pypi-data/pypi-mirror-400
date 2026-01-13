from ..base_layer import BaseDataLayer


class Calculation(BaseDataLayer):
    def fetch_roi_multiplication_factor(self, investment_type_id, reinvest):
        sql = """
            SELECT factor_to_be_multiplied
            FROM t_calculation_master
            WHERE investment_type_id = %(investment_type_id)s
              AND reinvest = %(reinvest)s
              AND deleted IS NULL
        """

        params = {
            'investment_type_id': investment_type_id,
            'reinvest': reinvest
        }

        result = self.execute_fetch_one(sql, params)
        return result['factor_to_be_multiplied'] if result else None
