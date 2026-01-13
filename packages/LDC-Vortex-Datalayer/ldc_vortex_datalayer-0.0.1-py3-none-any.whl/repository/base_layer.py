"""
Base Data Layer for handling all database operations with connection management.
This class provides a centralized way to handle database operations with proper error handling
and connection management.
"""

import logging
import time
from abc import ABC
from typing import Optional

from django.db import connections
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)

# PostgreSQL error codes
# Reference: https://www.postgresql.org/docs/current/errcodes-appendix.html
PG_UNIQUE_VIOLATION = '23505'  # unique_violation
PG_FOREIGN_KEY_VIOLATION = '23503'  # foreign_key_violation
PG_NOT_NULL_VIOLATION = '23502'  # not_null_violation


class DataLayerError(Exception):
    """Base exception class for all data layer errors."""

    def __init__(self, message, error_code=None, db_alias=None):
        super().__init__(message)
        self.error_code = error_code
        self.db_alias = db_alias
        self.timestamp = time.time()


class DbConnectionError(DataLayerError):
    """Raised when database connection fails."""

    def __init__(self, message, db_alias=None):
        super().__init__(message, error_code="DB_CONNECTION_ERROR", db_alias=db_alias)


class QueryError(DataLayerError):
    """Raised when query execution fails."""

    def __init__(self, message, sql=None, db_alias=None):
        super().__init__(message, error_code="DB_QUERY_ERROR", db_alias=db_alias)
        self.sql = sql


class ValidationError(DataLayerError):
    """Raised when data validation fails."""

    def __init__(self, message, field_name=None, invalid_value=None):
        super().__init__(message, error_code="DB_VALIDATION_ERROR")
        self.field_name = field_name
        self.invalid_value = invalid_value


class TransactionError(DataLayerError):
    """Raised when transaction operations fail."""

    def __init__(self, message, db_alias=None, operation_count=None):
        super().__init__(message, error_code="DB_TRANSACTION_ERROR", db_alias=db_alias)
        self.operation_count = operation_count


class UniqueConstraintError(DataLayerError):
    """Raised when unique constraint violation occurs."""

    def __init__(self, message, constraint_name=None, db_alias=None):
        super().__init__(message, error_code="DB_UNIQUE_CONSTRAINT_ERROR", db_alias=db_alias)
        self.constraint_name = constraint_name


class BaseDataLayer(ABC):

    def __init__(self, db_alias="default"):
        self.db_alias = db_alias
        if db_alias not in connections.databases:
            raise DbConnectionError(f"Database alias '{db_alias}' not found in settings", db_alias=db_alias)

    def execute_query(
        self,
        sql,
        params=None,
        fetch_one=False,
        fetch_all=False,
        fetch_single_column=False, #index_result/ sql_execute_fetch_single_col_all  in old architecture
        to_dict=True,
        return_row_count=False
    ):
        """
        Execute a SQL query with various fetch options.

        Args:
            sql: SQL query string
            params: Query parameters
            fetch_one: Whether to fetch one row
            fetch_all: Whether to fetch all rows
            fetch_single_column: Whether to fetch single column values
            to_dict: Whether to return results as dictionaries
            return_row_count: Whether to return row count instead of data

        Returns:
            Query results based on fetch options
        """
        try:
            with connections[self.db_alias].cursor() as cursor:
                cursor.execute(sql, params or [])

                if return_row_count:
                    return cursor.rowcount

                if fetch_one:
                    result = cursor.fetchone()
                    if result and to_dict :
                        return self._row_to_dict(cursor, result)
                    elif result and fetch_single_column:
                        return result[0]
                    return result

                if fetch_all:
                    if to_dict:
                        return self._rows_to_dict(cursor)
                    elif fetch_single_column:
                        return [row[0] for row in cursor.fetchall()]
                    return cursor.fetchall()

                return None
        except Exception as e:
            logger.error(f"Failed to execute query on database alias '{self.db_alias}': {str(e)}")
            raise QueryError(f"Failed to execute query: {str(e)}", sql=sql, db_alias=self.db_alias) from e

    def execute_fetch_one(
        self,
        sql,
        params=None,
        to_dict=True,
        index_result=False
    ):
        """
        Execute query and fetch one result.

        Args:
            sql: SQL query string
            params: Query parameters
            to_dict: Whether to return as dictionary
            index_result: Whether to return first column only

        Returns:
            Single row result
        """
        return self.execute_query(
            sql=sql,
            params=params,
            fetch_one=True,
            to_dict=to_dict and not index_result
        )

    def execute_fetch_all(
        self,
        sql,
        params=None,
        to_dict=True
    ):
        """
        Execute query and fetch all results.

        Args:
            sql: SQL query string
            params: Query parameters
            to_dict: Whether to return as list of dictionaries

        Returns:
            List of rows
        """
        return self.execute_query(
            sql=sql,
            params=params,
            fetch_all=True,
            to_dict=to_dict
        )

    def execute_fetch_single_column(
        self,
        sql,
        params=None
    ):
        """
        Execute query and fetch single column values.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of single column values
        """
        return self.execute_query(
            sql=sql,
            params=params,
            fetch_all=True,
            fetch_single_column=True,
            to_dict=False
        )

    def execute_no_return(
        self,
        sql,
        params=None
    ):
        """
        Execute query without returning results.

        Args:
            sql: SQL query string
            params: Query parameters
        """
        self.execute_query(sql=sql, params=params)

    def execute_update(
        self,
        sql,
        params=None
    ):
        """
        Execute UPDATE, INSERT, or DELETE statement and return affected row count.
        
        This is a convenience method for data modification operations (INSERT, UPDATE, DELETE)
        that need to know how many rows were affected. It's semantically clearer than
        using execute_query with return_row_count=True.

        Args:
            sql: SQL query string (INSERT, UPDATE, or DELETE statement)
            params: Query parameters

        Returns:
            int: Number of affected rows
        """
        return self.execute_query(sql=sql, params=params, return_row_count=True)

    def execute_insert(
        self,
        sql,
        params=None
    ):
        """
        Execute INSERT statement and return affected row count.
        
        This is a convenience method specifically for INSERT operations that don't use
        RETURNING clause. For INSERT statements with RETURNING clause, use execute_fetch_one
        instead to get the returned values.
        
        This method is semantically clearer than using execute_query with return_row_count=True
        for INSERT operations.

        Args:
            sql: SQL INSERT statement (without RETURNING clause)
            params: Query parameters

        Returns:
            int: Number of affected rows
        """
        return self.execute_query(sql=sql, params=params, return_row_count=True)

    def execute_bulk_update(
        self,
        sql,
        values,
        return_row_count=True
    ):
        """
        Execute bulk update operation.

        Args:
            sql: SQL query string
            values: List of parameter sets for bulk operation
            return_row_count: Whether to return affected row count

        Returns:
            Number of affected rows
        """
        try:
            with connections[self.db_alias].cursor() as cursor:
                cursor.executemany(sql, values)
                return cursor.rowcount if return_row_count else None
        except Exception as e:
            logger.error(f"Failed to execute bulk update on database alias '{self.db_alias}': {str(e)}")
            raise QueryError(f"Failed to execute bulk update: {str(e)}", sql=sql, db_alias=self.db_alias) from e

    def _execute_bulk_insert(
        self,
        table_name,
        data_list
    ):
        """
        A private helper to construct and execute a bulk INSERT statement.
        This should only be called by other methods within the data layer.
        """
        # All dictionaries in data_list must have the same keys
        columns = ", ".join(data_list[0].keys())

        # Using %(key)s syntax for clarity with dictionaries
        placeholders = ", ".join([f"%({key})s" for key in data_list[0].keys()])

        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            with connections[self.db_alias].cursor() as cursor:
                cursor.executemany(sql, data_list)
                return cursor.rowcount
        except Exception as e:
            logger.error(
                f"Failed to execute bulk insert on database alias "
                f"{self.db_alias}: {str(e)}"
            )
            raise QueryError(
                f"Failed to execute bulk insert: {str(e)}",
                sql=sql,
                db_alias=self.db_alias
            ) from e


    @staticmethod
    def _row_to_dict(cursor, row):
        """
        Convert a database row to dictionary.

        Args:
            cursor: Database cursor
            row: Database row tuple

        Returns:
            Dictionary representation of the row
        """
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    @staticmethod
    def _rows_to_dict(cursor):
        """
        Convert database rows to list of dictionaries.

        Args:
            cursor: Database cursor

        Returns:
            List of dictionary representations of rows
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute_procedure(
        self,
        procedure_name,
        params=None,
        fetch_one=True,
        to_dict=True,
        fetch_single_column=False
    ):
        """
        Execute a stored procedure with parameters.

        Args:
            procedure_name: Name of the stored procedure
            params: List of parameters to pass to the procedure
            fetch_one: Whether to fetch one row (default True)
            to_dict: Whether to return results as dictionaries (default True)
            fetch_single_column: Whether to fetch single column values (default False)

        Returns:
            Query results based on fetch options
        """
        try:
            with connections[self.db_alias].cursor() as cursor:
                # Build the CALL statement
                param_placeholders = ", ".join(["%s" for _ in range(len(params or []))])
                sql = f"CALL {procedure_name}({param_placeholders})"

                cursor.execute("BEGIN")
                cursor.execute(sql, params or [])

                # Fetch results if any
                if fetch_one:
                    result = cursor.fetchone()
                    cursor.execute("COMMIT")

                    if result:
                        if fetch_single_column:
                            return result[0]
                        if to_dict and cursor.description:  # Only convert to dict if we have column info
                            return self._row_to_dict(cursor, result)
                    return result

                if not fetch_one:
                    results = cursor.fetchall()
                    cursor.execute("COMMIT")

                    if results:
                        if fetch_single_column:
                            return [row[0] for row in results]
                        if to_dict and cursor.description:  # Only convert to dict if we have column info
                            return self._rows_to_dict(cursor)
                    return results

                cursor.execute("COMMIT")
                return None

        except Exception as e:
            logger.error(f"Failed to execute procedure {procedure_name} on database alias '{self.db_alias}': {str(e)}")
            raise QueryError(
                f"Failed to execute procedure: {str(e)}",
                sql=f"CALL {procedure_name}",
                db_alias=self.db_alias
            ) from e

    @staticmethod
    def is_unique_constraint_error(exception: Exception) -> bool:
        """
        Check if an exception is a unique constraint violation.
        
        Args:
            exception: The exception to check
            
        Returns:
            True if it's a unique constraint violation, False otherwise
        """
        # Check for Django's IntegrityError
        if isinstance(exception, IntegrityError):
            # Get PostgreSQL error code from the exception
            # Django wraps psycopg2 errors, error code is in pgcode attribute
            if hasattr(exception, 'pgcode') and exception.pgcode == PG_UNIQUE_VIOLATION:
                return True
            # Also check the exception message as fallback
            error_msg = str(exception).lower()
            if 'unique constraint' in error_msg or 'duplicate key' in error_msg:
                return True
        
        # Check for psycopg2 errors directly (if not wrapped by Django)
        if hasattr(exception, 'pgcode') and exception.pgcode == PG_UNIQUE_VIOLATION:
            return True
        
        # Fallback: check error message
        error_msg = str(exception).lower()
        return 'unique constraint' in error_msg or 'duplicate key' in error_msg

    @staticmethod
    def get_constraint_name(exception: Exception) -> Optional[str]:
        """
        Extract constraint name from unique constraint violation exception.
        
        Args:
            exception: The exception to extract constraint name from
            
        Returns:
            Constraint name if found, None otherwise
        """
        error_msg = str(exception)
        
        # Try to extract constraint name from error message
        # PostgreSQL format: "duplicate key value violates unique constraint \"constraint_name\""
        if 'constraint "' in error_msg:
            start = error_msg.find('constraint "') + len('constraint "')
            end = error_msg.find('"', start)
            if end > start:
                return error_msg[start:end]
        
        return None

