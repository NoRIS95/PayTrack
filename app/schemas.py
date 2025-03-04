from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    login: str
    full_name: str
    email: str

class UserCreate(UserBase):
    login: str
    full_name: str
    email: str
    role: str = "user" 

class Wallet(BaseModel):
    id: int
    owner_id: int
    balance: float

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    wallets: List[Wallet] = []

    class Config:
        from_attributes = True

class Payment(BaseModel):
    id: int
    wallet_id: int
    user_id: int
    amount: float
    transaction_id: str

class PaymentWebhook(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float
    signature: str
