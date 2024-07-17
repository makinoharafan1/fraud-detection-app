def check_passport_validity(con):
    con.sql(
        """
    UPDATE temp SET passport_validity_fraud = 
    CASE
        WHEN TRY_CAST(passport_valid_to AS TIMESTAMP) IS NOT NULL
        AND TRY_CAST(date AS TIMESTAMP) > TRY_CAST(passport_valid_to AS TIMESTAMP)
        THEN TRUE
        ELSE FALSE
    END
    """
    )


def check_time_diff_fraud(con, time=10):
    con.sql(
        f"""
    UPDATE temp SET time_diff_fraud = 
    CASE
        WHEN time_diff <= {time} THEN TRUE
        ELSE FALSE
    END
    """
    )


def check_time_address_diff(con, time=600):
    con.sql(
        f""" 
    CREATE TEMP TABLE fraud_addresses AS
    SELECT DISTINCT client, address
    FROM temp
    WHERE changed_address AND time_diff < {time}
    """
    )

    con.sql(
        """
    UPDATE temp
    SET address_diff_fraud = TRUE
    WHERE temp.client IN (SELECT client FROM fraud_addresses)
    AND temp.address IN (SELECT address FROM fraud_addresses)
    """
    )


def check_time_city_diff(con, time=21600):
    con.sql(
        f"""
    CREATE TEMP TABLE fraud_citys AS
    SELECT DISTINCT client, city
    FROM temp
    WHERE changed_city AND time_diff < {time}
    """
    )

    con.sql(
        """
    UPDATE temp
    SET city_diff_fraud = TRUE
    WHERE temp.client IN (SELECT client FROM fraud_citys)
    AND temp.city IN (SELECT city FROM fraud_citys)
    """
    )


def check_data_discrepancy_fraud(con):
    con.sql(
        """
    CREATE TEMP TABLE temp_counts AS
    SELECT client, 
           COUNT(DISTINCT card) AS distinct_cards, 
           COUNT(DISTINCT passport) AS distinct_passport,
           COUNT(DISTINCT card || phone) AS distinct_combinations
    FROM temp
    GROUP BY client
    """
    )

    con.sql(
        """
    UPDATE temp
    SET data_discrepancy_fraud = (
        SELECT 
            CASE 
                WHEN temp_counts.distinct_cards < temp_counts.distinct_combinations THEN TRUE
                WHEN temp_counts.distinct_passport > 1 THEN TRUE
                ELSE FALSE
            END
        FROM temp_counts
        WHERE temp.client = temp_counts.client
    )
    """
    )


def detect_hampel_outliers(con, window_size=4, n_sigmas=1.5):
    con.execute("SELECT amount FROM temp;")
    con.sql(
        f"""
    CREATE TEMP TABLE sorted_temp AS
    SELECT *, 
           MEDIAN(amount) OVER (PARTITION BY client ORDER BY date ROWS BETWEEN {window_size} PRECEDING AND {window_size} FOLLOWING) AS rolling_median,
           AVG(amount) OVER (PARTITION BY client ORDER BY date ROWS BETWEEN {window_size} PRECEDING AND {window_size} FOLLOWING) AS rolling_avg,
           STDDEV_SAMP(amount) OVER (PARTITION BY client ORDER BY date ROWS BETWEEN {window_size} PRECEDING AND {window_size} FOLLOWING) AS rolling_stddev
    FROM temp
    """
    )

    con.sql(
        f"""
    UPDATE temp
    SET amount_outlier_fraud = 
    CASE 
        WHEN ABS(temp.amount - sorted_temp.rolling_avg) > {n_sigmas} * sorted_temp.rolling_stddev THEN TRUE
        ELSE FALSE
    END
    FROM sorted_temp
    WHERE temp.client = sorted_temp.client AND temp.date = sorted_temp.date
    """
    )
