from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.database import get_db
from app.models import User, Wallet, Payment
from app.schemas import UserCreate
from app.schemas import User as UserSchema

app = FastAPI()


@app.post("/users/")
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
    return new_user

@app.get("/users/{user_id}")
async def get_user_info(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не найден")
    else:
        return db_user

@app.post("/users/{user_id}/wallets_and_balances")
async def create_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    result_user = await db.execute(select(User).filter(User.id == user_id))
    db_user = result_user.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не найден")
    new_wallet = Wallet(owner_id=user_id, balance=0.0)
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)
    return new_wallet

@app.get("/users/{user_id}/wallets_and_balances")
async def get_wallets_and_balances(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).filter(Wallet.owner_id == user_id))
    wallets = result.scalars().all()
    if not wallets :
        return {"message": "На данный момент у Вас отсутствуют счета"}
    else:
        return wallets

@app.get("/users/{user_id}/payments")
async def get_payments(user_id: int, db: AsyncSession = Depends(get_db)):
    result_payments = await db.execute(select(Payment).filter(Payment.user_id == user_id))
    payments = result_payments.scalars().all()
    if not payments:
        return {"message": "На данный момент Вы не проводили никаких платежей"}
    else:
        return payments


@app.post("/admins/")
async def create_admin(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.email == user.email, User.role == "admin")))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Администратор с этим email уже зарегистрирован!")
    new_admin = User(
        full_name=user.full_name,
        login=user.login,
        email=user.email,
        role='admin')
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin


@app.get("/admins/{admin_id}")
async def get_admin_info(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.id == user_id, User.role == "admin")))
    db_admin = result.scalars().first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    else:
        return db_admin

@app.post("/admins/{admin_id}/users")
async def create_user_by_admin(admin_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.id == admin_id, User.role == "admin")))
    db_admin = result.scalars().first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с этим email уже зарегистрирован!")
    new_user = User(
        full_name=user.full_name,
        login=user.login,
        email=user.email,
        role=user.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.delete("/admins/{admin_id}/users/{user_id}")
async def delete_user_by_admin(admin_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.id == admin_id, User.role == "admin")))
    db_admin = result.scalars().first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Не удалось удалить! Пользователь не обнаружен!")
    await db.delete(db_user)
    await db.commit()
    return {"message": "Удаление пользователя произошло успешно"}

@app.get("/admins/{admin_id}/users", response_model=List[UserSchema])
async def get_all_users_with_wallets_and_balances(admin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.id == admin_id, User.role == "admin")))
    db_admin = result.scalars().first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    result_users = await db.execute(
        select(User).options(selectinload(User.wallets))
    )
    users = result_users.scalars().all()
    if not users:
        raise HTTPException(status_code=400, detail="Не удалось отобразить данные! Пользователи отсутствуют")
    else:
        return users