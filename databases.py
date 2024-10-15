from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)


# User model with flask-login support
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    family_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=True, nullable=False)
    confirm: Mapped[bool] = mapped_column(nullable=False)
    onboarding: Mapped[bool] = mapped_column()


# Onboarding options model
class Details(db.Model):
    __tablename__ = 'details'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    account_type: Mapped[int] = mapped_column(nullable=False)
