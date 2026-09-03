from datetime import datetime, timezone
from uuid import UUID
from app.db.cassandra import get_cassandra_session

def upsert_user_repair_task(user,
                           reason: str,
                           last_error: str) -> None:
    session = get_cassandra_session()
    session.execute(
        """
        INSERT INTO user_repair_tasks (
            user_id,
            task_type,
            email,
            full_name_en,
            full_name_ch,
            created_at,
            reason,
            attempts,
            last_error
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            user["id"],
            "insert_user",
            user["email"],
            user["full_name_en"],
            user["full_name_ch"],
            datetime.now(timezone.utc).isoformat(),
            reason,
            0,
            last_error
        ]
    )

def get_repair_tasks(limit: int = 100):
    session = get_cassandra_session()

    rows = session.execute(
        """
        SELECT user_id
        task_type,
        email,
        created_at,
        full_name_en,
        full_name_ch,
        reason,
        attempts,
        last_error
        FROM user_repair_tasks
        LIMIT %s
        """,
        [limit],
    )

    return list(rows)


def increment_repair_attempt(
        user_id: UUID,
        task_type: str,
        last_error: str,
        attempts: int,
) -> None:
    session = get_cassandra_session()

    session.execute(
        """
        UPDATE user_repair_tasks
        SET attempts   = %s,
            last_error = %s
        WHERE user_id = %s
          AND task_type = %s
        """,
        [ attempts + 1, last_error, user_id, task_type]
    )