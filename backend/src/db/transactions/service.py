from sqlmodel.ext.asyncio.session import AsyncSession
from db.models import Transaction
from sqlmodel import select


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_transactions(self):
        subquery = (
            select(Transaction.client)
            .where((Transaction.alg_fraud_status) | (Transaction.ml_fraud_status))
            .distinct()
        ).subquery()

        query = select(Transaction).where(Transaction.client.in_(subquery)).order_by(Transaction.client)
        result = await self.session.exec(query)

        return result.all()
