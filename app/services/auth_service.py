from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import SessionLocal
from app.models.user import User


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, password)


def get_user_by_username(username: str):
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def get_user_by_id(user_id: int):
    session = SessionLocal()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def seed_default_users():
    session = SessionLocal()
    try:
        defaults = [
            {
                "name": "Administrator",
                "username": "admin",
                "password": "admin123",
                "is_admin": True,
            },
            {
                "name": "Tester",
                "username": "tester",
                "password": "tester123",
                "is_admin": False,
            },
        ]

        for item in defaults:
            existing = session.query(User).filter(User.username == item["username"]).first()
            if existing:
                continue

            session.add(
                User(
                    name=item["name"],
                    username=item["username"],
                    password=hash_password(item["password"]),
                    is_admin=item["is_admin"],
                )
            )

        session.commit()
    finally:
        session.close()
