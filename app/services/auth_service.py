from pydantic import EmailStr


def start_login(email: EmailStr):
    return {
        "message": "Magic sign-in link sent",
        "email": email,
    }