import hashlib
from app.schemas import PaymentWebhook
from app.models import User, Payment, Wallet
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db, SECRET_KEY
from sqlalchemy import select

router = APIRouter()

@router.post("/webhook/payment")
async def process_payment_webhook(payment: PaymentWebhook, db: AsyncSession = Depends(get_db)):
    print(f"account_id: {payment.account_id}, amount: {payment.amount}, transaction_id: {payment.transaction_id}, user_id: {payment.user_id}")
    print(f"SECRET_KEY: {SECRET_KEY}")
    expected_signature = hashlib.sha256(
        f"{payment.account_id}{f'{payment.amount:.2f}'}{payment.transaction_id}{payment.user_id}{SECRET_KEY}".encode()
    ).hexdigest()
    print(f"expected signature: {expected_signature}" )
    print(f"payment signature: {payment.signature}" )
    if expected_signature != payment.signature:
        raise HTTPException(status_code=400, detail="Ошибка в webhook подписи")

    db_user = await db.get(User, payment.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Этот пользователь не найден")

    result_transaction = await db.execute(select(Payment).filter(Payment.transaction_id == str(payment.transaction_id)))
    db_result_transaction  = result_transaction.scalars().first()
    if db_result_transaction:
        raise HTTPException(status_code=400, detail="Эта транзакция уже проведена")

    db_wallet = await db.get(Wallet, payment.account_id)
    if not db_wallet:
        db_wallet = Wallet(owner_id=payment.user_id, balance=0.0)
        db.add(db_wallet)
        await db.commit()
        await db.refresh(db_wallet)

    db_wallet.balance += payment.amount
    new_payment = Payment(
        wallet_id = db_wallet.id,
        user_id = payment.user_id,
        amount = payment.amount,
        transaction_id = payment.transaction_id
    )
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return {"message": "Начисление проведено успешно"}

