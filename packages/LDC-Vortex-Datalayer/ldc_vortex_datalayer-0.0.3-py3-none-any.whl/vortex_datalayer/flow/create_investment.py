import json

from ..base_layer import BaseDataLayer


class CreateInvestment(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """
    def create_scheme(self, lending_data):
        """
        Creates a new scheme using the stored procedure.
        Args:
            lending_data (dict): Data required for scheme creation
        Returns:
            str: Raw result from the stored procedure, either '-1' for failure
                 or a JSON string containing scheme details
        """
        jsonb_data = json.dumps(lending_data)

        # Execute the procedure and return raw result
        return self.execute_procedure(
            procedure_name="prc_create_scheme_wrapper",
            params=[jsonb_data],
            fetch_one=True,
            fetch_single_column=True
        )
