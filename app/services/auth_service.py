from pydantic import EmailStr
from fastapi import HTTPException, status

def start_login(email: EmailStr):
    return {
        "message": "Magic sign-in link sent",
        "email": email,
    }