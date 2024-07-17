from pydantic import ValidationError, BaseModel
from typing import Type
import pandas as pd


class TransactionParameters(BaseModel):
    id_transaction: int
    date: str
    card: str
    client: str
    date_of_birth: str
    passport: str
    passport_valid_to: str
    phone: str 
    operation_type: str
    amount: float
    operation_result: str
    terminal_type: str
    city: str
    address: str


class DataFrameValidationError(Exception):
    """Custom exception for Dataframe validation errors."""

    pass


def validate_transactions_dataframe(df: pd.DataFrame, model: Type[BaseModel]):
    errors = []

    for i, row in enumerate(df.to_dict(orient="records")):
        try:
            model(**row)
        except ValidationError as e:
            errors.append(f"Row {i} failed validation: {e}")

    if errors:
        error_message = "\n".join(errors)
        raise DataFrameValidationError(
            f"DataFrame validation failed with the following errors:\n{error_message}"
        )
