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


@router.get("/admins/{admin_id}")
async def get_admin_info(admin_id: int, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    return db_admin, {"message": "Данные администратора отображены успешно"}


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
    return new_user, {"message": "Добавление нового пользователя администратором завершено успешно"}


@router.patch("/admins/{admin_id}/users/{user_id}")
async def update_user_by_admin(admin_id: int, user_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_admin = await db.get(User, admin_id)
    if not db_admin or db_admin.role != "admin":
        raise HTTPException(status_code=404, detail="Этот пользователь не является администратором")
    db_user = await db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if db_user.email != user.email:
        result = await db.execute(select(User).filter(User.email == user.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с этим email уже существует!")
    db_user.full_name = user.full_name
    db_user.login = user.login
    db_user.email = user.email
    db_user.role = user.role
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user, {"message": "Данные пользователя успешно отредактированы"}


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
    return users, {"message": "Данные пользователей и их счетов успешно отображены"}