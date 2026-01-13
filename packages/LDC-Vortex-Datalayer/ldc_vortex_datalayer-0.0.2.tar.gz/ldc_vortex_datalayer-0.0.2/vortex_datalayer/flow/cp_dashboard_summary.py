"""
CP Dashboard Summary Flow Layer

This flow layer contains all CP dashboard-specific data layer methods.
All methods use JOINs with t_channel_partner_mapping_table and apply filter_type
conditions directly in WHERE clauses to avoid performance issues with large lender lists.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import date, timedelta
from ..base_layer import BaseDataLayer
from ..entity.investment_product_config import InvestmentProductConfig
from ..helper.master_account_helper import get_master_account_type_id
from ..constants import (
    InvestmentType,
    TransactionType,
    RedemptionType,
    FilterKey,
    AccountType,
    LendingInvestmentStatus,
    InvestorActivityType,
    PartnerCode,
    CpFilterType,
    MonthNames
)
from ..helper.date_utils import convert_ist_date_to_utc_start_of_day, convert_ist_date_to_utc_end_of_day

logger = logging.getLogger(__name__)


class CpDashboardSummaryFlow(BaseDataLayer):
    """
    Flow layer for CP dashboard summary queries.
    All methods use JOINs with filter_type conditions in WHERE clauses.
    """
    
    def __init__(self, db_alias: str = "default"):
        super().__init__(db_alias)
        self.product_config_entity = InvestmentProductConfig(db_alias=db_alias)
    
    def _build_cp_filter_join(
        self, 
        filter_type: str, 
        partner_id: str, 
        source: str, 
        cp_user_id: Optional[str],
        alias_prefix: str = 'cpm'
    ) -> Tuple[str, str, Dict[str, Any]]:
       
        join_sql = f"""
            JOIN t_channel_partner_mapping_table {alias_prefix}
                ON tl.partner_mapping_id = {alias_prefix}.id
                AND {alias_prefix}.deleted IS NULL
        """
        
        where_conditions = []
        params = {}
        
        if source == PartnerCode.MCP:
            if filter_type == CpFilterType.ALL:
                # MCP: all (own + CP lenders)
                where_conditions.append(
                    f"({alias_prefix}.master_partner_id = %(partner_id)s "
                    f"OR {alias_prefix}.channel_partner_id = %(partner_id)s)"
                )

            elif filter_type == CpFilterType.SELF:
                # MCP: self (own lenders only)
                where_conditions.append(
                    f"{alias_prefix}.master_partner_id = %(partner_id)s "
                    f"AND {alias_prefix}.channel_partner_id IS NULL"
                )

            elif filter_type == CpFilterType.ALL_CP:
                # MCP: all_cp (CP lenders only)
                where_conditions.append(
                    f"{alias_prefix}.master_partner_id = %(partner_id)s "
                    f"AND {alias_prefix}.channel_partner_id IS NOT NULL"
                )

            elif filter_type == CpFilterType.CP_USER_ID:
                # MCP: cp_user_id (specific CP lenders)
                if not cp_user_id:
                    raise ValueError("cp_user_id is required when filter_type='cp_user_id'")
                where_conditions.append(
                    f"{alias_prefix}.channel_partner_id = %(cp_user_id)s "
                    f"AND {alias_prefix}.master_partner_id = %(partner_id)s"
                )
                params['cp_user_id'] = cp_user_id

            else:
                raise ValueError(f"Invalid filter_type '{filter_type}' for source '{source}'")
        elif source == PartnerCode.LCP:
            if filter_type in [CpFilterType.ALL, CpFilterType.SELF]:
                # LCP: all/self (own lenders only)
                where_conditions.append(f"{alias_prefix}.channel_partner_id = %(partner_id)s")
            elif filter_type in [CpFilterType.ALL_CP, CpFilterType.CP_USER_ID]:
                # LCP: all_cp/cp_user_id (not applicable - return empty)
                where_conditions.append("1 = 0")  # Always false condition
            else:
                raise ValueError(f"Invalid filter_type '{filter_type}' for source '{source}'")
        else:
            raise ValueError(f"Invalid source '{source}'")
        
        params['partner_id'] = partner_id
        where_sql = " AND " + " AND ".join(where_conditions)
        
        return join_sql, where_sql, params
    
    def _build_cp_join(
        self,
        partner_id: str,
        source: str,
        alias_prefix: str = 'cpm',
        fetch_all: bool = False
    ) -> Tuple[str, str, Dict[str, Any]]:

        join_sql = f"""JOIN t_channel_partner_mapping_table {alias_prefix}
         ON tl.partner_mapping_id = {alias_prefix}.id 
         AND {alias_prefix}.deleted IS NULL"""

        where_conditions = []
        params = {}

        if source == PartnerCode.MCP:
            if fetch_all:
                # MCP: Get all lenders (own + CP lenders)
                where_conditions.append(
                    f"({alias_prefix}.master_partner_id = %(partner_id)s "
                    f"OR {alias_prefix}.channel_partner_id IS NOT NULL)"
                )

            else:
                # MCP: Get own lenders only
                where_conditions.append(
                    f"({alias_prefix}.master_partner_id = %(partner_id)s "
                    f"AND {alias_prefix}.channel_partner_id IS NULL)"
                )

        elif source == PartnerCode.LCP:
            # LCP: Get own lenders
            where_conditions.append(f"{alias_prefix}.channel_partner_id = %(partner_id)s")
        else:
            raise ValueError(f"Invalid source '{source}'")

        params['partner_id'] = partner_id
        where_sql = " AND " + " AND ".join(where_conditions)

        return join_sql, where_sql, params

    def _build_date_filter(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        date_alias_prefix: str,
        date_column: str = 'created_dtm'
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build date filter for SQL queries with UTC conversion.
        
        Converts IST dates to UTC datetime for accurate filtering.
        """
        date_filter = ""
        params = {}

        full_date_column = f"{date_alias_prefix}.{date_column}"

        # Convert dates to UTC
        from_date_utc = convert_ist_date_to_utc_start_of_day(from_date)
        to_date_utc = convert_ist_date_to_utc_end_of_day(to_date)

        if from_date_utc and to_date_utc:
            date_filter = f"AND {full_date_column} BETWEEN %(from_date)s AND %(to_date)s"
            params['from_date'] = from_date_utc
            params['to_date'] = to_date_utc
        elif from_date_utc:
            date_filter = f"AND {full_date_column} >= %(from_date)s"
            params['from_date'] = from_date_utc
        elif to_date_utc:
            date_filter = f"AND {full_date_column} <= %(to_date)s"
            params['to_date'] = to_date_utc

        return date_filter, params

    def fetch_aum_metrics(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute AUM summary query grouped by product type.
        
        Returns:
            Query result or None
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        sql = f"""
            SELECT
                COALESCE(SUM(CASE WHEN tipc.investment_type = 'MANUAL_LENDING' THEN tilrs.principal_outstanding ELSE 0 END), 0) as manual_lending,
                COALESCE(SUM(CASE WHEN tipc.investment_type = 'ONE_TIME_LENDING' THEN tilrs.principal_outstanding ELSE 0 END), 0) as one_time_lending,
                COALESCE(SUM(CASE WHEN tipc.investment_type = 'MEDIUM_TERM_LENDING' THEN tilrs.principal_outstanding ELSE 0 END), 0) as medium_term_lending
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
            JOIN t_investment_product_config tipc ON tli.product_config_id = tipc.id
                AND tipc.deleted IS NULL
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                AND tild.deleted IS NULL
            JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                AND tilrs.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
        """
        
        return self.execute_fetch_one(sql, params)

    def get_aum_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get AUM summary grouped by product type.
        
        Returns:
            Dict with total_aum, manual_lending, one_time_lending, medium_term_lending
        """
        result = self.fetch_aum_metrics(
            filter_type, partner_id, source, cp_user_id
        )
        
        if not result:
            return {
                'total_aum': 0.0,
                'manual_lending': 0.0,
                'one_time_lending': 0.0,
                'medium_term_lending': 0.0
            }
        
        total_aum = (
            (result.get('manual_lending') or 0) +
            (result.get('one_time_lending') or 0) +
            (result.get('medium_term_lending') or 0)
        )
        
        return {
            'total_aum': float(total_aum),
            'manual_lending': float(result.get('manual_lending') or 0),
            'one_time_lending': float(result.get('one_time_lending') or 0),
            'medium_term_lending': float(result.get('medium_term_lending') or 0)
        }
    
    def fetch_aum_lender_records(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        product_config_ids: List[int],
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'tcpmt'
        )
        
        params['account_type_id'] = account_type_id
        
        product_filter = ""
        if product_config_ids:
            product_filter = "AND tli.product_config_id = ANY(%(product_config_ids)s)"
            params['product_config_ids'] = product_config_ids
        else:
            product_filter = "AND tli.product_config_id IS NOT NULL"

        # Date filter
        date_filter, date_params = self._build_date_filter(from_date, to_date, 'tli', 'created_dtm')
        params.update(date_params)

        sql = f"""
            SELECT 
                tl.user_id as user_id,
                tipc.investment_type as scheme_type,
                tli.investment_id as scheme_id,
                0 as expected_return,
                tli.created_dtm::date as scheme_creation_date,
                tli.expected_closure_date as scheme_maturity_date,
                tipc.tenure as tenure,
                ROUND(SUM(tilrs.total_principal_received), 2) as principal_received,
                ROUND(SUM(tilrs.total_interest_received), 2) as interest_received,
                ROUND(SUM(tilrs.total_npa_amount), 2) as total_npa_amount,
                ROUND(SUM(tilrs.total_fee_levied), 2) as total_fee,
                COALESCE(tli.actual_principal_lent, tli.amount_lent_on_investment) as scheme_amount,
                ROUND(SUM(tilrs.principal_outstanding), 2) as pos,
                COALESCE(tli.total_amount_redeemed, 0) as sum_of_credit_in_bank,
                0 as xirr,
                tl.partner_id as partner_id,
                ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
            FROM t_lender_investment tli
            JOIN t_lender tl ON tl.id = tli.lender_id
                AND tl.deleted IS NULL
            {join_sql}
            JOIN t_account ta ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            JOIN t_investment_product_config tipc ON tipc.id = tli.product_config_id
                AND tipc.deleted IS NULL
                {product_filter}
            JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                AND tild.deleted IS NULL
            JOIN t_investment_loan_repayment_summary tilrs ON tilrs.investment_loan_id = tild.id
                AND tilrs.deleted IS NULL
            WHERE tli.deleted IS NULL
                AND tli.actual_closure_date IS NULL
                {date_filter}
            {where_sql}
            GROUP BY 
                tl.user_id,
                tipc.investment_type,
                tli.investment_id,
                tli.created_dtm,
                tli.expected_closure_date,
                tipc.tenure,
                tli.actual_principal_lent,
                tli.amount_lent_on_investment,
                tli.total_amount_redeemed,
                tl.partner_id,
                ta.balance
            ORDER BY tl.user_id, tli.investment_id
        """
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_aum_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        product_config_ids: List[int],
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        
        # Get LENDER_WALLET account_type_id
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return []
        
        account_type_id = master_account.get('id')

        return self.fetch_aum_lender_records(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, product_config_ids, from_date, to_date,
            limit, offset, download
        )
    
    def fetch_monthly_investment_totals(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        from_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get monthly investment summary for the specified period.
        
        Returns:
            List of investment amounts grouped by month
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['from_date'] = from_date
        
        sql = f"""
            SELECT
                DATE_TRUNC('month', tli.created_dtm)::date as month_date,
                COALESCE(SUM(tli.actual_principal_lent), 0) as investment_amount
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
                AND tli.created_dtm >= %(from_date)s
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY DATE_TRUNC('month', tli.created_dtm)::date
        """
        
        results = self.execute_fetch_all(sql, params)
        return results or []

    def fetch_monthly_withdrawal_totals(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        from_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get monthly withdrawal summary for the specified period.
        
        Returns:
            List of withdrawal amounts grouped by month
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['withdraw_transaction_type'] = TransactionType.WITHDRAW_MONEY
        params['success_status'] = 'SUCCESS'
        params['from_date'] = from_date
        
        sql = f"""
            SELECT
                DATE_TRUNC('month', tlwt.created_dtm)::date as month_date,
                COALESCE(SUM(tlwt.amount), 0) as total_withdraw_money
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_wallet_transaction tlwt ON tl.id = tlwt.lender_id
                AND tlwt.deleted IS NULL
                AND tlwt.transaction_type = %(withdraw_transaction_type)s
                AND tlwt.status = %(success_status)s
                AND tlwt.created_dtm >= %(from_date)s
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY DATE_TRUNC('month', tlwt.created_dtm)::date
        """
        
        results = self.execute_fetch_all(sql, params)
        return results or []

    def get_monthly_business_trends_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get monthly business trends summary for last 3 months.
        
        Returns:
            Dict with investment_results, withdrawal_results, and today
        """
        today = date.today()
        three_months_ago = today - timedelta(days=90)
        
        investment_results = self.fetch_monthly_investment_totals(
            filter_type, partner_id, source, cp_user_id, three_months_ago
        )
        
        withdrawal_results = self.fetch_monthly_withdrawal_totals(
            filter_type, partner_id, source, cp_user_id, three_months_ago
        )
        
        return {
            'investment_results': investment_results,
            'withdrawal_results': withdrawal_results,
            'today': today
        }
    
    def fetch_business_trends_data(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        filter_key: str,
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
       
        if from_date is None or to_date is None:
            to_date = date.today()
            from_date = to_date - timedelta(days=90)

        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['account_type_id'] = account_type_id
        
        if filter_key == FilterKey.FMPP_INVESTMENT:
            # Build date filter for t_lender_investment table
            date_filter, date_params = self._build_date_filter(from_date, to_date, 'tli')
            params.update(date_params)

            # Query for FMPP Investments
            sql = f"""
                SELECT
                    tl.user_id as lender_user_id,
                    tl.user_source_group_id as lender_user_source_id,
                    tipc.investment_type as scheme_type,
                    tli.investment_id as scheme_id,
                    0 as expected_return,
                    tli.created_dtm::date as scheme_creation_date,
                    tli.expected_closure_date as scheme_maturity_date,
                    tipc.tenure as tenure,
                    ROUND(SUM(tilrs.total_principal_received), 2) as principal_received,
                    ROUND(SUM(tilrs.total_interest_received), 2) as interest_received,
                    ROUND(SUM(tilrs.total_npa_amount), 2) as total_npa_amount,
                    ROUND(SUM(tilrs.total_fee_levied), 2) as total_fee,
                    COALESCE(tli.actual_principal_lent, tli.amount_lent_on_investment) as scheme_amount,
                    ROUND(SUM(tilrs.principal_outstanding), 2) as pos,
                    COALESCE(tli.total_amount_redeemed, 0) as sum_of_credit_in_bank,
                    0 as xirr,
                    tl.partner_id as partner_id,
                    ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
                FROM t_lender_investment tli
                JOIN t_lender tl ON tl.id = tli.lender_id
                    AND tl.deleted IS NULL
                {join_sql}
                JOIN t_account ta ON tl.id = ta.lender_id
                    AND ta.account_type_id = %(account_type_id)s
                    AND ta.deleted IS NULL
                JOIN t_investment_product_config tipc ON tipc.id = tli.product_config_id
                    AND tipc.deleted IS NULL
                JOIN t_investment_loan_detail tild ON tild.investment_id = tli.id
                    AND tild.deleted IS NULL
                JOIN t_investment_loan_repayment_summary tilrs ON tilrs.investment_loan_id = tild.id
                    AND tilrs.deleted IS NULL
                WHERE tli.deleted IS NULL
                    AND tli.actual_closure_date IS NULL
                    {date_filter}
                {where_sql}
                GROUP BY 
                    tl.user_id,
                    tl.user_source_group_id,
                    tipc.investment_type,
                    tli.investment_id,
                    tli.created_dtm,
                    tli.expected_closure_date,
                    tipc.tenure,
                    tli.actual_principal_lent,
                    tli.amount_lent_on_investment,
                    tli.total_amount_redeemed,
                    tl.partner_id,
                    ta.balance
                ORDER BY tli.created_dtm DESC, tl.user_id
            """

        elif filter_key == FilterKey.WITHDRAW_MONEY:
            # Build date filter for t_lender_wallet_transaction table
            date_filter, date_params = self._build_date_filter(from_date, to_date, 'tlwt')
            params.update(date_params)
            
            # Query for Withdraw Money transactions
            params['withdraw_transaction_type'] = TransactionType.WITHDRAW_MONEY
            params['success_status'] = 'SUCCESS'
            
            sql = f"""
                SELECT
                    tl.user_id as lender_user_id,
                    tl.user_source_group_id as lender_user_source_id,
                    tlwt.transaction_id,
                    tlwt.amount as total_withdraw_money,
                    tlwt.created_dtm::date as transaction_date,
                    tlwt.status,
                    ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
                FROM t_lender tl
                {join_sql}
                JOIN t_account ta ON tl.id = ta.lender_id
                    AND ta.account_type_id = %(account_type_id)s
                    AND ta.deleted IS NULL
                JOIN t_lender_wallet_transaction tlwt ON tl.id = tlwt.lender_id
                    AND tlwt.deleted IS NULL
                    AND tlwt.transaction_type = %(withdraw_transaction_type)s
                    AND tlwt.status = %(success_status)s
                    {date_filter}
                WHERE tl.deleted IS NULL
                {where_sql}
                ORDER BY tlwt.created_dtm DESC, tl.user_id
            """
        else:
            raise ValueError(f"Invalid filter_key: {filter_key}. Must be 'FMPP_INVESTMENT' or 'WITHDRAW_MONEY'")
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_monthly_business_trends_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        filter_key: str,
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
       
        # Get LENDER_WALLET account_type_id
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return []
        
        account_type_id = master_account.get('id')

        return self.fetch_business_trends_data(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, filter_key, from_date, to_date,
            limit, offset, download
        )
    
    def fetch_unutilised_funds_total(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get unutilised funds summary.
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        sql = f"""
            SELECT COALESCE(SUM(ta.balance), 0) as unutilised_funds
            FROM t_lender tl
            {join_sql}
            JOIN t_account ta ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
        """
        
        params['account_type_id'] = account_type_id
        
        return self.execute_fetch_one(sql, params)

    def get_unutilised_funds_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get unutilised funds summary.
        """
        # Get LENDER_WALLET account_type_id
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return {'unutilised_funds': 0.0}
        
        account_type_id = master_account.get('id')
        
        result = self.fetch_unutilised_funds_total(
            filter_type, partner_id, source, cp_user_id, account_type_id
        )
        
        return {
            'unutilised_funds': float(result.get('unutilised_funds') or 0) if result else 0.0
        }
    
    def fetch_unutilised_funds_by_lender(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get unutilised funds details (lender-level breakdown).
        
        Args:
            download: If True, return all data without pagination
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        sql = f"""
            SELECT
                tl.user_source_group_id as lender_user_source_id,
                COALESCE(ta.balance, 0) as unutilised_funds
            FROM t_lender tl
            {join_sql}
            LEFT JOIN t_account ta ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
            AND ta.balance > 0
            ORDER BY tl.user_id
        """
        
        params['account_type_id'] = account_type_id
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_unutilised_funds_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get unutilised funds details (lender-level breakdown).
        
        Args:
            download: If True, return all data without pagination
        """
        # Get LENDER_WALLET account_id
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            return []
        
        account_type_id = master_account.get('id')
        
        return self.fetch_unutilised_funds_by_lender(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, limit, offset, download
        )
    
    def fetch_stl_open_investments_metrics(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        product_config_ids: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Get STL business summary for open investments (actual_closure_date IS NULL).
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['product_config_ids'] = product_config_ids
        
        sql = f"""
            SELECT
                COALESCE(SUM(tild.investment_amount), 0) as total_lending_amount,
                COALESCE(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 0) as interest_received,
                COALESCE(SUM(tilrs.total_principal_received), 0) as principal_received,
                COALESCE(SUM(tilrs.principal_outstanding), 0) as principal_outstanding,
                COALESCE(SUM(tilrs.total_fee_levied), 0) as total_fee_amount,
                COALESCE(SUM(tilrs.total_amount_received), 0) as total_repayment_amount,
                COALESCE(SUM(CASE WHEN tild.is_cancelled = TRUE THEN tild.investment_amount ELSE 0 END), 0) as loan_cancel_amount,
                COALESCE(SUM(tilrs.total_npa_amount), 0) as total_npa_amount
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
                AND tli.product_config_id = ANY(%(product_config_ids)s)
                AND tli.actual_closure_date IS NULL
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                AND tild.deleted IS NULL
            JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                AND tilrs.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
        """
        
        return self.execute_fetch_one(sql, params)

    def fetch_stl_closed_investments_metrics(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        product_config_ids: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Get STL business summary for closed investments (actual_closure_date IS NOT NULL).
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['product_config_ids'] = product_config_ids
        
        sql = f"""
            SELECT
                COALESCE(SUM(tild.investment_amount), 0) as total_lending_amount,
                COALESCE(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 0) as interest_received,
                COALESCE(SUM(tilrs.total_principal_received), 0) as principal_received,
                COALESCE(SUM(tilrs.principal_outstanding), 0) as principal_outstanding,
                COALESCE(SUM(tilrs.total_fee_levied), 0) as total_fee_amount,
                COALESCE(SUM(tilrs.total_amount_received), 0) as total_repayment_amount,
                COALESCE(SUM(CASE WHEN tild.is_cancelled = TRUE THEN tild.investment_amount ELSE 0 END), 0) as loan_cancel_amount,
                COALESCE(SUM(tilrs.total_npa_amount), 0) as total_npa_amount
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
                AND tli.product_config_id = ANY(%(product_config_ids)s)
                AND tli.actual_closure_date IS NOT NULL
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                AND tild.deleted IS NULL
            JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                AND tilrs.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
        """
        
        return self.execute_fetch_one(sql, params)

    def get_stl_business_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        investment_type: str
    ) -> Dict[str, Any]:
        """
        Get STL business summary for both open and closed investments.
        """
        # Get product_config_ids for the investment_type
        product_config_ids = self.product_config_entity.get_product_config_ids_by_investment_type(investment_type)
        if not product_config_ids:
            return {
                'open': self._get_empty_stl_metrics(),
                'closed': self._get_empty_stl_metrics()
            }
        
        open_result = self.fetch_stl_open_investments_metrics(
            filter_type, partner_id, source, cp_user_id, product_config_ids
        )
        
        closed_result = self.fetch_stl_closed_investments_metrics(
            filter_type, partner_id, source, cp_user_id, product_config_ids
        )
        
        return {
            'open': self._format_stl_metrics(open_result),
            'closed': self._format_stl_metrics(closed_result)
        }
    
    def fetch_stl_investment_records(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        product_config_ids: List[int],
        is_open: bool,
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        closure_filter = "AND tli.actual_closure_date IS NULL" if is_open else "AND tli.actual_closure_date IS NOT NULL"
        
        sql = f"""
            SELECT
                tl.user_id as lender_user_id,
                tli.investment_id,
                tli.actual_principal_lent as total_lending_amount,
                COALESCE(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 0) as interest_received,
                COALESCE(SUM(tilrs.total_principal_received), 0) as principal_received,
                COALESCE(SUM(tilrs.principal_outstanding), 0) as principal_outstanding,
                COALESCE(SUM(tilrs.total_fee_levied), 0) as total_fee_amount,
                COALESCE(SUM(tilrs.total_amount_received), 0) as total_repayment_amount,
                COALESCE(SUM(CASE WHEN tild.is_cancelled = TRUE THEN tild.investment_amount ELSE 0 END), 0) as loan_cancel_amount,
                COALESCE(SUM(tilrs.total_npa_amount), 0) as total_npa_amount
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
                AND tli.product_config_id = ANY(%(product_config_ids)s)
                {closure_filter}
            JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                AND tild.deleted IS NULL
            LEFT JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                AND tilrs.deleted IS NULL
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY tl.user_id, tli.investment_id, tli.actual_principal_lent
            ORDER BY tl.user_id, tli.investment_id
        """
        
        params['product_config_ids'] = product_config_ids
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_stl_business_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        investment_type: str,
        is_open: bool,
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        

        # Get product_config_ids for the investment_type
        product_config_ids = self.product_config_entity.get_product_config_ids_by_investment_type(investment_type)
        if not product_config_ids:
            return []
        
        return self.fetch_stl_investment_records(
            filter_type, partner_id, source, cp_user_id,
            product_config_ids, is_open, limit, offset, download
        )
    
    def fetch_repayment_transfers_by_date(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        redemption_type: str
    ) -> Dict[str, Any]:
        """
        Execute SQL query to get repayment transfer summary.
        Note: Caller must validate redemption_type before calling.
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        # Last 5 days
        today = date.today()
        five_days_ago = today - timedelta(days=5)
        
        sql = f"""
            SELECT
                trs.created_dtm::date as repayment_date,
                COALESCE(SUM(trs.total_amount_received), 0) as total_repayment_amount,
                COUNT(DISTINCT trs.lender_id) as lender_count
            FROM t_lender tl
            {join_sql}
            JOIN t_redemption_summary trs ON tl.id = trs.lender_id
                AND trs.deleted IS NULL
                AND trs.type = %(redemption_type)s
                AND trs.created_dtm::date >= %(from_date)s
                AND trs.created_dtm::date <= %(to_date)s
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY trs.created_dtm::date
            ORDER BY trs.created_dtm::date DESC
        """
        
        params['redemption_type'] = redemption_type
        params['from_date'] = five_days_ago
        params['to_date'] = today
        
        results = self.execute_fetch_all(sql, params)
        
        return {
            'results': results,
            'today': today
        }

    def get_repayment_transfer_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        investment_type: str
    ) -> List[Dict[str, Any]]:
        
        # Map investment_type to redemption type
        redemption_type_map = {
            InvestmentType.ONE_TIME_LENDING: RedemptionType.SHORT_TERM_LENDING_REPAYMENT_TRANSFER,
            InvestmentType.MEDIUM_TERM_LENDING: RedemptionType.MEDIUM_TERM_LENDING_REPAYMENT_TRANSFER
        }
        redemption_type = redemption_type_map.get(investment_type)
        if not redemption_type:
            return []
        
        query_result = self.fetch_repayment_transfers_by_date(
            filter_type, partner_id, source, cp_user_id, redemption_type
        )
        
        results = query_result.get('results', [])
        today = query_result.get('today', date.today())
        
        # Format results with labels
        month_names = MonthNames.NAMES
        formatted_results = []
        for row in results:
            repayment_date = row['repayment_date']
            formatted_results.append({
                'label': f"{repayment_date.day} {month_names[repayment_date.month - 1]}",
                'total_repayment_amount': float(row.get('total_repayment_amount') or 0),
                'repayment_date': repayment_date.strftime('%d/%m/%Y'),
                'lender_count': row.get('lender_count', 0)
            })
        
        # Ensure we have 5 days (fill missing days with zeros)
        all_dates = []
        for i in range(5):
            check_date = today - timedelta(days=i)
            found = False
            for result in formatted_results:
                if result['repayment_date'] == check_date.strftime('%d/%m/%Y'):
                    all_dates.append(result)
                    found = True
                    break
            if not found:
                all_dates.append({
                    'label': f"{check_date.day} {month_names[check_date.month - 1]}",
                    'total_repayment_amount': 0.0,
                    'repayment_date': check_date.strftime('%d/%m/%Y'),
                    'lender_count': 0
                })
        
        return all_dates
    
    def get_repayment_transfer_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        investment_type: str,
        investment_type_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        offset: int,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get repayment transfer details for the specified investment type.
        """
        # Map investment_type to redemption type
        redemption_type_map = {
            InvestmentType.ONE_TIME_LENDING: RedemptionType.SHORT_TERM_LENDING_REPAYMENT_TRANSFER,
            InvestmentType.MEDIUM_TERM_LENDING: RedemptionType.MEDIUM_TERM_LENDING_REPAYMENT_TRANSFER
        }
        redemption_type = redemption_type_map.get(investment_type)
        if not redemption_type:
            return []
        
        # Build CP filter join and where clause
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'tcpmt'
        )

        # Build date filter
        date_filter_sql, date_params = self._build_date_filter(
            from_date, to_date, 'trs', 'created_dtm'
        )
        params.update(date_params)

        sql = f"""
            SELECT
                tl.user_id,
                tl.partner_id,
                mclikm.last_scheme_created_date,
                mclikm.total_active_lending_amount,
                mclikm.total_lending_amount,
                SUM(trs.total_amount_received) AS total_repayment_amount,
                SUM(trs.total_principal) AS principal_received,
                SUM(trs.total_interest - trs.total_fee_levied) AS interest_received,
                COUNT(*) OVER() AS total_count
            FROM t_lender tl
            JOIN t_lender_investment tli ON tl.id = tli.lender_id
                AND tli.deleted IS NULL
            JOIN t_redemption_summary trs ON trs.investment_id = tli.id
                AND trs.deleted IS NULL
                AND trs.redemption_status <> 'SCHEDULED'
                AND trs.type = %(redemption_type)s
                {date_filter_sql}
            {join_sql}
            JOIN mv_cp_lender_investment_key_metrics mclikm 
                ON tli.lender_id = mclikm.lender_id
                AND mclikm.investment_type_id = %(investment_type_id)s
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY 
                tl.user_id, 
                tl.partner_id, 
                mclikm.last_scheme_created_date, 
                mclikm.total_active_lending_amount, 
                mclikm.total_lending_amount
            ORDER BY mclikm.last_scheme_created_date DESC NULLS LAST, tl.user_id
        """
        
        params['redemption_type'] = redemption_type
        params['investment_type_id'] = investment_type_id
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []
    
    def fetch_money_flow_by_month(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get add money and FMPP redemption summary for last 3 months.
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        # Last 3 months
        today = date.today()
        three_months_ago = today - timedelta(days=90)
        
        params['add_money_transaction_type'] = TransactionType.ADD_MONEY
        params['fmpp_redemption_transaction_type'] = TransactionType.FMPP_REDEMPTION
        params['from_date'] = three_months_ago
        params['transaction_types'] = [TransactionType.ADD_MONEY, TransactionType.FMPP_REDEMPTION]
        sql = f"""
            SELECT
                DATE_TRUNC('month', tlwt.created_dtm)::date as month_date,
                COALESCE(SUM(CASE WHEN tlwt.transaction_type = %(add_money_transaction_type)s 
                    THEN tlwt.amount ELSE 0 END), 0) as money_added,
                COALESCE(SUM(CASE WHEN tlwt.transaction_type = %(fmpp_redemption_transaction_type)s 
                    THEN tlwt.amount ELSE 0 END), 0) as redemption_amount
            FROM t_lender tl
            {join_sql}
            JOIN t_lender_wallet_transaction tlwt ON tl.id = tlwt.lender_id
                AND tlwt.deleted IS NULL
                AND tlwt.transaction_type = ANY (%(transaction_types)s)
                AND tlwt.created_dtm::date >= %(from_date)s
            WHERE tl.deleted IS NULL
            {where_sql}
            GROUP BY DATE_TRUNC('month', tlwt.created_dtm)::date
            ORDER BY DATE_TRUNC('month', tlwt.created_dtm)::date DESC
            LIMIT 3
        """
        
        results = self.execute_fetch_all(sql, params)
        
        return {
            'results': results or [],
            'today': today
        }

    def get_add_money_and_matured_amount_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Get add money and FMPP redemption summary for last 3 months.
        """
        query_result = self.fetch_money_flow_by_month(
            filter_type, partner_id, source, cp_user_id
        )
        
        results = query_result.get('results', [])
        today = query_result.get('today', date.today())
        
        # Format results with labels
        month_names = MonthNames.NAMES
        formatted_results = []
        for row in results:
            month_date = row['month_date']
            formatted_results.append({
                'label': month_names[month_date.month - 1],
                'money_added': float(row.get('money_added') or 0),
                'redemption_amount': float(row.get('redemption_amount') or 0)
            })
        
        # Ensure we have 3 months (fill missing months with zeros)
        all_months = []
        for i in range(3):
            check_date = today.replace(day=1) - timedelta(days=30*i)
            found = False
            for result in formatted_results:
                if result['label'] == month_names[check_date.month - 1]:
                    all_months.append(result)
                    found = True
                    break
            if not found:
                all_months.append({
                    'label': month_names[check_date.month - 1],
                    'money_added': 0.0,
                    'redemption_amount': 0.0
                })
        
        return all_months
    
    def fetch_money_flow_transactions(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        from_date: date,
        to_date: date,
        limit: int,
        offset: int,
        transaction_type: str,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get add money details (transaction-level) with date filters.
        
        Args:
            download: If True, return all data without pagination
            transaction_type: Transaction type to filter by (defaults to ADD_MONEY if not provided)
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
        
        params['transaction_type'] = transaction_type
        params['account_type_id'] = account_type_id
        # Build date filter with UTC conversion
        date_filter, date_params = self._build_date_filter(from_date, to_date, 'tlwt')
        params.update(date_params)
        
        sql = f"""
            SELECT
                tl.user_id as lender_user_id,
                tlwt.transaction_id,
                tlwt.amount as money_added,
                tlwt.created_dtm::date as transaction_date,
                tlwt.status,
                ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
            FROM t_lender tl
            {join_sql}
            JOIN t_account ta ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            JOIN t_lender_wallet_transaction tlwt ON tl.id = tlwt.lender_id
                AND tlwt.deleted IS NULL
                AND tlwt.transaction_type = %(transaction_type)s
                {date_filter}
            WHERE tl.deleted IS NULL
            {where_sql}
            ORDER BY tlwt.created_dtm DESC, tl.user_id
        """
        
        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset
        
        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_add_money_and_matured_amount_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        from_date: date,
        to_date: date,
        limit: int,
        offset: int,
        transaction_type: str,
        download: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get add money details (transaction-level) with date filters.
        
        Args:
            download: If True, return all data without pagination
            transaction_type: Transaction type to filter by (defaults to ADD_MONEY if not provided)
        """
        # Get LENDER_WALLET account_type_id
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return []
        
        account_type_id = master_account.get('id')
        
        return self.fetch_money_flow_transactions(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, from_date, to_date, limit, offset,
            transaction_type, download
        )
    
    def fetch_lender_activity_counts(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get lender activity summary with active, inactive, and zero investment counts.
        """
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'cpm'
        )
    
        ninety_days_ago = date.today() - timedelta(days=90)
        
        sql = f"""
            WITH partner_lenders AS (
                SELECT tl.id as lender_id
                FROM t_lender tl
                {join_sql}
                WHERE tl.deleted IS NULL
                {where_sql}
            ),
            latest_investment AS (
                SELECT
                    tli.lender_id,
                    MAX(tli.created_dtm) AS max_created_dtm
                FROM t_lender_investment tli
                JOIN partner_lenders pl ON pl.lender_id = tli.lender_id
                WHERE tli.deleted IS NULL
                GROUP BY tli.lender_id
            )
            SELECT
                COUNT(DISTINCT CASE
                    WHEN li.max_created_dtm >= %(ninety_days_ago)s THEN pl.lender_id
                END) AS active_since_last_90_days,
                COUNT(DISTINCT CASE
                    WHEN li.max_created_dtm < %(ninety_days_ago)s 
                         AND li.max_created_dtm IS NOT NULL THEN pl.lender_id
                END) AS inactive_since_last_90_days,
                COUNT(DISTINCT CASE
                    WHEN li.max_created_dtm IS NULL THEN pl.lender_id
                END) AS inactive_with_zero_investments
            FROM partner_lenders pl
            LEFT JOIN latest_investment li ON li.lender_id = pl.lender_id
        """
        
        params['ninety_days_ago'] = ninety_days_ago
        
        return self.execute_fetch_one(sql, params)

    def get_lender_activity_summary(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get lender activity summary with active, inactive, and zero investment counts.
        """
        result = self.fetch_lender_activity_counts(
            filter_type, partner_id, source, cp_user_id
        )
        
        return {
            'active_since_last_90_days': result['active_since_last_90_days'],
            'inactive_since_last_90_days': result['inactive_since_last_90_days'],
            'inactive_with_zero_investments': result['inactive_with_zero_investments']
        }
    
    def _get_empty_stl_metrics(self) -> Dict[str, float]:
        """Helper to return empty STL metrics."""
        return {
            'total_lending_amount': 0.0,
            'interest_received': 0.0,
            'principal_received': 0.0,
            'principal_outstanding': 0.0,
            'total_fee_amount': 0.0,
            'total_repayment_amount': 0.0,
            'loan_cancel_amount': 0.0,
            'total_npa_amount': 0.0
        }
    
    def _format_stl_metrics(self, result: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Helper to format STL metrics from query result."""
        if not result:
            return self._get_empty_stl_metrics()
        
        return {
            'total_lending_amount': float(result.get('total_lending_amount') or 0),
            'interest_received': float(result.get('interest_received') or 0),
            'principal_received': float(result.get('principal_received') or 0),
            'principal_outstanding': float(result.get('principal_outstanding') or 0),
            'total_fee_amount': float(result.get('total_fee_amount') or 0),
            'total_repayment_amount': float(result.get('total_repayment_amount') or 0),
            'loan_cancel_amount': float(result.get('loan_cancel_amount') or 0),
            'total_npa_amount': float(result.get('total_npa_amount') or 0)
        }

    def get_stl_closed_scheme_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """
        Get STL closed scheme details for a specific investment scheme.

        Args:
            scheme_id: Investment scheme ID (investment_id from t_lender_investment)

        Returns:
            Dictionary with STL closed scheme details or None if not found
        """
        sql = """
            SELECT
                t.investor_scheme_id,
                COALESCE(ROUND(t.amount, 2), 0) as lent_amount,
                COALESCE(ROUND(t.cancelled_loan_amount, 2), 0) as cancelled_loan_amount,
                COALESCE(ROUND(t.pending_transfer, 2), 0) as pending_transfer,
                COALESCE(ROUND(t.total_recieved_amount, 2), 0) as total_received_amount,
                COALESCE(ROUND(SUM(t.expected_repayment_sum), 2), 0) as expected_returns,
                COALESCE(ROUND(SUM(t.principal_received), 2), 0) as principal,
                COALESCE(ROUND(SUM(t.interest), 2), 0) as interest,
                COALESCE(ROUND(SUM(t.fee_deducted), 2), 0) as platform_fees,
                COALESCE(ROUND(SUM(t.principal_outstanding), 2), 0) as principal_outstanding,
                COALESCE(ROUND(SUM(t.total_npa_amount), 2), 0) as npa,
                COALESCE(ROUND(SUM(t.weighted_tenure), 2), 0) as weighted_tenure,
                CURRENT_DATE AS report_date,
                t.source_id,
                t.maturity_date,
                t.created_date::DATE,
                t.tenure
            FROM (
                SELECT
                    tli.id as investor_scheme_id,
                    tli.amount_lent_on_investment as amount,
                    0 as pending_transfer,
                    tli.cancelled_loan_amount,
                    tilrs.total_amount_received as total_recieved_amount,
                    ROUND(tl.expected_repayment_sum * tild.allocation_percentage / 100, 2) as expected_repayment_sum,
                    tilrs.principal_outstanding as principal_outstanding,
                    tilrs.total_npa_amount,
                    tilrs.total_fee_levied AS fee_deducted,
                    tilrs.total_principal_received as principal_received,
                    tilrs.total_interest_received as interest,
                    tild.investment_amount * tl.tenure as weighted_tenure,
                    tlender.user_id as source_id,
                    tli.expected_closure_date as maturity_date,
                    tli.created_dtm as created_date,
                    tpc.tenure
                FROM t_lender_investment tli
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_lender tlender ON tli.lender_id = tlender.id
                JOIN t_product_config tpc on tpc.id = tli.product_config_id
                WHERE tli.investment_id = %(scheme_id)s
                AND tli.expected_closure_date < CURRENT_DATE - INTERVAL '15 DAY'
                AND tli.deleted IS NULL
                AND tild.deleted IS NULL
                AND tilrs.deleted IS NULL
                AND tl.deleted IS NULL
                AND tlender.deleted IS NULL
                AND tpc.deleted IS NULL
            ) t
            GROUP BY t.investor_scheme_id, t.amount, t.pending_transfer, t.cancelled_loan_amount, t.total_recieved_amount, t.source_id, t.maturity_date, t.created_date, t.tenure
        """

        params = {
            'scheme_id': scheme_id
        }

        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_stl_cashflow_data(
        self,
        lender_id: int,
        investment_type_id: int,
        is_matured: Optional[bool] = None
    ) -> list:
        """
        Get STL cashflow data for a lender and investment type.

        Args:
            lender_id: Lender ID
            investment_type_id: Investment type ID from mst_parameter
            is_matured: Optional filter for matured schemes (True for closed, False for active)

        Returns:
            List of dictionaries with cashflow data
        """
        sql = """
            SELECT
                tli.created_dtm,
                tli.investment_id AS urn_id,
                COALESCE(tli.actual_closure_date IS NOT NULL, FALSE) AS is_matured,
                COALESCE(ROUND(
                    SUM(tilrs.total_amount_received) - COALESCE(mliprad.pending_repayment_amount, 0),
                    2
                ), 0) AS redeemed_amount,
                COALESCE(mliprad.pending_repayment_amount, 0) AS pending_repayment_transfer,
                tipc.tenure,
                ROUND(tli.amount_lent_on_investment, 2) AS investment_amount,
                COALESCE(ROUND(SUM(tilrs.total_principal_received), 2), 0) AS actual_principal_sum,
                COALESCE(ROUND(SUM(tilrs.total_interest_received - tilrs.total_fee_levied), 2), 0) AS actual_interest_sum,
                COALESCE(ROUND(SUM(tilrs.total_fee_levied), 2), 0) AS total_facilitation_fee,
                COALESCE(ROUND(SUM(tilrs.principal_outstanding), 2), 0) AS pos,
                COALESCE(ROUND(SUM(tilrs.total_npa_amount), 2), 0) AS total_npa_amount,
                COALESCE(ROUND(tli.cancelled_loan_amount, 2), 0) AS loan_cancellation_amount
            FROM
                t_lender_investment tli
            JOIN
                t_investment_loan_detail tild ON tli.id = tild.investment_id
            JOIN
                t_loan tl ON tl.id = tild.loan_id
            JOIN
                t_investment_loan_repayment_summary tilrs ON tilrs.investment_loan_id = tild.id
            JOIN
                t_investment_product_config tipc ON tipc.id = tli.product_config_id
            LEFT JOIN
                mv_lender_investment_pending_repayment_amount_details mliprad ON tli.id = mliprad.investment_id
            WHERE
                tli.lender_id = %(lender_id)s
                AND tli.investment_type_id = %(investment_type_id)s
                AND (%(is_matured)s IS NULL OR (%(is_matured)s IS NOT NULL AND (
                    (%(is_matured)s = TRUE)
                )))
                AND tli.deleted IS NULL
                AND tild.deleted IS NULL
                AND tilrs.deleted IS NULL
                AND tl.deleted IS NULL
            GROUP BY
                tli.id, tli.amount_lent_on_investment, tli.cancelled_loan_amount, 
                tli.investment_id, mliprad.pending_repayment_amount, tipc.tenure, 
                tli.investment_type_id, tli.created_dtm, tli.actual_closure_date
            ORDER BY
                tli.created_dtm
        """

        params = {
            'lender_id': lender_id,
            'investment_type_id': investment_type_id,
            'is_matured': is_matured
        }

        return self.execute_fetch_all(sql, params, to_dict=True)

    def get_lenders_under_partner_with_active_schemes(
        self,
        partner_id: str,
        investment_type_id: int
    ) -> list:
        """
        Get list of lenders under a partner (CP or MCP) that have active schemes.

        Args:
            partner_id: Channel Partner ID or Master Channel Partner ID
            investment_type_id: Investment type ID from mst_parameter

        Returns:
            List of dictionaries with lender IDs and related info
        """
        sql = """
            SELECT DISTINCT 
                tl.id as lender_id,
                tl.user_id,
                tl.partner_id,
                tcpmt.channel_partner_id,
                tcpmt.master_partner_id
            FROM t_channel_partner_mapping_table tcpmt
            JOIN t_lender tl ON tl.partner_mapping_id = tcpmt.id
            JOIN t_lender_investment tli ON tli.lender_id = tl.id
            JOIN t_investment_product_config tipc ON tipc.id = tli.product_config_id
            WHERE (tcpmt.channel_partner_id = %(partner_id)s OR tcpmt.master_partner_id = %(partner_id)s)
            AND tipc.investment_type_id = %(investment_type_id)s
            AND tli.deleted IS NULL
            AND tl.deleted IS NULL
            AND tcpmt.deleted IS NULL
            AND tipc.deleted IS NULL
        """

        params = {
            'partner_id': partner_id,
            'investment_type_id': investment_type_id
        }

        return self.execute_fetch_all(sql, params, to_dict=True)

    def get_lender_portfolio_summary(self, lender_id: int, investment_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Get portfolio summary for a specific lender.

        Args:
            lender_id: Lender ID

        Returns:
            Dictionary with portfolio summary or None if not found
        """
        sql = """
            SELECT
                ROUND(SUM(s.investment_amount), 2) AS total_lending_amount,
                ROUND(SUM(s.cancelled_loan_amount), 2) AS loan_cancel_amount,
                ROUND(SUM(s.expected_repayment_sum), 2) AS expected_returns,
                ROUND(SUM(s.total_received_amount), 2) AS total_repayment_amount,
                ROUND(SUM(s.principal_received), 2) AS principal_received,
                ROUND(GREATEST(SUM(s.interest - s.fee_deducted), 0), 2) AS interest_received,
                ROUND(SUM(s.fee_deducted), 2) AS total_fee_amount,
                ROUND(SUM(s.principal_outstanding), 2) AS principal_outstanding,
                ROUND(SUM(s.total_npa_amount), 2) AS total_npa,
                ROUND(SUM(s.pending_transfer), 2) AS pending_repayment_transfer
            FROM (
                SELECT
                    tli.investment_id,
                    tli.amount_lent_on_investment AS investment_amount,
                    tli.cancelled_loan_amount AS cancelled_loan_amount,
                    COALESCE(mliprad.pending_repayment_amount, 0) AS pending_transfer,
                    SUM(tilrs.total_amount_received) AS total_received_amount,
                    SUM(tl.expected_repayment_sum * tild.allocation_percentage / 100) AS expected_repayment_sum,
                    SUM(tilrs.total_principal_received) AS principal_received,
                    SUM(tilrs.total_interest_received - tilrs.total_fee_levied) AS interest,
                    SUM(tilrs.total_fee_levied) AS fee_deducted,
                    SUM(tilrs.total_npa_amount) AS total_npa_amount,
                    SUM(tilrs.principal_outstanding) AS principal_outstanding
                FROM t_lender_investment tli
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_investment_loan_repayment_summary tilrs ON tild.id = tilrs.investment_loan_id
                JOIN t_loan tl ON tl.id = tild.loan_id
                LEFT JOIN mv_lender_investment_pending_repayment_amount_details mliprad
                    ON tli.id = mliprad.investment_id
                WHERE tli.lender_id = %(lender_id)s
                AND tli.investment_type_id = %(investment_type_id)s
                AND tli.deleted IS NULL
                AND tild.deleted IS NULL
                AND tilrs.deleted IS NULL
                AND tl.deleted IS NULL
                GROUP BY
                    tli.investment_id,
                    tli.amount_lent_on_investment,
                    tli.cancelled_loan_amount,
                    mliprad.pending_repayment_amount
            ) s
        """

        params = {
            'lender_id': lender_id,
            'investment_type_id': investment_type_id
        }

        return self.execute_fetch_one(sql, params, to_dict=True)

    def get_investor_schemes_data(
        self,
        lender_id: int,
        product_config_ids: Optional[List[int]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get investor schemes data for a specific lender.

        Args:
            lender_id: Lender ID
            product_config_ids: Optional list of product_config_ids to filter by investment_type
            limit: Number of results to return
            offset: Number of results to skip

        Returns:
            List of investment dictionaries with all required fields
        """
        from ..entity.lender_investment import LenderInvestment

        lender_investment_entity = LenderInvestment(db_alias=self.db_alias)
        return lender_investment_entity.get_investor_schemes_data(
            lender_id=lender_id,
            product_config_ids=product_config_ids,
            limit=limit,
            offset=offset
        )

    def fetch_cp_lender_portfolio_data(
        self,
        partner_id: str,
        source: str,
        account_type_id: int,
        limit: int,
        offset: int,
        download: bool = False,
        fetch_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get CP lender investment details with wallet and investment summaries.
        
        Args:
            partner_id: Partner ID to filter by
            source: Source type (MCP or LCP)
            account_type_id: Account type ID for LENDER_WALLET
            limit: Number of records to return
            offset: Number of records to skip
            download: If True, returns all records without pagination
            fetch_all: If True, includes CP lenders for MCP source
            
        Returns:
            List of lender investment details
        """
        join_sql, where_sql, params = self._build_cp_join(
            partner_id, source, 'tcpmt', fetch_all
        )

        sql = f"""
            SELECT
                tl.user_id,
                tl.partner_id,
                tl.partner_code_id,
                COALESCE(ROUND(SUM(CASE WHEN tlwt.transaction_type = %(add_money_type)s THEN tlwt.amount ELSE 0 END), 2), 0) AS total_funds_added,
                COALESCE(ROUND(SUM(CASE WHEN tlwt.transaction_type = %(withdraw_money_type)s THEN tlwt.amount ELSE 0 END), 2), 0) AS total_funds_withdrawn,
                COALESCE(ROUND(SUM(CASE WHEN tli.actual_closure_date IS NULL THEN tli.amount_lent_on_investment ELSE 0 END), 2), 0) AS active_investment_amount,
                COALESCE(ROUND(SUM(tli.actual_principal_lent), 2), 0) AS total_investment_amount,
                COALESCE(ROUND(ta.balance, 2), 0) AS wallet_balance,
                COUNT(tli.id) AS fmpps
            FROM t_lender tl
            {join_sql}
            JOIN t_account ta 
                ON ta.lender_id = tl.id 
                AND ta.account_type_id = %(account_type_id)s 
                AND ta.deleted IS NULL
            LEFT JOIN t_lender_wallet_transaction tlwt 
                ON tlwt.lender_id = tl.id 
                AND tlwt.deleted IS NULL
            LEFT JOIN t_lender_investment tli 
                ON tli.lender_id = tl.id 
                AND tli.transaction_id = tlwt.id
            WHERE tl.deleted IS NULL {where_sql}
            GROUP BY tl.id, tl.user_id, tl.partner_id, tl.partner_code_id, ta.id, ta.balance
            ORDER BY tl.id
        """

        params['account_type_id'] = account_type_id
        params['add_money_type'] = TransactionType.ADD_MONEY
        params['withdraw_money_type'] = TransactionType.WITHDRAW_MONEY

        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset

        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_cp_lender_investment_details(
        self,
        partner_id: str,
        source: str,
        limit: int,
        offset: int,
        download: bool = False,
        fetch_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get CP lender investment details with wallet and investment summaries.
        
        Args:
            partner_id: Partner ID to filter by
            source: Source type (MCP or LCP)
            limit: Number of records to return
            offset: Number of records to skip
            download: If True, returns all records without pagination
            fetch_all: If True, includes CP lenders for MCP source
            
        Returns:
            List of lender investment details
        """
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            return []
        
        account_type_id = master_account.get('id')

        return self.fetch_cp_lender_portfolio_data(
            partner_id, source, account_type_id, limit, offset, download, fetch_all
        )

    def fetch_lender_wallet_balance(
        self,
        user_source_group_id: str,
        account_type_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get CP lender profile balance with wallet balance and blocked balance for a single user.

        Args:
            user_source_group_id: User source group ID from t_lender table
            account_type_id: Account type ID for LENDER_WALLET

        Returns:
            Lender profile balance data or None if not found
        """
        sql = """
            SELECT
                tl.user_id,
                tl.partner_id,
                tl.partner_code_id,
                ROUND(ta.balance, 2) AS wallet_balance,
                ROUND(tlio.blocked_balance, 2) AS blocked_balance
            FROM t_lender tl
            JOIN t_account ta
                ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            JOIN (
                SELECT
                    tlio.lender_id,
                    SUM(tlio.amount_lent) AS blocked_balance
                FROM t_lender_investment_order tlio
                WHERE tlio.deleted IS NULL
                  AND tlio.status = %(pending_status)s
                GROUP BY tlio.lender_id
            ) tlio ON tlio.lender_id = tl.id
            WHERE tl.deleted IS NULL
              AND tl.user_source_group_id = %(user_source_group_id)s
        """

        params = {
            'user_source_group_id': user_source_group_id,
            'account_type_id': account_type_id,
            'pending_status': LendingInvestmentStatus.PENDING
        }

        return self.execute_fetch_one(sql, params)

    def get_cp_lender_profile_balance(
        self,
        user_source_group_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get CP lender profile balance with wallet balance and blocked balance for a single user.

        Args:
            user_source_group_id: User source group ID from t_lender table

        Returns:
            Lender profile balance data or None if not found
        """
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            return None

        account_type_id = master_account.get('id')

        return self.fetch_lender_wallet_balance(
            user_source_group_id, account_type_id
        )

    def fetch_investor_records(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        limit: Optional[int],
        offset: Optional[int],
        download: bool = False
    ) -> List[Dict[str, Any]]:
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'tcpmt'
        )

        if from_date is None:
            today = date.today()
            if today.month >= 3:
                two_months_ago_month = today.month - 2
                two_months_ago_year = today.year
            else:
                two_months_ago_month = today.month + 10
                two_months_ago_year = today.year - 1
            first_day_two_months_ago = date(two_months_ago_year, two_months_ago_month, 1)
            default_from_date = first_day_two_months_ago - timedelta(days=1)
            from_date = default_from_date
            if to_date is None:
                to_date = today

        date_filter, date_params = self._build_date_filter(from_date, to_date, 'tli', 'created_dtm')
        params.update(date_params)
        params['account_type_id'] = account_type_id

        sql = f"""
            SELECT
                tl.user_id,
                tl.partner_id,
                tipc.investment_type,
                ROUND(SUM(tli.amount_lent_on_investment), 2) as amount_invested_in_fmpp_current_month,
                MAX(tli.created_dtm::date) as last_created_date,
                (now()::date - MAX(tli.created_dtm::date)) as no_of_days_last_fmpp_created,
                ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
            FROM t_lender_investment tli
            JOIN t_lender tl ON tl.id = tli.lender_id
                AND tl.deleted IS NULL
            JOIN t_investment_product_config tipc ON tipc.id = tli.product_config_id
                AND tipc.deleted IS NULL
            JOIN t_account ta ON tl.id = ta.lender_id
                AND ta.account_type_id = %(account_type_id)s
                AND ta.deleted IS NULL
            {join_sql}
            WHERE tli.deleted IS NULL
                AND tli.actual_closure_date IS NULL
                {date_filter}
            {where_sql}
            GROUP BY tl.user_id, tl.partner_id, tipc.investment_type, ta.balance
            ORDER BY tl.user_id, tipc.investment_type
        """

        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset

        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_investors_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        from_date: Optional[date],
        to_date: Optional[date],
        limit: Optional[int],
        offset: Optional[int],
        download: bool = False
    ) -> List[Dict[str, Any]]:
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return []
        
        account_type_id = master_account.get('id')

        return self.fetch_investor_records(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, from_date, to_date, limit, offset, download
        )

    def fetch_investor_transaction_history(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        account_type_id: int,
        activity_type: str,
        limit: Optional[int],
        offset: Optional[int],
        download: bool = False
    ) -> List[Dict[str, Any]]:
        join_sql, where_sql, params = self._build_cp_filter_join(
            filter_type, partner_id, source, cp_user_id, 'tcpmt'
        )
        params['account_type_id'] = account_type_id
        ninety_days_ago = date.today() - timedelta(days=90)

        if activity_type == InvestorActivityType.ACTIVE_SINCE_LAST_90_DAYS:
            sql = f"""
                SELECT
                    tl.user_id,
                    tl.partner_id,
                    ROUND(SUM(CASE 
                        WHEN tli.created_dtm >= %(ninety_days_ago)s THEN tli.amount_lent_on_investment
                        ELSE 0 
                    END), 2) as amount_invested_in_fmpp_current_month,
                    (now()::date - MAX(tli.created_dtm::date)) as no_of_days_last_fmpp_created,
                    ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
                FROM t_lender_investment tli
                JOIN t_lender tl ON tl.id = tli.lender_id
                    AND tl.deleted IS NULL
                JOIN t_account ta ON tl.id = ta.lender_id
                    AND ta.account_type_id = %(account_type_id)s
                    AND ta.deleted IS NULL
                {join_sql}
                WHERE tli.deleted IS NULL
                    AND tli.actual_closure_date IS NULL
                    AND tli.created_dtm >= %(ninety_days_ago)s
                {where_sql}
                GROUP BY tl.user_id, tl.partner_id, ta.balance
                ORDER BY tl.user_id
            """
            params['ninety_days_ago'] = ninety_days_ago

        elif activity_type == InvestorActivityType.INACTIVE_WITH_ZERO_AUM:
            sql = f"""
                SELECT
                    tl.user_id,
                    tl.partner_id,
                    ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
                FROM t_lender tl
                {join_sql}
                JOIN t_account ta ON tl.id = ta.lender_id
                    AND ta.account_type_id = %(account_type_id)s
                    AND ta.deleted IS NULL
                WHERE tl.deleted IS NULL
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_lender_investment tli
                        WHERE tli.lender_id = tl.id
                            AND tli.deleted IS NULL
                    )
                {where_sql}
                ORDER BY tl.user_id
            """

        elif activity_type == InvestorActivityType.INACTIVE_SINCE_LAST_90_DAYS:
            sql = f"""
                SELECT
                    tl.user_id,
                    tl.partner_id,
                    0 as amount_invested_in_fmpp_current_month,
                    (now()::date - MAX(tli.created_dtm::date)) as no_of_days_last_fmpp_created,
                    ROUND(COALESCE(ta.balance, 0), 2) as available_balance_in_wallet
                FROM t_lender_investment tli
                JOIN t_lender tl ON tl.id = tli.lender_id
                    AND tl.deleted IS NULL
                JOIN t_account ta ON tl.id = ta.lender_id
                    AND ta.account_type_id = %(account_type_id)s
                    AND ta.deleted IS NULL
                {join_sql}
                WHERE tli.deleted IS NULL
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_lender_investment tli2
                        WHERE tli2.lender_id = tl.id
                            AND tli2.deleted IS NULL
                            AND tli2.created_dtm >= %(ninety_days_ago)s
                    )
                {where_sql}
                GROUP BY tl.user_id, tl.partner_id, ta.balance
                ORDER BY tl.user_id
            """
            params['ninety_days_ago'] = ninety_days_ago

        else:
            raise ValueError(f"Invalid activity_type: {activity_type}")

        if not download and limit is not None and offset is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params['limit'] = limit
            params['offset'] = offset

        results = self.execute_fetch_all(sql, params)
        return results if results else []

    def get_investor_activity_details(
        self,
        filter_type: str,
        partner_id: str,
        source: str,
        cp_user_id: Optional[str],
        activity_type: str,
        limit: Optional[int],
        offset: Optional[int],
        download: bool = False
    ) -> List[Dict[str, Any]]:
        master_account = get_master_account_type_id(AccountType.LENDER_WALLET)
        if not master_account:
            logger.warning("LENDER_WALLET account not found in t_master_account")
            return []
        
        account_type_id = master_account.get('id')

        return self.fetch_investor_transaction_history(
            filter_type, partner_id, source, cp_user_id,
            account_type_id, activity_type, limit, offset, download
        )
