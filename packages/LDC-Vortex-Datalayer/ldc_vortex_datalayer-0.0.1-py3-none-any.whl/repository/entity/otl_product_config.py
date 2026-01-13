from ..base_layer import BaseDataLayer


class OtlProductConfig(BaseDataLayer):

    def get_otl_product_config_data(
            self, otl_tenure, amount, loan_tenure, product_type, investment_type,
            partner_code
    ):
        sql = """
                SELECT DISTINCT product_name, 
                string_agg(DISTINCT TRUNC(loan_tenure)::INT::text, ',') AS loan_tenures
                FROM t_otl_product_config
                WHERE otl_tenure = %(otl_tenure)s
                AND %(amount)s BETWEEN min_amount AND max_amount
                AND loan_tenure = ANY(%(loan_tenure)s)
                AND deleted IS NULL
                AND product_type = %(product_type)s
                AND investment_type = %(investment_type)s
                AND partner_code = %(partner_code)s
                AND is_active
                GROUP BY product_name
            """

        params = {
            'otl_tenure': otl_tenure,
            'amount': amount,
            'loan_tenure': loan_tenure,
            'investment_type': investment_type,
            'product_type': product_type,
            'partner_code': partner_code
        }

        return self.execute_fetch_all(sql, params)

    def get_distinct_per_loan_amount(
            self, otl_tenure, loan_tenure, investment_amount, product_type,
            investment_type, partner_code
    ):
        sql = """
                SELECT per_loan_amount
                FROM t_otl_product_config
                WHERE otl_tenure = %(otl_tenure)s
                AND loan_tenure = ANY(%(loan_tenure)s)
                AND %(investment_amount)s BETWEEN min_amount AND max_amount
                AND deleted IS NULL
                AND product_type = %(product_type)s
                AND investment_type = %(investment_type)s
                AND partner_code = %(partner_code)s
                AND is_active
                LIMIT 1
            """

        params = {
            'otl_tenure': otl_tenure,
            'loan_tenure': loan_tenure,
            'investment_amount': investment_amount,
            'product_type': product_type,
            'investment_type': investment_type,
            'partner_code': partner_code
        }

        return self.execute_fetch_one(sql, params)

    def get_otl_loan_tenures(self, tenure, product_names):
        sql = """
            SELECT DISTINCT loan_tenure
            FROM t_otl_product_config
            WHERE otl_tenure = %(tenure)s
              AND product_name = ANY(%(product_names)s)
              AND deleted IS NULL
            ORDER BY loan_tenure
        """

        params = {
            'tenure': tenure,
            'product_names': product_names
        }

        result = self.execute_fetch_all(sql, params)
        return [str(int(row['loan_tenure'])) for row in result] if result else []

    def get_otl_config_tenure_keys(self, otl_tenure):
        sql = """
            SELECT DISTINCT 
                CONCAT('tenure_', CAST(loan_tenure AS INTEGER), 'M') as formatted_tenure
            FROM t_otl_product_config
            WHERE otl_tenure = %(otl_tenure)s
              AND deleted IS NULL
            ORDER BY formatted_tenure
        """

        params = {'otl_tenure': otl_tenure}
        result = self.execute_fetch_all(sql, params)

        return [row['formatted_tenure'] for row in result] if result else []
    
    def get_loan_details_by_tenure(self, otl_tenure, min_amount, product_name_list):
        sql = """
            SELECT 
                per_loan_amount,
                ARRAY_AGG(DISTINCT loan_tenure ORDER BY loan_tenure) as loan_tenure
            FROM t_otl_product_config
            WHERE otl_tenure = %(otl_tenure)s
              AND min_amount <= %(min_amount)s
              AND product_name = ANY(%(product_name_list)s)
              AND deleted IS NULL
            GROUP BY per_loan_amount
        """
        
        params = {
            'otl_tenure': otl_tenure,
            'min_amount': min_amount,
            'product_name_list': product_name_list
        }
        
        return self.execute_fetch_all(sql, params)

    def get_distinct_slabs_for_otl_tenure(
            self, otl_tenure, product_type, investment_type, product_name, partner_code
    ):
        """Get distinct slabs for a given OTL tenure and configuration."""
        sql = """
            SELECT DISTINCT 
                min_amount::INTEGER,
                max_amount::INTEGER,
                per_loan_amount::INTEGER
            FROM t_otl_product_config
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s 
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND product_name = %(product_name)s 
              AND deleted IS NULL 
              AND is_active = true
            ORDER BY min_amount
        """

        params = {
            'otl_tenure': otl_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_fetch_all(sql, params)

    def get_all_otl_tenure_combinations(self):
        """Get all distinct OTL tenure combinations."""
        sql = """
            SELECT DISTINCT 
                partner_code,
                otl_tenure, 
                investment_type, 
                product_type,
                product_name
            FROM t_otl_product_config
            WHERE deleted IS NULL 
              AND is_active = true
            ORDER BY partner_code, otl_tenure
        """

        return self.execute_fetch_all(sql, {})

    def get_source_loan_tenure(
            self, otl_tenure, product_type, investment_type, product_name, partner_code
    ):
        """Get available loan tenures for a given OTL configuration."""
        sql = """
            SELECT DISTINCT loan_tenure 
            FROM t_otl_product_config
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND product_name = %(product_name)s 
              AND deleted IS NULL 
              AND is_active = true
            ORDER BY loan_tenure
        """

        params = {
            'otl_tenure': otl_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_fetch_all(sql, params)

    def get_product_names_for_combination(
            self, otl_tenure, product_type, investment_type, partner_code
    ):
        """Get product names for a given OTL tenure, product type and investment type."""
        sql = """
            SELECT DISTINCT product_name 
            FROM t_otl_product_config
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s 
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND deleted IS NULL 
              AND is_active = true
        """

        params = {
            'otl_tenure': otl_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'partner_code': partner_code
        }

        return self.execute_fetch_all(sql, params)

    def get_slabs_and_partners_for_source(
            self, otl_tenure, source_loan_tenure, product_type, investment_type, 
            product_name, partner_code
    ):
        """Get slabs and partners for a given OTL tenure and source loan tenure."""
        sql = """
            SELECT DISTINCT min_amount, max_amount, per_loan_amount
            FROM t_otl_product_config
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s 
              AND loan_tenure = %(source_loan_tenure)s
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND product_name = %(product_name)s
              AND deleted IS NULL 
              AND is_active = true
        """

        params = {
            'otl_tenure': otl_tenure,
            'source_loan_tenure': source_loan_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_fetch_all(sql, params)

    def update_loan_amount(
            self, new_loan_amount, min_amount, max_amount, unique_key_min_amount, 
            unique_key_max_amount, otl_tenure, product_type, investment_type, 
            product_name, partner_code
    ):
        """Update loan amount for specific criteria."""
        sql = """
            UPDATE t_otl_product_config
            SET per_loan_amount = %(new_loan_amount)s,
                min_amount = %(unique_key_min_amount)s,
                max_amount = %(unique_key_max_amount)s,
                updated_dtm = now()
            WHERE min_amount = %(min_amount)s 
              AND max_amount = %(max_amount)s 
              AND partner_code = %(partner_code)s
              AND otl_tenure = %(otl_tenure)s 
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND product_name = %(product_name)s 
              AND deleted IS NULL 
              AND is_active = true
        """

        params = {
            'new_loan_amount': new_loan_amount,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'unique_key_min_amount': unique_key_min_amount,
            'unique_key_max_amount': unique_key_max_amount,
            'otl_tenure': otl_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_update(sql, params)

    def deactivate_existing_slabs(
            self, otl_tenure, product_type, investment_type, product_name, 
            partner_code, apply_to_all_products
    ):
        """Deactivate existing slabs for a tenure."""
        sql = """
            UPDATE t_otl_product_config
            SET is_active = false, deleted = NOW()
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s 
              AND product_type = %(product_type)s
              AND investment_type = %(investment_type)s
        """
        
        if not apply_to_all_products:
            sql += " AND product_name = %(product_name)s"
        
        sql += " AND deleted IS NULL AND is_active = true"

        params = {
            'otl_tenure': otl_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_update(sql, params)

    def bulk_insert_slabs(self, data_for_bulk_insert):
        """
        Bulk insert slabs into database.
        
        Args:
            data_for_bulk_insert: List of tuples with format:
                (product_name, product_type, otl_tenure, loan_tenure,
                 min_amount, max_amount, per_loan_amount,
                 investment_type, is_active, created_dtm, updated_dtm, partner_code)
        
        Returns:
            Number of rows inserted
        """
        sql = """
            INSERT INTO t_otl_product_config
            (product_name, product_type, otl_tenure, loan_tenure, min_amount, 
             max_amount, per_loan_amount, investment_type, is_active, 
             created_dtm, updated_dtm, partner_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        return self.execute_bulk_update(sql, data_for_bulk_insert)

    def deactivate_loan_tenure(
            self, otl_tenure, loan_tenure, product_type, investment_type, 
            product_name, partner_code
    ):
        """Deactivate a loan tenure for a given OTL tenure and product type."""
        sql = """
            UPDATE t_otl_product_config
            SET is_active = false, deleted = now()
            WHERE partner_code = %(partner_code)s 
              AND otl_tenure = %(otl_tenure)s 
              AND loan_tenure = %(loan_tenure)s
              AND product_type = %(product_type)s 
              AND investment_type = %(investment_type)s 
              AND product_name = %(product_name)s 
              AND deleted IS NULL 
              AND is_active = true
        """

        params = {
            'otl_tenure': otl_tenure,
            'loan_tenure': loan_tenure,
            'product_type': product_type,
            'investment_type': investment_type,
            'product_name': product_name,
            'partner_code': partner_code
        }

        return self.execute_update(sql, params)