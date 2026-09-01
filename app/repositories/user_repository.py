from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from cassandra.query import SimpleStatement
from app.db.cassandra import get_cassandra_session

def get_user_by_email(email: str) -> Optional[dict]:
    session = get_cassandra_session()

    statement = SimpleStatement(
        """
        SELECT * 
        FROM users_by_email
        WHERE email = %s
        """
    )

    row = session.execute(statement, [email]).one()

    return row


def get_user_by_id(user_id: UUID) -> Optional[dict]:
    session = get_cassandra_session()

    statement = SimpleStatement(
        """
        SELECT * 
        FROM users_by_id
        WHERE id = %s
        """
    )
    row = session.execute(statement, [user_id]).one()

    return row

def create_email_user(
        email: str,
        password_hash: str,
        full_name: Optional[str] = None) -> dict:
    session = get_cassandra_session()
    user_id = uuid4()
    created_at = datetime.utcnow()

    is_active = True
    is_verified = False

    session.execute(
        """
        INSERT INTO users_by_email
            (email, 
             id,
             full_name,
             hashed_password,
             is_active, 
             is_verified,
             created_at,
             updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        [email, user_id,full_name,is_active,is_verified,created_at,created_at],
    )

    session.execute(
        """
        INSERT INTO users_by_id
            (id,
             email,
             full_name,
             hashed_password,
             is_active,
             is_verified,
             created_at,
             updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        [user_id,email,full_name,is_active,is_verified,created_at,created_at],
    )

    return {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "hashed_password": password_hash,
        "is_active": is_active,
        "is_verified": is_verified,
        "created_at": created_at,
        "updated_at": created_at
    }