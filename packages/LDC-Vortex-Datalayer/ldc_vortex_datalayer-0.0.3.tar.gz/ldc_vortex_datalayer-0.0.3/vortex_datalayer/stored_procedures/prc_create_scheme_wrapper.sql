create procedure prc_create_scheme_wrapper(IN in_scheme_data jsonb, INOUT inout_response jsonb DEFAULT NULL::jsonb)
    language plpgsql
as
$$
DECLARE
    v_investor_scheme_id BIGINT;
    v_scheme_product_type product_type_enum;
    v_inout_response JSONB := '{}'::JSONB;
    v_maturity_date DATE;
    v_start_date DATE;
    v_order_id VARCHAR;
    v_user_id VARCHAR;
    v_inv_wallet_txn_id VARCHAR;
    v_loan_records JSONB;
    v_funding_response JSONB := '{}'::JSONB;
BEGIN
    -- Step 1: Create scheme header
    CALL prc_insert_scheme_record(
        in_scheme_data,
        v_investor_scheme_id,
        v_inv_wallet_txn_id,
        v_maturity_date,
        v_start_date,
        v_order_id,
        v_user_id,
        v_scheme_product_type,
        v_inout_response
    );

    IF v_inout_response = '-1' THEN
        RAISE EXCEPTION 'Error in prc_insert_scheme_record';
    END IF;

    -- Step 2: Map loans to scheme
    CALL prc_get_selected_loans(
        in_scheme_data,
        v_loan_records,
        v_inout_response
    );

    IF v_inout_response = '-1' THEN
        RAISE EXCEPTION 'Error in prc_get_selected_loans';
    END IF;

    -- Step 3: Fund the loans
    CALL prc_fund_and_map_scheme_loans(
        in_scheme_data,
        v_inv_wallet_txn_id,
        v_investor_scheme_id,
        v_loan_records,
        v_funding_response
    );

    IF v_funding_response = '-1' THEN
        RAISE EXCEPTION 'Error in prc_fund_and_map_scheme_loans';
    END IF;

    -- Build final wrapper response
    inout_response := jsonb_build_object(
        'investor_id', v_user_id,
        'investor_scheme_id', v_investor_scheme_id,
        'start_date', v_start_date,
        'maturity_date', v_maturity_date,
        'order_id', v_order_id,
        'funding_details', v_funding_response
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
                ('PRC_CREATE_SCHEME_WRAPPER',my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx,now(),now());
            raise info 'THE FOLLOWING ERROR OCCURED % % % % %', my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx;
            inout_response = -1;
        END;
END;
$$;