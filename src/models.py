from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
import bcrypt

engine = create_engine('sqlite:///budget_tracker.db')
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))




class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)
    email = Column(String)

    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

    def __init__(self, username, password_hash, email=None, is_login=False):
        self.username = username
        self.password_hash = password_hash

        if is_login:
            self.email = None
        else:
            if email is None:
                raise ValueError("Email is required during registration.")
            self.email = email

    def save(self):
        """Save the user to the database."""
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def update(self, **kwargs):
        """Update the user with new values."""
        session = Session()
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        session.close()

    def delete(self):
        """Delete the user from the database."""
        session = Session()
        session.delete(self)
        session.commit()
        session.close()

    @staticmethod
    def get_all():
        """Retrieve all users from the database."""
        session = Session()
        users = session.query(User).all()
        session.close()
        return users

    @staticmethod
    def get_by_id(user_id):
        """Retrieve a user by their ID from the database."""
        session = Session()
        user = session.query(User).get(user_id)
        session.close()
        return user

    @staticmethod
    def get_by_username(username):
        """Retrieve a user by their username from the database."""
        session = Session()
        user = session.query(User).filter_by(username=username).first()
        session.close()


class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="budgets")
    
    user = relationship("User", back_populates="budgets")

    def save(self):
        """Save the budget to the database."""
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def update(self, **kwargs):
        """Update the budget with new values."""
        session = Session()
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        session.close()

    def delete(self):
        """Delete the budget from the database."""
        session = Session()
        session.delete(self)
        session.commit()
        session.close()

    @staticmethod
    def get_all():
        """Retrieve all budgets from the database."""
        session = Session()
        budgets = session.query(Budget).all()
        session.close()
        return budgets

    @staticmethod
    def get_by_id(budget_id):
        """Retrieve a budget by its ID from the database."""
        session = Session()
        budget = session.query(Budget).get(budget_id)
        session.close()
        return budget


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    transaction_type = Column(String(20))  # Rename 'transaction_type' to 'type'
    category = Column(String(50))
    amount = Column(Float)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship("User", back_populates="transactions")

    def __init__(self, transaction_type, category, amount, date,user_id):
        self.transaction_type = transaction_type
        self.category = category
        self.amount = amount
        self.date = date
        self.user_id = user_id

    def save(self):
        """Save the transaction to the database."""
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def update(self, **kwargs):
        """Update the transaction with new values."""
        session = Session()
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        session.close()

    def delete(self):
        """Delete the transaction from the database."""
        session = Session()
        session.delete(self)
        session.commit()
        session.close()

    @staticmethod
    def get_all():
        """Retrieve all transactions from the database."""
        session = Session()
        transactions = session.query(Transaction).all()
        session.close()
        return transactions

    @staticmethod
    def get_by_id(transaction_id):
        """Retrieve a transaction by its ID from the database."""
        session = Session()
        transaction = session.query(Transaction).get(transaction_id)
        session.close()
        return transaction

    @staticmethod
    def get_by_category(category):
        """Retrieve transactions by category from the database."""
        session = Session()
        transactions = session.query(Transaction).filter_by(category=category).all()
        session.close()
        return transactions

    @staticmethod
    def get_by_user(user_id):
        """Retrieve transactions by user from the database."""
        session = Session()
        transactions = session.query(Transaction).join(User).filter(User.id == user_id).all()
        session.close()
        return transactions


def create_tables():
    Base.metadata.create_all(engine)

