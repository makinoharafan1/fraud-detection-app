from fastapi import APIRouter, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from db.connection import get_session
from db.transactions.service import TransactionService

transaction_router = APIRouter(prefix="/transactions")


@transaction_router.get("/")
async def read_transactions(session: AsyncSession = Depends(get_session)):
    transactions = await TransactionService(session).get_all_transactions()
    return transactions
