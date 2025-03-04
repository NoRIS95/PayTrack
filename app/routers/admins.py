from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.database import get_db
from app.models import User, Wallet, Payment
from app.schemas import UserCreate
from app.schemas import User as UserSchema

router = APIRouter()


@router.post("/admins/")
async def create_admin(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(and_(User.email == user.email, User.role == "admin")))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Администратор с этим email уже зарегистрирован!")
    new_admin = User(
        full_name=user.full_name,
        login=user.login,
        email=user.email,
        role="admin")
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin


@router.get("/admins/{admin_id}")
async def get_admin_info(admin_id: int, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    return db_admin

@router.post("/admins/{admin_id}/users")
async def create_user_by_admin(admin_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
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

@router.delete("/admins/{admin_id}/users/{user_id}")
async def delete_user_by_admin(admin_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    db_user = await db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Не удалось удалить! Пользователь не обнаружен!")
    await db.delete(db_user)
    await db.commit()
    return {"message": "Удаление пользователя произошло успешно"}

@router.get("/admins/{admin_id}/users", response_model=List[UserSchema])
async def get_all_users_with_wallets_and_balances(admin_id: int, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    result_users = await db.execute(
        select(User).options(selectinload(User.wallets))
    )
    users = result_users.scalars().all()
    if not users:
        raise HTTPException(status_code=400, detail="Не удалось отобразить данные! Пользователи отсутствуют")
    return users