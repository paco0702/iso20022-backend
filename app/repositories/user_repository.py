from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4
from cassandra.query import (SimpleStatement, BatchStatement, ConsistencyLevel)
from app.db.cassandra import get_cassandra_session
from pydantic import EmailStr

def get_user_by_email(email: str) -> Optional[dict]:
    session = get_cassandra_session()

    statement = SimpleStatement(
        """
        SELECT *
        FROM user_by_email
        WHERE email = %s
        """
    )

    row = session.execute(statement, [email]).one()
    return _row_user_dic(row)


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

def insert_user(user) -> bool:
    session = get_cassandra_session()
    batch =  BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    batch.add(
        """
        INSERT INTO user_by_email (email,
                                   id,
                                   full_name_en,
                                   full_name_ch,
                                   hashed_password,
                                   is_active,
                                   is_verified,
                                   created_at,
                                   updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [user["email"], user["id"], user["full_name_en"], user["full_name_ch"], user["hashed_password"],
         user["is_active"], user["is_verified"],
         user["created_at"], user["created_at"]]
    )
    batch.add(
        """
        INSERT INTO user_by_id (id,
                                 email,
                                 full_name_en,
                                 full_name_ch,
                                 hashed_password,
                                 is_active,
                                 is_verified,
                                 created_at,
                                 updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [user["id"], user["email"], user["full_name_en"], user["full_name_ch"], user["hashed_password"],
         user["is_active"], user["is_verified"],
         user["created_at"], user["created_at"]]
    )
    result = session.execute(batch)
    row = result.one()
    return bool(row["[applied]"])

def insert_user_by_email(user) -> bool:
    session = get_cassandra_session()
    print("user to be registered: ", user)
    result = session.execute(
        """
        INSERT INTO user_by_email (email,
                                    id,
                                    full_name_en,
                                    full_name_ch,
                                    hashed_password,
                                    is_active,
                                    is_verified,
                                    created_at,
                                    updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [user["email"], user["id"], user["full_name_en"], user["full_name_ch"], user["hashed_password"], user["is_active"], user["is_verified"],
         user["created_at"], user["created_at"]]
    )
    row = result.one()
    print("user inserted ", row)
    return bool(row["[applied]"])

def insert_user_by_id(
        user) -> bool:
    session = get_cassandra_session()

    result = session.execute(
        """
        INSERT INTO user_by_id (id,
                                email,
                                full_name_en,
                                full_name_ch,
                                hashed_password,
                                is_active,
                                is_verified,
                                created_at,
                                updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS
        """,
        [user["id"], user["email"], user["full_name_en"], user["full_name_ch"], user["hashed_password"],
         user["is_active"], user["is_verified"],
         user["created_at"], user["created_at"]]
    )
    row = result.one()
    print("user inserted ", row)
    return bool(row["[applied]"])

def get_user_by_id(user_id: UUID) -> Optional[dict[str, Any]]:
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
        FROM user_by_id
        WHERE id = %s
        """,
        [user_id],
    ).one()

    return _row_user_dic(row)

def _row_user_dic(row):
    if row is None:
        return None

    return {
        "id": row["id"],
        "email": row["email"],
        "full_name_en": row["full_name_en"],
        "full_name_ch": row["full_name_ch"],
        "hashed_password": row["hashed_password"],
        "is_active": row["is_active"],
        "is_verified": row["is_verified"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

def rollback_inserted_record(user):
    delete_user_by_email(user.email)
    delete_user_by_id(user.id)


def delete_user_by_email(email:EmailStr):
    session = get_cassandra_session()
    session.execute(
        """
        DELETE FROM user_by_email
        WHERE email = %s
        """,
        [email],
    )


def delete_user_by_id(user_id):
    session = get_cassandra_session()
    session.execute(
        """
        DELETE FROM user_by_id
        WHERE id = %s
        """,
        [user_id],
    )