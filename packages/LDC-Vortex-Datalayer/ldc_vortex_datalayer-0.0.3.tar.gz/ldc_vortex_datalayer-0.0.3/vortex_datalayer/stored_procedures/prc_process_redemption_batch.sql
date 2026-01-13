create procedure prc_process_redemption_batch(IN lender_ids bigint[], INOUT inout_response integer DEFAULT NULL::integer)
    language plpgsql
as
$$
DECLARE
    v_current_timestamp timestamp with time zone := NOW();
    v_rows_processed INTEGER := 0;
    v_lender_repayment_master_account_id bigint;

    v_pg_account_id BIGINT;
    v_lender_repayment_account_id BIGINT;
    v_repayment_wallet_pg_txn_id VARCHAR;


    v_prev_balance NUMERIC;
    v_updated_balance NUMERIC;
    v_pg_acc_id BIGINT;
    v_repayment_wallet_acc_id BIGINT;

    v_redemption_record RECORD;
BEGIN
    select id into v_lender_repayment_master_account_id from t_master_account where account_name = 'LENDER_REPAYMENT_WALLET';
    if v_lender_repayment_master_account_id is null then
        raise exception 'Lender repayment master account not found';
    end if;

    v_pg_account_id = (SELECT id FROM t_master_account WHERE account_name = 'PG');
    v_lender_repayment_account_id = (SELECT id FROM t_master_account WHERE account_name = 'LENDER_REPAYMENT_WALLET');

    -- Step 1: Create temp table with aggregated data by (lender_id, investment_id)
    -- This aggregates all redemption_details into investment-level summaries
    -- UNLOGGED for better performance (no WAL writes, acceptable for temp tables)
    --
    -- IMPORTANT: Lock only t_redemption_details rows, not joined tables
    -- This is done by first selecting and locking from t_redemption_details in a subquery,
    -- then joining with other tables. This way, FOR UPDATE only applies to t_redemption_details.
    CREATE TEMP TABLE temp_redemption_investment_summary AS
    WITH locked_redemption_details AS (
        -- First, select and lock only t_redemption_details rows
        SELECT
            trd.id,
            trd.lender_id,
            trd.investment_loan_id,
            trd.amount_received,
            trd.principal_received,
            trd.interest_received,
            trd.fee_levied
        FROM t_redemption_details trd
        WHERE trd.redemption_status = 'SCHEDULED'
          AND trd.redemption_id IS NULL
          AND trd.redemption_type = 'REPAYMENT'
          AND trd.lender_id = ANY(lender_ids)
            FOR UPDATE SKIP LOCKED  -- Lock only t_redemption_details rows
    )
    SELECT
        lrd.lender_id,
        tild.investment_id,
        tli.product_config_id,
        tprtcm.repayment_type::investment_repayment_transaction_type as investment_type,
        tprtcm.repayment_type::text as transaction_type,  -- Transaction type from mapping table
        ta.account_id,
        SUM(lrd.amount_received) as total_amount_received,
        SUM(lrd.principal_received) as total_principal,
        SUM(lrd.interest_received) as total_interest,
        SUM(lrd.fee_levied) as total_fee_levied,
        ARRAY_AGG(lrd.id ORDER BY lrd.id) as redemption_detail_ids  -- Array of IDs for bulk update
    FROM locked_redemption_details lrd
             JOIN t_investment_loan_detail tild ON lrd.investment_loan_id = tild.id
             JOIN t_lender_investment tli ON tli.id = tild.investment_id
             JOIN t_product_repayment_transaction_config_mapping tprtcm ON tli.product_config_id = tprtcm.product_config_id
             JOIN t_account ta ON ta.lender_id = tli.lender_id AND ta.account_id = v_lender_repayment_master_account_id
    WHERE tild.deleted IS NULL
    GROUP BY lrd.lender_id, tild.investment_id, tli.product_config_id, tprtcm.repayment_type, ta.account_id;

    -- Add index on lender_id for faster JOINs
    CREATE INDEX idx_temp_redemption_investment_summary_lender_id
        ON temp_redemption_investment_summary(lender_id);

    -- Get count of rows processed
    SELECT COUNT(*) INTO v_rows_processed FROM temp_redemption_investment_summary;

    -- If no rows to process, return early
    IF v_rows_processed = 0 THEN
        inout_response := 0;
        RAISE INFO 'NO RECORD TO PROCESS: %', v_rows_processed;
        RETURN;
    END IF;

    -- Step 2: Create temp table with aggregated data by lender_id
    -- This aggregates investment-level summaries into lender-level totals
    CREATE TEMP TABLE temp_redemption_lender_summary AS
    SELECT
        lender_id,
        SUM(total_amount_received) as total_amount_received,
        SUM(total_principal) as total_principal,
        SUM(total_interest) as total_interest,
        SUM(total_fee_levied) as total_fee_levied
    FROM temp_redemption_investment_summary
    GROUP BY lender_id;

    -- Add index on lender_id for faster JOINs
    CREATE INDEX idx_temp_redemption_lender_summary_lender_id
        ON temp_redemption_lender_summary(lender_id);

    -- Step 3 & 4: Create t_lender_redemption records and capture redemption_ids using RETURNING
    -- This approach uses CTE with RETURNING to directly capture the mapping
    -- More reliable than using created_dtm for mapping - eliminates race conditions
    CREATE TEMP TABLE temp_redemption_id_map AS
    WITH inserted_redemptions AS (
        INSERT INTO t_lender_redemption (
                                         lender_id,
                                         total_amount_redeemed,
                                         total_amount_received,
                                         total_principal,
                                         total_interest,
                                         total_fee_levied,
                                         redemption_status,
                                         redemption_type,
                                         status_dtm,
                                         created_dtm,
                                         updated_dtm
            )
            SELECT
                lender_id,
                0.00,  -- amount_redeemed updated via callback API
                total_amount_received,
                total_principal,
                total_interest,
                total_fee_levied,
                'PENDING',
                'REPAYMENT',  -- Only processing REPAYMENT type redemptions
                v_current_timestamp,
                v_current_timestamp,
                v_current_timestamp
            FROM temp_redemption_lender_summary
            RETURNING id as redemption_id, lender_id
    )
    SELECT
        redemption_id,
        lender_id
    FROM inserted_redemptions;

    -- Add index on lender_id for faster JOINs
    CREATE INDEX idx_temp_redemption_id_map_lender_id
        ON temp_redemption_id_map(lender_id);

    -- Step 5: Create t_redemption_summary records and capture IDs for wallet transactions
    CREATE TEMP TABLE temp_redemption_summary_with_ids AS
    WITH inserted_redemption_summaries AS (
        INSERT INTO t_redemption_summary (
                                          lender_id,
                                          investment_id,
                                          total_amount_redeemed,
                                          total_amount_received,
                                          total_principal,
                                          total_interest,
                                          total_fee_levied,
                                          type,
                                          redemption_status,
                                          redemption_id,
                                          redemption_type,
                                          created_dtm,
                                          updated_dtm
            )
            SELECT
                tris.lender_id,
                tris.investment_id,
                0.00,  -- amount_redeemed updated via callback API
                tris.total_amount_received,
                tris.total_principal,
                tris.total_interest,
                tris.total_fee_levied,
                tris.investment_type,
                'PENDING',
                trim.redemption_id,
                'REPAYMENT',  -- Only processing REPAYMENT type redemptions
                v_current_timestamp,
                v_current_timestamp
            FROM temp_redemption_investment_summary tris
                     JOIN temp_redemption_id_map trim ON tris.lender_id = trim.lender_id
            RETURNING
                id as redemption_summary_id,
                lender_id,
                investment_id,
                total_amount_received,
                type as investment_type,
                redemption_id
    )
    SELECT
        redemption_summary_id,
        lender_id,
        investment_id,
        total_amount_received,
        investment_type,
        redemption_id
    FROM inserted_redemption_summaries;

    -- Add index for faster JOINs
    CREATE INDEX idx_temp_redemption_summary_with_ids_lender_id
        ON temp_redemption_summary_with_ids(lender_id);

    -- Step 6: Insert wallet transactions for t_redemption_summary records
    -- Transaction type comes from t_product_repayment_transaction_config_mapping
    INSERT INTO t_lender_wallet_transaction (
        created_dtm,
        account_id,
        amount,
        transaction_type,
        lender_id,
        status,
        transaction_id
    )
    SELECT
        v_current_timestamp,
        v_lender_repayment_master_account_id,
        trswi.total_amount_received,
        tris.transaction_type,  -- Use transaction_type from mapping table
        trswi.lender_id,
        'SUCCESS',
        generate_txn_id(NULL)  -- No prefix for redemption_summary transactions
    FROM temp_redemption_summary_with_ids trswi
             JOIN temp_redemption_investment_summary tris
                  ON trswi.lender_id = tris.lender_id
                      AND trswi.investment_id = tris.investment_id;

    -- Step 7: Insert wallet transactions for a t_lender_redemption records
    -- Transaction type: 'REPAYMENT AUTO WITHDRAWAL' with prefix 'INVW'
    INSERT INTO t_lender_wallet_transaction (
        created_dtm,
        account_id,
        amount,
        transaction_type,
        lender_id,
        status,
        transaction_id
    )
    SELECT
        v_current_timestamp,
        v_lender_repayment_master_account_id,
        trls.total_amount_received,
        'REPAYMENT AUTO WITHDRAWAL',
        trim.lender_id,
        'SCHEDULED',
        generate_txn_id('INVW')  -- Prefix 'INVW' for lender_redemption transactions
    FROM temp_redemption_id_map trim
             JOIN temp_redemption_lender_summary trls ON trim.lender_id = trls.lender_id;

    -- Step 8: Bulk UPDATE t_redemption_details (single UPDATE for all records)
    -- This updates all redemption_details with their redemption_id and status
    UPDATE t_redemption_details trd
    SET redemption_id = trim.redemption_id,
        redemption_status = 'PENDING',
        updated_dtm = v_current_timestamp
    FROM temp_redemption_investment_summary tris
             JOIN temp_redemption_id_map trim ON tris.lender_id = trim.lender_id
    WHERE trd.id = ANY(tris.redemption_detail_ids);


    v_repayment_wallet_pg_txn_id = generate_txn_id();

    FOR v_redemption_record IN
        SELECT * from temp_redemption_investment_summary
        LOOP

        SELECT balance, id INTO v_prev_balance, v_repayment_wallet_acc_id
        FROM t_account
        WHERE account_id = v_lender_repayment_account_id and lender_id = v_redemption_record.lender_id  FOR UPDATE NOWAIT;

        UPDATE t_account
        SET balance = v_prev_balance - v_redemption_record.total_amount_received
        WHERE id = v_repayment_wallet_acc_id
        RETURNING balance INTO v_updated_balance;

        INSERT INTO t_ledger_lender_repayment_wallet (
            account_id, event_type, amount, transaction_dtm, transaction_id, narration, created_by, previous_balance,
            current_balance
        )
        VALUES (
                   v_repayment_wallet_acc_id, 'DR', v_redemption_record.total_amount_received,
                now(), v_repayment_wallet_pg_txn_id,
                   'REPAYMENT TRANSFERRED TO PG', 'SYSTEM', v_prev_balance, v_updated_balance
               );

        SELECT balance, id INTO v_prev_balance, v_pg_acc_id
        FROM t_account
        WHERE account_id = v_pg_account_id FOR UPDATE NOWAIT;

        UPDATE t_account
        SET balance = v_prev_balance + v_redemption_record.total_amount_received
        WHERE account_id = v_pg_account_id
        RETURNING balance INTO v_updated_balance;

        INSERT INTO t_ledger_pg (
            account_id, event_type, amount, transaction_dtm, transaction_id, narration, created_by, previous_balance,
            current_balance
        )
        VALUES (
                   v_pg_acc_id, 'CR', v_redemption_record.total_amount_received,
                   now(), v_repayment_wallet_pg_txn_id,
                   'REPAYMENT TRANSFERRED TO PG', 'SYSTEM', v_prev_balance,
                v_updated_balance
               );
    END LOOP;
    
    -- Step 9: Cleanup temp tables (optional, auto-dropped at the end of transaction)
    -- Explicitly dropping for clarity and to free memory immediately
    DROP TABLE IF EXISTS temp_redemption_investment_summary;
    DROP TABLE IF EXISTS temp_redemption_lender_summary;
    DROP TABLE IF EXISTS temp_redemption_id_map;
    DROP TABLE IF EXISTS temp_redemption_summary_with_ids;

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

            -- Cleanup temp tables on error
            DROP TABLE IF EXISTS temp_redemption_investment_summary;
            DROP TABLE IF EXISTS temp_redemption_lender_summary;
            DROP TABLE IF EXISTS temp_redemption_id_map;
            DROP TABLE IF EXISTS temp_redemption_summary_with_ids;

            INSERT INTO t_error_log (
                sp_name, err_state, err_message, err_details, err_hint, err_context, created_dtm
            )
            VALUES (
                       'prc_process_redemption_batch',
                       my_ex_state,
                       my_ex_message,
                       my_ex_detail,
                       my_ex_hint,
                       my_ex_ctx,
                       NOW()
                   );

            RAISE INFO 'THE FOLLOWING ERROR OCCURRED % % % % %',
                my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;
            inout_response := -1;
        END;
END;
$$;