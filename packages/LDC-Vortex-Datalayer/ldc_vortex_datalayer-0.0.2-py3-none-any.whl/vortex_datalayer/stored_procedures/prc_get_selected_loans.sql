create procedure prc_get_selected_loans(IN in_scheme_data jsonb, INOUT loan_records jsonb, INOUT inout_response jsonb DEFAULT NULL::jsonb)
    language plpgsql
as
$$
DECLARE
    v_batch_number BIGINT := in_scheme_data ->> 'batch_number';
BEGIN

    SELECT jsonb_agg(
        jsonb_build_object(
            'loan_id', lslm.loan_id,
            'lent_amount', lslm.lent_amount,
            'loan_roi', lslm.loan_roi,
            'is_modified', lslm.is_modified
        )
    )
    INTO loan_records
    FROM t_scheme_loan_mapping lslm
    WHERE lslm.batch_number = v_batch_number
      AND lslm.is_selected = TRUE;

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
                ('PRC_GET_SELECTED_LOANS',my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx,now(),now());
            raise info 'THE FOLLOWING ERROR OCCURED % % % % %', my_ex_state,my_ex_message,my_ex_detail,my_ex_hint,my_ex_ctx;
            inout_response = -1;
        END;
END;
$$;