create procedure prc_process_repayments(IN loan_ids bigint[], IN batch_id_str character varying, INOUT inout_response integer DEFAULT NULL::integer)
    language plpgsql
as
$$
DECLARE
    v_repayment_record RECORD;
    v_loan_investment_record RECORD;

    v_loan_id BIGINT;
    v_redemption_detail_id BIGINT;

    v_repayment_amount NUMERIC(10, 2);
    v_fees_to_deduct NUMERIC(10, 2);
    v_ff_to_deduct NUMERIC(10, 2);
    v_cf_to_deduct NUMERIC(10, 2);
    v_rf_to_deduct NUMERIC(10, 2);
    v_repayment_principal NUMERIC(10, 2);
    v_repayment_interest NUMERIC(10, 2);

    v_distributed_principal_p4 NUMERIC(10, 4);
    v_distributed_interest_p4 NUMERIC(10, 4);
    v_distributed_fees_p4 NUMERIC(10, 4);
    v_distributed_ff_p4 NUMERIC(10, 4);
    v_distributed_cf_p4 NUMERIC(10, 4);
    v_distributed_amount_p4 NUMERIC(10, 4);

    v_distributed_principal_p2 NUMERIC(10, 2);
    v_distributed_interest_p2 NUMERIC(10, 2);
    v_distributed_fees_p2 NUMERIC(10, 2);
    v_distributed_ff_p2 NUMERIC(10, 2);
    v_distributed_cf_p2 NUMERIC(10, 2);
    v_distributed_amount_p2 NUMERIC(10, 2);

    v_total_distributed_amount NUMERIC(10, 2) := 0;
    v_distribution_adjustment_amount NUMERIC(10, 4) := 0;
    v_adjustment_amount_p4_to_p2 NUMERIC(10, 2) := 0;
    v_amount_to_distribute_p4 NUMERIC(10, 4) := 0;
    v_principal_to_distribute_p4 NUMERIC(10, 4) := 0;
    v_interest_to_distribute_p4 NUMERIC(10, 4) := 0;
    v_fees_to_distribute_p4 NUMERIC(10, 4) := 0;
    v_last_processed_investment_loan_id BIGINT;
    v_batch_id BIGINT;
    v_current_timestamp timestamp with time zone := NOW();

    v_pg_account_id BIGINT;
    v_borrower_escrow_account_id BIGINT;
    v_loan_account_id BIGINT;
    v_lender_repayment_account_id BIGINT;

    v_pg_to_escrow_txn_id VARCHAR;
    v_escrow_loan_account_txn_id VARCHAR;
    v_loan_account_repayment_wallet_txn_id VARCHAR;
    
    v_prev_balance NUMERIC;
    v_updated_balance NUMERIC;
    v_pg_acc_id BIGINT;
    v_borrower_escrow_acc_id BIGINT;
    v_loan_acc_id BIGINT;
    v_repayment_wallet_acc_id BIGINT;
    v_income_acc_id BIGINT;
    v_income_account_id BIGINT;
BEGIN
    -- Create processing log entry and get batch_id (PK)
    INSERT INTO t_repayment_processing_logs (
        batch_id, status, total_loans, processed_loans, failed_loans,
        created_dtm, updated_dtm
    )
    VALUES (
               batch_id_str, 'PROCESSING', array_length(loan_ids, 1), 0, 0,
               v_current_timestamp, v_current_timestamp
           )
    RETURNING id INTO v_batch_id;

    v_pg_account_id = (SELECT id FROM t_master_account WHERE account_name = 'PG');
    v_borrower_escrow_account_id = (SELECT id FROM t_master_account WHERE account_name = 'BORROWER_ESCROW');
    v_loan_account_id = (SELECT id FROM t_master_account WHERE account_name = 'LOAN_ACCOUNT');
    v_lender_repayment_account_id = (SELECT id FROM t_master_account WHERE account_name = 'LENDER_REPAYMENT_WALLET');
    v_income_account_id = (SELECT id FROM t_master_account WHERE account_name = 'INCOME_ACCOUNT');

    -- Step 1: Process Loan Repayments
    FOR v_repayment_record IN
        SELECT
            id,
            loan_id,
            purpose_amount as emi_amount,
            CASE WHEN purpose IN ('PRINCIPAL', 'OTHER_CHARGES') THEN purpose_amount ELSE 0 END AS principal,
            CASE WHEN purpose IN ('INTEREST', 'DELAY_INTEREST') THEN purpose_amount ELSE 0 END AS interest,
            total_fees,
            batch_id
        FROM t_loan_repayment_detail
        WHERE loan_id = ANY(loan_ids)
          AND is_processed = false
            FOR UPDATE SKIP LOCKED
        LOOP
            RAISE INFO 'LOOP: % ', v_repayment_record.id; 
            v_loan_id := v_repayment_record.loan_id;
            v_repayment_amount := COALESCE(v_repayment_record.emi_amount, 0);
            v_repayment_principal := COALESCE(v_repayment_record.principal, 0);
            v_repayment_interest := COALESCE(v_repayment_record.interest, 0);

            -- Fetch fee amounts
            v_ff_to_deduct := COALESCE((SELECT fee_amount FROM t_fee_details WHERE fee_source_id = v_repayment_record.id AND fee_type = 'FF' AND fee_source = 'LOAN'), 0);
            v_cf_to_deduct := COALESCE((SELECT fee_amount FROM t_fee_details WHERE fee_source_id = v_repayment_record.id AND fee_type = 'CF' AND fee_source = 'LOAN'), 0);
            v_rf_to_deduct := COALESCE((SELECT fee_amount FROM t_fee_details WHERE fee_source_id = v_repayment_record.id AND fee_type = 'RF' AND fee_source = 'LOAN'), 0);
            v_fees_to_deduct := COALESCE(v_repayment_record.total_fees, 0);
            
            IF v_fees_to_deduct > 0 THEN
                SELECT balance, id INTO v_prev_balance, v_income_acc_id
                FROM t_account
                WHERE account_id = v_income_account_id FOR UPDATE NOWAIT;
                
                UPDATE t_account
                SET balance = v_prev_balance + v_fees_to_deduct
                WHERE account_id = v_income_account_id
                RETURNING balance INTO v_updated_balance;
    
                INSERT INTO t_ledger_income_account (
                    account_id, event_type, amount, transaction_dtm, transaction_id,
                    narration, created_by, source_transaction_id, previous_balance, current_balance
                )
                VALUES (
                           v_income_acc_id, 'CR', v_fees_to_deduct, now(), 
                        generate_txn_id(),
                           'INNOFIN INCOME RECEIVED', 'SYSTEM', 
                        v_repayment_record.id, v_prev_balance, v_updated_balance
                       );
            END IF;

            -- Validation: Fees should not exceed EMI amount
            IF v_fees_to_deduct > v_repayment_amount THEN
                RAISE INFO 'FEES IS GT EMI_AMOUNT: %, F: %, EA: %', v_loan_id, v_fees_to_deduct, v_repayment_amount;
                INSERT INTO t_error_log (sp_name, err_state, err_message, created_dtm)
                VALUES ('PRC_PROCESS_REPAYMENTS', 'P0001', 'INVALID_REPAY_FEES_GT_EMI_AMOUNT_FOR_LOAN_ID: ' || v_loan_id, NOW());
                CONTINUE;
            END IF;

            -- Validation: Fee totals should match
            IF v_fees_to_deduct <> (v_ff_to_deduct + v_cf_to_deduct + v_rf_to_deduct) THEN
                RAISE INFO 'FEES MISMATCH: %, F: %', v_loan_id, v_fees_to_deduct;
                INSERT INTO t_error_log (sp_name, err_state, err_message, created_dtm)
                VALUES ('PRC_PROCESS_REPAYMENTS', 'P0001', 'INVALID_REPAY_FEES_MISMATCH_FOR_LOAN_ID: ' || v_loan_id, NOW());
                CONTINUE;
            END IF;

            -- Handle Recovery Fee (RF): Deduct from interest/principal
            IF v_rf_to_deduct > 0 THEN
                IF v_rf_to_deduct > v_repayment_interest THEN
                    v_repayment_interest := 0;
                    v_repayment_principal := v_repayment_principal + v_repayment_interest - v_rf_to_deduct;
                ELSE
                    v_repayment_interest := v_repayment_interest - v_rf_to_deduct;
                END IF;

                v_fees_to_deduct := v_fees_to_deduct - v_rf_to_deduct;
                v_repayment_amount := v_repayment_amount - v_rf_to_deduct;
            END IF;

            -- Skip if entire repayment is RF
            IF v_repayment_amount = 0 THEN
                RAISE INFO 'REPAYMENT CONSUMPTION SKIPPED FURTHER AS WHOLE REPAY IS RF FOR LOAN_ID: %', v_loan_id;
                RAISE INFO 'P: %, I: %, F: %', v_repayment_principal, v_repayment_interest, v_fees_to_deduct;
                CONTINUE;
            END IF;

            -- Calculate repayment amount after fees
            v_repayment_amount := v_repayment_amount - v_fees_to_deduct;

            -- Update loan repayment summary
            UPDATE t_loan_repayment_summary
            SET
                principal_received = principal_received + v_repayment_principal,
                interest_received = interest_received + v_repayment_interest,
                fee_levied = fee_levied + v_fees_to_deduct,
                total_amount_received = total_amount_received + v_repayment_amount,
                principal_outstanding = CASE WHEN principal_outstanding > 0 THEN principal_outstanding - v_repayment_principal ELSE principal_outstanding END,
                npa_amount = CASE WHEN npa_amount > 0 THEN npa_amount - v_repayment_principal ELSE npa_amount END,
                updated_dtm = NOW()
            WHERE loan_id = v_loan_id;

            -- Reset distributed amount for this repayment
            v_total_distributed_amount := 0;

            -- Distribute to investments
            FOR v_loan_investment_record IN
                SELECT
                    tild.id,
                    tild.allocation_percentage,
                    tli.lender_id
                FROM t_investment_loan_detail tild
                         JOIN t_lender_investment tli ON tli.id = tild.investment_id
                WHERE tild.loan_id = v_loan_id
                  AND tild.deleted IS NULL
                LOOP
                    v_last_processed_investment_loan_id := v_loan_investment_record.id;

                    -- Calculate distributed amounts (precision 4)
                    v_distributed_principal_p4 := TRUNC(v_repayment_principal * (v_loan_investment_record.allocation_percentage / 100), 4);
                    v_distributed_interest_p4 := TRUNC(v_repayment_interest * (v_loan_investment_record.allocation_percentage / 100), 4);
                    v_distributed_ff_p4 := TRUNC(v_ff_to_deduct * (v_loan_investment_record.allocation_percentage / 100), 4);
                    v_distributed_cf_p4 := TRUNC(v_cf_to_deduct * (v_loan_investment_record.allocation_percentage / 100), 4);
                    v_distributed_amount_p4 := TRUNC(v_repayment_amount * (v_loan_investment_record.allocation_percentage / 100), 4);
                    v_distributed_fees_p4 := v_distributed_ff_p4 + v_distributed_cf_p4;

                    -- Update investment loan repayment summary (add to to_distribute columns)
                    UPDATE t_investment_loan_repayment_summary
                    SET
                        principal_to_distribute = principal_to_distribute + v_distributed_principal_p4,
                        interest_to_distribute = interest_to_distribute + v_distributed_interest_p4,
                        fee_to_distribute = fee_to_distribute + v_distributed_fees_p4,
                        amount_to_distribute = amount_to_distribute + v_distributed_amount_p4,
                        updated_dtm = NOW()
                    WHERE investment_loan_id = v_loan_investment_record.id
                    RETURNING principal_to_distribute, interest_to_distribute, fee_to_distribute, amount_to_distribute
                        INTO v_principal_to_distribute_p4, v_interest_to_distribute_p4, v_fees_to_distribute_p4, v_amount_to_distribute_p4;

                    v_total_distributed_amount := v_total_distributed_amount + v_amount_to_distribute_p4;

                    -- Create fee records for FF and CF
                    IF v_distributed_ff_p4 > 0 THEN
                        INSERT INTO t_fee_details (fee_type, fee_amount, fee_source, fee_levy_date, fee_source_id, created_dtm, txn_reference_id)
                        VALUES ('FF', v_distributed_ff_p4, 'INVESTMENT_LOAN', CURRENT_DATE, v_loan_investment_record.id, NOW(), v_batch_id);
                    END IF;

                    -- Create fee records for CF
                    IF v_distributed_cf_p4 > 0 THEN
                        INSERT INTO t_fee_details (fee_type, fee_amount, fee_source, fee_levy_date, fee_source_id, created_dtm, txn_reference_id)
                        VALUES ('CF', v_distributed_cf_p4, 'INVESTMENT_LOAN', CURRENT_DATE, v_loan_investment_record.id, NOW(), v_batch_id);
                    END IF;

                    -- Convert to precision 2 for further distribution in redemption detail
                    v_distributed_principal_p2 := TRUNC(v_principal_to_distribute_p4, 2);
                    v_distributed_interest_p2 := TRUNC(v_interest_to_distribute_p4, 2);
                    v_distributed_ff_p2 := TRUNC(v_distributed_ff_p4, 2);
                    v_distributed_cf_p2 := TRUNC(v_distributed_cf_p4, 2);
                    v_distributed_fees_p2 := v_distributed_ff_p2 + v_distributed_cf_p2;
                    v_distributed_amount_p2 := v_distributed_principal_p2 + v_distributed_interest_p2 - v_distributed_fees_p2;

                    -- Handle rounding adjustments
                    IF v_distributed_amount_p2 > v_amount_to_distribute_p4 THEN
                        v_adjustment_amount_p4_to_p2 := 0.01;
                        IF v_distributed_fees_p2 <= v_distributed_interest_p2 THEN
                            v_distributed_interest_p2 := TRUNC(v_interest_to_distribute_p4 - v_adjustment_amount_p4_to_p2, 2);
                        ELSE
                            v_distributed_principal_p2 := TRUNC(v_distributed_principal_p2 - v_adjustment_amount_p4_to_p2, 2);
                        END IF;
                        v_distributed_amount_p2 := v_distributed_principal_p2 + v_distributed_interest_p2 - v_distributed_fees_p2;
                    END IF;

                    IF v_distributed_amount_p2 < 1 THEN
                        CONTINUE;
                    END IF;  -- Close IF v_distributed_principal_p2 >= 1

                    -- Update investment loan repayment summary (actual distribution)
                    UPDATE t_investment_loan_repayment_summary
                    SET
                        principal_to_distribute = principal_to_distribute - v_distributed_principal_p2,
                        interest_to_distribute = interest_to_distribute - v_distributed_interest_p2,
                        fee_to_distribute = fee_to_distribute - v_distributed_fees_p2,
                        amount_to_distribute = amount_to_distribute - v_distributed_amount_p2,
                        total_principal_received = total_principal_received + v_distributed_principal_p2,
                        total_interest_received = total_interest_received + v_distributed_interest_p2,
                        total_fee_levied = total_fee_levied + v_distributed_fees_p2,
                        total_amount_received = total_amount_received + v_distributed_amount_p2,
                        principal_outstanding = CASE WHEN principal_outstanding > 0 THEN principal_outstanding - v_distributed_principal_p2 ELSE principal_outstanding END,
                        total_npa_amount = CASE WHEN total_npa_amount > 0 THEN total_npa_amount - v_distributed_principal_p2 ELSE total_npa_amount END,
                        updated_dtm = NOW()
                    WHERE investment_loan_id = v_loan_investment_record.id;

                    -- Create redemption detail
                    INSERT INTO t_redemption_details (
                        investment_loan_id,
                        lender_id,
                        amount_received,
                        principal_received,
                        interest_received,
                        fee_levied,
                        created_dtm,
                        batch_id,
                        redemption_status
                    )
                    VALUES (
                               v_loan_investment_record.id,
                               v_loan_investment_record.lender_id,
                               v_distributed_amount_p2,
                               v_distributed_principal_p2,
                               v_distributed_interest_p2,
                               v_distributed_fees_p2,
                               NOW(),
                               v_batch_id,
                               'SCHEDULED'
                           )
                    RETURNING id INTO v_redemption_detail_id;

                    v_pg_to_escrow_txn_id = generate_txn_id();
                    
                    SELECT balance, id INTO v_prev_balance, v_pg_acc_id
                    FROM t_account
                    WHERE account_id = v_pg_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance - v_distributed_amount_p2
                    WHERE account_id = v_pg_account_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_pg (
                        account_id, event_type, amount, transaction_dtm, transaction_id, narration, created_by, 
                        previous_balance, current_balance
                    )
                    VALUES (
                               v_pg_acc_id, 'DR', v_distributed_amount_p2, now(),
                               v_pg_to_escrow_txn_id,'REPAYMENT RECEIVED', 'SYSTEM', 
                                v_prev_balance, v_updated_balance
                           );
                    
                    SELECT balance, id INTO v_prev_balance, v_borrower_escrow_acc_id
                    FROM t_account
                    WHERE account_id = v_borrower_escrow_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance + v_distributed_amount_p2
                    WHERE account_id = v_borrower_escrow_account_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_borrower_escrow (
                        account_id, event_type, amount, transaction_dtm, transaction_id, narration, created_by,
                        previous_balance, current_balance
                    )
                    VALUES (
                               v_borrower_escrow_acc_id, 'CR', v_distributed_amount_p2,
                               now(), v_pg_to_escrow_txn_id,'REPAYMENT RECEIVED',
                               'SYSTEM', v_prev_balance, v_updated_balance
                           );

                    v_escrow_loan_account_txn_id = generate_txn_id();
                    
                    SELECT balance, id INTO v_prev_balance, v_borrower_escrow_acc_id
                    FROM t_account
                    WHERE account_id = v_borrower_escrow_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance - v_distributed_amount_p2
                    WHERE account_id = v_borrower_escrow_account_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_borrower_escrow (
                        account_id, event_type, amount, transaction_dtm, transaction_id, narration, created_by,
                        source_transaction_id, previous_balance, current_balance
                    )
                    VALUES (
                               v_borrower_escrow_acc_id, 'DR', v_distributed_amount_p2,
                               now(), v_escrow_loan_account_txn_id,
                               'REPAYMENT TRANSFERRED TO LOAN ACCOUNT', 'SYSTEM', v_loan_id,
                            v_prev_balance, v_updated_balance
                           );
                    
                    SELECT balance, id INTO v_prev_balance, v_loan_acc_id
                    FROM t_account
                    WHERE account_id = v_loan_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance + v_distributed_amount_p2
                    WHERE account_id = v_loan_account_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_loan_account (
                        account_id, event_type, amount, transaction_dtm, transaction_id,
                        narration, created_by, source_transaction_id, previous_balance, current_balance
                    )
                    VALUES (
                               v_loan_acc_id, 'CR', v_distributed_amount_p2,
                               now(), v_escrow_loan_account_txn_id,
                               'REPAYMENT TRANSFERRED TO LOAN ACCOUNT', 'SYSTEM', v_loan_id,
                            v_prev_balance, v_updated_balance
                           );

                    v_loan_account_repayment_wallet_txn_id = generate_txn_id();
                    
                    SELECT balance, id INTO v_prev_balance, v_loan_acc_id
                    FROM t_account
                    WHERE account_id = v_loan_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance - v_distributed_amount_p2
                    WHERE account_id = v_loan_account_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_loan_account (
                        account_id, event_type, amount, transaction_dtm, transaction_id,
                        narration, created_by, source_transaction_id, previous_balance, current_balance
                    )
                    VALUES (
                               v_loan_acc_id, 'DR', v_distributed_amount_p2, now(), v_loan_account_repayment_wallet_txn_id,
                               'REPAYMENT CONSUMED AT SCHEME', 'SYSTEM', v_loan_investment_record.id, v_prev_balance, v_updated_balance
                           );
                    
                    SELECT balance, id INTO v_prev_balance, v_repayment_wallet_acc_id
                    FROM t_account
                    WHERE lender_id = v_loan_investment_record.lender_id and account_id = v_lender_repayment_account_id FOR UPDATE NOWAIT;
                    
                    UPDATE t_account
                    SET balance = v_prev_balance + v_distributed_amount_p2
                    WHERE id = v_repayment_wallet_acc_id
                    RETURNING balance INTO v_updated_balance;

                    INSERT INTO t_ledger_lender_repayment_wallet (
                        account_id, event_type, amount, transaction_dtm, transaction_id,
                        narration, created_by, source_transaction_id, previous_balance, current_balance
                    )
                    VALUES (
                               v_repayment_wallet_acc_id, 'CR', v_distributed_amount_p2, now(), v_loan_account_repayment_wallet_txn_id,
                               'REPAYMENT CONSUMED AT SCHEME', 'SYSTEM', v_loan_investment_record.id, v_prev_balance, v_updated_balance
                           );
                    
                    -- Create fee records for FF
                    IF v_distributed_ff_p2 > 0 THEN
                        INSERT INTO t_fee_details (fee_type, fee_amount, fee_source, fee_levy_date, fee_source_id, created_dtm, txn_reference_id)
                        VALUES ('FF', v_distributed_ff_p2, 'REDEMPTION', CURRENT_DATE, v_redemption_detail_id, NOW(), v_batch_id);
                    END IF;

                    -- Create fee records for CF
                    IF v_distributed_cf_p2 > 0 THEN
                        INSERT INTO t_fee_details (fee_type, fee_amount, fee_source, fee_levy_date, fee_source_id, created_dtm, txn_reference_id)
                        VALUES ('CF', v_distributed_cf_p2, 'REDEMPTION', CURRENT_DATE, v_redemption_detail_id, NOW(), v_batch_id);
                    END IF;


                END LOOP;

            -- Validate distribution totals
            IF v_total_distributed_amount > v_repayment_amount THEN
                RAISE EXCEPTION 'Distributed Amount % > Repayment Amount % : %', v_total_distributed_amount, v_repayment_amount, v_loan_id;
            ELSEIF v_total_distributed_amount < v_repayment_amount THEN
                v_distribution_adjustment_amount := v_repayment_amount - v_total_distributed_amount;
                UPDATE t_investment_loan_repayment_summary
                SET total_adjustment_amount = total_adjustment_amount + v_distribution_adjustment_amount,
                    updated_dtm = NOW()
                WHERE investment_loan_id = v_last_processed_investment_loan_id;
                RAISE INFO 'Distributed Amount % < Repayment Amount % : Adjusted at %', v_total_distributed_amount, v_repayment_amount, v_last_processed_investment_loan_id;
            END IF;

            -- Mark the repayment as processed and update batch_id
            UPDATE t_loan_repayment_detail
            SET is_processed = TRUE,
                batch_id = v_batch_id,
                updated_dtm = NOW()
            WHERE id = v_repayment_record.id AND is_processed = FALSE;

        END LOOP;

    -- Update processing log
    UPDATE t_repayment_processing_logs
    SET status = 'COMPLETED',
        processed_loans = (SELECT COUNT(*) FROM t_loan_repayment_detail WHERE batch_id = v_batch_id AND is_processed = TRUE),
        updated_dtm = v_current_timestamp
    WHERE id = v_batch_id;

    inout_response := 0;

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
                my_ex_state = RETURNED_SQLSTATE,
                my_ex_message = MESSAGE_TEXT,
                my_ex_detail = PG_EXCEPTION_DETAIL,
                my_ex_hint = PG_EXCEPTION_HINT,
                my_ex_ctx = PG_EXCEPTION_CONTEXT;

            -- Update processing log with error
            IF v_batch_id IS NOT NULL THEN
                UPDATE t_repayment_processing_logs
                SET status = 'FAILED',
                    error_message = 'ERROR: ' || my_ex_message,
                    updated_dtm = NOW()
                WHERE id = v_batch_id;
            END IF;

            INSERT INTO t_error_log (sp_name, err_state, err_message, err_details, err_hint, err_context, created_dtm)
            VALUES ('prc_process_repayments', my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx, NOW());

            RAISE INFO 'THE FOLLOWING ERROR OCCURRED % % % % %', my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;
            inout_response := -1;
        END;
END;
$$;
