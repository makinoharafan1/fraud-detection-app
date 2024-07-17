from duck.fraud_patterns import (
    check_data_discrepancy_fraud,
    check_passport_validity,
    check_time_address_diff,
    check_time_city_diff,
    check_time_diff_fraud,
    detect_hampel_outliers,
)

from ml_utils.reporting import AnomalyDetector


class FraudDetectionPipeline:
    def __init__(self, duckdb_con, autoencoder):
        self.duckdb_con = duckdb_con
        self.autoencoder = autoencoder

    def create_temp_table_with_features(self):
        self.duckdb_con.sql(
            """
        CREATE OR REPLACE TEMP TABLE temp AS
        SELECT *, 
            EXTRACT(EPOCH FROM (TRY_CAST(date AS TIMESTAMP) - LAG(TRY_CAST(date AS TIMESTAMP)) 
            OVER (PARTITION BY client ORDER BY date))) AS time_diff,
            CASE WHEN address != LAG(address) OVER (PARTITION BY client ORDER BY date) THEN true ELSE false END AS changed_address,
            CASE WHEN city != LAG(city) OVER (PARTITION BY client ORDER BY date) THEN true ELSE false END AS changed_city
        FROM temp_df
        """
        )

    def add_fraud_columns(self):
        fraud_columns = [
            "passport_validity_fraud",
            "time_diff_fraud",
            "address_diff_fraud",
            "city_diff_fraud",
            "data_discrepancy_fraud",
            "amount_outlier_fraud",
            "alg_fraud_status",
            "ml_fraud_status",
        ]

        for col in fraud_columns:
            self.duckdb_con.sql(
                f"ALTER TABLE temp ADD COLUMN {col} BOOLEAN DEFAULT false;"
            )

    def apply_fraud_detection_rules(
        self,
        clicks_delta_time,
        city_delta_time,
        address_delta_time,
        window_size,
        n_sigmas,
    ):
        check_passport_validity(self.duckdb_con)
        check_time_diff_fraud(self.duckdb_con, clicks_delta_time)
        check_time_address_diff(self.duckdb_con, address_delta_time)
        check_time_city_diff(self.duckdb_con, city_delta_time)
        check_data_discrepancy_fraud(self.duckdb_con)
        detect_hampel_outliers(self.duckdb_con, window_size, n_sigmas)

    def normalize_amounts(self):
        self.duckdb_con.sql(
            """
        CREATE TEMP TABLE median_amounts AS
        SELECT client, AVG(amount) AS median_amount
        FROM temp_df
        GROUP BY client;
        """
        )

        self.duckdb_con.sql(
            """
        CREATE TEMP TABLE temp_df_normalized AS
        SELECT 
            t.*,
            t.amount / m.median_amount AS normalized_amount
        FROM 
            temp t
        JOIN 
            median_amounts m
        ON 
            t.client = m.client;
        """
        )

    def detect_anomalies_with_autoencoder(self, q_mad_quantile):
        detector = AnomalyDetector(self.autoencoder, q_mad_quantile)
        autoencoder_outliers = detector.report(
            self.duckdb_con.sql(
                "SELECT id_transaction, operation_type, terminal_type, normalized_amount FROM temp_df_normalized ORDER BY date"
            ).df()
        )
        self.duckdb_con.register("outliers_df", autoencoder_outliers)
        self.duckdb_con.sql(
            "CREATE TEMP TABLE temp_outliers AS SELECT id_transaction, outlier_status FROM outliers_df"
        )

        self.duckdb_con.sql(
            """
        UPDATE temp
        SET ml_fraud_status = TRUE
        WHERE id_transaction IN (SELECT id_transaction FROM temp_outliers WHERE outlier_status IS TRUE);
        """
        )

    def update_algorithmic_fraud_status(self):
        self.duckdb_con.sql(
            """
        UPDATE temp
        SET alg_fraud_status = TRUE 
        WHERE passport_validity_fraud = TRUE 
        OR time_diff_fraud = TRUE
        OR address_diff_fraud = TRUE
        OR city_diff_fraud = TRUE
        OR data_discrepancy_fraud = TRUE
        OR amount_outlier_fraud = TRUE;
        """
        )

    def clean_up_temp_table(self):
        self.duckdb_con.sql("ALTER TABLE temp DROP time_diff;")
        self.duckdb_con.sql("ALTER TABLE temp DROP changed_address;")
        self.duckdb_con.sql("ALTER TABLE temp DROP changed_city;")

    def insert_into_transactions_db(self):
        self.duckdb_con.sql(
            """
        INSERT INTO db.transactions 
        SELECT * FROM temp
        """
        )

    def execute_pipeline(
        self,
        df,
        clicks_delta_time,
        city_delta_time,
        address_delta_time,
        window_size,
        n_sigmas,
        q_mad_quantile,
    ):
        self.duckdb_con.register("temp_df", df)

        self.create_temp_table_with_features()
        self.add_fraud_columns()
        self.apply_fraud_detection_rules(
            clicks_delta_time,
            city_delta_time,
            address_delta_time,
            window_size,
            n_sigmas,
        )
        self.normalize_amounts()
        self.detect_anomalies_with_autoencoder(q_mad_quantile)
        self.update_algorithmic_fraud_status()
        self.clean_up_temp_table()
        self.insert_into_transactions_db()

        self.duckdb_con.close()
