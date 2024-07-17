from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.connection import init_db
from db.transactions.routes import transaction_router
from db.transactions.schemas import (
    validate_transactions_dataframe,
    DataFrameValidationError,
    TransactionParameters,
)

from io import StringIO
from pathlib import Path
import os
from dotenv import load_dotenv

from duck.pipeline import FraudDetectionPipeline
from duck.connection import connect_to_postgres

import pandas as pd
import keras
import duckdb

import pytest

from sklearn.metrics import confusion_matrix


clicks_delta_time = int(os.getenv("CLICKS_DELTA_TIME"))
city_delta_time = int(os.getenv("CITY_DELTA_TIME"))
address_delta_time = int(os.getenv("ADDRESS_DELTA_TIME"))
window_size = int(os.getenv("WINDOW_SIZE"))
n_sigmas = float(os.getenv("N_SIGMAS"))
mad_quantile = float(os.getenv("MAD_QUANTILE"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    con = duckdb.connect()
    connect_to_postgres(con)
    yield
    con.sql("DROP TABLE db.transactions;")
    con.close()


app = FastAPI(lifespan=lifespan)
autoencoder = keras.models.load_model("src/ml_utils/gitkeep.h5")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    content_str = content.decode("utf-8")
    temp_df = pd.read_csv(StringIO(content_str), on_bad_lines="skip", sep=";")

    try:
        validate_transactions_dataframe(temp_df, TransactionParameters)
    except DataFrameValidationError as e:
        pytest.fail(f"DataFrame validation failed: {e}")
    else:
        duckdb_con = duckdb.connect()
        connect_to_postgres(duckdb_con)

        pipeline = FraudDetectionPipeline(duckdb_con, autoencoder)
        pipeline.execute_pipeline(
            temp_df,
            clicks_delta_time,
            city_delta_time,
            address_delta_time,
            window_size,
            n_sigmas,
            mad_quantile,
        )

    return {"filename": file.filename}


@app.get("/fetchmetrics/")
async def fetch_metrics():
    duckdb_con = duckdb.connect()
    connect_to_postgres(duckdb_con)

    temp_df = duckdb_con.sql(
        "SELECT alg_fraud_status, ml_fraud_status FROM db.transactions;"
    ).df()

    cm = confusion_matrix(temp_df["alg_fraud_status"], temp_df["ml_fraud_status"])

    (tn, fp, fn, tp) = cm.flatten()

    precision = tp / (fp + tp)
    recall = tp / (fn + tp)

    transactions_amount = len(temp_df)

    temp_df = duckdb_con.sql(
        """
        SELECT alg_fraud_status, ml_fraud_status 
        FROM db.transactions 
        WHERE transactions.alg_fraud_status OR transactions.ml_fraud_status;
    """
    ).df()

    frauldent_transactions_amount = len(temp_df)

    return {
        "precision": f"{precision:.2%}",
        "recall": f"{recall:.2%}",
        "overall_transactions": f"{transactions_amount}",
        "fraudlent_transactions": f"{frauldent_transactions_amount} ({(frauldent_transactions_amount / transactions_amount):.2%})",
    }


app.include_router(transaction_router, tags=["transactions"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("APP_HOST_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
