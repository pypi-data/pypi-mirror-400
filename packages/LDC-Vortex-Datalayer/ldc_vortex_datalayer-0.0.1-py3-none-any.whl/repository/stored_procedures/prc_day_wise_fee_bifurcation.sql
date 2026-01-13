create procedure prc_day_wise_fee_bifurcation(IN in_date date DEFAULT CURRENT_DATE)
    language plpgsql
as
$$
DECLARE
    ts_start                TIMESTAMP;
    ts_end                  TIMESTAMP;
    v_total_fee             NUMERIC(18, 4) := 0;
    v_remaining_amount      NUMERIC(18, 4) := 0;
    v_chunk_amount          NUMERIC(18, 4) := 5000000;
    v_redemption_txn_id     VARCHAR;
    v_txn_id                VARCHAR;
    v_income_master_acc_id  BIGINT;
    v_income_acc_id         BIGINT;
    v_txn_pk                BIGINT;

BEGIN
    ---------------------------------------------
    -- Load core parameters
    ---------------------------------------------
    SELECT id INTO v_income_master_acc_id
    FROM t_master_account
    WHERE account_name = 'INCOME_ACCOUNT';

    SELECT id INTO v_income_acc_id
    FROM t_account
    WHERE account_type_id = v_income_master_acc_id;

    ---------------------------------------------
    -- STEP 1: Fee calculation for yesterday
    ---------------------------------------------
    SELECT COALESCE(SUM(fee_amount),0)
    INTO v_total_fee
    FROM t_fee_details
    WHERE fee_source = 'INVESTMENT_LOAN'
      AND fee_levy_date = in_date - 1;

    IF v_total_fee = 0 THEN
        RAISE EXCEPTION 'No fee amount available for processing.';
    END IF;

    v_remaining_amount := v_total_fee;

    ---------------------------------------------
    -- STEP 2: Create unique batch ID
    ---------------------------------------------
    v_redemption_txn_id := 'INRR' || (EXTRACT(EPOCH FROM clock_timestamp()) * 1000000)::BIGINT;

    ---------------------------------------------
    -- STEP 3: wallet transaction
    ---------------------------------------------
    WHILE v_remaining_amount > v_chunk_amount LOOP
        v_txn_id := generate_txn_id();

        INSERT INTO t_lender_wallet_transaction (
            account_id, amount, transaction_type, status, transaction_id
        )
        VALUES (
            v_income_acc_id,
            v_chunk_amount,
            'INNOFIN TRANSFER',
            'SCHEDULED',
            v_txn_id
        )
        RETURNING id INTO v_txn_pk;

        INSERT INTO t_innofin_gst_mapping (
            wallet_transaction_id, mapping_id, amount
        )
        VALUES (
            v_txn_pk,
            v_redemption_txn_id,
            v_chunk_amount
        );

        INSERT INTO t_ledger_income_account (
            account_id, event_type, amount, transaction_dtm, transaction_id,
            narration, created_by, source_transaction_id
        )
        VALUES (
            v_income_acc_id, 'DR', v_chunk_amount, now(),
            v_txn_id,'INNOFIN INCOME TRANSFERRED', 'SYSTEM',
            v_txn_pk
        );

        v_remaining_amount := v_remaining_amount - v_chunk_amount;
    END LOOP;

    v_txn_id := generate_txn_id();

    INSERT INTO t_lender_wallet_transaction (
        account_id, amount, transaction_type, status, transaction_id
    )
    VALUES (
        v_income_acc_id,
        v_remaining_amount,
        'INNOFIN TRANSFER',
        'SCHEDULED',
        v_txn_id
    )
    RETURNING id INTO v_txn_pk;

    INSERT INTO t_innofin_gst_mapping (
        wallet_transaction_id,
        mapping_id,
        amount
    )
    VALUES (
        v_txn_pk,
        v_redemption_txn_id,
        v_remaining_amount
    );

    INSERT INTO t_ledger_income_account (
        account_id, event_type, amount, transaction_dtm, transaction_id,
        narration, created_by, source_transaction_id
    )
    VALUES (
        v_income_acc_id, 'DR', v_remaining_amount, now(),
        v_txn_id,'INNOFIN INCOME TRANSFERRED', 'SYSTEM',
        v_txn_pk
    );

    ---------------------------------------------
    -- STEP 4: Insert bifurcation
    ---------------------------------------------
    ts_start := clock_timestamp();

    INSERT INTO investors.lendenapp_day_wise_fee_bifurcation (
        user_id, amount, net_fee_amount, purpose, transaction_date,
        partner_code, status, batch_id
    )
    SELECT
        tl.user_id,
        tfd.fee_amount,
        tfd.fee_amount AS net_fee_amount,
        CASE tfd.fee_type
            WHEN 'FF' THEN 'FF001'
            WHEN 'CF' THEN 'CF001'
            WHEN 'RF' THEN 'RF001'
        END AS purpose,
        tfd.fee_levy_date,
        tlpc.partner_code,
        'PROCESSING',
        v_redemption_txn_id
    FROM t_fee_details tfd
    JOIN t_investment_loan_detail tild ON tfd.fee_source_id = tild.id
    JOIN t_loan tlo ON tild.loan_id = tlo.id
    JOIN t_loan_product_config tlpc ON tlo.loan_product_config_id = tlpc.id
    JOIN t_lender_investment tli ON tild.investment_id = tli.id
    JOIN t_lender tl ON tli.lender_id = tl.id
    WHERE tfd.fee_source = 'INVESTMENT_LOAN'
      AND tfd.fee_levy_date = in_date - 1;

    ts_end := clock_timestamp();

EXCEPTION WHEN OTHERS THEN
    DECLARE
        my_ex_state   TEXT;
        my_ex_message TEXT;
        my_ex_detail  TEXT;
        my_ex_hint    TEXT;
        my_ex_ctx     TEXT;
    BEGIN
        RAISE NOTICE 'ERROR OCCURRED';

        -- Capture detailed error information
        GET STACKED DIAGNOSTICS
            my_ex_state   = RETURNED_SQLSTATE,
            my_ex_message = MESSAGE_TEXT,
            my_ex_detail  = PG_EXCEPTION_DETAIL,
            my_ex_hint    = PG_EXCEPTION_HINT,
            my_ex_ctx     = PG_EXCEPTION_CONTEXT;

        -- Log the error
        INSERT INTO t_error_log (
            sp_name, err_state, err_message, err_details,
            err_hint, err_context, created_dtm, updated_dtm
        )
        VALUES (
            'PRC_DAY_WISE_FEE_BIFURCATION', my_ex_state, my_ex_message,
            my_ex_detail, my_ex_hint, my_ex_ctx, NOW(), NOW()
        );

        RAISE INFO 'ERROR: % % % % %',
            my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;
    END;
END;
$$;