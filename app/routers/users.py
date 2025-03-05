from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Wallet, Payment
from app.schemas import UserCreate, UserLogin


router = APIRouter()

@router.post("/users/login")
async def user_login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await db.execute(
        select(User).filter(User.email == user_login.email)
    )
    db_user = db_user.scalars().first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или вы не зарегистрированы на этом сайте")
    return {"message": "Авторизация прошла успешно", "user_id": db_user.id}

@router.post("/users/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с этим email уже зарегистрирован!")
    new_user = User(
        full_name=user.full_name,
        login=user.login,
        email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user, {"message": "Добавление нового пользователя завершено успешно"}


@router.get("/users/{user_id}")
async def get_user_info(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Этот пользователь не найден")
    return db_user, {"message": "Данные пользователя отображены успешно"}


@router.post("/users/{user_id}/wallets_and_balances")
async def create_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Этот пользователь не найден")
    new_wallet = Wallet(owner_id=user_id, balance=0.0)
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)
    return new_wallet, {"message": "Создание счёта завершено успешно"}


@router.get("/users/{user_id}/wallets_and_balances")
async def get_wallets_and_balances(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).filter(Wallet.owner_id == user_id))
    wallets = result.scalars().all()
    if not wallets :
        return {"message": "На данный момент у Вас отсутствуют счета"}
    return wallets, {"message": "Счета с балансами отображены успешно"}


@router.get("/users/{user_id}/payments")
async def get_payments(user_id: int, db: AsyncSession = Depends(get_db)):
    result_payments = await db.execute(select(Payment).filter(Payment.user_id == user_id))
    payments = result_payments.scalars().all()
    if not payments:
        return {"message": "На данный момент Вы не проводили никаких платежей"}
    return payments, {"message": "Данные о совершённых платежах отображены успешно"}