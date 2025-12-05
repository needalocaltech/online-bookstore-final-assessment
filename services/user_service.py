import os
from typing import Dict, Optional

import bcrypt
from flask import session

from models import User

# In-memory user store
_USERS: Dict[str, User] = {}

# Simple in-memory login failure tracking (for basic lockout)
_FAILED_LOGINS: Dict[str, int] = {}
_LOCKED_ACCOUNTS: Dict[str, bool] = {}

# How many failed attempts before we temporarily lock an account
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


def _make_user(email: str, raw_password: str, name: str, role: str = "user") -> None:
    """
    Helper to create a user with a bcrypt-hashed password and store in _USERS.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)

    # is_admin flag is still supported on the User model
    is_admin = (role.lower() == "admin")

    user = User(
        email=email,
        password=hashed_password,
        name=name,
        address="",
        is_admin=is_admin,
        role=role.lower(),
    )
    _USERS[email] = user


def init_demo_user() -> None:
    """
    Create demo accounts using hashed passwords.

    These *only* live in memory – they are recreated every time
    the app starts.

    Demo accounts:

        Email: demo@bookstore.com      Password: demo123      Role: user
        Email: admin@bookstore.com     Password: Admin123!    Role: admin
        Email: reviewer@bookstore.com  Password: Review123!   Role: reviewer
        Email: user@bookstore.com      Password: User123!     Role: user
    """
    # If we already initialised users once, don't do it again
    if _USERS:
        return

    # Match the credentials shown on the login page
    _make_user(
        email="demo@bookstore.com",
        raw_password=os.environ.get("DEMO_DEMO_PASSWORD", "demo123"),
        name="Demo User",
        role="user",
    )

    _make_user(
        email="admin@bookstore.com",
        raw_password=os.environ.get("DEMO_ADMIN_PASSWORD", "Admin123!"),
        name="Admin User",
        role="admin",
    )

    _make_user(
        email="reviewer@bookstore.com",
        raw_password=os.environ.get("DEMO_REVIEWER_PASSWORD", "Review123!"),
        name="Reviewer User",
        role="reviewer",
    )

    _make_user(
        email="user@bookstore.com",
        raw_password=os.environ.get("DEMO_USER_PASSWORD", "User123!"),
        name="Standard User",
        role="user",
    )


def get_current_user() -> Optional[User]:
    """
    Return the currently logged-in user (based on session), or None.
    """
    email = session.get("user_email")
    if not email:
        return None
    return _USERS.get(email)


def register_user(email: str, raw_password: str, name: str, address: str = "") -> User:
    """
    Public self-registration: always creates a standard 'user' role.
    """
    if email in _USERS:
        raise ValueError("Email already registered")

    _validate_password_policy(raw_password)

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)

    user = User(
        email=email,
        password=hashed_password,
        name=name,
        address=address,
        is_admin=False,
        role="user",
    )
    _USERS[email] = user
    return user


def create_user_with_role(
    email: str,
    raw_password: str,
    name: str,
    address: str,
    role: str,
) -> User:
    """
    Admin-only helper: create a user with an explicit role
    ('user', 'reviewer', 'admin').
    """
    if email in _USERS:
        raise ValueError("Email already exists")

    role = role.lower()
    if role not in {"user", "reviewer", "admin"}:
        raise ValueError("Role must be one of: user, reviewer, admin")

    _validate_password_policy(raw_password)

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)

    is_admin = (role == "admin")
    user = User(
        email=email,
        password=hashed_password,
        name=name,
        address=address,
        is_admin=is_admin,
        role=role,
    )
    _USERS[email] = user
    return user


def authenticate(email: str, raw_password: str) -> Optional[User]:
    """
    Authenticate a user using a bcrypt hash, with basic lockout after
    repeated failures. Returns the User on success, or None on failure.
    """
    # Locked accounts always fail generically (do not reveal lock status)
    if _LOCKED_ACCOUNTS.get(email):
        return None

    user = _USERS.get(email)
    if not user:
        return None

    if not bcrypt.checkpw(raw_password.encode("utf-8"), user.password):
        # Failed attempt
        _FAILED_LOGINS[email] = _FAILED_LOGINS.get(email, 0) + 1
        if _FAILED_LOGINS[email] >= MAX_FAILED_ATTEMPTS:
            _LOCKED_ACCOUNTS[email] = True
        return None

    # Reset counters on success
    _FAILED_LOGINS[email] = 0
    _LOCKED_ACCOUNTS[email] = False
    return user


def has_role(user: Optional[User], *roles: str) -> bool:
    """
    Return True if the user's role matches any of the provided roles.
    """
    if not user:
        return False
    return user.role in {r.lower() for r in roles}


def is_admin(user: Optional[User]) -> bool:
    return has_role(user, "admin")


def is_reviewer(user: Optional[User]) -> bool:
    return has_role(user, "reviewer")


def update_profile(user: User, name: str | None = None, address: str | None = None) -> None:
    """
    Update basic profile details for the given user.
    """
    if name:
        user.name = name
    if address:
        user.address = address
