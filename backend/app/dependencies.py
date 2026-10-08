from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import get_settings

settings = get_settings()


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt="admin-session")


def create_session_token(username: str) -> str:
    return _serializer().dumps({"username": username})


def read_session_token(token: str) -> str | None:
    try:
        data = _serializer().loads(token, max_age=settings.session_max_age_seconds)
        return data.get("username")
    except (BadSignature, SignatureExpired):
        return None


def require_admin(session: str | None = Cookie(default=None, alias=settings.session_cookie_name)) -> str:
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    username = read_session_token(session)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return username
