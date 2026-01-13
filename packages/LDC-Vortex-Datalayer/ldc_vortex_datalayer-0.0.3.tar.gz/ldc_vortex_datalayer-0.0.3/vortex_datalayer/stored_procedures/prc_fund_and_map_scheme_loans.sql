create procedure prc_fund_and_map_scheme_loans(IN in_scheme_data jsonb, IN v_inv_wallet_txn_id character varying, IN in_investor_scheme_id bigint, IN loan_records jsonb, INOUT inout_response jsonb DEFAULT NULL::jsonb)
    language plpgsql
as
$$
DECLARE
    v_investment_amount NUMERIC := (in_scheme_data ->> 'investment_amount')::NUMERIC;
    v_investment_type VARCHAR := in_scheme_data ->> 'investment_type';
    v_partial_funding BOOLEAN := in_scheme_data ->> 'partial_funding';
    v_investor_id INT := (in_scheme_data ->> 'lender_id')::INT;
    v_failed_loans TEXT[] := '{}';
    v_amount_funded NUMERIC := 0;
    v_success_json JSONB := '{}'::JSONB;
    v_loan_id VARCHAR;
    v_loan_acc_txn_id VARCHAR;
    v_pg_acc_txn_id VARCHAR;
    v_pg_escrow_id BIGINT;
    v_amount_per_loan NUMERIC;
    v_amount_remaining NUMERIC;
    v_balance NUMERIC;
    v_updated_balance NUMERIC;
    v_prev_balance NUMERIC;
    v_remaining_amount NUMERIC;
    v_is_negotiated BOOLEAN;
    v_loan_record RECORD;
    v_investment_loan_id BIGINT;
    v_loan_account_id BIGINT;
    v_borrower_escrow_id BIGINT;
    v_loan_acc_id BIGINT;
    v_borrower_escrow_acc_id BIGINT;
    v_pg_acc_id BIGINT;
    v_total_unfunded_count BIGINT := 0;
    v_total_funded_count BIGINT := 0;
    v_total_modified_count BIGINT := 0;
    v_loan JSONB;
BEGIN

    IF loan_records IS NULL THEN
        RAISE EXCEPTION 'No loans available';
    END IF;

    v_loan_account_id = (SELECT id FROM t_master_account WHERE account_name = 'LOAN_ACCOUNT');
    v_borrower_escrow_id = (SELECT id FROM t_master_account WHERE account_name = 'BORROWER_ESCROW');
    v_pg_escrow_id = (SELECT id FROM t_master_account WHERE account_name = 'PG');
    v_loan_acc_txn_id = generate_txn_id();
    v_pg_acc_txn_id = generate_txn_id();
    v_amount_remaining := v_investment_amount;

    -- Fund selected loans
    FOR v_loan IN SELECT * FROM jsonb_array_elements(loan_records)
    LOOP
        v_amount_per_loan := (v_loan->>'lent_amount')::NUMERIC;
        v_loan_id := (v_loan->>'loan_id');
        v_is_negotiated := (v_loan->>'is_modified');

        IF v_investment_type in ('ONE_TIME_LENDING', 'MEDIUM_TERM_LENDING') THEN
            IF v_amount_remaining < v_amount_per_loan THEN
                v_amount_per_loan := v_amount_remaining;
            END IF;
        END IF;

        -- Lock on loan
        BEGIN
            SELECT tl.id, tl.amount, tl.loan_ref_id, tl.investment_amount_sum, tl.remaining_amount,
                   tl.borrower_name, tl.tenure, tl.loan_product_config_id, tl.interest_rate,
                   tl.repayment_frequency
            INTO v_loan_record
            FROM t_loan tl
            WHERE tl.loan_ref_id = v_loan_id
              AND tl.status = 'LIVE'
              AND (
                    v_investment_type <> 'ONE_TIME_LENDING'
                    OR (tl.investment_amount_sum + v_amount_per_loan) <= tl.amount
                  )
              AND NOT EXISTS(
                  SELECT 1
                  FROM t_lender_investment tli
                  JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                  WHERE tli.lender_id = v_investor_id
                    AND tild.loan_id = tl.id
                    AND tild.deleted IS NULL
                    AND tli.deleted IS NULL
              )
            FOR UPDATE NOWAIT;
        EXCEPTION WHEN LOCK_NOT_AVAILABLE THEN
            INSERT INTO t_app_logs(created_dtm, msg, event_name)
            VALUES (now(), 'lock is unavailable for scheme' || in_investor_scheme_id, 'LOCK_NOT_AVAILABLE');
            v_failed_loans := array_append(v_failed_loans, v_loan_id);
            v_total_unfunded_count := (v_total_unfunded_count + 1);
            CONTINUE;
        END;

        IF (v_loan_record.id IS NULL) OR (v_loan_record.amount <= v_loan_record.investment_amount_sum) OR (v_loan_record.remaining_amount < 250) THEN
            v_failed_loans := array_append(v_failed_loans, v_loan_id);
            v_total_unfunded_count := (v_total_unfunded_count + 1);
            CONTINUE;
        END IF;

        IF v_investment_type = 'MANUAL_LENDING' THEN
            IF v_partial_funding THEN
                IF v_amount_per_loan > v_loan_record.remaining_amount THEN
                   v_amount_per_loan := v_loan_record.remaining_amount;
                END IF;
            ELSE
                IF v_loan_record.amount < (v_loan_record.amount + v_amount_per_loan) THEN
                    v_failed_loans := array_append(v_failed_loans, v_loan_id);
                    v_total_unfunded_count := (v_total_unfunded_count + 1);
                    CONTINUE;
                END IF;
            END IF;
        END IF;

        IF v_is_negotiated THEN
            INSERT INTO t_investment_loan_detail(
                created_dtm, investment_id, loan_id, investment_amount, allocation_percentage, is_negotiated, has_lent
            )
            VALUES (now(), in_investor_scheme_id, v_loan_record.id,
                    0, 0,
                    v_is_negotiated, NOT v_is_negotiated)
            RETURNING id INTO v_investment_loan_id;
            v_total_modified_count := v_total_modified_count + 1;
            v_amount_funded := v_amount_funded + v_amount_per_loan;

            v_success_json := v_success_json || jsonb_build_object(
                v_loan_id,
                jsonb_build_object(
                    'scheme_id', in_scheme_data ->> 'investment_id',
                    'tenure', v_loan_record.tenure,
                    'loan_id', v_loan_id,
                    'interest_rate', v_loan_record.interest_rate,
                    'repayment_type', v_loan_record.repayment_frequency,
                    'lent_amount', v_amount_per_loan
                )
            );
            CONTINUE;
        END IF;

        -- Update loan
        UPDATE t_loan
        SET investment_amount_sum = investment_amount_sum + v_amount_per_loan,
            remaining_amount = amount - (investment_amount_sum + v_amount_per_loan),
            updated_dtm = now()
        WHERE id = v_loan_record.id;

        -- Insert loan detail
        INSERT INTO t_investment_loan_detail(
                created_dtm, investment_id, loan_id, investment_amount, allocation_percentage, is_negotiated, has_lent
        )
        VALUES (now(), in_investor_scheme_id, v_loan_record.id,
                v_amount_per_loan, (v_amount_per_loan/v_loan_record.amount*100),
                v_is_negotiated, NOT v_is_negotiated)
        RETURNING id INTO v_investment_loan_id;

        -- Repayment summary
        INSERT INTO t_investment_loan_repayment_summary (
            investment_loan_id, created_dtm, principal_outstanding
        )
        VALUES (v_investment_loan_id, now(), v_amount_per_loan);

         -- Redemption summary
        INSERT INTO t_investment_loan_redemption_summary (
            investment_loan_id, principal_outstanding, created_dtm
        )
        VALUES (v_investment_loan_id, v_amount_per_loan, now());

        SELECT balance, id INTO v_balance, v_loan_acc_id
        FROM t_account
        WHERE account_type_id = v_loan_account_id AND deleted IS NULL FOR UPDATE NOWAIT;

        UPDATE t_account
        SET balance = balance + v_amount_per_loan
        WHERE account_type_id = v_loan_account_id;

        -- LEDGER
        INSERT INTO t_ledger_loan_account (
            account_id, event_type, amount, transaction_dtm, transaction_id, source_transaction_id,
            narration, created_by, previous_balance, current_balance
        )
        VALUES (
            v_loan_acc_id, 'CR', v_amount_per_loan, now(),
            v_inv_wallet_txn_id,
            in_investor_scheme_id,
            CONCAT('BY SCHEME - ', in_scheme_data ->> 'investment_id', ', LOAN - ', v_loan_record.loan_ref_id),
            'SYSTEM',
            v_balance, v_balance + v_amount_per_loan
        );

        SELECT remaining_amount INTO v_remaining_amount
        FROM t_loan
        WHERE loan_ref_id = v_loan_record.loan_ref_id;

        IF v_remaining_amount = 0 THEN

            SELECT balance INTO v_prev_balance
            FROM t_account
            WHERE account_type_id = v_loan_account_id FOR UPDATE NOWAIT;

            UPDATE t_account
            SET balance = v_prev_balance - v_loan_record.amount
            WHERE account_type_id = v_loan_account_id
            RETURNING balance INTO v_updated_balance;

            INSERT INTO t_ledger_loan_account (
                account_id, event_type, amount, transaction_dtm, transaction_id, source_transaction_id,
                narration, created_by, previous_balance, current_balance
            )
            VALUES (
                v_loan_acc_id, 'DR', v_loan_record.amount, now(),
                v_loan_acc_txn_id,
                v_loan_record.id,CONCAT('LOAN DISBURSED - ', v_loan_record.loan_ref_id),
                'SYSTEM', v_prev_balance, v_updated_balance
            );

            SELECT balance, id INTO v_prev_balance, v_borrower_escrow_acc_id
            FROM t_account
            WHERE account_type_id = v_borrower_escrow_id FOR UPDATE NOWAIT;

            UPDATE t_account
            SET balance = v_prev_balance + v_loan_record.amount
            WHERE account_type_id = v_borrower_escrow_id
            RETURNING balance INTO v_updated_balance;

            INSERT INTO t_ledger_borrower_escrow (
                account_id, event_type, amount, transaction_dtm, transaction_id, source_transaction_id,
                narration, created_by, previous_balance, current_balance
            )
            VALUES (
                v_borrower_escrow_acc_id, 'CR', v_loan_record.amount, now(),
                v_loan_acc_txn_id,
                v_loan_record.id,CONCAT('LOAN DISBURSED - ', v_loan_record.loan_ref_id), 'SYSTEM',
                v_prev_balance, v_updated_balance
            );

            SELECT balance INTO v_prev_balance
            FROM t_account
            WHERE account_type_id = v_borrower_escrow_id FOR UPDATE NOWAIT;

            UPDATE t_account
            SET balance = v_prev_balance - v_loan_record.amount
            WHERE account_type_id = v_borrower_escrow_id
            RETURNING balance INTO v_updated_balance;

            INSERT INTO t_ledger_borrower_escrow (
                account_id, event_type, amount, transaction_dtm, transaction_id,
                narration, created_by, previous_balance, current_balance
            )
            VALUES (
                v_borrower_escrow_acc_id, 'DR', v_loan_record.amount, now(),
                v_pg_acc_txn_id,
                CONCAT('LOAN DISBURSED - ', v_loan_record.loan_ref_id), 'SYSTEM',
                v_prev_balance, v_updated_balance
            );

            SELECT balance, id INTO v_prev_balance, v_pg_acc_id
            FROM t_account
            WHERE account_type_id = v_pg_escrow_id FOR UPDATE NOWAIT;

            UPDATE t_account
            SET balance = v_prev_balance + v_loan_record.amount
            WHERE account_type_id = v_pg_escrow_id
            RETURNING balance INTO v_updated_balance;

            INSERT INTO t_ledger_pg (
                account_id, event_type, amount, transaction_dtm, transaction_id,
                narration, created_by, previous_balance, current_balance
            )
            VALUES (
                v_pg_acc_id, 'CR', v_loan_record.amount, now(),
                v_pg_acc_txn_id,
                CONCAT('LOAN DISBURSED - ', v_loan_record.loan_ref_id), 'SYSTEM',
                v_prev_balance, v_updated_balance
            );
        END IF;

        -- Build success JSON
        v_success_json := v_success_json || jsonb_build_object(
            v_loan_id,
            jsonb_build_object(
                'scheme_id', in_scheme_data ->> 'investment_id',
                'tenure', v_loan_record.tenure,
                'loan_id', v_loan_id,
                'interest_rate', v_loan_record.interest_rate,
                'repayment_type', v_loan_record.repayment_frequency,
                'lent_amount', v_amount_per_loan
            )
        );

        v_total_funded_count := v_total_funded_count + 1;
        v_amount_funded := v_amount_funded + v_amount_per_loan;
        v_amount_remaining := v_amount_remaining - v_amount_per_loan;

        -- Stop if fully funded
        IF v_amount_funded = v_investment_amount THEN
            EXIT;
        END IF;

    END LOOP;

    IF v_investment_type in ('ONE_TIME_LENDING', 'MEDIUM_TERM_LENDING') THEN
        IF v_investment_amount != v_amount_funded OR v_amount_funded = 0 THEN
               RAISE EXCEPTION 'Amount not satisfied | SCHEME_ID: % | v_lending_amount: % | v_amount_funded: %', in_investor_scheme_id, v_investment_amount, v_amount_funded;
        END IF;
    END IF;

    IF NOT v_is_negotiated THEN
        IF v_amount_funded > 0 THEN
            UPDATE t_lender_investment
            SET amount_lent_on_investment = v_amount_funded
            WHERE id = in_investor_scheme_id;
        ELSE
            RAISE EXCEPTION 'All loans are funded';
        END IF;
    END IF;

    -- Build final response
    inout_response := jsonb_build_object(
        'failed_loan_ids', to_jsonb(v_failed_loans),
        'total_funded_count', COALESCE(v_total_funded_count, 0),
        'total_unfunded_count', COALESCE(v_total_unfunded_count, 0),
        'total_modified_count', COALESCE(v_total_modified_count, 0),
        'total_success_lent_amount', v_amount_funded,
        'total_pending_amount', v_investment_amount - v_amount_funded,
        'total_lending_amount', v_investment_amount,
        'success_transaction_list', v_success_json
    );

EXCEPTION
    WHEN OTHERS THEN
        DECLARE
            my_ex_state text;
            my_ex_message text;
            my_ex_detail text;
            my_ex_hint text;
            my_ex_ctx text;
        BEGIN
            raise notice 'ERROR OCCURED';
            GET STACKED DIAGNOSTICS
                my_ex_state   = RETURNED_SQLSTATE,
                my_ex_message = MESSAGE_TEXT,
                my_ex_detail  = PG_EXCEPTION_DETAIL,
                my_ex_hint    = PG_EXCEPTION_HINT,
                my_ex_ctx     = PG_EXCEPTION_CONTEXT
            ;
            INSERT INTO t_error_log (sp_name,err_state,err_message,err_details,err_hint,err_context,created_dtm,updated_dtm) values
                ('PRC_FUND_AND_MAP_SCHEME_LOANS',my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx,now(),now());
            raise info 'THE FOLLOWING ERROR OCCURED % % % % %', my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx;
            inout_response = -1;
        END;
END;
$$;