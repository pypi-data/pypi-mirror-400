-- Function: Generate Transaction ID
-- Generates a unique transaction ID with optional prefix
-- Format: [PREFIX] + Random Alphanumeric String (16 chars)
-- Example: '1P4TPALF9142DDUV' or 'INVW1P4TPALF9142DDUV'

CREATE OR REPLACE FUNCTION generate_txn_id(prefix VARCHAR DEFAULT NULL)
RETURNS VARCHAR
LANGUAGE plpgsql
AS
$$
DECLARE
    v_txn_id VARCHAR;
    v_random_part VARCHAR;
    v_chars VARCHAR := '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    v_char_count INTEGER := 16;  -- Length of random part
    v_i INTEGER;
    v_random_char CHAR(1);
BEGIN
    -- Generate random alphanumeric string (16 characters)
    v_random_part := '';
    FOR v_i IN 1..v_char_count LOOP
        -- Use random() to select a character from v_chars
        -- random() returns 0.0 to 1.0, multiply by length and floor to get index
        v_random_char := SUBSTRING(
            v_chars, 
            FLOOR(RANDOM() * LENGTH(v_chars))::INTEGER + 1, 
            1
        );
        v_random_part := v_random_part || v_random_char;
    END LOOP;
    
    -- Combine prefix (if provided) with random part
    IF prefix IS NOT NULL AND prefix != '' THEN
        v_txn_id := prefix || v_random_part;
    ELSE
        v_txn_id := v_random_part;
    END IF;
    
    RETURN v_txn_id;
END;
$$;

COMMENT ON FUNCTION generate_txn_id(VARCHAR) IS 
    'Generates a unique transaction ID with optional prefix. Returns 16-char random alphanumeric string, or prefix + 16-char string if prefix provided.';

