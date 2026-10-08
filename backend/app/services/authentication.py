from passlib.context import CryptContext

from app.config import get_settings
from app.models import AdminUser
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def ensure_default_admin(db: Session) -> None:
    settings = get_settings()
    existing = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
    if existing:
        return
    admin = AdminUser(
        username=settings.admin_username,
        password_hash=hash_password(settings.admin_password),
    )
    db.add(admin)
    db.commit()
