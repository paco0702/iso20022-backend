import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(password_bytes,
                         bcrypt.gensalt())

    return hashed.decode("utf-8");