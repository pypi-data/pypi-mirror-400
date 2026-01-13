-- ============================================================================
-- Stored Procedure: prc_calculate_portfolio_summary
-- Purpose: Calculate and update portfolio summary for given lender(s) and product type(s)
-- 
-- This procedure efficiently calculates portfolio metrics for OPEN and CLOSED loans
-- and updates records in t_portfolio_summary table.
--
-- Parameters:
--   in_lender_user_ids: Array of lender user IDs (VARCHAR) to calculate portfolio for
--   in_product_types: Array of product types ('ML', 'OTL') - if NULL, calculates for all
--   in_loan_types: Array of loan types ('OPEN', 'CLOSED') - if NULL, calculates for all
--   inout_response: Response code (0 = success, -1 = error)
--
-- Performance: Optimized for batch processing of multiple lenders
-- Note: Portfolio summary records must already exist (created via create_lender_portfolio_profile)
-- ============================================================================

CREATE OR REPLACE PROCEDURE prc_calculate_portfolio_summary(
    IN in_lender_user_ids VARCHAR(20)[],
    IN in_product_types product_type_enum[] DEFAULT NULL,
    IN in_loan_types loan_portfolio_enum[] DEFAULT NULL,
    INOUT inout_response INTEGER DEFAULT NULL::INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_lender_user_id VARCHAR(20);
    v_product_type product_type_enum;
    v_loan_type loan_portfolio_enum;
    v_product_config_ids INTEGER[];
    v_total_records_updated INTEGER := 0;
    v_records_updated_for_combination INTEGER := 0;
    
    -- Open portfolio variables
    v_open_principal_lent NUMERIC(10, 2) := 0;
    v_open_principal_received NUMERIC(10, 2) := 0;
    v_open_interest_received NUMERIC(10, 2) := 0;
    v_open_fee_levied NUMERIC(10, 2) := 0;
    v_open_principal_outstanding NUMERIC(10, 2) := 0;
    v_open_npa_amount NUMERIC(10, 2) := 0;
    v_open_amount_received NUMERIC(10, 2) := 0;
    v_open_loan_count INTEGER := 0;
    v_open_principal_receivable NUMERIC(10, 2) := 0;
    
    -- Closed portfolio variables
    v_closed_principal_lent NUMERIC(10, 2) := 0;
    v_closed_principal_received NUMERIC(10, 2) := 0;
    v_closed_interest_received NUMERIC(10, 2) := 0;
    v_closed_fee_levied NUMERIC(10, 2) := 0;
    v_closed_principal_outstanding NUMERIC(10, 2) := 0;
    v_closed_npa_amount NUMERIC(10, 2) := 0;
    v_closed_amount_received NUMERIC(10, 2) := 0;
    v_closed_loan_count INTEGER := 0;
    v_closed_sum_product NUMERIC(10, 2) := 0;
    v_closed_absolute_return NUMERIC(10, 2) := 0;
    v_closed_weighted_average NUMERIC(10, 2) := 0;
    v_closed_annualised_net_return NUMERIC(10, 2) := 0;
    v_closed_principal_receivable NUMERIC(10, 2) := 0;
BEGIN
    -- Default to all product types and loan types if not specified
    IF in_product_types IS NULL THEN
        in_product_types := ARRAY['ML'::product_type_enum, 'OTL'::product_type_enum];
    END IF;
    
    IF in_loan_types IS NULL THEN
        in_loan_types := ARRAY['OPEN'::loan_portfolio_enum, 'CLOSED'::loan_portfolio_enum];
    END IF;
    
    -- Loop through each lender user ID
    FOREACH v_lender_user_id IN ARRAY in_lender_user_ids
    LOOP
        -- Loop through each product type
        FOREACH v_product_type IN ARRAY in_product_types
        LOOP
            -- Get product_config_ids for this product type
            -- ML: product_config_id = 1, OTL: product_config_id IN (2,3,4)
            -- TODO: This mapping should be configurable or come from a mapping table
            IF v_product_type = 'ML' THEN
                v_product_config_ids := ARRAY[1];
            ELSIF v_product_type = 'OTL' THEN
                v_product_config_ids := ARRAY[2, 3, 4];
            ELSE
                CONTINUE; -- Skip unknown product types
            END IF;
            
            -- Process OPEN portfolio if requested
            IF 'OPEN' = ANY(in_loan_types) THEN
                -- Calculate OPEN portfolio metrics
                SELECT 
                    COALESCE(SUM(tild.investment_amount), 0),
                    COALESCE(SUM(tilrs.total_principal_redeemed), 0),
                    COALESCE(SUM(tilrs.total_interest_redeemed), 0),
                    COALESCE(SUM(tilrs.total_fee_levied), 0),
                    COALESCE(SUM(tilrs.principal_outstanding), 0),
                    COALESCE(SUM(tilrs.total_npa_amount), 0),
                    COALESCE(SUM(tilrs.total_amount_redeemed), 0),
                    COUNT(tild.id),
                    COALESCE(SUM(ROUND(tl.expected_repayment_sum * tild.allocation_percentage / 100, 2) - tilrs.total_principal_redeemed), 0)
                INTO 
                    v_open_principal_lent,
                    v_open_principal_received,
                    v_open_interest_received,
                    v_open_fee_levied,
                    v_open_principal_outstanding,
                    v_open_npa_amount,
                    v_open_amount_received,
                    v_open_loan_count,
                    v_open_principal_receivable
                FROM t_lender_investment tli
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_investment_loan_redemption_summary tilrs ON tild.id = tilrs.investment_loan_id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_lender tlender ON tli.lender_id = tlender.id
                WHERE tlender.user_id = v_lender_user_id
                  AND tl.status = 'DISBURSED'::loan_status
                  AND tli.product_config_id = ANY(v_product_config_ids)
                  AND tli.deleted IS NULL
                  AND tild.deleted IS NULL
                  AND tlender.deleted IS NULL;
                
                -- Update OPEN portfolio summary (record must already exist)
                UPDATE t_portfolio_summary
                SET
                    total_principal_lent = v_open_principal_lent,
                    total_principal_received = v_open_principal_received,
                    total_principal_outstanding = v_open_principal_outstanding,
                    total_principal_receivable = v_open_principal_receivable,
                    total_interest_received = v_open_interest_received,
                    total_amount_received = v_open_amount_received,
                    total_fee_levied = v_open_fee_levied,
                    total_npa_amount = v_open_npa_amount,
                    absolute_return = 0.00, -- not applicable for OPEN
                    annualized_net_return = 0.00, -- not applicable for OPEN
                    loan_count = v_open_loan_count,
                    updated_dtm = NOW()
                WHERE lender_user_id = v_lender_user_id
                  AND product_type = v_product_type
                  AND loan_type = 'OPEN'::loan_portfolio_enum;
                
                v_records_updated_for_combination := v_records_updated_for_combination + 1;
                v_total_records_updated := v_total_records_updated + 1;
            END IF;
            
            -- Process CLOSED portfolio if requested
            IF 'CLOSED' = ANY(in_loan_types) THEN
                -- Calculate CLOSED portfolio metrics
                SELECT 
                    COALESCE(SUM(tild.investment_amount), 0),
                    COALESCE(SUM(tilrs.total_principal_redeemed), 0),
                    COALESCE(SUM(tilrs.total_interest_redeemed), 0),
                    COALESCE(SUM(tilrs.total_fee_levied), 0),
                    COALESCE(SUM(tilrs.principal_outstanding), 0),
                    COALESCE(SUM(tilrs.total_npa_amount), 0),
                    COALESCE(SUM(tilrs.total_amount_redeemed), 0),
                    COUNT(tild.id),
                    COALESCE(SUM(tild.investment_amount * tl.tenure), 0),
                    COALESCE(SUM(ROUND(tl.expected_repayment_sum * tild.allocation_percentage / 100, 2) - tilrs.total_principal_redeemed), 0)
                INTO 
                    v_closed_principal_lent,
                    v_closed_principal_received,
                    v_closed_interest_received,
                    v_closed_fee_levied,
                    v_closed_principal_outstanding,
                    v_closed_npa_amount,
                    v_closed_amount_received,
                    v_closed_loan_count,
                    v_closed_sum_product,
                    v_closed_principal_receivable
                FROM t_lender_investment tli
                JOIN t_investment_loan_detail tild ON tli.id = tild.investment_id
                JOIN t_investment_loan_redemption_summary tilrs ON tild.id = tilrs.investment_loan_id
                JOIN t_loan tl ON tl.id = tild.loan_id
                JOIN t_lender tlender ON tli.lender_id = tlender.id
                WHERE tlender.user_id = v_lender_user_id
                  AND tl.status = ANY(ARRAY['CLOSED'::loan_status, 'NPA'::loan_status])
                  AND tli.product_config_id = ANY(v_product_config_ids)
                  AND tli.deleted IS NULL
                  AND tild.deleted IS NULL
                  AND tlender.deleted IS NULL;
                
                -- Calculate absolute return and annualized return for CLOSED portfolio
                IF v_closed_principal_lent > 0 THEN
                    v_closed_absolute_return := ROUND(
                        ((v_closed_amount_received - v_closed_principal_lent) / v_closed_principal_lent) * 100, 
                        2
                    );
                    
                    v_closed_weighted_average := v_closed_sum_product / v_closed_principal_lent;
                    
                    IF v_closed_weighted_average > 0 THEN
                        v_closed_annualised_net_return := ROUND(
                            v_closed_absolute_return * (12 / v_closed_weighted_average), 
                            2
                        );
                    ELSE
                        v_closed_annualised_net_return := 0.00;
                    END IF;
                ELSE
                    v_closed_absolute_return := 0.00;
                    v_closed_annualised_net_return := 0.00;
                END IF;
                
                -- Update CLOSED portfolio summary (record must already exist)
                UPDATE t_portfolio_summary
                SET
                    total_principal_lent = v_closed_principal_lent,
                    total_principal_received = v_closed_principal_received,
                    total_principal_outstanding = v_closed_principal_outstanding,
                    total_principal_receivable = v_closed_principal_receivable,
                    total_interest_received = v_closed_interest_received,
                    total_amount_received = v_closed_amount_received,
                    total_fee_levied = v_closed_fee_levied,
                    total_npa_amount = v_closed_npa_amount,
                    absolute_return = v_closed_absolute_return,
                    annualized_net_return = v_closed_annualised_net_return,
                    loan_count = v_closed_loan_count,
                    updated_dtm = NOW()
                WHERE lender_user_id = v_lender_user_id
                  AND product_type = v_product_type
                  AND loan_type = 'CLOSED'::loan_portfolio_enum;
                
                v_records_updated_for_combination := v_records_updated_for_combination + 1;
                v_total_records_updated := v_total_records_updated + 1;
            END IF;
            
            -- Reset variables for next iteration
            v_open_principal_lent := 0;
            v_open_principal_received := 0;
            v_open_interest_received := 0;
            v_open_fee_levied := 0;
            v_open_principal_outstanding := 0;
            v_open_npa_amount := 0;
            v_open_amount_received := 0;
            v_open_loan_count := 0;
            v_open_principal_receivable := 0;
            
            v_closed_principal_lent := 0;
            v_closed_principal_received := 0;
            v_closed_interest_received := 0;
            v_closed_fee_levied := 0;
            v_closed_principal_outstanding := 0;
            v_closed_npa_amount := 0;
            v_closed_amount_received := 0;
            v_closed_loan_count := 0;
            v_closed_sum_product := 0;
            v_closed_absolute_return := 0;
            v_closed_weighted_average := 0;
            v_closed_annualised_net_return := 0;
            v_closed_principal_receivable := 0;
        END LOOP;
    END LOOP;
    
    -- Set success response
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
            
            -- Log error to error log table
            INSERT INTO t_error_log (
                sp_name, 
                err_state, 
                err_message, 
                err_details, 
                err_hint, 
                err_context, 
                created_dtm
            )
            VALUES (
                'prc_calculate_portfolio_summary', 
                my_ex_state, 
                my_ex_message, 
                my_ex_detail, 
                my_ex_hint, 
                my_ex_ctx, 
                NOW()
            );
            
            RAISE INFO 'THE FOLLOWING ERROR OCCURRED IN prc_calculate_portfolio_summary: % % % % %', 
                my_ex_state, my_ex_message, my_ex_detail, my_ex_hint, my_ex_ctx;
            
            -- Set error response
            inout_response := -1;
        END;
END;
$$;

COMMENT ON PROCEDURE prc_calculate_portfolio_summary IS 
    'Calculate and update portfolio summary for given lender(s), product type(s), and loan type(s). Sets inout_response to 0 on success, -1 on error.';

