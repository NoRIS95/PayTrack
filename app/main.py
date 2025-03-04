from fastapi import FastAPI
from app.routers import users, admins, payments

app = FastAPI()

app.include_router(users.router)
app.include_router(admins.router)
app.include_router(payments.router)