import os
import bcrypt
from typing import Dict, Optional

from flask import session
from models import User

# In-memory user store
_USERS: Dict[str, User] = {}

# Simple in-memory login failure tracking (for basic lockout)
_FAILED_LOGINS: Dict[str, int] = {}
_LOCKED_ACCOUNTS: Dict[str, bool] = {}

MAX_FAILED_ATTEMPTS = int(os.environ.get("MAX_FAILED_ATTEMPTS", "5"))


def _validate_password_policy(password: str) -> None:
    """
    Enforce a simple password policy:
    - minimum length 8
    - at least one digit
    - at least one lowercase letter
    - at least one uppercase letter
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit.")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter.")


def init_demo_user() -> None:
    """
    Create a demo *admin* user using a hashed password.

    In a real deployment this would be replaced by a proper user
    provisioning process.
    """
    if "admin@bookstore.com" in _USERS:
        return

    demo_password = os.environ.get("DEMO_ADMIN_PASSWORD", "AdminPass123!")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(demo_password.encode("utf-8"), salt)

    demo_user = User(
        email="admin@bookstore.com",
        password=hashed_password,
        name="Admin User",
        address="123 Admin Street",
        is_admin=True,
    )
    _USERS[demo_user.email] = demo_user


def get_current_user() -> Optional[User]:
    email = session.get("user_email")
    if not email:
        return None
    return _USERS.get(email)


def register_user(email: str, raw_password: str, name: str, address: str = "") -> User:
    """
    Register a new non-admin user with a hashed password and basic policy checks.
    """
    if email in _USERS:
        raise ValueError("Email already registered")

    _validate_password_policy(raw_password)

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    user = User(email=email, password=hashed_password, name=name, address=address, is_admin=False)
    _USERS[email] = user
    return user


def authenticate(email: str, raw_password: str) -> Optional[User]:
    """
    Authenticate a user using a bcrypt hash, with basic lockout after
    repeated failures. Returns the User on success, or None on failure.
    """
    # Locked accounts always fail generically (do not reveal lock status to user)
    if _LOCKED_ACCOUNTS.get(email):
        return None

    user = _USERS.get(email)
    if not user:
        return None

    if not bcrypt.checkpw(raw_password.encode("utf-8"), user.password):
        # failed attempt
        _FAILED_LOGINS[email] = _FAILED_LOGINS.get(email, 0) + 1
        if _FAILED_LOGINS[email] >= MAX_FAILED_ATTEMPTS:
            _LOCKED_ACCOUNTS[email] = True
        return None

    # reset counters on success
    _FAILED_LOGINS[email] = 0
    _LOCKED_ACCOUNTS[email] = False
    return user


def is_admin(user: Optional[User]) -> bool:
    """Return True if the current user has administrative privileges."""
    return bool(user and getattr(user, "is_admin", False))


def update_profile(user: User, name: str | None = None, address: str | None = None) -> None:
    """
    Update basic profile details for the given user.
    """
    if name:
        user.name = name
    if address:
        user.address = address
