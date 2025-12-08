import os
import bcrypt
from typing import Dict, Optional
from flask import session
from models import User

_USERS: Dict[str, User] = {}


def init_demo_user() -> None:
    """Create a demo user using a hashed password."""
    if "demo@bookstore.com" in _USERS:
        return

    demo_password = os.environ.get("DEMO_USER_PASSWORD", "demou123")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(demo_password.encode("utf-8"), salt)

    demo_user = User(
        email="demo@bookstore.com",
        password=hashed_password,
        name="Demo User",
        address="123 Demo Street, Demo City, DC 12345",
    )
    _USERS[demo_user.email] = demo_user


def get_current_user() -> Optional[User]:
    email = session.get("user_email")
    if not email:
        return None
    return _USERS.get(email)


def register_user(email: str, raw_password: str, name: str, address: str = "") -> User:
    if email in _USERS:
        raise ValueError("Email already registered")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    user = User(email=email, password=hashed_password, name=name, address=address)
    _USERS[email] = user
    return user


def authenticate(email: str, raw_password: str) -> Optional[User]:
    user = _USERS.get(email)
    if not user:
        return None

    # User.password here is the hashed password
    if not bcrypt.checkpw(raw_password.encode("utf-8"), user.password):
        return None
    return user


def update_profile(user: User, name: str | None = None, address: str | None = None) -> None:
    if name:
        user.name = name
    if address:
        user.address = address
