from typing import Dict, Any, Optional
from datetime import date
from ..base_layer import BaseDataLayer
from ..constants import LoanStatus, FmppInvestmentType, PartnerCode


class Loan(BaseDataLayer):
    """
    Data layer for loan related database operations.
    """
    def get_loan_data(self, loan_ref_id):
        sql = """
                SELECT 
                    tl.id, loan_ref_id, tl.tenure, amount, expected_repayment_sum, 
                    interest_rate, is_modified_roi, interest_rate, remaining_amount, 
                    investment_amount_sum, tlpc.partner_code, risk_type, ldc_score, 
                    borrower_type, income, tlpc.source
                FROM t_loan tl
                JOIN t_loan_product_config tlpc ON tl.loan_product_config_id = tlpc.id    
                WHERE loan_ref_id = %(loan_ref_id)s
            """

        params = {
            'loan_ref_id': loan_ref_id
        }

        return self.execute_fetch_one(sql, params)

    def get_live_loans_count(self):
        sql = """
                SELECT
                    count(id) as live_loans_count
                FROM t_loan
                WHERE 
                    status = %(loan_status)s
                    AND deleted IS NULL
                    AND loan_ref_id ~ '^[^_]+$'
                    AND investment_amount_sum < amount
                    AND created_dtm <= (
                SELECT 
                    COALESCE((((now() + interval '5:30 hours')::date)-date_difference+cig_to_time::text::time)- interval '5:30 hours',now())
                FROM t_cig_funding_master 
                WHERE 
                    scheme_type = %(scheme_type)s
                    AND TO_CHAR((now() + interval '5:30 hours'),'HH24:MI:SS')::TIME 
                    BETWEEN from_time and to_time
                );
            """

        params = {
            'loan_status': LoanStatus.LIVE,
            'scheme_type': FmppInvestmentType.MANUAL_LENDING
        }

        return self.execute_fetch_one(sql, params)

    def fetch_loan_master_date(self, investment_type):
        sql = """ 
                select 
                coalesce((((now() + interval '5:30 hours')::date) - date_difference + cig_to_time::text::time)- interval '5:30 hours',now()) as funding_time
                from t_cig_funding_master 
                where scheme_type = %(scheme_type)s 
                AND TO_CHAR((now() + interval '5:30 hours'),'HH24:MI:SS')::TIME 
                BETWEEN from_time and to_time 
            """

        params = {
            'scheme_type': investment_type
        }

        result = self.execute_fetch_one(sql, params)
        if result:
            return result['funding_time']
        return None
    
    def check_loan_exists_by_ref_id(self, loan_ref_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if a loan already exists by loan_ref_id.
        
        Args:
            loan_ref_id: Loan reference ID from source system
            
        Returns:
            Dict with loan_id and urn_id if exists, None otherwise
        """
        sql = """
            SELECT id, urn_id
            FROM t_loan
            WHERE loan_ref_id = %(loan_ref_id)s
              AND deleted IS NULL
            LIMIT 1
        """
        
        params = {'loan_ref_id': loan_ref_id}
        result = self.execute_fetch_one(sql, params)
        
        if result:
            return {
                'loan_id': result['id'],
                'urn_id': result['urn_id']
            }
        return None
    
    def create_loan(
        self,
        loan_product_config_id: int,
        loan_ref_id: str,
        amount: float,
        interest_rate: float,
        is_modified_roi: bool,
        expected_repayment_sum: float,
        first_repayment_date: date,
        last_repayment_date: date,
        borrower_name: Optional[str],
        borrower_age: Optional[int],
        borrower_type: str,
        risk_type: str,
        ldc_score: int,
        income: float,
        repayment_frequency: str,
        tenure: int,
        status: str,
        fees_config_id: str,
        borrower_id: int
    ) -> Dict[str, Any]:
        """
        Create a new loan record.
        
        Returns:
            Dict with loan_id and urn_id
        """
        sql = """
            INSERT INTO t_loan (
                loan_product_config_id,
                loan_ref_id,
                amount,
                interest_rate,
                is_modified_roi,
                expected_repayment_sum,
                first_repayment_date,
                last_repayment_date,
                borrower_name,
                borrower_age,
                borrower_type,
                risk_type,
                ldc_score,
                income,
                repayment_frequency,
                tenure,
                status,
                status_date,
                fees_config_id,
                remaining_amount,
                borrower_id
            )
            VALUES (
                %(loan_product_config_id)s,
                %(loan_ref_id)s,
                %(amount)s,
                %(interest_rate)s,
                %(is_modified_roi)s,
                %(expected_repayment_sum)s,
                %(first_repayment_date)s,
                %(last_repayment_date)s,
                %(borrower_name)s,
                %(borrower_age)s,
                %(borrower_type)s,
                %(risk_type)s,
                %(ldc_score)s,
                %(income)s,
                %(repayment_frequency)s,
                %(tenure)s,
                %(status)s,
                %(status_date)s,
                %(fees_config_id)s,
                %(remaining_amount)s,
                %(borrower_id)s
            )
            RETURNING id, urn_id
        """
        
        params = {
            'loan_product_config_id': loan_product_config_id,
            'loan_ref_id': loan_ref_id,
            'amount': amount,
            'interest_rate': interest_rate,
            'is_modified_roi': is_modified_roi,
            'expected_repayment_sum': expected_repayment_sum,
            'first_repayment_date': first_repayment_date,
            'last_repayment_date': last_repayment_date,
            'borrower_name': borrower_name,
            'borrower_age': borrower_age,
            'borrower_type': borrower_type,
            'risk_type': risk_type,
            'ldc_score': ldc_score,
            'income': income,
            'repayment_frequency': repayment_frequency,
            'tenure': tenure,
            'status': status,
            'status_date': first_repayment_date,
            'fees_config_id': fees_config_id,
            'remaining_amount': amount,
            'borrower_id': borrower_id
        }
        
        result = self.execute_fetch_one(sql, params)
        return {
            'loan_id': result['id'],
            'urn_id': result['urn_id']
        }
    
    def get_loan_by_id(self, loan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get loan by ID.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            Dict with loan data or None
        """
        sql = """
            SELECT 
                id,
                loan_ref_id,
                status,
                investment_amount_sum,
                deleted
            FROM t_loan
            WHERE id = %(loan_id)s
        """
        
        params = {'loan_id': loan_id}
        return self.execute_fetch_one(sql, params)
    
    def get_loan_by_ref_id(self, loan_ref_id: str) -> Optional[Dict[str, Any]]:
        """
        Get loan by loan_ref_id (alphanumeric reference ID).
        
        Args:
            loan_ref_id: Loan reference ID (alphanumeric)
            
        Returns:
            Dict with loan data including id, or None if not found
        """
        sql = """
            SELECT 
                id,
                loan_ref_id,
                status,
                investment_amount_sum,
                deleted
            FROM t_loan
            WHERE loan_ref_id = %(loan_ref_id)s
              AND deleted IS NULL
        """
        
        params = {'loan_ref_id': loan_ref_id}
        return self.execute_fetch_one(sql, params)
    
    def update_loan_cancellation(self, loan_id: int) -> bool:
        """
        Update loan status to CANCELLED and reset investment_amount_sum.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_loan
            SET status = %(cancelled_loan_status)s,
                investment_amount_sum = 0,
                updated_dtm = NOW()
            WHERE id = %(loan_id)s
        """
        
        params = {
            'loan_id': loan_id,
            'cancelled_loan_status': LoanStatus.CANCELLED
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def update_loan_funding_confirmation(
        self,
        loan_id: int
    ) -> bool:
        """
        Update loan funding notification timestamp after funding confirmation.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            bool: True if update successful, False otherwise
        """
        sql = """
            UPDATE t_loan
            SET 
                status = %(disbusred_status)s,
                funding_notified_dtm = NOW(),
                updated_dtm = NOW()
            WHERE id = %(loan_id)s
              AND status = %(funded_status)s
              AND deleted IS NULL
        """
        
        params = {
            'loan_id': loan_id,
            'disbusred_status': LoanStatus.DISBURSED,
            'funded_status': LoanStatus.FUNDED

        }
        
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def get_loans_for_funding_confirmation(self, limit: int = 50) -> list:
        """
        Get loans that need funding confirmation.
        
        Selects loans with:
        - status = 'LIVE'
        - remaining_amount = 0
        - funding_notified_dtm IS NULL
        - deleted IS NULL
        
        Uses SELECT FOR UPDATE SKIP LOCKED to allow concurrent processing.
        
        Args:
            limit: Maximum number of loans to fetch (default: 50)
            
        Returns:
            list: List of dictionaries containing loan data (id, loan_ref_id, source)
        """
        sql = """
            SELECT 
                tl.id,
                tl.loan_ref_id,
                tlpc.source
            FROM t_loan tl
            JOIN t_loan_product_config tlpc ON tl.loan_product_config_id = tlpc.id
            WHERE tl.status = %(status)s
              AND tl.remaining_amount = 0
              AND tl.funding_notified_dtm IS NULL
              AND tl.deleted IS NULL
            ORDER BY tl.created_dtm ASC
            LIMIT %(limit)s
            FOR UPDATE SKIP LOCKED
        """
        
        params = {
            'status': LoanStatus.LIVE,
            'limit': limit
        }
        
        return self.execute_fetch_all(sql, params) or []
    
    def create_loan_repayment_summary(self, loan_id: int, loan_ref_id: str) -> None:
        """
        Create loan repayment summary record.
        
        Args:
            loan_id: Loan ID
            loan_ref_id: Loan reference ID
        """
        sql = """
            INSERT INTO t_loan_repayment_summary (
                loan_id,
                loan_ref_id
            )
            VALUES (
                %(loan_id)s,
                %(loan_ref_id)s
            )
        """
        
        params = {
            'loan_id': loan_id,
            'loan_ref_id': loan_ref_id
        }
        
        self.execute_no_return(sql, params)
    
    def create_loan_modified_offer(self, loan_id: int, actual_interest_rate: float, modified_interest_rate: float) -> None:
        """
        Create loan modified offer record.
        
        Args:
            loan_id: Loan ID
            actual_interest_rate: Actual interest rate from source
            modified_interest_rate: Modified interest rate (platform_roi)
        """
        sql = """
            INSERT INTO t_loan_modified_offer (
                loan_id,
                actual_interest_rate,
                modified_interest_rate
            )
            VALUES (
                %(loan_id)s,
                %(actual_interest_rate)s,
                %(modified_interest_rate)s
            )
        """
        
        params = {
            'loan_id': loan_id,
            'actual_interest_rate': actual_interest_rate,
            'modified_interest_rate': modified_interest_rate
        }
        
        self.execute_no_return(sql, params)

    def get_loan_fee_config(self, loan_ids_list):
        sql = """
                SELECT
                    tl.tenure,
                    tl.loan_ref_id,
                    tl.expected_repayment_sum,
                    tl.amount,
                    tlfc.facilitation_fee_percentage,
                    tlfc.recovery_fee_percentage,
                    tlfc.collection_fee_percentage
                FROM t_loan tl
                JOIN t_loan_fees_config tlfc ON tl.fees_config_id = tlfc.config_id
                WHERE tl.loan_ref_id = ANY(%(loan_ids_list)s);
            """

        params = {
            'loan_ids_list': loan_ids_list
        }

        return self.execute_fetch_all(sql, params)
    
    def update_loan_disbursal(self, loan_id: int, liquidation_date: str) -> bool:
        """
        Update loan status to DISBURSED and set liquidation_date.
        
        Args:
            loan_id: Loan ID
            liquidation_date: Liquidation date (YYYY-MM-DD format)
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_loan
            SET status = %(disbursed_loan_status)s,
                liquidation_date = %(liquidation_date)s::DATE,
                updated_dtm = NOW()
            WHERE id = %(loan_id)s
              AND status = %(funded_loan_status)s
              AND deleted IS NULL
        """
        
        params = {
            'loan_id': loan_id,
            'liquidation_date': liquidation_date,
            'funded_loan_status': LoanStatus.FUNDED,
            'disbursed_loan_status': LoanStatus.DISBURSED
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def update_loan_closure(self, loan_id: int) -> bool:
        """
        Update loan status to CLOSED.
        
        Args:
            loan_id: Loan ID
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_loan
            SET status = %(closed_loan_status)s,
                updated_dtm = NOW()
            WHERE id = %(loan_id)s
              AND deleted IS NULL
        """
        
        params = {
            'loan_id': loan_id,
            'closed_loan_status': LoanStatus.CLOSED
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def update_loan_dpd(
        self,
        loan_id: int,
        days_past_due: int,
        npa_as_on_date: Optional[str],
        status: str
    ) -> bool:
        """
        Update loan DPD (Days Past Due) and status.
        If DPD > 120, status should be 'NPA', otherwise 'DISBURSED'.
        
        Args:
            loan_id: Loan ID
            days_past_due: Days past due
            npa_as_on_date: NPA as on date (YYYY-MM-DD format) or None
            status: New loan status ('DISBURSED' or 'NPA')
            
        Returns:
            bool: True if update successful
        """
        sql = """
            UPDATE t_loan
            SET status = %(status)s,
                updated_dtm = NOW()
            WHERE id = %(loan_id)s
              AND deleted IS NULL
        """
        
        params = {
            'loan_id': loan_id,
            'status': status
        }
        rows_affected = self.execute_update(sql, params)
        return rows_affected > 0
    
    def get_loans_for_dpd_update(self) -> list:
        """
        Get all active loans that need DPD update.
        
        Selects loans with:
        - status IN ('DISBURSED', 'NPA')
        - deleted IS NULL
        - last_repayment_date + interval '4.5 months' > current_date
          (This means check DPD actively only till 120 + some grace period of 15 days after its last due)
        
        Note: This fetches ALL active loans, not limited batches.
        The job should process all active loans daily.
        
        Returns:
            list: List of dictionaries containing loan data (id, loan_ref_id, status, last_repayment_date)
        """
        sql = """
            SELECT 
                id,
                loan_ref_id,
                status,
                last_repayment_date
            FROM t_loan
            WHERE status = ANY(%(disbursed_and_npa_loan_status)s)
              AND deleted IS NULL
              AND last_repayment_date + INTERVAL '4.5 months' > CURRENT_DATE
            ORDER BY created_dtm ASC
        """
        
        params = {
            'status': [LoanStatus.DISBURSED, LoanStatus.NPA]
        }
        return self.execute_fetch_all(sql, params) or []

    def get_funded_loan_details(self, loan_ref_id: str, lender_id: int) -> Optional[Dict[str, Any]]:
        """
        Get funded loan details for a specific loan and lender.

        Args:
            loan_ref_id: Loan reference ID (loan_ref_id) to fetch details for
            lender_id: Lender ID to filter by

        Returns:
            Dict with loan details or None if not found
        """
        sql = """
            SELECT 
                tl.risk_type,
                tl.ldc_score,
                tl.borrower_type,
                tl.income,
                tl.liquidation_date as disbursement_date,
                tild.created_dtm as funding_time,
                tilrs.total_amount_redeemed,
                tl.loan_ref_id
            FROM t_loan tl
            JOIN t_investment_loan_detail tild ON tild.loan_id = tl.id
            JOIN t_investment_loan_redemption_summary tilrs ON tilrs.investment_loan_id = tild.id
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
            WHERE tl.loan_ref_id = %(loan_ref_id)s 
              AND tli.lender_id = %(lender_id)s
              AND tl.deleted IS NULL
              AND tild.deleted IS NULL
              AND tilrs.deleted IS NULL
              AND tli.deleted IS NULL
        """

        params = {
            'loan_ref_id': loan_ref_id,
            'lender_id': lender_id
        }

        return self.execute_fetch_one(sql, params)

    def get_exposure_loan_details(self, loan_ref_id: str) -> list:
        """
        Get exposure loan details for a specific loan.
        Returns all investors who have invested in this loan.

        Args:
            loan_ref_id: Loan reference ID (loan_ref_id) to fetch exposure details for

        Returns:
            List of dictionaries containing exposure details
        """
        sql = """
            SELECT 
                tli.investment_id as investor_scheme_id,
                TO_CHAR(tl.liquidation_date + interval '5:30 hours', 'YYYY-MM-DD HH:MI AM') as disbursement_date,
                tilrs.total_amount_redeemed as amount_invested,
                tl2.user_id as investor_id
            FROM t_loan tl
            JOIN t_investment_loan_detail tild ON tild.loan_id = tl.id
            JOIN t_investment_loan_redemption_summary tilrs ON tilrs.investment_loan_id = tild.id
            JOIN t_lender_investment tli ON tli.id = tild.investment_id
            JOIN t_lender tl2 ON tl2.id = tli.lender_id
            WHERE tl.loan_ref_id = %(loan_ref_id)s
              AND tl.deleted IS NULL
              AND tild.deleted IS NULL
              AND tilrs.deleted IS NULL
              AND tli.deleted IS NULL
              AND tl2.deleted IS NULL
            ORDER BY tild.created_dtm DESC
        """

        params = {
            'loan_ref_id': loan_ref_id
        }

        return self.execute_fetch_all(sql, params, to_dict=True) or []

    def reject_loan(self, loan_id, batch_number):
        sql = """
                UPDATE t_scheme_loan_mapping
                SET is_selected = false
                WHERE batch_number = %(batch_number)s AND loan_id = %(loan_id)s
                RETURNING lent_amount
            """

        params = {
            'loan_id': loan_id,
            'batch_number': batch_number
        }

        return self.execute_fetch_one(sql, params)

    def get_modified_loan_data(self, loan_id):
        sql = """
                SELECT modified_interest_rate 
                FROM t_loan_modified_offer 
                WHERE loan_id = %(loan_id)s
            """

        params = {
            'loan_id': loan_id
        }

        return self.execute_fetch_one(sql, params)
