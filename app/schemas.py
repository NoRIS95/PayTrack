from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    full_name: str
    email: str

class User(UserBase):
    id: int

class Administrator(UserBase):
    id: int
    role: str = "admin"

class Wallet(BaseModel):
    id: int
    user_id: int
    balance: float

class Payment(BaseModel):
    id: int
    wallet_id: int
    user_id: int
    amount: float
    transaction_id: str

class PaymentWebhook(BaseModel):
    transaction_id: str
    user_id: int
    wallet_id: int
    amount: float
    signature: str
