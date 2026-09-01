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


def insert_email_user(
        email: str,
        hashed_password: str,
        user_id: UUID,
        created_at: Optional[datetime] = None,
        full_name: Optional[str] = None) -> bool:
    session = get_cassandra_session()

    is_active = True
    is_verified = False

    result = session.execute(
        """
        INSERT INTO users_by_email (email,
                                    id,
                                    full_name,
                                    hashed_password,
                                    is_active,
                                    is_verified,
                                    created_at,
                                    updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [email, user_id, full_name, hashed_password, is_active, is_verified, created_at, created_at],
    )
    row = result.one()
    return bool(row.applied)


def insert_user_by_id(
        email: str,
        hashed_password: str,
        user_id: UUID,
        created_at: Optional[datetime] = None,
        full_name: Optional[str] = None) -> bool:
    session = get_cassandra_session()
    is_active = True
    is_verified = False

    result = session.execute(
        """
        INSERT INTO users_by_id (id,
                                 email,
                                 full_name,
                                 hashed_password,
                                 is_active,
                                 is_verified,
                                 created_at,
                                 updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [user_id, email, full_name, hashed_password, is_active, is_verified, created_at, created_at]
    )
    row = result.one()
    return bool(row.applied)


def get_user_by_email(email: str) -> None:
    """
    :param email:
    :return:
    """
    session = get_cassandra_session()

    row = session.execute(
        """
        SELECT email,
               id,
               full_name,
               hashed_password,
               is_active,
               is_verified,
               created_at,
               updated_at
        FROM users_by_email
        WHERE email = %s
        """,
        [email],
    ).one()

    return _row_to_dic(row)


def get_user_by_id(user_id: UUID) -> None:
    """
    :param user_id:
    :return:
    """
    session = get_cassandra_session()

    row = session.execute(
        """
        SELECT email,
               id,
               full_name,
               hashed_password,
               is_active,
               is_verified,
               created_at,
               updated_at
        FROM users_by_id
        WHERE id = %s
        """,
        [user_id],
    ).one()

    return _row_to_dic(row)


def _row_to_dic(row):
    if row is None:
        return None

    return {
        "id": row.id,
        "email": row.email,
        "full_name": row.full_name,
        "hashed_password": row.hashed_password,
        "is_active": row.is_active,
        "is_verified": row.is_verified,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
