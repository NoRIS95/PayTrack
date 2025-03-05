from sqlalchemy import create_engine, Table, Column, Integer, String, Float, ForeignKey, MetaData
from app.database import SYNC_DB_URL
from sqlalchemy.orm import sessionmaker
from app.models import User, Wallet

engine = create_engine(SYNC_DB_URL)

metadata = MetaData()

users = Table('users', metadata,
              Column('id', Integer, primary_key=True, index=True),
              Column('full_name', String),
              Column('login', String, unique=True),
              Column('email', String, unique=True),
              Column('role', String, default="user"))

wallets = Table('wallets', metadata,
                Column('id', Integer, primary_key=True, index=True),
                Column('balance', Float, default=0.0),
                Column('owner_id', Integer, ForeignKey('users.id')))

payments = Table('payments', metadata,
                 Column('id', Integer, primary_key=True, index=True),
                 Column('user_id', Integer, ForeignKey('users.id')),
                 Column('wallet_id', Integer, ForeignKey('wallets.id')),
                 Column('amount', Float),
                 Column('transaction_id', String, unique=True, nullable=False))

metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

existing_users = session.query(User).filter(User.email.in_(['Petrov42@test.com', 'user1@test.com'])).all()

if not existing_users:
    users_to_add = [
        User(full_name="Петров Василий Иванович", login="VasyaAdmin", email="Petrov42@test.com", role="admin"),
        User(full_name="Test User1", login="user_test1", email="user1@test.com", role="user")
    ]

    session.add_all(users_to_add)
    session.commit()

    test_admin = users_to_add[0]
    test_user = users_to_add[1]
    wallet_to_add = [
        Wallet(owner_id=test_admin.id, balance=0.0),
        Wallet(owner_id=test_user.id, balance=100.0)
    ]

    session.add_all(wallet_to_add)
    session.commit()

session.close()