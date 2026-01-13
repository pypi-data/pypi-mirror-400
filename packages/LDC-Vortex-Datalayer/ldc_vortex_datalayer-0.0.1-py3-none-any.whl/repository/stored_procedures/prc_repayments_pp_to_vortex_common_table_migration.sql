-- Stored Procedure: PP to Vortex Common Table Repayment Migration
-- This procedure migrates repayment records from PP to the common table (fmpp_vortex_common_repayment_transfer)
-- Both FMPP and Vortex can then consume from this common table independently
-- Note: PP uses secondary_loan_id field (maps to loan_id in common table)

CREATE OR REPLACE PROCEDURE prc_repayments_pp_to_vortex_common_table_migration(
    INOUT inout_response character varying DEFAULT NULL::character varying,
    IN batch_size integer DEFAULT 5000
)
LANGUAGE plpgsql
AS
$$
DECLARE
    v_current_timestamp timestamp with time zone := NOW();
    v_rows_processed int := 0;
    v_migration_batch_id varchar(30);
    v_migration_id bigint;
    v_repayment_record RECORD;
    v_conflict_count int := 0;
BEGIN
    -- Generate migration_batch_id (format: YYYYMMDDHHMMSS_XXXX)
    v_migration_batch_id := TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '_' || 
                           LPAD(EXTRACT(MICROSECONDS FROM NOW())::bigint % 10000::bigint, 4, '0');
    
    -- Create migration log entry and get migration_id
    INSERT INTO t_common_table_repayment_migration_logs (
        migration_batch_id, source_system, status, rows_processed,
        created_dtm, updated_dtm
    )
    VALUES (
        v_migration_batch_id, 'PP', 'PROCESSING', 0,
        v_current_timestamp, v_current_timestamp
    )
    RETURNING id INTO v_migration_id;
    
    -- Process each repayment record individually
    FOR v_repayment_record IN 
        SELECT 
            imt.secondary_loan_id as loan_id,
            imt.transaction_id,
            imt.emi_amount,
            imt.emi_amount_without_ff,
            imt.is_last_repayment,
            imt.is_prepayment,
            imt.transaction_date,
            imt.source,
            imt.borrower_id,
            imt.collection_fee,
            imt.facilitation_fee,
            imt.recovery_fee,
            imt.repayment_status,
            imt.settlement_date,
            imt.days_past_due,
            imt.principal_outstanding,
            imt.principal_receivable,
            imt.purpose
        FROM ldcpp.loan_ims_repayment_transfer imt
        WHERE imt.is_processed = false
        ORDER BY imt.id
        LIMIT batch_size
    LOOP
        BEGIN
            -- Insert into common table
            INSERT INTO fmpp_vortex_common_repayment_transfer (
                is_processed_fmpp,
                is_processed_vortex,
                created_dtm,
                updated_dtm,
                transaction_id,
                purpose,
                emi_amount,
                emi_amount_without_ff,
                is_last_repayment,
                is_prepayment,
                transaction_date,
                source,
                borrower_id,
                loan_id,
                collection_fee,
                facilitation_fee,
                recovery_fee,
                repayment_status,
                settlement_date,
                days_past_due,
                principal_outstanding,
                principal_receivable,
                migration_id
            )
            VALUES (
                false,
                false,
                v_current_timestamp,
                v_current_timestamp,
                v_repayment_record.transaction_id,
                v_repayment_record.purpose,
                COALESCE(v_repayment_record.emi_amount, 0),
                COALESCE(v_repayment_record.emi_amount_without_ff, 0),
                COALESCE(v_repayment_record.is_last_repayment, false),
                COALESCE(v_repayment_record.is_prepayment, false),
                v_repayment_record.transaction_date,
                v_repayment_record.source,
                v_repayment_record.borrower_id,
                v_repayment_record.loan_id,
                COALESCE(v_repayment_record.collection_fee, 0),
                COALESCE(v_repayment_record.facilitation_fee, 0),
                COALESCE(v_repayment_record.recovery_fee, 0),
                v_repayment_record.repayment_status,
                v_repayment_record.settlement_date,
                v_repayment_record.days_past_due,
                v_repayment_record.principal_outstanding,
                v_repayment_record.principal_receivable,
                v_migration_id
            );
            
            v_rows_processed := v_rows_processed + 1;
            
        EXCEPTION
            WHEN unique_violation THEN
                -- Log conflict to t_error_log
                v_conflict_count := v_conflict_count + 1;
                INSERT INTO t_error_log (
                    sp_name, err_state, err_message, err_details, 
                    err_hint, err_context, created_dtm, updated_dtm
                )
                VALUES (
                    'prc_repayments_pp_to_vortex_common_table_migration',
                    '23505',
                    'Unique constraint violation on (loan_id, transaction_id)',
                    json_build_object(
                        'loan_id', v_repayment_record.loan_id,
                        'transaction_id', v_repayment_record.transaction_id,
                        'migration_batch_id', v_migration_batch_id
                    )::text,
                    'Record already exists in common table',
                    'Conflict detected during PP to common table migration',
                    v_current_timestamp,
                    v_current_timestamp
                );
        END;
    END LOOP;
    
    -- Mark PP records as processed (outside the loop, once per batch)
    IF v_rows_processed > 0 THEN
        UPDATE ldcpp.loan_ims_repayment_transfer imt
        SET is_processed = true,
            updated_dtm = v_current_timestamp
        WHERE imt.is_processed = false
          AND imt.transaction_id IN (
            SELECT transaction_id 
            FROM fmpp_vortex_common_repayment_transfer 
            WHERE migration_id = v_migration_id
          );
    END IF;
    
    -- Update migration log
    UPDATE t_common_table_repayment_migration_logs
    SET status = CASE WHEN v_rows_processed > 0 THEN 'COMPLETED' ELSE 'NO_DATA' END,
        rows_processed = v_rows_processed,
        updated_dtm = v_current_timestamp
    WHERE id = v_migration_id;
    
    -- Return response with batch information
    inout_response := json_build_object(
        'status', CASE WHEN v_rows_processed > 0 THEN 'SUCCESS' ELSE 'NO_DATA' END,
        'migration_id', v_migration_id,
        'migration_batch_id', v_migration_batch_id,
        'rows_processed', v_rows_processed,
        'conflicts_logged', v_conflict_count,
        'message', CASE 
            WHEN v_rows_processed > 0 THEN 'Batch processed successfully' 
            ELSE 'No records found' 
        END
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
                UPDATE t_common_table_repayment_migration_logs
                SET status = 'FAILED',
                    error_message = 'ERROR: ' || my_ex_message,
                    updated_dtm = v_current_timestamp
                WHERE id = v_migration_id;
            END IF;

            -- Log to error table
            INSERT INTO t_error_log (
                sp_name, err_state, err_message, err_details, 
                err_hint, err_context, created_dtm, updated_dtm
            )
            VALUES (
                'prc_repayments_pp_to_vortex_common_table_migration', 
                my_ex_state, my_ex_message, my_ex_detail, 
                my_ex_hint, my_ex_ctx, NOW(), NOW()
            );

            RAISE INFO 'THE FOLLOWING ERROR OCCURRED % % % % %',
                my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;

            inout_response := json_build_object(
                'status', 'ERROR',
                'migration_id', COALESCE(v_migration_id, 0),
                'migration_batch_id', COALESCE(v_migration_batch_id, 'ERROR_BATCH'),
                'rows_processed', 0,
                'conflicts_logged', 0,
                'message', 'ERROR: ' || my_ex_message
            )::text;
        END;
END;
$$;

