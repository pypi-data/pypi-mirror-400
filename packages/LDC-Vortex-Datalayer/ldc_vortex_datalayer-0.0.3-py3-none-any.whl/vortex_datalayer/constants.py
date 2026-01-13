class TransactionStatus:
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    INITIATED = 'INITIATED'
    SCHEDULED = 'SCHEDULED'
    EXPIRED = 'EXPIRED'
    PROCESSING = 'PROCESSING'
    PENDING = 'PENDING'


class FmppInvestmentType:
    MANUAL_LENDING = 'MANUAL_LENDING'
    ONE_TIME_LENDING = 'ONE_TIME_LENDING'
    MEDIUM_TERM_LENDING = 'MEDIUM_TERM_LENDING'


class BatchSizeConstants:
    REDEMPTION_BATCH_SIZE = 10000
    PORTFOLIO_CALCULATION_BATCH_SIZE = 1000
    LOAN_FUNDING_CALLBACK = 50


class TenureType:
    DAILY = 'DAILY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'


class LoanSource:
    BPE = 'BPE'
    PP = 'PP'
    MONO = 'MONO'
    MICRO = 'MICRO'
    LMS = 'LMS'


class Entity:
    BORROWER = 'BORROWER'
    PLATFORM = 'PLATFORM'
    SCHEME = 'SCHEME'
    LOAN = 'CIG'
    INVESTOR = 'INVESTOR'
    PARKING_ACCOUNT = 'PARKING_ACCOUNT'
    PARKING = 'PARKING'


class LoanStatus:
    LIVE = 'LIVE'
    FUNDED = 'FUNDED'
    CANCELLED = 'CANCELLED'
    DISBURSED = 'DISBURSED'
    NPA = 'NPA'
    CLOSED = 'CLOSED'
    HOLD = 'HOLD'


class PartnerCode:
    LENDER_PARTNER_GROUP = ['LDC', 'LENDER CHANNEL PARTNER', 'LENDER',
                            'MASTER CHANNEL PARTNER']
    STL_PARTNER_GROUP = ['CC', 'LENDER CHANNEL PARTNER', 'MASTER CHANNEL PARTNER']
    MONO = 'IM'
    MICRO = 'IM+'
    PP = 'PP'
    MCP = 'MASTER CHANNEL PARTNER'
    LCP = 'LENDER CHANNEL PARTNER'
    LDC = 'LDC'
    RAJ = 'RAJ'
    EPF = 'EPF'
    LENDER = 'LENDER'
    LENDENCLUB = 'LenDenClub'
    NC = 'NC'
    ZOHO_PARTNER_GROUP = ['CC', 'LENDER CHANNEL PARTNER', 'MASTER CHANNEL PARTNER', 'FTSO']
    INTERNAL_SOURCES = ['LDC', 'LCP', 'MCP']


class OTLInvestment:
    OTL_REPAYMENT_FREQUENCY_MONTHLY = 'MONTHLY'
    OTL_REPAYMENT_FREQUENCY_DAILY = 'DAILY'
    OTL_LOAN_TENURE_TYPE = ' Month(s)'
    ALL_PREFERENCES_ID = 152


class AccountStatus:
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'
    CLOSED = 'CLOSED'


class RetailManualLendingReportFilter:
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    ALL = 'ALL'

class RepaymentMigrationSource:
    """Constants for repayment migration source systems."""
    LMS = 'LMS'
    PP = 'PP'
    COMMON_TABLE = 'COMMON_TABLE'


class RepaymentMigrationStatus:
    """Constants for repayment migration status values."""
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    NO_DATA = 'NO_DATA'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    READY = 'READY'
    PARTIAL_SUCCESS = 'PARTIAL_SUCCESS'


class InoffinUser:
    USER_SOURCE_GROUP_ID=4416752
    

class LoanAnalyticsKeys:
    LIVE_LOAN_COUNT = 'live_loan_count'
    FUNDED_LOAN_COUNT = 'funded_loan_count'
    
class DpdThreshold:
    DPD = 120


class OrderStatus:
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    CANCELLED = 'CANCELLED'
    PENDING = 'PENDING'
    

class QueueStatus:
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class CpFilterType:
    """Filter types for CP dashboard queries."""
    ALL = 'all'
    SELF = 'self'
    ALL_CP = 'all_cp'
    CP_USER_ID = 'cp_user_id'


class MonthNames:
    """Month name abbreviations."""
    NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class SchemeStatus:
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'
    POPULAR = 'Popular'
    NEW_PLANS = 'New Plans'
    PAST_PERFORMANCE = 'Past Performance >'
    COLOR_MANUAL = '#38ADD7'
    COLOR_MIP = '#FAD100'
    COLOR_LUMPSUM = '#21A978'
    COLOR_AUTO_LENDING = '#38ADD7'
    INITIATED = 'INITIATED'
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    CANCELLED = 'CANCELLED'
    EXPIRED = 'EXPIRED'
    FAILED = 'FAILED'
    BG_COLOR_MANUAL = '#FFFDF3'
    BG_COLOR_AUTO_LENDING = '#F2FEFA'
    PENDING = 'PENDING'
    ALL = 'ALL'


class LoanSystemSource:
    INSTAMONEY = "Instamoney"
    INSTAMONEYPLUS = "Instamoney-plus"
    PP = "PP"
    RAJ = "JAR"
    EPF = "EPF"
    PERSONAL_LOAN_LIST = ['IM', 'IM+', 'RAJ', 'EPF']
    PERSONAL_LOAN = "Personal Loan"
    MERCHANT_LOAN = "Merchant Loan"

    source_system_name_map = {
        'IM': INSTAMONEY,
        'IM+': INSTAMONEYPLUS,
        'PP': PP,
        'RAJ': RAJ,
        'EPF': EPF
    }


class WalletTransactionType:
    ADD_MONEY = 'ADD MONEY'
    MIP_AUTO_WITHDRAWAL = 'MIP AUTO WITHDRAWAL'
    MANUAL_LENDING_AUTO_WITHDRAWAL = 'MANUAL LENDING AUTO WITHDRAWAL'
    LUMPSUM_AUTO_WITHDRAWAL = 'LUMPSUM AUTO WITHDRAWAL'
    SHORT_TERM_LENDING_AUTO_WITHDRAWAL = 'SHORT TERM LENDING AUTO WITHDRAWAL'
    IDLE_FUND_WITHDRAWAL = 'IDLE FUND WITHDRAWAL'
    REPAYMENT_AUTO_WITHDRAWAL = 'REPAYMENT AUTO WITHDRAWAL'
    FMPP_REPAYMENT_WITHDRAWAL = 'FMPP REPAYMENT WITHDRAWAL'
    AUTO_LENDING_REPAYMENT_WITHDRAWAL = 'AUTO LENDING REPAYMENT WITHDRAWAL'
    AUTO_LENDING_REPAYMENT_ADD_MONEY = 'AUTO LENDING REPAYMENT ADD MONEY'
    WITHDRAW_MONEY = 'WITHDRAW MONEY'
    INVESTMENT = 'INVESTMENT'
    INVESTMENT_CANCELLATION = 'INVESTMENT CANCELLATION'
    IDLE_FUND_REFUND = 'IDLE FUND REFUND'
    IDLE_FUND_WITHDRAWAL = 'IDLE FUND WITHDRAWAL'
    INVESTMENT_REFUND = 'INVESTMENT REFUND'
    MANUAL_LENDING_REFUND = 'MANUAL LENDING REFUND'
    LUMPSUM_REFUND = 'LUMPSUM REFUND'
    SHORT_TERM_LENDING_REFUND = 'SHORT TERM LENDING REFUND'
    MEDIUM_TERM_LENDING_REFUND = 'MEDIUM TERM LENDING REFUND'
    REFUND_ADD_MONEY = 'REFUND ADD MONEY'
    INNOFIN_TRANSFER = 'INNOFIN TRANSFER'
    REVENUE_TRANSFER = 'REVENUE TRANSFER'
    REPAYMENT_AUTO_WITHDRAWAL = 'REPAYMENT AUTO WITHDRAWAL'
    FMPP_REPAYMENT_WITHDRAWAL = 'FMPP REPAYMENT WITHDRAWAL'


class TransactionAction:
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


class ProductConfig:
    ML_PRODUCT_CONFIG_ID = 1
    OTL_PRODUCT_CONFIG_IDS = [2, 3, 4]


# CP Dashboard Constants
class InvestmentType:
    """Investment types."""
    MANUAL_LENDING = "MANUAL_LENDING"
    ONE_TIME_LENDING = "ONE_TIME_LENDING"
    MEDIUM_TERM_LENDING = "MEDIUM_TERM_LENDING"
    SIPP = "SIPP"
    SIP = "SIP"
    AUTO_LENDING = "AUTO_LENDING"
    
    CHOICES = [
        (MANUAL_LENDING, "Manual Lending"),
        (ONE_TIME_LENDING, "One Time Lending"),
        (MEDIUM_TERM_LENDING, "Medium Term Lending")
    ]
    
    TERM_LENDING_CHOICES = [
        (ONE_TIME_LENDING, "One Time Lending"),
        (MEDIUM_TERM_LENDING, "Medium Term Lending")
    ]


class TransactionType:
    """Wallet transaction types."""
    ADD_MONEY = 'ADD MONEY'
    WITHDRAW_MONEY = 'WITHDRAW MONEY'
    MANUAL_REPAYMENT_TRANSFER = 'MANUAL REPAYMENT TRANSFER'
    LUMPSUM_REPAYMENT_TRANSFER = 'LUMPSUM REPAYMENT TRANSFER'
    MIP_AUTO_WITHDRAWAL = 'MIP AUTO WITHDRAWAL'
    MANUAL_LENDING_AUTO_WITHDRAWAL = 'MANUAL LENDING AUTO WITHDRAWAL'
    LUMPSUM_AUTO_WITHDRAWAL = 'LUMPSUM AUTO WITHDRAWAL'
    REPAYMENT_AUTO_WITHDRAWAL = 'REPAYMENT AUTO WITHDRAWAL'
    AUTO_LENDING_REPAYMENT_WITHDRAWAL = 'AUTO LENDING REPAYMENT WITHDRAWAL'
    AUTO_LENDING_REPAYMENT_ADD_MONEY = 'AUTO LENDING REPAYMENT ADD MONEY'
    FMPP_REPAYMENT_WITHDRAWAL = 'FMPP REPAYMENT WITHDRAWAL'
    IDLE_FUND_WITHDRAWAL = 'IDLE FUND WITHDRAWAL'
    CANCELLED_LOAN_REFUND = 'CANCELLED LOAN REFUND'
    REJECTED_LOAN_REFUND = 'REJECTED LOAN REFUND'
    FMPP_REDEMPTION = "FMPP REDEMPTION"
    CHOICES = [
        (ADD_MONEY, "Add Money"),
        (WITHDRAW_MONEY, "Withdraw Money"),
        (FMPP_REDEMPTION, "FMPP Redemption")
    ]


class RedemptionType:
    """Redemption summary types."""
    SHORT_TERM_LENDING_REPAYMENT_TRANSFER = "SHORT TERM LENDING REPAYMENT TRANSFER"
    MEDIUM_TERM_LENDING_REPAYMENT_TRANSFER = "MEDIUM TERM LENDING REPAYMENT TRANSFER"
   
    CHOICES = [
        (SHORT_TERM_LENDING_REPAYMENT_TRANSFER, "Short Term Lending Repayment Transfer"),
        (MEDIUM_TERM_LENDING_REPAYMENT_TRANSFER, "Medium Term Lending Repayment Transfer")
    ]


class FilterKey:
    """Filter key types for monthly business trends details."""
    FMPP_INVESTMENT = "FMPP_INVESTMENT"
    WITHDRAW_MONEY = "WITHDRAW_MONEY"
    
    CHOICES = [
        (FMPP_INVESTMENT, "FMPP_INVESTMENT"),
        (WITHDRAW_MONEY, "WITHDRAW_MONEY")
    ]


class AccountType:
    """Master account types."""
    LENDER_WALLET = "LENDER_WALLET"


class LendingInvestmentStatus:
    """Lender investment status types."""
    PENDING = "PENDING"


class InvestorActivityType:
    """Investor activity types."""
    ACTIVE_SINCE_LAST_90_DAYS = "ACTIVE_SINCE_LAST_90_DAYS"
    INACTIVE_SINCE_LAST_90_DAYS = "INACTIVE_SINCE_LAST_90_DAYS"
    INACTIVE_WITH_ZERO_AUM = "INACTIVE_WITH_ZERO_AUM"
    
    CHOICES = [
        (ACTIVE_SINCE_LAST_90_DAYS, "Active Since Last 90 Days"),
        (INACTIVE_SINCE_LAST_90_DAYS, "Inactive Since Last 90 Days"),
        (INACTIVE_WITH_ZERO_AUM, "Inactive With Zero AUM")
    ]


class TransactionFilter:
    """Transaction filter categories."""
    CATEGORY_ADD_FUNDS = 'ADD_FUNDS'
    CATEGORY_REPAYMENT = 'REPAYMENT'
    CATEGORY_WITHDRAWAL = 'WITHDRAWAL'
    CATEGORY_AUTO_WITHDRAWAL = 'AUTO_WITHDRAWAL'


class AccountAction:
    """Account action types."""
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


class TransactionActionFilterMap:
    """Maps account actions to wallet transaction types."""
    ACTION_FILTER_MAP = {
        AccountAction.DEBIT: (
            WalletTransactionType.WITHDRAW_MONEY,
            WalletTransactionType.INVESTMENT,
            WalletTransactionType.IDLE_FUND_WITHDRAWAL,
        ),
        AccountAction.CREDIT: (
            WalletTransactionType.ADD_MONEY,
            WalletTransactionType.INVESTMENT_REFUND,
            WalletTransactionType.IDLE_FUND_REFUND,
            WalletTransactionType.INVESTMENT_CANCELLATION,
        )
    }


class TransactionTypeFilterMap:
    """Maps transaction filter categories to transaction types."""
    TYPE_FILTER_MAP = {
        TransactionFilter.CATEGORY_ADD_FUNDS: [
            TransactionType.ADD_MONEY,
        ],
        TransactionFilter.CATEGORY_WITHDRAWAL: [
            TransactionType.WITHDRAW_MONEY,
        ],
        TransactionFilter.CATEGORY_REPAYMENT: [
            TransactionType.MANUAL_REPAYMENT_TRANSFER,
            TransactionType.LUMPSUM_REPAYMENT_TRANSFER,
            TransactionType.MIP_AUTO_WITHDRAWAL,
            TransactionType.MANUAL_LENDING_AUTO_WITHDRAWAL,
            TransactionType.LUMPSUM_AUTO_WITHDRAWAL,
            TransactionType.REPAYMENT_AUTO_WITHDRAWAL,
            TransactionType.AUTO_LENDING_REPAYMENT_WITHDRAWAL,
            TransactionType.AUTO_LENDING_REPAYMENT_ADD_MONEY,
            TransactionType.FMPP_REPAYMENT_WITHDRAWAL
        ],
        TransactionFilter.CATEGORY_AUTO_WITHDRAWAL: [
            TransactionType.IDLE_FUND_WITHDRAWAL,
            TransactionType.CANCELLED_LOAN_REFUND,
            TransactionType.REJECTED_LOAN_REFUND
        ]
    }


class TransactionStatusFilterMap:
    """Maps transaction status filters."""
    STATUS_FILTER_MAP = {
        TransactionStatus.SUCCESS: (TransactionStatus.SUCCESS,),
        TransactionStatus.FAILED: (TransactionStatus.FAILED,),
        TransactionStatus.PROCESSING: (TransactionStatus.PROCESSING, TransactionStatus.PENDING, TransactionStatus.SCHEDULED),
    }


class TransactionSortBy:
    """Transaction sort conditions."""
    SORT_CONDITIONS = {
        'amount_low_high': 'lt.amount ASC',
        'amount_high_low': 'lt.amount DESC',
        'date_low_high': 'lt.created_dtm ASC, lt.id ASC',
        'date_high_low': 'lt.created_dtm DESC, lt.id DESC',
    }


class TimeZone:
    """Timezone constants."""
    indian_time = 'Asia/Kolkata'
    
    
class IdleFundWithdrawalBlockedDates:
    """
    Blocked dates for idle fund withdrawal.
    These dates should be in the format: ['YYYY-MM-DD', ...]
    """
    BLOCKED_DATES = [
        '2025-02-08', '2025-02-09', '2025-02-16', '2025-02-19',
        '2025-02-22', '2025-02-23', '2025-02-26', '2025-03-02',
        '2025-03-08', '2025-03-09', '2025-03-14', '2025-03-16',
        '2025-03-22', '2025-03-23', '2025-03-30', '2025-03-31',
        '2025-04-06', '2025-04-10', '2025-04-12', '2025-04-13',
        '2025-04-14', '2025-04-18', '2025-04-20', '2025-04-26',
        '2025-04-27', '2025-05-01', '2025-05-04', '2025-05-10',
        '2025-05-11', '2025-05-12', '2025-05-18', '2025-05-24',
        '2025-05-25', '2025-06-01', '2025-06-07', '2025-06-08',
        '2025-06-14', '2025-06-15', '2025-06-22', '2025-06-28',
        '2025-06-29', '2025-07-06', '2025-07-12', '2025-07-13',
        '2025-07-20', '2025-07-26', '2025-07-27', '2025-08-03',
        '2025-08-09', '2025-08-10', '2025-08-15', '2025-08-17',
        '2025-08-23', '2025-08-24', '2025-08-27', '2025-08-31',
        '2025-09-05', '2025-09-07', '2025-09-13', '2025-09-14',
        '2025-09-21', '2025-09-27', '2025-09-28', '2025-10-02',
        '2025-10-05', '2025-10-11', '2025-10-12', '2025-10-19',
        '2025-10-21', '2025-10-22', '2025-10-25', '2025-10-26',
        '2025-11-02', '2025-11-05', '2025-11-08', '2025-11-09',
        '2025-11-16', '2025-11-22', '2025-11-23', '2025-11-30',
        '2025-12-07', '2025-12-13', '2025-12-14', '2025-12-21',
        '2025-12-25', '2025-12-27', '2025-12-28'
    ]

class JobProcessIdleFund:
    BATCH_SIZE = 0
    MIN_WITHDRAWAL_AMOUNT = 1
    BLOCK_INVESTMENT_ACCOUNT = [4573596, 4416752, 5181231, 5484943]
    JOB_NAME = "JobProcessIdleFunds"
    SUPPORT_EMAIL = ["bhavesh.vaswani@lendenclub.com", "sandesh.kanagal@lendenclub.com",
                     "namita.mote@lendenclub.com", "sahil.singh@lendenclub.com"]
