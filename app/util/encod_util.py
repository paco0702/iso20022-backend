import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(password_bytes,
                         bcrypt.gensalt())

    return hashed.decode("utf-8");

def create_access_token(user_id: str, email: str):
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.jwt_secret_key, settings.jwt_algorithm)

    return token