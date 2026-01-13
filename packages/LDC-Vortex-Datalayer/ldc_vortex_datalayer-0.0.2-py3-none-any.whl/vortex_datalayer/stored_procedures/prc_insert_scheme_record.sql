create procedure prc_insert_scheme_record(IN in_scheme_data jsonb, INOUT v_investor_scheme_id bigint, INOUT v_inv_wallet_txn_id character varying, INOUT v_maturity_date date, INOUT v_start_date date, INOUT v_order_id character varying, INOUT v_user_id character varying, INOUT v_scheme_product_type product_type_enum, INOUT inout_response jsonb DEFAULT NULL::jsonb)
    language plpgsql
as
$$
DECLARE
    v_investment_id VARCHAR := in_scheme_data ->> 'investment_id';
    v_investment_type VARCHAR := in_scheme_data ->> 'investment_type';
    v_partner_code VARCHAR := in_scheme_data ->> 'partner_code';
    v_tenure INT := (in_scheme_data ->> 'tenure')::INT;
    v_investment_amount NUMERIC := (in_scheme_data ->> 'investment_amount')::NUMERIC;
    v_balance NUMERIC;
    v_preference_id   BIGINT := COALESCE((in_scheme_data ->> 'preference_id')::BIGINT, 4);
    v_loan_tenure     VARCHAR := REPLACE(REPLACE(in_scheme_data ->> 'loan_tenure', '[', ''), ']', '');
    v_investor_id INT := (in_scheme_data ->> 'lender_id')::INT;
    v_investment_type_id BIGINT;
    v_product_config RECORD;
    v_inv_wallet_account_id BIGINT;
    v_inv_wallet_id BIGINT;
    v_partner_code_id BIGINT;
BEGIN
    -- Check if scheme already exists
    IF EXISTS (SELECT 1 FROM t_lender_investment WHERE investment_id = v_investment_id) THEN
        RAISE EXCEPTION 'Scheme is already created';
    END IF;

    v_inv_wallet_account_id = (SELECT id FROM t_master_account WHERE account_name = 'INVESTMENT_WALLET');
    v_inv_wallet_txn_id = generate_txn_id();

    v_scheme_product_type := CASE
                                WHEN in_scheme_data->>'investment_type' = 'MANUAL_LENDING' THEN 'ML'
                                WHEN in_scheme_data->>'investment_type' = 'MEDIUM_TERM_LENDING' THEN 'MTL'
                            ELSE 'OTL' END;
    v_loan_tenure := REPLACE(v_loan_tenure, ' ', '');

    -- Fetch investment type ID
    SELECT id INTO v_investment_type_id
    FROM t_mst_parameter
    WHERE logical_group = 'investment_type'
      AND key_2 = v_investment_type;

    SELECT id INTO v_partner_code_id
    FROM t_mst_parameter
    WHERE logical_group = 'partner_code'
      AND key_2 = v_partner_code;

    SELECT user_id INTO v_user_id
    FROM t_lender
    WHERE id = v_investor_id;

    SELECT balance, id INTO v_balance, v_inv_wallet_id
    FROM t_account
    WHERE account_type_id = v_inv_wallet_account_id AND deleted IS NULL;

    -- Fetch product config and maturity date
    SELECT * INTO v_product_config
    FROM t_investment_product_config tpc
    WHERE
        partner_code_id = v_partner_code_id
        AND investment_type_id = v_investment_type_id
        AND is_active = TRUE
        AND deleted IS NULL
        AND (
            (v_investment_type = 'MANUAL_LENDING')
            OR (tenure = v_tenure)
        );

    v_maturity_date := CASE WHEN v_investment_type = 'MANUAL_LENDING' THEN current_date + (12 || ' MONTH')::INTERVAL ELSE current_date + (v_tenure || ' MONTH')::INTERVAL END;
    v_start_date := current_date;

    -- Generate order ID
    v_order_id := CASE WHEN v_investment_type = 'MANUAL_LENDING' THEN fn_generate_order_id(v_investment_type) END;

    -- Insert scheme record
    INSERT INTO t_lender_investment(
            created_dtm, product_config_id, lender_id, actual_principal_lent, expected_closure_date,
            source_transaction_id, order_id, total_principal_outstanding, investment_type_id
    )
    VALUES (now(), v_product_config.id, v_investor_id,
            v_investment_amount, v_maturity_date,
            in_scheme_data ->> 'transaction_id', v_order_id,
            v_investment_amount, v_investment_type_id)
    RETURNING id INTO v_investor_scheme_id;

    IF v_investment_type = 'ONE_TIME_LENDING' THEN
        INSERT INTO t_scheme_preference(created_dtm, investor_scheme_id, preference_id, reinvest,
                                        calculation_master_id, exposure_5, loan_tenure)
        VALUES (now(), v_investor_scheme_id,
                v_preference_id,true, 1, true,
                v_loan_tenure);
    END IF;

    UPDATE t_lender_investment SET investment_id = v_investment_id WHERE id = v_investor_scheme_id;

    -- LEDGER
    INSERT INTO t_ledger_investment_wallet (
        account_id, event_type, amount, transaction_dtm, transaction_id, source_transaction_id,
        narration, created_by, previous_balance, current_balance
    )
    VALUES (
        v_inv_wallet_id, 'DR', v_investment_amount, now(),
        v_inv_wallet_txn_id,v_investor_scheme_id,
        CONCAT('SCHEME CREATED - ', v_investment_id), 'SYSTEM', v_balance,
        v_balance - v_investment_amount
    );

    UPDATE t_account
    SET balance = balance - v_investment_amount
    WHERE account_type_id = v_inv_wallet_account_id;

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
                ('PRC_INSERT_SCHEME_RECORD',my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx,now(),now());
            raise info 'THE FOLLOWING ERROR OCCURED % % % % %', my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx;
            inout_response = -1;
        END;

END;
$$;