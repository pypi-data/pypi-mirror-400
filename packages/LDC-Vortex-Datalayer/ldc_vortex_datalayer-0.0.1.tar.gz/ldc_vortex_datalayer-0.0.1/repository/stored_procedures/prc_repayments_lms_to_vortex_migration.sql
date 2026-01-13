-- Consolidated Stored Procedure: LMS to Vortex Repayment Migration with Fee Details
-- This procedure handles the complete data migration from LMS to Vortex architecture
-- including repayment details and fee breakdown in a single transaction

CREATE OR REPLACE PROCEDURE prc_repayments_lms_to_vortex_migration(
    INOUT inout_response character varying DEFAULT NULL::character varying,
    IN batch_size integer DEFAULT 5000
)
LANGUAGE plpgsql
AS
$$
DECLARE
    v_current_timestamp timestamp with time zone := NOW();
    v_rows_processed int := 0;
    v_fee_records_inserted int := 0;
    v_migration_batch_id varchar(30);
    v_migration_id bigint;
    v_repayment_detail_id bigint;
    v_fee_record RECORD;
    v_repayment_record RECORD;
BEGIN
    -- Generate migration_batch_id (format: YYYYMMDDHHMMSS_XXXX)
    v_migration_batch_id := TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '_' || 
                           LPAD(EXTRACT(MICROSECONDS FROM NOW())::bigint % 10000::bigint, 4, '0');
    
    -- Create migration log entry and get migration_id
    INSERT INTO t_repayment_migration_logs (
        migration_batch_id, source_system, status, rows_processed, fee_records_inserted,
        created_dtm, updated_dtm
    )
    VALUES (
        v_migration_batch_id, 'LMS', 'PROCESSING', 0, 0,
        v_current_timestamp, v_current_timestamp
    )
    RETURNING id INTO v_migration_id;
    
    -- Process each repayment record individually for better control
    FOR v_repayment_record IN 
        SELECT 
            tl.id as loan_id,
            tl.loan_ref_id,
            imt.transaction_id,
            imt.emi_amount,
            imt.facilitation_fee,
            imt.collection_fee,
            imt.recovery_fee,
            imt.purpose,
            imt.days_past_due,
            imt.transaction_date,
            imt.settlement_date,
            imt.created_dtm,
            imt.id as lms_id
        FROM ldclmsprod.ims_repayment_transfer imt
        JOIN t_loan tl ON imt.loan_id = tl.loan_ref_id
        JOIN t_borrowers tb ON imt.borrower_id = tb.source_id
        WHERE imt.is_processed = false
          AND imt.settlement_date IS NOT NULL
          AND imt.emi_amount > 0
          AND imt.purpose IN ('PRINCIPAL', 'INTEREST', 'DELAY_INTEREST', 'OTHER_CHARGES')
        ORDER BY imt.id
        LIMIT batch_size
    LOOP
        -- Insert repayment detail and get the ID
        INSERT INTO t_loan_repayment_detail(
            loan_id,
            loan_ref_id,
            purpose,
            purpose_amount,
            emi_amount,
            total_fees,
            is_processed,
            days_past_due,
            src_txn_id,
            sys_txn_id,
            migration_id,
            ammort_id,
            transaction_date,
            settlement_date,
            src_created_dtm,
            sys_created_dtm,
            updated_dtm
        )
        VALUES (
            v_repayment_record.loan_id,
            v_repayment_record.loan_ref_id,
            v_repayment_record.purpose::repayment_purpose,
            COALESCE(v_repayment_record.emi_amount, 0),
            COALESCE(v_repayment_record.emi_amount, 0),
            COALESCE(v_repayment_record.facilitation_fee, 0) + 
            COALESCE(v_repayment_record.collection_fee, 0) + 
            COALESCE(v_repayment_record.recovery_fee, 0),
            false,
            COALESCE(v_repayment_record.days_past_due, 0),
            v_repayment_record.transaction_id,
            v_migration_id,
            NULL,
            v_repayment_record.transaction_date,
            v_repayment_record.settlement_date,
            v_repayment_record.created_dtm,
            v_current_timestamp,
            v_current_timestamp
        )
        RETURNING id INTO v_repayment_detail_id;
        
        v_rows_processed := v_rows_processed + 1;
        
        -- Insert fee details for this repayment record
        -- Facilitation Fee
        IF COALESCE(v_repayment_record.facilitation_fee, 0) > 0 THEN
            INSERT INTO t_fee_details (
                fee_source_id,
                fee_source,
                fee_type,
                fee_amount,
                fee_levy_date,
                created_dtm,
                txn_reference_id
            )
            VALUES (
                v_repayment_detail_id,
                'LOAN'::fee_source_type,
                'FF'::fee_type_enum,
                v_repayment_record.facilitation_fee,
                CURRENT_DATE,
                v_current_timestamp,
                v_migration_id
            );
            v_fee_records_inserted := v_fee_records_inserted + 1;
        END IF;
        
        -- Collection Fee
        IF COALESCE(v_repayment_record.collection_fee, 0) > 0 THEN
            INSERT INTO t_fee_details (
                fee_source_id,
                fee_source,
                fee_type,
                fee_amount,
                fee_levy_date,
                created_dtm,
                txn_reference_id
            )
            VALUES (
                v_repayment_detail_id,
                'LOAN'::fee_source_type,
                'CF'::fee_type_enum,
                v_repayment_record.collection_fee,
                CURRENT_DATE,
                v_current_timestamp,
                v_migration_id
            );
            v_fee_records_inserted := v_fee_records_inserted + 1;
        END IF;
        
        -- Recovery Fee
        IF COALESCE(v_repayment_record.recovery_fee, 0) > 0 THEN
            INSERT INTO t_fee_details (
                fee_source_id,
                fee_source,
                fee_type,
                fee_amount,
                fee_levy_date,
                created_dtm,
                txn_reference_id
            )
            VALUES (
                v_repayment_detail_id,
                'LOAN'::fee_source_type,
                'RF'::fee_type_enum,
                v_repayment_record.recovery_fee,
                CURRENT_DATE,
                v_current_timestamp,
                v_migration_id
            );
            v_fee_records_inserted := v_fee_records_inserted + 1;
        END IF;
    END LOOP;
    
    -- Mark LMS records as processed (outside the loop, once per batch)
    IF v_rows_processed > 0 THEN
        UPDATE ldclmsprod.ims_repayment_transfer imt
        SET is_processed = true,
            updated_dtm = v_current_timestamp
        WHERE imt.is_processed = false
          AND imt.transaction_id IN (
            SELECT src_txn_id 
            FROM t_loan_repayment_detail 
            WHERE migration_id = v_migration_id
          );
    END IF;
    
    -- Update migration log
    UPDATE t_repayment_migration_logs
    SET status = CASE WHEN v_rows_processed > 0 THEN 'COMPLETED' ELSE 'NO_DATA' END,
        rows_processed = v_rows_processed,
        fee_records_inserted = v_fee_records_inserted,
        updated_dtm = v_current_timestamp
    WHERE id = v_migration_id;
    
    -- Return response with batch information
    inout_response := json_build_object(
        'status', CASE WHEN v_rows_processed > 0 THEN 'SUCCESS' ELSE 'NO_DATA' END,
        'migration_id', v_migration_id,
        'migration_batch_id', v_migration_batch_id,
        'rows_processed', v_rows_processed,
        'fee_records_inserted', v_fee_records_inserted,
        'message', CASE WHEN v_rows_processed > 0 THEN 'Batch processed successfully' ELSE 'No records found' END
    )::text;
    
EXCEPTION
    WHEN OTHERS THEN
        DECLARE
            my_ex_state text;
            my_ex_message text;
            my_ex_detail text;
            my_ex_hint text;
            my_ex_ctx text;
        BEGIN
            GET STACKED DIAGNOSTICS
                my_ex_state   = returned_sqlstate,
                my_ex_message = message_text,
                my_ex_detail  = pg_exception_detail,
                my_ex_hint    = pg_exception_hint,
                my_ex_ctx     = pg_exception_context;

            -- Update migration log with error
            IF v_migration_id IS NOT NULL THEN
                UPDATE t_repayment_migration_logs
                SET status = 'FAILED',
                    error_message = 'ERROR: ' || my_ex_message,
                    updated_dtm = v_current_timestamp
                WHERE id = v_migration_id;
            END IF;

            -- Log to error table if exists
            INSERT INTO t_error_log (sp_name, err_state, err_message, err_details, err_hint, err_context, created_dtm, updated_dtm)
            VALUES ('PRC_REPAYMENTS_LMS_TO_VORTEX_MIGRATION', my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx, NOW(), NOW());

            RAISE INFO 'THE FOLLOWING ERROR OCCURRED % % % % %',
                my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;

            inout_response := json_build_object(
                'status', 'ERROR',
                'migration_id', COALESCE(v_migration_id, 0),
                'migration_batch_id', COALESCE(v_migration_batch_id, 'ERROR_BATCH'),
                'rows_processed', 0,
                'fee_records_inserted', 0,
                'message', 'ERROR: ' || my_ex_message
            )::text;
        END;
END;
$$;
