-- ============================================================================
-- REPAYMENT SYSTEM - COMPREHENSIVE DATABASE SCHEMA
-- ============================================================================
-- This file contains all database schema definitions for the repayment system
-- including migration logs, processing logs, and related table structures.
-- 
-- Tables:
--   1. t_repayment_migration_logs - Logs migration batches from LMS/PP
--   2. t_repayment_processing_logs - Logs repayment consumption batches
--   3. t_loan_repayment_detail - Repayment transaction details (structure reference)
--   4. t_fee_details - Fee records (structure reference)
--   5. t_redemption_details - Redemption transaction details
--   6. t_redemption_summary - Redemption summary at investment level
--   7. t_lender_redemption - Redemption summary at lender level
--
-- Enum Types:
--   - repayment_purpose
--   - fee_source_type
--   - fee_type_enum
--   - redemption_status_types
--   - investment_types
-- ============================================================================

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Repayment Purpose Enum
-- Used in t_loan_repayment_detail.purpose
DO $$ BEGIN
    CREATE TYPE repayment_purpose AS ENUM (
        'PRINCIPAL',
        'INTEREST',
        'DELAY_INTEREST',
        'OTHER_CHARGES'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE repayment_purpose IS 'Repayment purpose types: PRINCIPAL, INTEREST, DELAY_INTEREST, OTHER_CHARGES';

-- Fee Source Type Enum
-- Used in t_fee_details.fee_source
DO $$ BEGIN
    CREATE TYPE fee_source_type AS ENUM (
        'LOAN',
        'INVESTMENT_LOAN',
        'REDEMPTION'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE fee_source_type IS 'Fee source types: LOAN (migration), INVESTMENT_LOAN (consumption), REDEMPTION';

-- Fee Type Enum
-- Used in t_fee_details.fee_type
DO $$ BEGIN
    CREATE TYPE fee_type_enum AS ENUM (
        'FF',  -- Facilitation Fee
        'CF',  -- Collection Fee
        'RF'   -- Recovery Fee
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE fee_type_enum IS 'Fee types: FF (Facilitation Fee), CF (Collection Fee), RF (Recovery Fee)';

-- Redemption Status Types Enum
-- Used in t_redemption_details, t_redemption_summary, t_lender_redemption
DO $$ BEGIN
    CREATE TYPE redemption_status_types AS ENUM (
        'SCHEDULED',
        'PENDING',
        'SUCCESS'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE redemption_status_types IS 'Redemption status types: SCHEDULED, PENDING, SUCCESS';

-- Redemption Type Enum
-- Used in t_redemption_details, t_redemption_summary, t_lender_redemption
DO $$ BEGIN
    CREATE TYPE redemption_type_enum AS ENUM (
        'REPAYMENT',
        'LOAN_CANCELLATION',
        'LOAN_REJECTION'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE redemption_type_enum IS 'Redemption types: REPAYMENT (normal repayment), LOAN_CANCELLATION (loan cancelled), LOAN_REJECTION (loan rejected)';

-- investment_repayment_transaction_type Types Enum
-- Used in t_redemption_summary.type

DO $$ BEGIN
    CREATE TYPE investment_repayment_transaction_type AS ENUM (
        'MANUAL REPAYMENT TRANSFER',   -- Manual Lending
        'LUMPSUM REPAYMENT TRANSFER',  -- Retail One Time Lending
        'SHORT TERM LENDING REPAYMENT TRANSFER',   -- CP Monthly One Time Lending
        'MEDIUM TERM LENDING REPAYMENT TRANSFER',   -- CP Daily One Time Lending
        'MANUAL LOAN CANCELLATION',   -- Manual Lending Loan Cancellation
        'LUMPSUM LOAN CANCELLATION',  -- Retail One Time Lending Loan Cancellation
        'SHORT TERM LENDING LOAN CANCELLATION',   -- CP Monthly One Time Lending Loan Cancellation
        'MEDIUM TERM LENDING LOAN CANCELLATION'   -- CP Daily One Time Lending Loan Cancellation
        );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE investment_repayment_transaction_type IS 'Redemption summary types: MANUAL REPAYMENT TRANSFER, LUMPSUM REPAYMENT TRANSFER, SHORT TERM LENDING REPAYMENT TRANSFER, MEDIUM TERM LENDING REPAYMENT TRANSFER, MANUAL LOAN CANCELLATION, LUMPSUM LOAN CANCELLATION, SHORT TERM LENDING LOAN CANCELLATION, MEDIUM TERM LENDING LOAN CANCELLATION';

-- ============================================================================
-- MIGRATION LOGS TABLE
-- ============================================================================

-- Table: t_repayment_migration_logs
-- Purpose: Logs repayment migration batches from LMS/PP to Vortex
CREATE TABLE IF NOT EXISTS t_repayment_migration_logs (
    id BIGSERIAL PRIMARY KEY,
    migration_batch_id VARCHAR(30) UNIQUE NOT NULL,
    source_system VARCHAR(10) NOT NULL CHECK (source_system IN ('LMS', 'PP')),
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'NO_DATA', 'FAILED')),
    rows_processed INTEGER DEFAULT 0 NOT NULL,
    fee_records_inserted INTEGER DEFAULT 0 NOT NULL,
    error_message TEXT,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for t_repayment_migration_logs
CREATE INDEX IF NOT EXISTS idx_repayment_migration_logs_status 
    ON t_repayment_migration_logs(status);
CREATE INDEX IF NOT EXISTS idx_repayment_migration_logs_source_system 
    ON t_repayment_migration_logs(source_system);
CREATE INDEX IF NOT EXISTS idx_repayment_migration_logs_created_dtm 
    ON t_repayment_migration_logs(created_dtm);
CREATE INDEX IF NOT EXISTS idx_repayment_migration_logs_migration_batch_id 
    ON t_repayment_migration_logs(migration_batch_id);

-- Comments for t_repayment_migration_logs
COMMENT ON TABLE t_repayment_migration_logs IS 
    'Logs repayment migration batches from LMS/PP to Vortex architecture';
COMMENT ON COLUMN t_repayment_migration_logs.id IS 
    'Primary key, used as migration_id in t_loan_repayment_detail and txn_reference_id in t_fee_details';
COMMENT ON COLUMN t_repayment_migration_logs.migration_batch_id IS 
    'Unique migration batch identifier (format: YYYYMMDDHHMMSS_XXXX, max 30 chars)';
COMMENT ON COLUMN t_repayment_migration_logs.source_system IS 
    'Source system: LMS or PP';
COMMENT ON COLUMN t_repayment_migration_logs.status IS 
    'Migration status: PENDING, PROCESSING, COMPLETED, NO_DATA, FAILED';
COMMENT ON COLUMN t_repayment_migration_logs.rows_processed IS 
    'Number of repayment records processed in this migration batch';
COMMENT ON COLUMN t_repayment_migration_logs.fee_records_inserted IS 
    'Number of fee records inserted in this migration batch';
COMMENT ON COLUMN t_repayment_migration_logs.error_message IS 
    'Error message if migration batch failed';

-- ============================================================================
-- PROCESSING LOGS TABLE
-- ============================================================================

-- Table: t_repayment_processing_logs
-- Purpose: Logs repayment processing/consumption batches
CREATE TABLE IF NOT EXISTS t_repayment_processing_logs (
    id BIGSERIAL PRIMARY KEY,
    batch_id VARCHAR(30) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    total_loans INTEGER DEFAULT 0 NOT NULL,
    processed_loans INTEGER DEFAULT 0 NOT NULL,
    failed_loans INTEGER DEFAULT 0 NOT NULL,
    error_message TEXT,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for t_repayment_processing_logs
CREATE INDEX IF NOT EXISTS idx_repayment_processing_logs_status 
    ON t_repayment_processing_logs(status);
CREATE INDEX IF NOT EXISTS idx_repayment_processing_logs_created_dtm 
    ON t_repayment_processing_logs(created_dtm);
CREATE INDEX IF NOT EXISTS idx_repayment_processing_logs_batch_id 
    ON t_repayment_processing_logs(batch_id);

-- Comments for t_repayment_processing_logs
COMMENT ON TABLE t_repayment_processing_logs IS 
    'Logs repayment processing/consumption batches for distribution to investments';
COMMENT ON COLUMN t_repayment_processing_logs.id IS 
    'Primary key, used as batch_id (BIGINT) in t_loan_repayment_detail, t_redemption_details, and t_fee_details';
COMMENT ON COLUMN t_repayment_processing_logs.batch_id IS 
    'Unique batch identifier string (format: YYYYMMDDHHMMSS_XXXX, max 30 chars)';
COMMENT ON COLUMN t_repayment_processing_logs.status IS 
    'Batch status: PENDING, PROCESSING, COMPLETED, FAILED';
COMMENT ON COLUMN t_repayment_processing_logs.total_loans IS 
    'Total number of loans in this processing batch';
COMMENT ON COLUMN t_repayment_processing_logs.processed_loans IS 
    'Number of successfully processed loans';
COMMENT ON COLUMN t_repayment_processing_logs.failed_loans IS 
    'Number of failed loans';
COMMENT ON COLUMN t_repayment_processing_logs.error_message IS 
    'Error message if batch processing failed';

-- ============================================================================
-- CORE REPAYMENT TABLES
-- ============================================================================

-- Table: t_loan_repayment_detail
-- Purpose: Stores repayment transaction details
CREATE TABLE IF NOT EXISTS t_loan_repayment_detail (
    id SERIAL PRIMARY KEY,
    deleted TIMESTAMP WITH TIME ZONE,
    loan_id BIGINT NOT NULL,
    loan_ref_id VARCHAR(25) NOT NULL,
    purpose repayment_purpose NOT NULL,
    purpose_amount NUMERIC(10, 2) DEFAULT 0 NOT NULL,
    emi_amount NUMERIC(10, 2) DEFAULT 0 NOT NULL,
    total_fees NUMERIC(10, 2) DEFAULT 0 NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE NOT NULL,
    days_past_due INTEGER DEFAULT 0,
    src_txn_id VARCHAR(30) UNIQUE NOT NULL,
    sys_txn_id VARCHAR(30) UNIQUE NOT NULL,
    batch_id BIGINT,  -- References t_repayment_processing_logs.id
    migration_id BIGINT NOT NULL,  -- References t_repayment_migration_logs.id
    ammort_id BIGINT,
    transaction_date DATE,
    settlement_date DATE,
    src_created_dtm TIMESTAMP WITH TIME ZONE NOT NULL,
    sys_created_dtm TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_dtm TIMESTAMP WITH TIME ZONE
);

-- Indexes for t_loan_repayment_detail
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_loan_id 
    ON t_loan_repayment_detail(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_is_processed 
    ON t_loan_repayment_detail(is_processed);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_batch_id 
    ON t_loan_repayment_detail(batch_id);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_migration_id 
    ON t_loan_repayment_detail(migration_id);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_src_txn_id 
    ON t_loan_repayment_detail(src_txn_id);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_detail_sys_txn_id 
    ON t_loan_repayment_detail(sys_txn_id);

-- Comments for t_loan_repayment_detail
COMMENT ON TABLE t_loan_repayment_detail IS 
    'Stores repayment transaction details from migration and consumption flows';
COMMENT ON COLUMN t_loan_repayment_detail.sys_txn_id IS 
    'System transaction ID (generated by trigger)';
COMMENT ON COLUMN t_loan_repayment_detail.batch_id IS 
    'References t_repayment_processing_logs.id - links to repayment consumption batch';
COMMENT ON COLUMN t_loan_repayment_detail.migration_id IS 
    'References t_repayment_migration_logs.id - links to repayment migration batch';

-- Table: t_fee_details
-- Purpose: Stores fee records for loans, investments, and redemptions
CREATE TABLE IF NOT EXISTS t_fee_details (
    id SERIAL PRIMARY KEY,
    fee_source_id BIGINT NOT NULL,
    fee_source fee_source_type NOT NULL,
    fee_type fee_type_enum NOT NULL,
    fee_amount NUMERIC(10, 4) DEFAULT 0.00 NOT NULL,
    fee_levy_date DATE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    txn_reference_id BIGINT  -- References t_repayment_migration_logs.id (for migration) or t_repayment_processing_logs.id (for consumption)
);

-- Indexes for t_fee_details
CREATE INDEX IF NOT EXISTS idx_fee_details_fee_source_id 
    ON t_fee_details(fee_source_id);
CREATE INDEX IF NOT EXISTS idx_fee_details_txn_reference_id 
    ON t_fee_details(txn_reference_id);
CREATE INDEX IF NOT EXISTS idx_fee_details_fee_source 
    ON t_fee_details(fee_source);
CREATE INDEX IF NOT EXISTS idx_fee_details_fee_type 
    ON t_fee_details(fee_type);

-- Comments for t_fee_details
COMMENT ON TABLE t_fee_details IS 
    'Stores fee records for loans, investments, and redemptions';
COMMENT ON COLUMN t_fee_details.fee_source_id IS 
    'ID of the source entity (loan_repayment_detail.id, investment_loan_id, redemption_detail.id)';
COMMENT ON COLUMN t_fee_details.txn_reference_id IS 
    'References t_repayment_migration_logs.id (for migration) or t_repayment_processing_logs.id (for consumption)';

-- Table: t_investment_loan_repayment_summary
-- Purpose: Aggregates repayment totals at investment_loan level
CREATE TABLE IF NOT EXISTS t_investment_loan_repayment_summary (
    investment_loan_id BIGINT NOT NULL PRIMARY KEY,
    deleted TIMESTAMP WITH TIME ZONE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_dtm TIMESTAMP WITH TIME ZONE,
    total_amount_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_interest_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_fee_levied NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    principal_outstanding NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_npa_amount NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    amount_to_distribute NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    principal_to_distribute NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    interest_to_distribute NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    fee_to_distribute NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    total_adjustment_amount NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL
);

-- Indexes for t_investment_loan_repayment_summary
CREATE INDEX IF NOT EXISTS idx_investment_loan_repayment_summary_investment_loan_id 
    ON t_investment_loan_repayment_summary(investment_loan_id);

-- Comments for t_investment_loan_repayment_summary
COMMENT ON TABLE t_investment_loan_repayment_summary IS 
    'Aggregates repayment totals at investment_loan level for distribution calculations';
COMMENT ON COLUMN t_investment_loan_repayment_summary.investment_loan_id IS 
    'References t_investment_loan_detail.id (primary key)';
COMMENT ON COLUMN t_investment_loan_repayment_summary.amount_to_distribute IS 
    'Amount available for distribution to lenders (precision 4)';
COMMENT ON COLUMN t_investment_loan_repayment_summary.principal_to_distribute IS 
    'Principal available for distribution (precision 4)';
COMMENT ON COLUMN t_investment_loan_repayment_summary.interest_to_distribute IS 
    'Interest available for distribution (precision 4)';
COMMENT ON COLUMN t_investment_loan_repayment_summary.fee_to_distribute IS 
    'Fee available for distribution (precision 4)';

-- ============================================================================
-- INVESTMENT SYSTEM - TABLES
-- ============================================================================

-- Table: t_lender_investment
-- Purpose: Stores lender investment details
CREATE TABLE IF NOT EXISTS t_lender_investment (
    id                          SERIAL PRIMARY KEY,
    deleted                     TIMESTAMP WITH TIME ZONE,
    created_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm                 TIMESTAMP WITH TIME ZONE,
    product_config_id           INTEGER,
    investment_id               VARCHAR(30) DEFAULT nextval('t_lender_investment_investment_id_seq'::regclass) NOT NULL UNIQUE,
    lender_id                   INTEGER REFERENCES t_lender(id),
    amount_lent_on_investment   NUMERIC(10, 2) DEFAULT 0.00,
    actual_principal_lent       NUMERIC(10, 2) DEFAULT 0.00,
    actual_closure_date         TIMESTAMP WITH TIME ZONE,
    expected_closure_date       DATE,
    order_id                    VARCHAR(30),
    total_amount_redeemed       NUMERIC(10, 2) DEFAULT 0.00,
    total_amount_refunded       NUMERIC(10, 2) DEFAULT 0.00,
    total_amount_received       NUMERIC(10, 2) DEFAULT 0.00,
    total_principal_received   NUMERIC(10, 2) DEFAULT 0.00,
    total_interest_received     NUMERIC(10, 2) DEFAULT 0.00,
    total_fee_levied            NUMERIC(10, 2) DEFAULT 0.00,
    total_amount_adjusted       NUMERIC(10, 7) DEFAULT 0.0000000,
    total_npa_amount            NUMERIC(10, 2) DEFAULT 0.00,
    total_principal_outstanding NUMERIC(10, 2) DEFAULT 0.00,
    balance                     NUMERIC(10, 2) DEFAULT 0.00,
    is_negotiated               BOOLEAN DEFAULT FALSE,
    source_transaction_id       VARCHAR(50),
    investment_type_id          BIGINT,
    cancelled_loan_amount       NUMERIC(10, 2) DEFAULT 0.00 NOT NULL
);

-- Sequence for t_lender_investment.investment_id
CREATE SEQUENCE IF NOT EXISTS t_lender_investment_investment_id_seq;

-- Indexes for t_lender_investment
CREATE INDEX IF NOT EXISTS idx_lender_investment_lender_id 
    ON t_lender_investment(lender_id);
CREATE INDEX IF NOT EXISTS idx_lender_investment_investment_id 
    ON t_lender_investment(investment_id);
CREATE INDEX IF NOT EXISTS idx_lender_investment_product_config_id 
    ON t_lender_investment(product_config_id);

-- Comments for t_lender_investment
COMMENT ON TABLE t_lender_investment IS 'Stores lender investment details';
COMMENT ON COLUMN t_lender_investment.investment_id IS 'Unique investment identifier (generated by sequence)';
COMMENT ON COLUMN t_lender_investment.lender_id IS 'References t_lender.id';
COMMENT ON COLUMN t_lender_investment.product_config_id IS 'References t_investment_product_config.id';

-- Table: t_investment_loan_detail
-- Purpose: Stores investment allocation to loans
CREATE TABLE IF NOT EXISTS t_investment_loan_detail (
    id                    BIGSERIAL PRIMARY KEY,
    deleted               TIMESTAMP WITH TIME ZONE,
    created_dtm           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm           TIMESTAMP WITH TIME ZONE,
    investment_amount     NUMERIC(10, 2) DEFAULT 0.00,
    allocation_percentage NUMERIC(5, 2) DEFAULT 0.00,
    loan_id               INTEGER,
    investment_id         INTEGER REFERENCES t_lender_investment(id),
    is_negotiated         BOOLEAN DEFAULT FALSE,
    has_lent              BOOLEAN DEFAULT TRUE,
    is_cancelled          BOOLEAN DEFAULT FALSE
);

-- Indexes for t_investment_loan_detail
CREATE INDEX IF NOT EXISTS idx_investment_loan_detail_loan_id 
    ON t_investment_loan_detail(loan_id);
CREATE INDEX IF NOT EXISTS idx_investment_loan_detail_investment_id 
    ON t_investment_loan_detail(investment_id);
CREATE INDEX IF NOT EXISTS idx_investment_loan_detail_loan_investment 
    ON t_investment_loan_detail(loan_id, investment_id);

-- Comments for t_investment_loan_detail
COMMENT ON TABLE t_investment_loan_detail IS 'Stores investment allocation to loans with allocation percentages';
COMMENT ON COLUMN t_investment_loan_detail.investment_id IS 'References t_lender_investment.id';
COMMENT ON COLUMN t_investment_loan_detail.loan_id IS 'References t_loan.id';
COMMENT ON COLUMN t_investment_loan_detail.allocation_percentage IS 'Percentage of loan allocated to this investment';

-- ============================================================================
-- RELATED TABLES (Referenced but not created here)
-- ============================================================================

-- t_loan_repayment_summary
-- Used for: Loan-level repayment totals
-- Key columns: loan_id, principal_received, interest_received, fee_levied, total_amount_received

-- t_redemption_details
-- Used for: Redemption records created during consumption
-- Key columns: investment_loan_id, lender_id, amount_received, batch_id

-- t_loan
-- Used for: Loan master data
-- Key columns: id, loan_ref_id

-- t_borrowers
-- Used for: Borrower master data
-- Key columns: id, source_id

-- ============================================================================
-- RELATIONSHIPS AND CONSTRAINTS
-- ============================================================================

-- Foreign Key Relationships (if not already defined):
-- Note: These are logical relationships. Actual foreign keys may or may not exist.

-- t_loan_repayment_detail.migration_id -> t_repayment_migration_logs.id
-- ALTER TABLE t_loan_repayment_detail 
--     ADD CONSTRAINT fk_repayment_detail_migration 
--     FOREIGN KEY (migration_id) REFERENCES t_repayment_migration_logs(id);

-- t_loan_repayment_detail.batch_id -> t_repayment_processing_logs.id
-- ALTER TABLE t_loan_repayment_detail 
--     ADD CONSTRAINT fk_repayment_detail_batch 
--     FOREIGN KEY (batch_id) REFERENCES t_repayment_processing_logs(id);

-- t_fee_details.txn_reference_id -> t_repayment_migration_logs.id OR t_repayment_processing_logs.id
-- (Logical relationship - may reference either table depending on context)

-- ============================================================================
-- DATA FLOW SUMMARY
-- ============================================================================

-- MIGRATION FLOW:
-- 1. Create entry in t_repayment_migration_logs -> get migration_id (PK)
-- 2. Insert into t_loan_repayment_detail with migration_id
-- 3. Insert into t_fee_details with txn_reference_id = migration_id
-- 4. Update t_repayment_migration_logs with status and metrics

-- CONSUMPTION FLOW:
-- 1. Generate batch_id_str (VARCHAR(30))
-- 2. SP creates entry in t_repayment_processing_logs -> get batch_id (PK)
-- 3. Process repayments and update t_loan_repayment_detail.batch_id
-- 4. Insert into t_redemption_details with batch_id
-- 5. Insert into t_fee_details with txn_reference_id = batch_id
-- 6. Update t_repayment_processing_logs with status and metrics

-- ============================================================================
-- BATCH ID FORMATS
-- ============================================================================

-- Migration Batch ID Format:
--   Format: YYYYMMDDHHMMSS_XXXX
--   Example: 20241201143025_1234
--   Max Length: 30 characters
--   Generated: PostgreSQL stored procedure
--   Stored In: t_repayment_migration_logs.migration_batch_id

-- Processing Batch ID Format:
--   Format: YYYYMMDDHHMMSS_XXXX
--   Example: 20241201143025_5678
--   Max Length: 30 characters
--   Generated: Python Flow layer (RepaymentConsumptionFlow.generate_batch_id())
--   Stored In: t_repayment_processing_logs.batch_id

-- ============================================================================
-- STATUS VALUES
-- ============================================================================

-- t_repayment_migration_logs.status:
--   - PENDING: Initial state (not used currently, SP creates as PROCESSING)
--   - PROCESSING: Migration in progress
--   - COMPLETED: Migration completed successfully
--   - NO_DATA: No records found to migrate
--   - FAILED: Migration failed with error

-- t_repayment_processing_logs.status:
--   - PENDING: Initial state (not used currently, SP creates as PROCESSING)
--   - PROCESSING: Batch processing in progress
--   - COMPLETED: Batch processed successfully
--   - FAILED: Batch processing failed with error

-- ============================================================================
-- KEY COLUMN USAGE
-- ============================================================================

-- t_repayment_migration_logs.id (migration_id):
--   - Used in: t_loan_repayment_detail.migration_id
--   - Used in: t_fee_details.txn_reference_id (for migration fees)
--   - Purpose: Links repayment records to migration batch

-- t_repayment_processing_logs.id (batch_id):
--   - Used in: t_loan_repayment_detail.batch_id
--   - Used in: t_redemption_details.batch_id
--   - Used in: t_fee_details.txn_reference_id (for consumption fees)
--   - Purpose: Links repayment records to processing batch

-- ============================================================================
-- REDEMPTION TABLES
-- ============================================================================

-- Table: t_redemption_details
-- Purpose: Stores individual redemption transaction details
CREATE TABLE IF NOT EXISTS t_redemption_details (
    id BIGSERIAL PRIMARY KEY,
    deleted TIMESTAMP WITH TIME ZONE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE,
    investment_loan_id BIGINT NOT NULL,
    lender_id BIGINT NOT NULL,
    redemption_id BIGINT,  -- References t_lender_redemption.id
    amount_redeemed NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    amount_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    fee_levied NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    principal_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    interest_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    batch_id BIGINT NOT NULL,  -- References t_repayment_processing_logs.id
    redemption_status redemption_status_types NOT NULL DEFAULT 'SCHEDULED',
    redemption_type redemption_type_enum DEFAULT 'REPAYMENT' NOT NULL
);

-- Indexes for t_redemption_details
CREATE INDEX IF NOT EXISTS idx_redemption_details_lender_id 
    ON t_redemption_details(lender_id);
CREATE INDEX IF NOT EXISTS idx_redemption_details_investment_loan_id 
    ON t_redemption_details(investment_loan_id);
CREATE INDEX IF NOT EXISTS idx_redemption_details_redemption_status 
    ON t_redemption_details(redemption_status);
CREATE INDEX IF NOT EXISTS idx_redemption_details_redemption_id 
    ON t_redemption_details(redemption_id);
CREATE INDEX IF NOT EXISTS idx_redemption_details_batch_id 
    ON t_redemption_details(batch_id);
CREATE INDEX IF NOT EXISTS idx_redemption_details_redemption_status_null 
    ON t_redemption_details(redemption_status, redemption_id) 
    WHERE redemption_status = 'SCHEDULED' AND redemption_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_redemption_details_redemption_type 
    ON t_redemption_details(redemption_type);
CREATE INDEX IF NOT EXISTS idx_redemption_details_redemption_type_status 
    ON t_redemption_details(redemption_type, redemption_status, redemption_id) 
    WHERE redemption_type = 'REPAYMENT' AND redemption_status = 'SCHEDULED' AND redemption_id IS NULL;

-- Comments for t_redemption_details
COMMENT ON TABLE t_redemption_details IS 
    'Stores individual redemption transaction details created during repayment consumption';
COMMENT ON COLUMN t_redemption_details.investment_loan_id IS 
    'References t_investment_loan_detail.id';
COMMENT ON COLUMN t_redemption_details.lender_id IS 
    'References t_lender.id';
COMMENT ON COLUMN t_redemption_details.redemption_id IS 
    'References t_lender_redemption.id - links redemption details to lender-level redemption transaction';
COMMENT ON COLUMN t_redemption_details.batch_id IS 
    'References t_repayment_processing_logs.id - links to repayment consumption batch';
COMMENT ON COLUMN t_redemption_details.redemption_status IS 
    'Redemption status: SCHEDULED (initial), PENDING (processing), SUCCESS (completed)';
COMMENT ON COLUMN t_redemption_details.amount_redeemed IS 
    'Amount to be redeemed (updated via callback API)';
COMMENT ON COLUMN t_redemption_details.amount_received IS 
    'Amount received from repayment consumption';
COMMENT ON COLUMN t_redemption_details.redemption_type IS 
    'Redemption type: REPAYMENT (normal repayment), LOAN_CANCELLATION (loan cancelled), LOAN_REJECTION (loan rejected)';

-- Table: t_redemption_summary
-- Purpose: Aggregates redemption at investment level (lender_id + investment_id)
CREATE TABLE IF NOT EXISTS t_redemption_summary (
    id BIGSERIAL PRIMARY KEY,
    deleted TIMESTAMP WITH TIME ZONE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE,
    lender_id BIGINT NOT NULL,
    investment_id BIGINT NOT NULL,
    total_amount_redeemed NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_amount_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_interest NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_fee_levied NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    type redemption_summary_types NOT NULL,
    redemption_status redemption_status_types NOT NULL DEFAULT 'SCHEDULED',
    urn_id VARCHAR(100) NOT NULL DEFAULT '' UNIQUE,  -- Generated by trigger
    redemption_id BIGINT,  -- References t_lender_redemption.id
    redemption_type redemption_type_enum DEFAULT 'REPAYMENT' NOT NULL
);

-- Indexes for t_redemption_summary
CREATE INDEX IF NOT EXISTS idx_redemption_summary_lender_id 
    ON t_redemption_summary(lender_id);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_investment_id 
    ON t_redemption_summary(investment_id);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_redemption_status 
    ON t_redemption_summary(redemption_status);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_redemption_id 
    ON t_redemption_summary(redemption_id);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_urn_id 
    ON t_redemption_summary(urn_id);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_lender_investment 
    ON t_redemption_summary(lender_id, investment_id);
CREATE INDEX IF NOT EXISTS idx_redemption_summary_redemption_type 
    ON t_redemption_summary(redemption_type);

-- Comments for t_redemption_summary
COMMENT ON TABLE t_redemption_summary IS 
    'Aggregates redemption at investment level (one record per lender_id + investment_id combination)';
COMMENT ON COLUMN t_redemption_summary.lender_id IS 
    'References t_lender.id';
COMMENT ON COLUMN t_redemption_summary.investment_id IS 
    'References t_lender_investment.id';
COMMENT ON COLUMN t_redemption_summary.type IS 
    'Investment type: ML (product_config_id=1), OTL (product_config_id=2), MTL (product_config_id=3)';
COMMENT ON COLUMN t_redemption_summary.redemption_id IS 
    'References t_lender_redemption.id - links to lender-level redemption transaction';
COMMENT ON COLUMN t_redemption_summary.urn_id IS 
    'Unique redemption identifier (generated by trigger)';
COMMENT ON COLUMN t_redemption_summary.redemption_type IS 
    'Redemption type: REPAYMENT (normal repayment), LOAN_CANCELLATION (loan cancelled), LOAN_REJECTION (loan rejected)';

-- Table: t_lender_redemption
-- Purpose: Aggregates redemption at lender level (one record per lender per batch)
CREATE TABLE IF NOT EXISTS t_lender_redemption (
    id BIGSERIAL PRIMARY KEY,
    deleted TIMESTAMP WITH TIME ZONE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE,
    lender_id BIGINT NOT NULL,
    total_amount_redeemed NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_amount_received NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_interest NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_fee_levied NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    redemption_status investment_repayment_transaction_type NOT NULL DEFAULT 'SCHEDULED',
    urn_id VARCHAR(100) NOT NULL DEFAULT '' UNIQUE,  -- Generated by trigger
    status_dtm TIMESTAMP WITH TIME ZONE,
    redemption_type redemption_type_enum DEFAULT 'REPAYMENT' NOT NULL
);

-- Indexes for t_lender_redemption
CREATE INDEX IF NOT EXISTS idx_lender_redemption_lender_id 
    ON t_lender_redemption(lender_id);
CREATE INDEX IF NOT EXISTS idx_lender_redemption_redemption_status 
    ON t_lender_redemption(redemption_status);
CREATE INDEX IF NOT EXISTS idx_lender_redemption_urn_id 
    ON t_lender_redemption(urn_id);
CREATE INDEX IF NOT EXISTS idx_lender_redemption_redemption_type 
    ON t_lender_redemption(redemption_type);

-- Comments for t_lender_redemption
COMMENT ON TABLE t_lender_redemption IS 
    'Aggregates redemption at lender level (one record per lender per redemption batch)';
COMMENT ON COLUMN t_lender_redemption.lender_id IS 
    'References t_lender.id';
COMMENT ON COLUMN t_lender_redemption.redemption_status IS 
    'Redemption status: SCHEDULED (initial), PENDING (processing), SUCCESS (completed)';
COMMENT ON COLUMN t_lender_redemption.urn_id IS 
    'Unique redemption identifier (generated by trigger)';
COMMENT ON COLUMN t_lender_redemption.status_dtm IS 
    'Timestamp when status was last updated';
COMMENT ON COLUMN t_lender_redemption.redemption_type IS 
    'Redemption type: REPAYMENT (normal repayment), LOAN_CANCELLATION (loan cancelled), LOAN_REJECTION (loan rejected)';


create table if not exists t_product_repayment_transaction_config_mapping(
    id serial primary key ,
    product_config_id           integer
        references t_investment_product_config,
    repayment_type investment_repayment_transaction_type
);
-- ============================================================================
-- SYS_TXN_ID GENERATION TRIGGER
-- ============================================================================

-- Function to generate sys_txn_id for t_loan_repayment_detail
-- Format: YYYYMMDDHHMMSS_XXXX where XXXX is microseconds-based sequence (max 30 chars)
CREATE OR REPLACE FUNCTION generate_sys_txn_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sys_txn_id IS NULL OR NEW.sys_txn_id = '' THEN
        -- Generate unique sys_txn_id: YYYYMMDDHHMMSS_XXXX (format matches batch_id pattern)
        NEW.sys_txn_id := TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '_' || 
                         LPAD((EXTRACT(MICROSECONDS FROM NOW())::BIGINT % 10000)::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for t_loan_repayment_detail sys_txn_id generation
DROP TRIGGER IF EXISTS trg_loan_repayment_detail_sys_txn_id ON t_loan_repayment_detail;
CREATE TRIGGER trg_loan_repayment_detail_sys_txn_id
    BEFORE INSERT ON t_loan_repayment_detail
    FOR EACH ROW
    EXECUTE FUNCTION generate_sys_txn_id();

-- ============================================================================
-- URN ID GENERATION TRIGGERS
-- ============================================================================

-- Function to generate URN ID for t_redemption_summary
-- Generates unique URN based on timestamp and microseconds
CREATE OR REPLACE FUNCTION generate_redemption_summary_urn_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.urn_id IS NULL OR NEW.urn_id = '' THEN
        -- Generate unique URN: REDSUM_YYYYMMDD_HHMMSS_XXXX
        NEW.urn_id := 'REDSUM_' || TO_CHAR(NOW(), 'YYYYMMDD') || '_' || 
                     TO_CHAR(NOW(), 'HH24MISS') || '_' ||
                     LPAD((EXTRACT(MICROSECONDS FROM NOW())::BIGINT % 10000)::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for t_redemption_summary URN ID generation
DROP TRIGGER IF EXISTS trg_redemption_summary_urn_id ON t_redemption_summary;
CREATE TRIGGER trg_redemption_summary_urn_id
    BEFORE INSERT ON t_redemption_summary
    FOR EACH ROW
    EXECUTE FUNCTION generate_redemption_summary_urn_id();

-- Function to generate URN ID for t_lender_redemption
-- Generates unique URN based on timestamp and microseconds
CREATE OR REPLACE FUNCTION generate_lender_redemption_urn_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.urn_id IS NULL OR NEW.urn_id = '' THEN
        -- Generate unique URN: REDLDR_YYYYMMDD_HHMMSS_XXXX
        NEW.urn_id := 'REDLDR_' || TO_CHAR(NOW(), 'YYYYMMDD') || '_' || 
                     TO_CHAR(NOW(), 'HH24MISS') || '_' ||
                     LPAD((EXTRACT(MICROSECONDS FROM NOW())::BIGINT % 10000)::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for t_lender_redemption URN ID generation
DROP TRIGGER IF EXISTS trg_lender_redemption_urn_id ON t_lender_redemption;
CREATE TRIGGER trg_lender_redemption_urn_id
    BEFORE INSERT ON t_lender_redemption
    FOR EACH ROW
    EXECUTE FUNCTION generate_lender_redemption_urn_id();

-- ============================================================================
-- LOAN SYSTEM - ENUM TYPES
-- ============================================================================

-- Loan Status Enum
-- Status flow: HOLD -> LIVE -> FUNDED -> DISBURSED -> CLOSED
--              -> NPA (can occur from any status)
--              -> CANCELLED (can occur from any status)
DO $$ BEGIN
    CREATE TYPE loan_status AS ENUM (
        'HOLD',
        'LIVE',
        'FUNDED',
        'DISBURSED',
        'CLOSED',
        'NPA',
        'CANCELLED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE loan_status IS 'Loan status types: HOLD -> LIVE -> FUNDED -> DISBURSED -> CLOSED, or NPA/CANCELLED';

-- Loan Repayment Frequency Enum
DO $$ BEGIN
    CREATE TYPE loan_repayment_frequency AS ENUM (
        'DAILY',
        'MONTHLY'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE loan_repayment_frequency IS 'Loan repayment frequency: DAILY, MONTHLY';

-- Source Enum
DO $$ BEGIN
    CREATE TYPE loan_source_enum AS ENUM (
        'MONO',
        'MICRO',
        'PP',
        'LMS'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE loan_source_enum IS 'Source systems: MONO, MICRO, PP, LMS';

-- Partner Code Enum
DO $$ BEGIN
    CREATE TYPE loan_partner_code_enum AS ENUM (
        'EPF',
        'IM',
        'RAJ',
        'MSM',
        'FP',
        'PP',
        'KL',
        'SM',
        'CT',
        'IM+'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE loan_partner_code_enum IS 'Partner codes: EPF, IM, RAJ, MSM, FP, PP, KL, SM, CT, IM+';

-- ============================================================================
-- LOAN SYSTEM - TABLES
-- ============================================================================

-- Borrowers Table
CREATE TABLE IF NOT EXISTS t_borrowers (
    id            BIGSERIAL PRIMARY KEY,
    deleted       TIMESTAMP WITH TIME ZONE,
    created_dtm   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_dtm   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    source        VARCHAR(10),
    source_id     VARCHAR(100),
    CONSTRAINT t_borrowers_source_source_id_b61b7246_uniq
        UNIQUE (source, source_id)
);

COMMENT ON TABLE t_borrowers IS 'Borrower information from external systems';
COMMENT ON COLUMN t_borrowers.source IS 'Source system: MONO, MICRO, PP, LMS';
COMMENT ON COLUMN t_borrowers.source_id IS 'Borrower ID in the source system';

-- Loan Product Config Table
CREATE TABLE IF NOT EXISTS t_loan_product_config (
    id           SERIAL PRIMARY KEY,
    deleted      TIMESTAMP WITH TIME ZONE,
    created_dtm  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_dtm  TIMESTAMP WITH TIME ZONE,
    source       loan_source_enum NOT NULL,
    partner_code loan_partner_code_enum NOT NULL,
    tenure       SMALLINT NOT NULL,
    is_live_enabled BOOLEAN DEFAULT TRUE NOT NULL
);

COMMENT ON TABLE t_loan_product_config IS 'Loan product configuration for different sources and partners';
COMMENT ON COLUMN t_loan_product_config.tenure IS 'Loan tenure in months';
COMMENT ON COLUMN t_loan_product_config.is_live_enabled IS 'If true, loans start as LIVE status, else HOLD';

-- Loan Fees Config Table
CREATE TABLE IF NOT EXISTS t_loan_fees_config (
    id                          SERIAL PRIMARY KEY,
    created_dtm                 TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    config_id                   VARCHAR(10) UNIQUE NOT NULL,
    repayment_frequency         loan_repayment_frequency NOT NULL,
    source                      loan_source_enum NOT NULL,
    partner_code                loan_partner_code_enum NOT NULL,
    tenure                      SMALLINT NOT NULL,
    facilitation_fee_percentage NUMERIC(5, 2) NOT NULL,
    collection_fee_percentage   NUMERIC(5, 2) NOT NULL,
    recovery_fee_percentage     NUMERIC(5, 2) NOT NULL,
    CONSTRAINT unique_cig_config_combination
        UNIQUE (source, partner_code, tenure, facilitation_fee_percentage, collection_fee_percentage, recovery_fee_percentage)
);

COMMENT ON TABLE t_loan_fees_config IS 'Loan fees configuration with unique config_id (LC0001, LC0002, etc.)';
COMMENT ON COLUMN t_loan_fees_config.config_id IS 'Generated config ID format: LC0001, LC0002, etc.';

-- Loan Table
CREATE TABLE IF NOT EXISTS t_loan (
    id                     BIGSERIAL PRIMARY KEY,
    deleted                TIMESTAMP WITH TIME ZONE,
    created_dtm            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_dtm            TIMESTAMP WITH TIME ZONE,
    loan_product_config_id INTEGER NOT NULL,
    loan_ref_id            VARCHAR(25) NOT NULL,
    amount                 NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    interest_rate          NUMERIC(4, 2) DEFAULT 0.00 NOT NULL,
    is_modified_roi        BOOLEAN DEFAULT FALSE NOT NULL,
    expected_repayment_sum  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    first_repayment_date    DATE NOT NULL,
    last_repayment_date    DATE NOT NULL,
    borrower_name          VARCHAR(100),
    borrower_age           SMALLINT,
    borrower_type          VARCHAR(20) NOT NULL,
    risk_type              VARCHAR(10) NOT NULL,
    ldc_score              INTEGER NOT NULL,
    income                 NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    repayment_frequency    loan_repayment_frequency NOT NULL,
    tenure                 SMALLINT NOT NULL,
    status                 loan_status NOT NULL,
    status_date            DATE,
    investment_amount_sum  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    remaining_amount       NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    liquidation_date       DATE,
    urn_id                 VARCHAR(20) NOT NULL,
    fees_config_id         VARCHAR(10),
    borrower_id            BIGINT NOT NULL,
    funding_notified_dtm   TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE t_loan IS 'Loan/CIG records with unique urn_id (CIGL + sequence)';
COMMENT ON COLUMN t_loan.urn_id IS 'Unique loan identifier format: CIGL + 16-digit sequence (e.g., CIGL0000000000000001)';
COMMENT ON COLUMN t_loan.loan_ref_id IS 'Loan reference ID from source system';
COMMENT ON COLUMN t_loan.status IS 'Loan status: HOLD, LIVE, FUNDED, DISBURSED, CLOSED, NPA, CANCELLED';

-- Loan Repayment Summary Table
CREATE TABLE IF NOT EXISTS t_loan_repayment_summary (
    loan_id               BIGINT NOT NULL PRIMARY KEY REFERENCES t_loan(id),
    loan_ref_id           VARCHAR(25),
    principal_received    NUMERIC(10, 2) DEFAULT 0.00,
    interest_received      NUMERIC(10, 2) DEFAULT 0.00,
    fee_levied             NUMERIC(10, 2) DEFAULT 0.00,
    total_amount_received  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    principal_outstanding  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    npa_amount             NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    npa_as_on_date         DATE,
    days_past_due          SMALLINT DEFAULT 0,
    created_dtm            TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm            TIMESTAMP WITH TIME ZONE,
    deleted                TIMESTAMP WITH TIME ZONE
);

-- Indexes for t_loan_repayment_summary
CREATE INDEX IF NOT EXISTS idx_loan_repayment_summary_loan_id 
    ON t_loan_repayment_summary(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_repayment_summary_loan_ref_id 
    ON t_loan_repayment_summary(loan_ref_id);

-- Comments for t_loan_repayment_summary
COMMENT ON TABLE t_loan_repayment_summary IS 'Loan repayment summary tracking principal, interest, fees, and outstanding amounts';
COMMENT ON COLUMN t_loan_repayment_summary.loan_id IS 'Primary key, references t_loan.id';
COMMENT ON COLUMN t_loan_repayment_summary.principal_received IS 'Total principal amount received';
COMMENT ON COLUMN t_loan_repayment_summary.interest_received IS 'Total interest amount received';
COMMENT ON COLUMN t_loan_repayment_summary.fee_levied IS 'Total fees levied';
COMMENT ON COLUMN t_loan_repayment_summary.total_amount_received IS 'Total amount received (principal + interest)';
COMMENT ON COLUMN t_loan_repayment_summary.principal_outstanding IS 'Outstanding principal amount';
COMMENT ON COLUMN t_loan_repayment_summary.npa_amount IS 'Non-performing asset amount';
COMMENT ON COLUMN t_loan_repayment_summary.days_past_due IS 'Number of days past due';

-- Loan Modified Offer Table
CREATE TABLE IF NOT EXISTS t_loan_modified_offer (
    id                    BIGSERIAL PRIMARY KEY,
    deleted               TIMESTAMP WITH TIME ZONE,
    created_dtm           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    actual_interest_rate  NUMERIC(5, 2) NOT NULL,
    modified_interest_rate NUMERIC(5, 2) NOT NULL,
    loan_id               BIGINT REFERENCES t_loan(id)
);

COMMENT ON TABLE t_loan_modified_offer IS 'Records modified ROI offers for loans';

-- ============================================================================
-- LOAN SYSTEM - FUNCTIONS
-- ============================================================================

-- Sequence for URN ID generation
CREATE SEQUENCE IF NOT EXISTS cig_urn_seq
    START WITH 1
    INCREMENT BY 1
    MINVALUE 1;

COMMENT ON SEQUENCE cig_urn_seq IS 'Sequence for generating unique sequence part in loan URN ID (padded to 16 digits)';

-- Function to generate Loan URN ID (CIGL + sequence)
CREATE OR REPLACE FUNCTION fn_generate_loan_urn_id()
RETURNS VARCHAR(100) AS
$$
DECLARE
    v_seq_part TEXT;
    v_id TEXT;
BEGIN
    -- Take next sequence value and pad to 16 digits to make total 20 chars (CIGL = 4 chars + 16 digits = 20 chars)
    v_seq_part := LPAD(nextval('cig_urn_seq')::text, 16, '0');
    
    -- Build URN ID: CIGL prefix (4 chars) + sequence (16 digits) = 20 chars total
    v_id := 'CIGL' || v_seq_part;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_generate_loan_urn_id() IS 'Generates unique loan URN ID in format CIGL + 16-digit sequence (e.g., CIGL0000000000000001)';

-- Function to generate Fees Config ID (LC + 4 digits)
CREATE OR REPLACE FUNCTION fn_generate_fees_config_id()
RETURNS VARCHAR(10) AS
$$
DECLARE
    v_config_id VARCHAR(10);
    v_sequence INTEGER;
BEGIN
    -- Get next sequence value from max existing config_id
    SELECT COALESCE(MAX(CAST(SUBSTRING(config_id FROM 3) AS INTEGER)), 0) + 1
    INTO v_sequence
    FROM t_loan_fees_config
    WHERE config_id LIKE 'LC%'
      AND LENGTH(config_id) = 6;
    
    -- Format: LC + 4 zero-padded digits
    v_config_id := 'LC' || LPAD(v_sequence::TEXT, 4, '0');
    
    RETURN v_config_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_generate_fees_config_id() IS 'Generates unique fees config ID in format LC + 4 digits (e.g., LC0001, LC0002)';

-- ============================================================================
-- LOAN SYSTEM - TRIGGERS
-- ============================================================================

-- Trigger to auto-generate URN ID for t_loan
CREATE OR REPLACE FUNCTION trg_generate_loan_urn_id()
RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.urn_id IS NULL OR NEW.urn_id = '' THEN
        NEW.urn_id := fn_generate_loan_urn_id();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_loan_urn_id
    BEFORE INSERT ON t_loan
    FOR EACH ROW
    WHEN (NEW.urn_id IS NULL OR NEW.urn_id = '')
    EXECUTE FUNCTION trg_generate_loan_urn_id();

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. sys_txn_id in t_loan_repayment_detail is generated by database trigger
-- 2. batch_id in t_loan_repayment_detail is updated by prc_process_repayments
-- 3. migration_id in t_loan_repayment_detail is set during migration
-- 4. txn_reference_id in t_fee_details can reference either migration_logs or processing_logs
-- 5. All timestamps use TIMESTAMP WITH TIME ZONE for consistency
-- 6. Batch ID strings are limited to 30 characters to match VARCHAR(30) constraint
-- 7. Purpose validation: Only PRINCIPAL, INTEREST, DELAY_INTEREST, OTHER_CHARGES are processed
-- 8. Invalid purposes are skipped (not forced to default)
-- 9. Fee records are created only if fee_amount > 0
-- 10. Recovery fee (RF) is deducted from interest/principal but not recorded in loan summary
-- 11. Loan URN ID is auto-generated by trigger if not provided (format: CIGL + 16-digit sequence)
-- 12. Fees Config ID is generated by function fn_generate_fees_config_id() (format: LC + 4 digits)
-- 13. Loan status flow: HOLD -> LIVE -> FUNDED -> DISBURSED -> CLOSED, or NPA/CANCELLED
-- 14. t_loan_repayment_summary should be created when loan is created

-- ============================================================================
-- PORTFOLIO SYSTEM - ENUM TYPES
-- ============================================================================

-- Loan Portfolio Enum
DO $$ BEGIN
    CREATE TYPE loan_portfolio_enum AS ENUM (
        'OPEN',
        'CLOSED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE loan_portfolio_enum IS 'Portfolio types: OPEN (active loans), CLOSED (closed/NPA loans)';

-- Product Type Enum
DO $$ BEGIN
    CREATE TYPE product_type_enum AS ENUM (
        'ML',  -- Manual Lending
        'OTL'  -- One Time Lending
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE product_type_enum IS 'Product types: ML (Manual Lending), OTL (One Time Lending)';

-- ============================================================================
-- PORTFOLIO SYSTEM - TABLES
-- ============================================================================

-- Investment Loan Redemption Summary Table
CREATE TABLE IF NOT EXISTS t_investment_loan_redemption_summary (
    investment_loan_id       BIGINT NOT NULL,
    total_principal_redeemed NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_interest_redeemed  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_fee_levied         NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    principal_outstanding    NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_npa_amount         NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    created_dtm              TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm              TIMESTAMP WITH TIME ZONE,
    total_amount_redeemed    NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    deleted                  TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (investment_loan_id),
    FOREIGN KEY (investment_loan_id) REFERENCES t_investment_loan_detail(id)
);

-- Indexes for t_investment_loan_redemption_summary
CREATE INDEX IF NOT EXISTS idx_investment_loan_redemption_summary_investment_loan_id 
    ON t_investment_loan_redemption_summary(investment_loan_id);

-- Comments for t_investment_loan_redemption_summary
COMMENT ON TABLE t_investment_loan_redemption_summary IS 'Redemption summary at investment-loan level';
COMMENT ON COLUMN t_investment_loan_redemption_summary.investment_loan_id IS 'References t_investment_loan_detail.id';

-- Portfolio Summary Table
CREATE TABLE IF NOT EXISTS t_portfolio_summary (
    id                          BIGSERIAL PRIMARY KEY,
    deleted                     TIMESTAMP WITH TIME ZONE,
    created_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    lender_user_id              VARCHAR(20) NOT NULL,
    product_type                product_type_enum NOT NULL,
    total_principal_lent        NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal_received    NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal_outstanding NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_principal_receivable  NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_interest_received     NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_amount_received       NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_fee_levied            NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    total_npa_amount            NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    absolute_return             NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    annualized_net_return       NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    loan_type                   loan_portfolio_enum NOT NULL,
    loan_count                  INTEGER DEFAULT 0 NOT NULL,
    UNIQUE (lender_user_id, product_type, loan_type)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_summary_lender_user_id 
    ON t_portfolio_summary(lender_user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_summary_product_type 
    ON t_portfolio_summary(product_type);
CREATE INDEX IF NOT EXISTS idx_portfolio_summary_loan_type 
    ON t_portfolio_summary(loan_type);
CREATE INDEX IF NOT EXISTS idx_portfolio_summary_lender_product_loan 
    ON t_portfolio_summary(lender_user_id, product_type, loan_type);

COMMENT ON TABLE t_portfolio_summary IS 'Pre-calculated portfolio summary for lenders by product type and loan type';
COMMENT ON COLUMN t_portfolio_summary.lender_user_id IS 'References t_lender.user_id';
COMMENT ON COLUMN t_portfolio_summary.product_type IS 'Product type: ML or OTL';
COMMENT ON COLUMN t_portfolio_summary.loan_type IS 'Portfolio type: OPEN (active) or CLOSED (closed/NPA)';
COMMENT ON COLUMN t_portfolio_summary.total_principal_receivable IS 'Expected repayment - principal received';

-- ============================================================================
-- PORTFOLIO CALCULATION QUEUE TABLE
-- ============================================================================

-- Portfolio Calculation Queue Table
CREATE TABLE IF NOT EXISTS t_portfolio_calculation_queue (
    id                          BIGSERIAL PRIMARY KEY,
    entity_type                 VARCHAR(20) NOT NULL,
    entity_id                   BIGINT NOT NULL,
    lender_id                   BIGINT NOT NULL,
    status                      VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority                    INTEGER DEFAULT 0,
    source_event                VARCHAR(50),
    created_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm                 TIMESTAMP WITH TIME ZONE,
    processed_dtm               TIMESTAMP WITH TIME ZONE,
    error_message               TEXT,
    retry_count                 INTEGER DEFAULT 0,
    max_retries                 INTEGER DEFAULT 3,
    CONSTRAINT chk_entity_type CHECK (entity_type IN ('LOAN', 'LENDER')),
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED'))
);

-- Indexes for portfolio calculation queue
CREATE INDEX IF NOT EXISTS idx_portfolio_queue_status_lender 
    ON t_portfolio_calculation_queue(status, lender_id, created_dtm);
CREATE INDEX IF NOT EXISTS idx_portfolio_queue_status_entity 
    ON t_portfolio_calculation_queue(status, entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_queue_priority 
    ON t_portfolio_calculation_queue(priority DESC, created_dtm);
CREATE INDEX IF NOT EXISTS idx_portfolio_queue_lender_id 
    ON t_portfolio_calculation_queue(lender_id);

COMMENT ON TABLE t_portfolio_calculation_queue IS 'Queue table for portfolio calculation tasks';
COMMENT ON COLUMN t_portfolio_calculation_queue.entity_type IS 'Type of entity: LOAN or LENDER';
COMMENT ON COLUMN t_portfolio_calculation_queue.entity_id IS 'ID of the entity (loan_id or lender_id)';
COMMENT ON COLUMN t_portfolio_calculation_queue.lender_id IS 'Lender ID for which portfolio needs to be calculated';
COMMENT ON COLUMN t_portfolio_calculation_queue.status IS 'Task status: PENDING, PROCESSING, SUCCESS, FAILED';
COMMENT ON COLUMN t_portfolio_calculation_queue.priority IS 'Priority (higher = processed first)';
COMMENT ON COLUMN t_portfolio_calculation_queue.source_event IS 'Source event: LOAN_DISBURSAL, LOAN_CLOSURE, LOAN_DPD, REDEMPTION';
COMMENT ON COLUMN t_portfolio_calculation_queue.retry_count IS 'Number of retry attempts';
COMMENT ON COLUMN t_portfolio_calculation_queue.max_retries IS 'Maximum retry attempts allowed';

-- ============================================================================
-- LENDER TABLE
-- ============================================================================

-- Lender Table
CREATE TABLE IF NOT EXISTS t_lender (
    id                      SERIAL PRIMARY KEY,
    deleted                 TIMESTAMP WITH TIME ZONE,
    created_dtm             TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id                 VARCHAR(20),
    partner_id              VARCHAR(20),
    state_code              VARCHAR(10),
    partner_code_id         INTEGER,
    partner_mapping_id      INTEGER,
    user_source_group_id    INTEGER
);

-- Indexes for t_lender
CREATE INDEX IF NOT EXISTS idx_lender_user_id 
    ON t_lender(user_id);
CREATE INDEX IF NOT EXISTS idx_lender_user_source_group_id 
    ON t_lender(user_source_group_id);
CREATE INDEX IF NOT EXISTS idx_lender_partner_mapping_id 
    ON t_lender(partner_mapping_id);
CREATE INDEX IF NOT EXISTS idx_lender_partner_id 
    ON t_lender(partner_id);

-- Comments for t_lender
COMMENT ON TABLE t_lender IS 'Lender master table';
COMMENT ON COLUMN t_lender.user_id IS 'User ID (unique across sources)';
COMMENT ON COLUMN t_lender.user_source_group_id IS 'User source group ID';

-- ============================================================================
-- LOAN EVENT QUEUE TABLE
-- ============================================================================

-- Loan Event Queue Table
CREATE TABLE IF NOT EXISTS t_loan_event_queue (
    id                          BIGSERIAL PRIMARY KEY,
    loan_ref_id                 VARCHAR(25) NOT NULL,
    task_type                   VARCHAR(20) NOT NULL,
    event_metadata              JSONB,
    status                      VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority                    INTEGER DEFAULT 0,
    created_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm                 TIMESTAMP WITH TIME ZONE,
    processed_dtm               TIMESTAMP WITH TIME ZONE,
    error_message               TEXT,
    retry_count                 INTEGER DEFAULT 0,
    max_retries                 INTEGER DEFAULT 3,
    CONSTRAINT chk_task_type CHECK (task_type IN ('DISBURSAL', 'CLOSURE', 'DPD_UPDATE')),
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED')),
    CONSTRAINT unique_loan_event UNIQUE (loan_ref_id, task_type)
);

-- Indexes for loan event queue
CREATE INDEX IF NOT EXISTS idx_loan_event_queue_status_task_type 
    ON t_loan_event_queue(status, task_type, created_dtm);
CREATE INDEX IF NOT EXISTS idx_loan_event_queue_priority 
    ON t_loan_event_queue(priority DESC, created_dtm);
CREATE INDEX IF NOT EXISTS idx_loan_event_queue_loan_ref_id 
    ON t_loan_event_queue(loan_ref_id);
CREATE INDEX IF NOT EXISTS idx_loan_event_queue_status_priority 
    ON t_loan_event_queue(status, priority DESC, created_dtm);

-- Comments for loan event queue
COMMENT ON TABLE t_loan_event_queue IS 'Queue table for loan-based events (DISBURSAL, CLOSURE, DPD_UPDATE). One task per loan event.';
COMMENT ON COLUMN t_loan_event_queue.loan_ref_id IS 'Loan reference ID (alphanumeric)';
COMMENT ON COLUMN t_loan_event_queue.task_type IS 'Task type: DISBURSAL, CLOSURE, DPD_UPDATE';
COMMENT ON COLUMN t_loan_event_queue.event_metadata IS 'Event-specific metadata in JSONB format. For DISBURSAL: {"liquidation_date": "YYYY-MM-DD"}. For DPD_UPDATE: {"days_past_due": int, "npa_as_on_date": "YYYY-MM-DD"}. For CLOSURE: {}.';
COMMENT ON COLUMN t_loan_event_queue.status IS 'Task status: PENDING, PROCESSING, SUCCESS, FAILED';
COMMENT ON COLUMN t_loan_event_queue.priority IS 'Priority (higher = processed first). CLOSURE=10, DISBURSAL=5, DPD_UPDATE=0';
COMMENT ON COLUMN t_loan_event_queue.retry_count IS 'Number of retry attempts';
COMMENT ON COLUMN t_loan_event_queue.max_retries IS 'Maximum retry attempts allowed';
COMMENT ON CONSTRAINT unique_loan_event ON t_loan_event_queue IS 'Prevents duplicate events for the same loan and task type';

-- ============================================================================
-- RETAIL PORTFOLIO CALCULATION QUEUE TABLE
-- ============================================================================

-- Retail Portfolio Calculation Queue Table
CREATE TABLE IF NOT EXISTS t_retail_portfolio_calculation_queue (
    id                          BIGSERIAL PRIMARY KEY,
    lender_user_id              VARCHAR(20) NOT NULL,
    status                      VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority                    INTEGER DEFAULT 0,
    source_event                VARCHAR(50),
    created_dtm                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm                 TIMESTAMP WITH TIME ZONE,
    processed_dtm               TIMESTAMP WITH TIME ZONE,
    error_message               TEXT,
    retry_count                 INTEGER DEFAULT 0,
    max_retries                 INTEGER DEFAULT 3,
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED'))
);

-- Indexes for retail portfolio calculation queue
CREATE INDEX IF NOT EXISTS idx_retail_portfolio_queue_status_lender_user_id 
    ON t_retail_portfolio_calculation_queue(status, lender_user_id, created_dtm);
CREATE INDEX IF NOT EXISTS idx_retail_portfolio_queue_priority 
    ON t_retail_portfolio_calculation_queue(priority DESC, created_dtm);
CREATE INDEX IF NOT EXISTS idx_retail_portfolio_queue_lender_user_id 
    ON t_retail_portfolio_calculation_queue(lender_user_id);

-- Comments for retail portfolio calculation queue
COMMENT ON TABLE t_retail_portfolio_calculation_queue IS 'Queue table for lender-based events (REDEMPTION) - Implementation deferred';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.lender_user_id IS 'Lender user ID for portfolio calculation';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.status IS 'Task status: PENDING, PROCESSING, SUCCESS, FAILED';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.priority IS 'Priority (higher = processed first)';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.source_event IS 'Source event: REDEMPTION';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.retry_count IS 'Number of retry attempts';
COMMENT ON COLUMN t_retail_portfolio_calculation_queue.max_retries IS 'Maximum retry attempts allowed';

-- ============================================================================
-- LOAN PORTFOLIO DETAILS TEMP TABLE
-- ============================================================================

-- Loan Portfolio Details Temp Table
-- Temporary table containing loan portfolio details from LMS/PP system
-- Populated by prc_move_loan_portfolio_details_lms_to_fmpp_temp() procedure
CREATE TABLE IF NOT EXISTS t_loan_portfolio_details_temp (
    id                    BIGSERIAL PRIMARY KEY,
    loan_id               VARCHAR(100) NOT NULL,
    principal_receivable  NUMERIC(90, 4),
    principal_paid        NUMERIC(90, 4),
    principal_outstanding NUMERIC(90, 4),
    next_due_date         DATE,
    transaction_date      DATE,
    created_date          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_date          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for loan portfolio details temp
CREATE INDEX IF NOT EXISTS idx_loan_portfolio_details_temp_loan_id 
    ON t_loan_portfolio_details_temp(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_portfolio_details_temp_transaction_date 
    ON t_loan_portfolio_details_temp(transaction_date);
CREATE INDEX IF NOT EXISTS idx_loan_portfolio_details_temp_loan_id_transaction_date 
    ON t_loan_portfolio_details_temp(loan_id, transaction_date);

-- Comments for loan portfolio details temp
COMMENT ON TABLE t_loan_portfolio_details_temp IS 'Temporary table containing loan portfolio details from LMS/PP system. Populated by prc_move_loan_portfolio_details_lms_to_fmpp_temp() procedure.';
COMMENT ON COLUMN t_loan_portfolio_details_temp.loan_id IS 'Loan reference ID (alphanumeric) from source system';
COMMENT ON COLUMN t_loan_portfolio_details_temp.principal_receivable IS 'Principal receivable amount';
COMMENT ON COLUMN t_loan_portfolio_details_temp.principal_paid IS 'Principal paid amount';
COMMENT ON COLUMN t_loan_portfolio_details_temp.principal_outstanding IS 'Principal outstanding amount';
COMMENT ON COLUMN t_loan_portfolio_details_temp.next_due_date IS 'Next due date for repayment';
COMMENT ON COLUMN t_loan_portfolio_details_temp.transaction_date IS 'Transaction date (typically CURRENT_DATE)';
COMMENT ON COLUMN t_loan_portfolio_details_temp.created_date IS 'Record creation timestamp';
COMMENT ON COLUMN t_loan_portfolio_details_temp.updated_date IS 'Record update timestamp';

-- ============================================================================
-- CP DASHBOARD SYSTEM - ENUM TYPES
-- ============================================================================

-- Account Type Enum
DO $$ BEGIN
    CREATE TYPE account_type_enum AS ENUM (
        'LENDER_WALLET',
        'INVESTMENT_ACCOUNT',
        'REDEMPTION_ACCOUNT'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE account_type_enum IS 'Account types: LENDER_WALLET, INVESTMENT_ACCOUNT, REDEMPTION_ACCOUNT';

-- Account Status Enum
DO $$ BEGIN
    CREATE TYPE account_status_enum AS ENUM (
        'ACTIVE',
        'INACTIVE',
        'SUSPENDED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE account_status_enum IS 'Account status types: ACTIVE, INACTIVE, SUSPENDED';

-- ============================================================================
-- CP DASHBOARD SYSTEM - TABLES
-- ============================================================================

-- Channel Partner Mapping Table
CREATE TABLE IF NOT EXISTS t_channel_partner_mapping_table (
    id                  SERIAL PRIMARY KEY,
    deleted             TIMESTAMP WITH TIME ZONE,
    created_dtm         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm         TIMESTAMP WITH TIME ZONE,
    channel_partner_id  VARCHAR(20),
    master_partner_id   VARCHAR(20)
);

-- Indexes for t_channel_partner_mapping_table
CREATE INDEX IF NOT EXISTS idx_channel_partner_mapping_channel_partner_id 
    ON t_channel_partner_mapping_table(channel_partner_id);
CREATE INDEX IF NOT EXISTS idx_channel_partner_mapping_master_partner_id 
    ON t_channel_partner_mapping_table(master_partner_id);
CREATE INDEX IF NOT EXISTS idx_channel_partner_mapping_channel_master 
    ON t_channel_partner_mapping_table(channel_partner_id, master_partner_id);
CREATE INDEX IF NOT EXISTS idx_channel_partner_mapping_deleted 
    ON t_channel_partner_mapping_table(deleted) WHERE deleted IS NULL;

-- Comments for t_channel_partner_mapping_table
COMMENT ON TABLE t_channel_partner_mapping_table IS 'Mapping table for channel partners (LCP) and master channel partners (MCP)';
COMMENT ON COLUMN t_channel_partner_mapping_table.channel_partner_id IS 'Channel Partner ID (LCP). NULL if lender belongs directly to MCP';
COMMENT ON COLUMN t_channel_partner_mapping_table.master_partner_id IS 'Master Channel Partner ID (MCP). NULL if lender belongs directly to LCP';

-- Lender Wallet Transaction Table
CREATE TABLE IF NOT EXISTS t_lender_wallet_transaction (
    id                    BIGSERIAL PRIMARY KEY,
    deleted               TIMESTAMP WITH TIME ZONE,
    created_dtm           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm           TIMESTAMP WITH TIME ZONE,
    account_id            INTEGER REFERENCES t_account(id),
    amount                NUMERIC(10, 2) DEFAULT 0.00,
    source_transaction_id VARCHAR(260) UNIQUE,
    transaction_type      VARCHAR(50),
    lender_id             INTEGER REFERENCES t_lender(id),
    parent_transaction_id BIGINT REFERENCES t_lender_wallet_transaction(id),
    status                VARCHAR(50),
    transaction_id        VARCHAR(260) NOT NULL UNIQUE
);

-- Indexes for t_lender_wallet_transaction
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_lender_id 
    ON t_lender_wallet_transaction(lender_id);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_transaction_type 
    ON t_lender_wallet_transaction(transaction_type);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_status 
    ON t_lender_wallet_transaction(status);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_created_dtm 
    ON t_lender_wallet_transaction(created_dtm);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_lender_type_status 
    ON t_lender_wallet_transaction(lender_id, transaction_type, status);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_lender_type_status_dtm 
    ON t_lender_wallet_transaction(lender_id, transaction_type, status, created_dtm);
CREATE INDEX IF NOT EXISTS idx_lender_wallet_transaction_deleted 
    ON t_lender_wallet_transaction(deleted) WHERE deleted IS NULL;

-- Comments for t_lender_wallet_transaction
COMMENT ON TABLE t_lender_wallet_transaction IS 'Lender wallet transaction records for add money, withdraw money, and other transactions';
COMMENT ON COLUMN t_lender_wallet_transaction.account_id IS 'References t_account.id';
COMMENT ON COLUMN t_lender_wallet_transaction.lender_id IS 'References t_lender.id';
COMMENT ON COLUMN t_lender_wallet_transaction.transaction_type IS 'Transaction type: ADD_MONEY, WITHDRAW_MONEY, INVESTMENT, etc.';
COMMENT ON COLUMN t_lender_wallet_transaction.status IS 'Transaction status: SUCCESS, FAILED, PENDING, etc.';
COMMENT ON COLUMN t_lender_wallet_transaction.transaction_id IS 'Unique transaction identifier';

-- Account Table
CREATE TABLE IF NOT EXISTS t_account (
    id          SERIAL PRIMARY KEY,
    deleted     TIMESTAMP WITH TIME ZONE,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm TIMESTAMP WITH TIME ZONE,
    account_id  INTEGER,
    lender_id   INTEGER REFERENCES t_lender(id),
    balance     NUMERIC(18, 4) DEFAULT 0.00,
    status      account_status_enum
);

-- Indexes for t_account
CREATE INDEX IF NOT EXISTS idx_account_lender_id 
    ON t_account(lender_id);
CREATE INDEX IF NOT EXISTS idx_account_account_id 
    ON t_account(account_id);
CREATE INDEX IF NOT EXISTS idx_account_lender_account_id 
    ON t_account(lender_id, account_id);
CREATE INDEX IF NOT EXISTS idx_account_status 
    ON t_account(status);
CREATE INDEX IF NOT EXISTS idx_account_deleted 
    ON t_account(deleted) WHERE deleted IS NULL;

-- Comments for t_account
COMMENT ON TABLE t_account IS 'Account records for lenders';
COMMENT ON COLUMN t_account.account_id IS 'Account type ID (references t_master_account.id)';
COMMENT ON COLUMN t_account.lender_id IS 'References t_lender.id';
COMMENT ON COLUMN t_account.balance IS 'Account balance';
COMMENT ON COLUMN t_account.status IS 'Account status: ACTIVE, INACTIVE, SUSPENDED';

-- Master Account Table
CREATE TABLE IF NOT EXISTS t_master_account (
    id           SERIAL PRIMARY KEY,
    deleted      TIMESTAMP WITH TIME ZONE,
    created_dtm  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_dtm  TIMESTAMP WITH TIME ZONE,
    account_id   VARCHAR(30),
    account_name VARCHAR(30),
    account_type account_type_enum,
    is_active    BOOLEAN
);

-- Indexes for t_master_account
CREATE INDEX IF NOT EXISTS idx_master_account_account_name 
    ON t_master_account(account_name);
CREATE INDEX IF NOT EXISTS idx_master_account_account_type 
    ON t_master_account(account_type);
CREATE INDEX IF NOT EXISTS idx_master_account_is_active 
    ON t_master_account(is_active);
CREATE INDEX IF NOT EXISTS idx_master_account_deleted 
    ON t_master_account(deleted) WHERE deleted IS NULL;

-- Comments for t_master_account
COMMENT ON TABLE t_master_account IS 'Master account configuration table';
COMMENT ON COLUMN t_master_account.account_id IS 'Account identifier';
COMMENT ON COLUMN t_master_account.account_name IS 'Account name (e.g., LENDER_WALLET)';
COMMENT ON COLUMN t_master_account.account_type IS 'Account type enum';
COMMENT ON COLUMN t_master_account.is_active IS 'Whether the account type is active';

-- ============================================================================
-- COMMON REPAYMENT TRANSFER TABLE
-- ============================================================================
-- Table: fmpp_vortex_common_repayment_transfer
-- Purpose: Common table for both FMPP and Vortex to consume repayments from LMS/PP
--          Prevents conflicts when both systems process repayments simultaneously

CREATE TABLE IF NOT EXISTS fmpp_vortex_common_repayment_transfer (
    id                    BIGSERIAL                NOT NULL PRIMARY KEY,
    is_processed_fmpp     BOOLEAN DEFAULT FALSE    NOT NULL,
    is_processed_vortex   BOOLEAN DEFAULT FALSE    NOT NULL,
    created_dtm           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_dtm           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_id        VARCHAR(30)              NOT NULL,
    purpose               VARCHAR(20)              NOT NULL,
    emi_amount            NUMERIC(15, 2)           NOT NULL,
    emi_amount_without_ff NUMERIC(15, 2)           NOT NULL,
    is_last_repayment     BOOLEAN                  NOT NULL,
    is_prepayment         BOOLEAN                  NOT NULL,
    transaction_date      DATE                     NOT NULL,
    source                VARCHAR(5)                NOT NULL,
    borrower_id           TEXT                     NOT NULL,
    loan_id               VARCHAR(21)              NOT NULL,
    collection_fee        NUMERIC(15, 2)           NOT NULL,
    facilitation_fee       NUMERIC(15, 2)          NOT NULL,
    recovery_fee           NUMERIC(15, 2)           NOT NULL,
    repayment_status      TEXT,
    settlement_date       DATE,
    days_past_due         INTEGER,
    principal_outstanding NUMERIC(15, 2),
    principal_receivable  NUMERIC(15, 2),
    migration_id          BIGINT,
    CONSTRAINT uq_common_repayment_loan_txn UNIQUE (loan_id, transaction_id)
);

-- Indexes for fmpp_vortex_common_repayment_transfer
CREATE INDEX IF NOT EXISTS idx_common_repayment_processed_flags 
    ON fmpp_vortex_common_repayment_transfer(is_processed_fmpp, is_processed_vortex);
CREATE INDEX IF NOT EXISTS idx_common_repayment_source_txn 
    ON fmpp_vortex_common_repayment_transfer(source, transaction_id);
CREATE INDEX IF NOT EXISTS idx_common_repayment_loan_id 
    ON fmpp_vortex_common_repayment_transfer(loan_id);
CREATE INDEX IF NOT EXISTS idx_common_repayment_settlement_date 
    ON fmpp_vortex_common_repayment_transfer(settlement_date) WHERE settlement_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_common_repayment_vortex_pending 
    ON fmpp_vortex_common_repayment_transfer(is_processed_vortex, settlement_date) 
    WHERE is_processed_vortex = FALSE AND settlement_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_common_repayment_migration_id 
    ON fmpp_vortex_common_repayment_transfer(migration_id) 
    WHERE migration_id IS NOT NULL;

-- Comments for fmpp_vortex_common_repayment_transfer
COMMENT ON TABLE fmpp_vortex_common_repayment_transfer IS 
    'Common repayment transfer table for both FMPP and Vortex systems to consume repayments from LMS/PP';
COMMENT ON COLUMN fmpp_vortex_common_repayment_transfer.loan_id IS 
    'Loan identifier (loan_ref_id from t_loan or secondary_loan_id from PP)';
COMMENT ON COLUMN fmpp_vortex_common_repayment_transfer.is_processed_fmpp IS 
    'Flag indicating if FMPP has processed this repayment';
COMMENT ON COLUMN fmpp_vortex_common_repayment_transfer.is_processed_vortex IS 
    'Flag indicating if Vortex has processed this repayment';
COMMENT ON CONSTRAINT uq_common_repayment_loan_txn ON fmpp_vortex_common_repayment_transfer IS 
    'Unique constraint on (loan_id, transaction_id) to prevent duplicate entries';
COMMENT ON COLUMN fmpp_vortex_common_repayment_transfer.migration_id IS 
    'References t_common_table_repayment_migration_logs.id - links to migration batch that inserted this record';

-- ============================================================================
-- COMMON TABLE REPAYMENT MIGRATION LOGS TABLE
-- ============================================================================
-- Table: t_common_table_repayment_migration_logs
-- Purpose: Logs repayment migration batches from LMS/PP to common table

CREATE TABLE IF NOT EXISTS t_common_table_repayment_migration_logs (
    id BIGSERIAL PRIMARY KEY,
    migration_batch_id VARCHAR(30) UNIQUE NOT NULL,
    source_system VARCHAR(10) NOT NULL CHECK (source_system IN ('LMS', 'PP')),
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'NO_DATA', 'FAILED')),
    rows_processed INTEGER DEFAULT 0 NOT NULL,
    error_message TEXT,
    created_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_dtm TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for t_common_table_repayment_migration_logs
CREATE INDEX IF NOT EXISTS idx_common_table_migration_logs_status 
    ON t_common_table_repayment_migration_logs(status);
CREATE INDEX IF NOT EXISTS idx_common_table_migration_logs_source_system 
    ON t_common_table_repayment_migration_logs(source_system);
CREATE INDEX IF NOT EXISTS idx_common_table_migration_logs_created_dtm 
    ON t_common_table_repayment_migration_logs(created_dtm);
CREATE INDEX IF NOT EXISTS idx_common_table_migration_logs_migration_batch_id 
    ON t_common_table_repayment_migration_logs(migration_batch_id);

-- Comments for t_common_table_repayment_migration_logs
COMMENT ON TABLE t_common_table_repayment_migration_logs IS 
    'Logs repayment migration batches from LMS/PP to common table (fmpp_vortex_common_repayment_transfer)';
COMMENT ON COLUMN t_common_table_repayment_migration_logs.id IS 
    'Primary key for migration log entry';
COMMENT ON COLUMN t_common_table_repayment_migration_logs.migration_batch_id IS 
    'Unique migration batch identifier (format: YYYYMMDDHHMMSS_XXXX, max 30 chars)';
COMMENT ON COLUMN t_common_table_repayment_migration_logs.source_system IS 
    'Source system: LMS or PP';
COMMENT ON COLUMN t_common_table_repayment_migration_logs.status IS 
    'Migration status: PENDING, PROCESSING, COMPLETED, NO_DATA, FAILED';
COMMENT ON COLUMN t_common_table_repayment_migration_logs.rows_processed IS 
    'Number of repayment records processed in this migration batch';

