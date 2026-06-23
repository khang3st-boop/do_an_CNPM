from passlib.context import CryptContext

from models.user import User
from repositories import user_repository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, password_hash):
    return pwd_context.verify(password, password_hash)


def authenticate(db, email, password):
    user = user_repository.get_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        return None

    if user.status != "active":
        return None

    return user


def ensure_admin_account(db):
    admin = user_repository.get_by_email(db, "admin@hotel.com")

    if admin:
        return admin

    admin = User(
        full_name="Admin Hotel",
        email="admin@hotel.com",
        password_hash=hash_password("123456"),
        role="admin",
        phone="0900000000",
        status="active",
    )
    return user_repository.create(db, admin)

