from sqlmodel import SQLModel, Field, Column, Integer


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction: int = Field(sa_column=Column(Integer, primary_key=True, unique=True))
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
    passport_validity_fraud: bool
    time_diff_fraud: bool
    address_diff_fraud: bool
    city_diff_fraud: bool
    data_discrepancy_fraud: bool
    amount_outlier_fraud: bool
    alg_fraud_status: bool
    ml_fraud_status: bool
