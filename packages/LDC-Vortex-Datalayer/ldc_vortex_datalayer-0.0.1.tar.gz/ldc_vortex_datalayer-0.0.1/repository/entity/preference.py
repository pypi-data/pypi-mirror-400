from ..base_layer import BaseDataLayer


class Preference(BaseDataLayer):
    def get_preference_by_id(self, preference_id):
        """
        Fetches a preference record by its ID for a specific set of boolean columns.
        """
        query = f"""
            SELECT 
                "tenure_below_3M", "tenure_3_to_1Y", "above_1Y", "risk_high", 
                "risk_medium", "risk_low", "income_below_25K", "income_25K_to_50K",
                "income_50K_to_1L", "income_above_1L", "salaried", "business",
                "lending_roi_15_18", "lending_roi_18_24", "lending_roi_24_30",
                "lending_roi_30_40", "lending_roi_40_60"
            FROM t_preference_master
            WHERE id = %(preference_id)s
        """

        params = {
            'preference_id': preference_id
        }

        return self.execute_fetch_one(query, params)

    def get_scheme_preference_by_investment_id(self, investor_scheme_id):
        """
        Get scheme preference details by investor scheme ID

        Args:
            investor_scheme_id: Investor scheme identifier

        Returns:
            Scheme preference data dictionary or None
        """
        sql = """
            SELECT 
                preference_id,
                reinvest,
                min_lending_roi,
                max_lending_roi,
                loan_tenure
            FROM t_scheme_preference
            WHERE investor_scheme_id = %(investor_scheme_id)s
              AND deleted IS NULL
            LIMIT 1
        """

        params = {'investor_scheme_id': investor_scheme_id}
        return self.execute_fetch_one(sql, params)

    def get_preference_data_by_id(self, preference_id):
        """
        Get preference master data by preference ID

        Args:
            preference_id: Preference identifier

        Returns:
            Preference data with borrower_percent and expected_returns
        """
        sql = """
            SELECT 
                *
            FROM t_preference_master
            WHERE id = %(preference_id)s
              AND deleted IS NULL
        """

        params = {'preference_id': preference_id}
        return self.execute_fetch_one(sql, params)

    def get_true_columns_from_preference(self, preference_id):
        """
        Execute database function to get true columns for a preference

        Args:
            preference_id: Preference identifier

        Returns:
            Result from get_true_columns function
        """
        sql = "SELECT get_true_columns(%(preference_id)s) as result"
        params = {'preference_id': preference_id}

        result = self.execute_fetch_one(sql, params)
        return result['result'] if result else None

    def find_preference_by_columns(self, true_columns, false_columns):
        """
        Find preference by matching true and false columns.
        Pure data layer - only executes the SQL query.

        Args:
            true_columns: List of column names that should be true
            false_columns: List of column names that should be false

        Returns:
            Tuple of (id, borrower_percent, expected_returns) or None
        """
        # Build WHERE clause for true columns
        params = " and ".join(f'"{w}"' for w in true_columns)

        # Add false columns to WHERE clause
        if false_columns:
            if params:
                params = params + " and not "
            params = params + " and not ".join(f'"{w}"' for w in false_columns)

        # Add deleted check
        params = params + " and deleted is null"

        sql = f"""
            SELECT id, borrower_percent, expected_returns 
            FROM t_preference_master 
            WHERE {params}
        """

        result = self.execute_fetch_one(sql, {})

        if result:
            return result['id'], result['borrower_percent'], result['expected_returns']
        return None
