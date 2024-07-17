import pandas as pd
import numpy as np


class AnomalyDetector:
    def __init__(self, autoencoder, q_mad_quantile=0.9):
        self.autoencoder = autoencoder
        self.q_mad_quantile = q_mad_quantile
        self.mn = pd.Series(
            [1.0, 1.0, 0.0003888591843678608],
            index=["operation_type", "terminal_type", "normalized_amount"],
        )
        self.mx = pd.Series(
            [4.0, 3.0, 3.954896798326836],
            index=["operation_type", "terminal_type", "normalized_amount"],
        )

        self.operation_mapping = {
            "Оплата": 1,
            "Перевод": 2,
            "Пополнение": 3,
            "Снятие": 4,
        }
        self.terminal_mapping = {"ATM": 1, "POS": 2, "WEB": 3}

    def normalize(self, df):
        return (df - self.mn) / (self.mx - self.mn)

    def detect_anomalies(self, reconstructions, original_df):
        mse = np.mean(np.power(original_df - reconstructions, 2), axis=1)
        outliers = self.q_mad_score(mse, self.q_mad_quantile)

        return outliers

    def map_operations_and_terminals(self, df):
        df["operation_type"] = df["operation_type"].map(self.operation_mapping)
        df["terminal_type"] = df["terminal_type"].map(self.terminal_mapping)

        return df

    def q_mad_score(self, points, quantile=0.9):
        m = np.median(points)
        ad = np.abs(points - m)
        mad = np.median(ad)
        z_scores = 0.6745 * ad / mad

        outliers = z_scores > np.quantile(z_scores, quantile)

        return outliers

    def report(self, df):
        transactions_ids = df["id_transaction"]
        df = df.drop(["id_transaction"], axis=1)

        df = self.map_operations_and_terminals(df)

        normalized_df = self.normalize(df)

        reconstructions = self.autoencoder.predict(normalized_df)

        outliers = self.detect_anomalies(reconstructions, normalized_df)

        result = pd.concat([transactions_ids, outliers], axis=1)
        result.columns = ["id_transaction", "outlier_status"]

        return result
