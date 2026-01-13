"""
Mapper functions for fetching data in jobs.
Contains SQL queries and data fetching logic for various job operations.
"""

from ..base_layer import BaseDataLayer
from ..entity.mst_parameter import MstParameter
from ..constants import IdleFundWithdrawalBlockedDates, JobProcessIdleFund


def _build_banking_condition(created_date_column='lwt.created_dtm', created_datetime_column='lwt.created_dtm'):
    """
    Build the banking condition SQL for idle fund withdrawal.
    
    Args:
        created_date_column: Column name for created date
        created_datetime_column: Column name for created datetime
        
    Returns:
        str: SQL condition string
    """
    working_days_count = f"""
            (
                SELECT COUNT(*)
                FROM generate_series(
                    {created_date_column} + INTERVAL '1 day',
                    (now() AT TIME ZONE 'Asia/Kolkata')::date - INTERVAL '1 day',
                    INTERVAL '1 day'
                ) AS day_series
                WHERE day_series::date <> ALL(%(holiday_dates)s::date[])
            )
        """

    return f"""
            (
                -- Check if transaction date is a holiday
                CASE 
                    WHEN {created_date_column} = ANY(%(holiday_dates)s::date[]) THEN
                        -- Holiday: always require at least 1 working day
                        {working_days_count} >= 1
                    ELSE
                        -- Regular day: check transaction time
                        CASE 
                            WHEN ({created_datetime_column})::time <= '15:30:00'::time THEN
                                -- Before 3:30 PM: processed next working day
                                {created_datetime_column} <= ((now() AT TIME ZONE 'Asia/Kolkata')::date - INTERVAL '1 day' + INTERVAL '15 hours 30 minutes')
                            ELSE
                                -- After 3:30 PM: processed after 1 working day
                                {working_days_count} >= 1
                        END
                END
            )
        """


def get_idle_txns(usg_id_list=None):
    """
    Fetch idle fund transactions from t_lender_wallet_tracker.
    
    Args:
        usg_id_list: Optional list of user_source_group_ids to filter
        
    Returns:
        list: List of dictionaries containing lender_id, total_balance, and track_txn_ids
    """
    # Build banking condition with proper table aliases
    banking_condition = _build_banking_condition(
        created_date_column='lwt.created_dtm',
        created_datetime_column='lwt.created_dtm'
    )
    
    # Build SQL query
    # Note: Using remaining_amount as balance, and joining with t_lender to get user_source_group_id
    sql = """
        SELECT
            lwt.lender_id,
            SUM(lwt.remaining_amount) AS total_balance,
            ARRAY_AGG(lwt.id) AS track_txn_ids,
            tl.user_source_group_id
        FROM
            t_lender_wallet_tracker lwt
        INNER JOIN t_lender tl ON lwt.lender_id = tl.id
        WHERE
            lwt.remaining_amount >= %(balance)s 
            AND tl.user_source_group_id <> ALL(%(block_investment_acc)s) 
            AND lwt.expiry_dtm::date <= (now() AT TIME ZONE 'Asia/Kolkata')::date
            AND lwt.deleted IS NULL
            AND tl.deleted IS NULL
            AND {banking_condition}
    """.format(banking_condition=banking_condition)
    
    params = {
        'balance': JobProcessIdleFund.MIN_WITHDRAWAL_AMOUNT,
        'block_investment_acc': JobProcessIdleFund.BLOCK_INVESTMENT_ACCOUNT,
        'holiday_dates': IdleFundWithdrawalBlockedDates.BLOCKED_DATES
    }
    
    if usg_id_list:
        sql += " AND tl.user_source_group_id = ANY(%(user_source_group_id)s)"
        params['user_source_group_id'] = usg_id_list
    
    sql += " GROUP BY lwt.lender_id, tl.user_source_group_id"
    
    # Execute query using BaseDataLayer
    base_layer = BaseDataLayer()
    results = base_layer.execute_fetch_all(sql, params, to_dict=True)
    
    # Convert track_txn_ids from list to list format if needed
    for result in results:
        if isinstance(result.get('track_txn_ids'), list):
            result['track_txn_ids'] = result['track_txn_ids']
        else:
            result['track_txn_ids'] = [result['track_txn_ids']] if result.get('track_txn_ids') else []
    
    return results


def get_pending_investment_orders(usg_id_list=None):
    """
    Fetch pending investment orders that meet banking conditions for refund processing.
    
    Args:
        usg_id_list: Optional list of user_source_group_ids to filter
        
    Returns:
        list: List of dictionaries containing investment order data
    """
    banking_condition = _build_banking_condition(
        created_date_column='tlio.created_dtm',
        created_datetime_column='tlio.created_dtm'
    )
    
    sql = """
        SELECT 
            tlio.investment_id, 
            tlio.created_dtm, 
            tlio.created_dtm::date as created_date, 
            tlio.product_config_id,
            tipc.investment_type_id, 
            tlio.amount_lent, 
            tlio.transaction_id, 
            tl.user_source_group_id,
            tl.partner_code_id,
            tipc.tenure,
            tipc.investment_type
        FROM t_lender_investment_order tlio
        JOIN t_lender tl ON tl.id = tlio.lender_id
        JOIN t_investment_product_config tipc ON tipc.id = tlio.product_config_id
        WHERE tlio.status = 'PENDING'
        AND tl.deleted IS NULL
        AND tlio.deleted IS null;
        AND {banking_condition}
    """.format(banking_condition=banking_condition)
    
    params = {
        'holiday_dates': IdleFundWithdrawalBlockedDates.BLOCKED_DATES
    }
    
    if usg_id_list:
        sql += " AND tl.user_source_group_id = ANY(%(user_source_group_id)s)"
        params['user_source_group_id'] = usg_id_list
    
    # Execute query using BaseDataLayer
    base_layer = BaseDataLayer()
    results = base_layer.execute_fetch_all(sql, params, to_dict=True)
    
    return results


def get_updated_account_balances(usg_id_list=None):
    """
    Fetch account balances that got updated, filtered by partner codes.
    Only includes lenders with partner_code_id matching:
    LENDER CHANNEL PARTNER, MASTER CHANNEL PARTNER, CC, PTSO
    
    Args:
        usg_id_list: Optional list of user_source_group_ids to filter
        
    Returns:
        list: List of dictionaries containing user_source_group_id and balance
    """
    # Get partner code IDs from mst_parameter
    mst_parameter = MstParameter()
    partner_codes = ['LENDER CHANNEL PARTNER', 'MASTER CHANNEL PARTNER', 'CC', 'PTSO']
    partner_code_ids = mst_parameter.get_bulk_partner_code_id(partner_codes)
    
    if not partner_code_ids:
        return []
    
    sql = """
        SELECT
            tl.user_source_group_id,
            ta.balance
        FROM
            t_account ta
        INNER JOIN t_lender tl ON ta.lender_id = tl.id
        WHERE
            tl.partner_code_id = ANY(%(partner_code_ids)s)
            AND ta.deleted IS NULL
            AND tl.deleted IS NULL
            AND ta.updated_dtm IS NOT NULL
    """
    
    params = {
        'partner_code_ids': partner_code_ids
    }
    
    if usg_id_list:
        sql += " AND tl.user_source_group_id = ANY(%(user_source_group_id)s)"
        params['user_source_group_id'] = usg_id_list
    
    # Execute query using BaseDataLayer
    base_layer = BaseDataLayer()
    results = base_layer.execute_fetch_all(sql, params, to_dict=True)
    
    return results


def get_scheduled_wallet_transactions():
    """
    Fetch scheduled wallet transactions without locking.
    Joins with t_lender to get user_source_group_id.
    
    Returns:
        list: List of dictionaries containing:
            - id: Transaction ID
            - amount: Transaction amount
            - transaction_type: Type of transaction
            - transaction_id: Unique transaction identifier
            - user_source_group_id: User source group ID from t_lender
    """
    sql = """
        SELECT 
            txn.id,
            txn.amount,
            txn.transaction_type,
            txn.transaction_id,
            tl.user_source_group_id
        FROM t_lender_wallet_transaction txn
        INNER JOIN t_lender tl ON tl.id = txn.lender_id
        WHERE txn.status = 'SCHEDULED'
        AND txn.deleted IS NULL
    """
    
    params = {}
    
    # Execute query using BaseDataLayer
    base_layer = BaseDataLayer()
    results = base_layer.execute_fetch_all(sql, params, to_dict=True)
    
    return results or []

