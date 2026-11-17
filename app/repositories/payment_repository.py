import base64
from datetime import timezone, datetime
from typing import Optional, Literal
from uuid import UUID
from zoneinfo import ZoneInfo
from cassandra.query import SimpleStatement
from fastapi import Query, HTTPException
from app.db.cassandra import get_cassandra_session
from app.repositories.user_repository import get_user_by_id
from app.schemas.common import Pagination
from app.schemas.payment import GetPaymentResponse, PaymentItem, PaymentBatchItem, GetPaymentBatchResponse


def insert_payment_by_id(payment) -> bool:
    session = get_cassandra_session()

    result = session.execute(
        """
            INSERT INTO payment_by_id (
                id,
                amount,
                currency,
                execute_date,
                end_to_end_id,
                remittance,
                charge_bearer,
                debtor_name,
                debtor_bic,
                debtor_iban,
                creditor_name,
                creditor_bic,
                creditor_iban,
                created_at,
                updated_at,
                message_id,
                initial_party,
                transaction_no,
                code,
                invoice_number,
                created_by,
                updated_by,
                status)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
        """,
        [payment["id"], payment["amount"], payment["currency"], payment["execute_date"],
         payment["end_to_end_id"], payment["remittance"], payment["charge_bearer"], payment["debtor_name"],
         payment["debtor_bic"],
         payment["debtor_iban"], payment["creditor_name"], payment["creditor_bic"], payment["creditor_iban"],
         payment["created_at"],
         payment["updated_at"], payment["message_id"], payment["initial_party"], payment["transaction_no"],
         payment["code"], payment["invoice_number"],
         payment["created_by"], payment["updated_by"], payment["status"]]
    )
    row = result.one()
    return bool(row["[applied]"])


def insert_payment_by_status(payment) -> bool:
    session = get_cassandra_session()

    result = session.execute(
        """
            INSERT INTO payment_by_status (
                id,
                amount,
                currency,
                execute_date,
                end_to_end_id,
                remittance,
                charge_bearer,
                debtor_name,
                debtor_bic,
                debtor_iban,
                creditor_name,
                creditor_bic,
                creditor_iban,
                created_at,
                updated_at,
                message_id,
                initial_party,
                transaction_no,
                code,
                invoice_number,
                created_by,
                updated_by,
                status)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
        """,
        [payment["id"], payment["amount"], payment["currency"], payment["execute_date"],
         payment["end_to_end_id"], payment["remittance"], payment["charge_bearer"], payment["debtor_name"],
         payment["debtor_bic"],
         payment["debtor_iban"], payment["creditor_name"], payment["creditor_bic"], payment["creditor_iban"],
         payment["created_at"],
         payment["updated_at"], payment["message_id"], payment["initial_party"], payment["transaction_no"],
         payment["code"], payment["invoice_number"],
         payment["created_by"], payment["updated_by"], payment["status"]]
    )
    row = result.one()

    return bool(row["[applied]"])


def insert_payment_by_user_id(payment) -> bool:
    session = get_cassandra_session()

    result = session.execute(
        """
            INSERT INTO payment_by_user_id (
                id,
                amount,
                currency,
                execute_date,
                end_to_end_id,
                remittance,
                charge_bearer,
                debtor_name,
                debtor_bic,
                debtor_iban,
                creditor_name,
                creditor_bic,
                creditor_iban,
                created_at,
                updated_at,
                message_id,
                initial_party,
                transaction_no,
                code,
                invoice_number,
                created_by,
                updated_by,
                status)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
        """,
        [payment["id"], payment["amount"], payment["currency"], payment["execute_date"],
         payment["end_to_end_id"], payment["remittance"], payment["charge_bearer"], payment["debtor_name"],
         payment["debtor_bic"],
         payment["debtor_iban"], payment["creditor_name"], payment["creditor_bic"], payment["creditor_iban"],
         payment["created_at"],
         payment["updated_at"], payment["message_id"], payment["initial_party"], payment["transaction_no"],
         payment["code"], payment["invoice_number"],
         payment["created_by"], payment["updated_by"], payment["status"]]
    )
    row = result.one()

    return bool(row["[applied]"])


def get_payment_by_user_id_and_status(
        user_id: UUID,
        payment_status: str,
                      page_state: Optional[str],
                      size: int,
                      ) -> GetPaymentResponse:
    session = get_cassandra_session()

    query = """ 
        SELECT * 
        FROM payment_by_status
        where status = %s
        and created_by = %s
        ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query,
        fetch_size=size
    )
    decoded_page_state = None
    if page_state:
        try:
            decoded_page_state = base64.b64decode(page_state)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid page_state")

    result = session.execute(
        statements,
        (payment_status, user_id),
        paging_state=decoded_page_state
    )
    for row in result.current_rows:
        print(row)

    items = []

    for row in result.current_rows:
        created_by_user = get_user_by_id(row["created_by"])
        updated_by_user = get_user_by_id(row["updated_by"])
        items.append(
                PaymentItem(
                id=str(row["id"]),
                status=row.get("status"),
                created_at=row["created_at"].replace(tzinfo=timezone.utc)
                .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                amount=row["amount"],
                currency=row["currency"],
                execute_date=row["execute_date"].replace(tzinfo=timezone.utc)
                .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                end_to_end_id=row["end_to_end_id"],
                remittance=row["remittance"],
                charge_bearer=row["charge_bearer"],
                debtor_name=row["debtor_name"],
                debtor_bic=row["debtor_bic"],
                debtor_iban=row["debtor_iban"],
                creditor_name=row["creditor_name"],
                creditor_bic=row["creditor_bic"],
                creditor_iban=row["creditor_iban"],
                created_by=created_by_user["full_name_en"],
                updated_by=updated_by_user["full_name_en"],
                transaction_no=row["transaction_no"],
            )
        )


    next_page_state = None

    if result.has_more_pages:
        next_page_state = base64.b64encode(
            result.paging_state
        ).decode("utf-8")

    return GetPaymentResponse(
        items=items,
        pagination=Pagination(
            page_size=size,
            count=len(items),
            next_page_state=next_page_state,
            has_next=result.has_more_pages,

        )
    )


def get_payment_by_status_and_id(payment_status: str, payment_id: UUID, user_id: UUID):
    session = get_cassandra_session()
    query = """ 
               SELECT * 
               FROM payment_by_status
               where status = %s
               and id = %s
               ALLOW FILTERING;
           """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (payment_status, payment_id)
    )
    row = result.one()
    if row is None:
        return HTTPException(status_code=400, detail="Payment was not successful")
    print(row)
    return row

def get_payment_by_status_and_debtor_iban(payment_status: str,
                      debtor_id: str,
                      page_state: Optional[str],
                      user_id: UUID,
                      size: int,
                      ) -> GetPaymentResponse:
        session = get_cassandra_session()

        query = """ 
            SELECT * 
            FROM payment_by_status
            where status = %s
            and created_by = %s
            and debtor_iban = %s
            ALLOW FILTERING;
        """
        statements = SimpleStatement(
            query,
            fetch_size=size
        )
        decoded_page_state = None
        if page_state:
            try:
                decoded_page_state = base64.urlsafe_b64decode(page_state)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid page_state")

        result = session.execute(
            statements,
            (payment_status, user_id, debtor_id),
            paging_state=decoded_page_state
        )
        for row in result.current_rows:
            print(row)

        items = []

        for row in result.current_rows:
            created_by_user = get_user_by_id(row["created_by"])
            updated_by_user = get_user_by_id(row["updated_by"])
            items.append(
                PaymentItem(
                    id=str(row["id"]),
                    status=row.get("status"),
                    created_at=row["created_at"].replace(tzinfo=timezone.utc)
                    .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                    amount=row["amount"],
                    currency=row["currency"],
                    execute_date=row["execute_date"].replace(tzinfo=timezone.utc)
                    .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                    end_to_end_id=row["end_to_end_id"],
                    remittance=row["remittance"],
                    charge_bearer=row["charge_bearer"],
                    debtor_name=row["debtor_name"],
                    debtor_bic=row["debtor_bic"],
                    debtor_iban=row["debtor_iban"],
                    creditor_name=row["creditor_name"],
                    creditor_bic=row["creditor_bic"],
                    creditor_iban=row["creditor_iban"],
                    created_by=created_by_user["full_name_en"],
                    updated_by=updated_by_user["full_name_en"],
                    transaction_no=row["transaction_no"],
                )
            )

        next_page_state = None

        if result.has_more_pages:
            next_page_state = base64.urlsafe_b64encode(
                result.paging_state
            ).decode("utf-8")

        return GetPaymentResponse(
            items=items,
            pagination=Pagination(
                page_size=size,
                count=len(items),
                next_page_state=next_page_state,
                has_next=result.has_more_pages,

            )
        )


def exist_payment_by_id(payment_status: str, payment_id: UUID, user_id: UUID):
    session = get_cassandra_session()
    query = """ 
    SELECT COUNT(*)
    FROM payment_by_id
    WHERE id = %s
    AND status = %s
    AND created_by = %s
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (payment_id, payment_status, user_id),
    )

    row = result.one()
    if row is None:
        return False

    return row["count"] > 0

def all_payment_by_ids_exists ( payment_ids: list[UUID]):
    session = get_cassandra_session()
    placeholders = ', '.join(['%s'] * len(payment_ids))

    query = f""" 
    SELECT COUNT(*)
    FROM payment_by_id
    WHERE id IN ({placeholders})
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        payment_ids
    )

    row = result.one()
    if row is None:
        return False

    return row["count"] == len(payment_ids)


def get_total_amount_by_payment_ids( payment_ids: list[UUID]):
    session = get_cassandra_session()
    placeholders = ', '.join(['%s'] * len(payment_ids))

    query = f""" 
    SELECT SUM(amount) AS total_amount
    FROM payment_by_id
    WHERE id IN ({placeholders})
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        payment_ids
    )

    row = result.one()
    if row is None:
        return False

    return row["total_amount"]



def update_payment_id_by_id(user_id: UUID, new_status: str, payment_id: UUID, updated_at: datetime):
    session = get_cassandra_session()
    query = """ 
    UPDATE payment_by_id
    SET status = %s, 
    updated_at = %s,
    updated_by = %s
    WHERE id = %s
    IF EXISTS
    """

    print("", user_id, " ", new_status, " ", payment_id, " ", updated_at)
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (new_status, updated_at, user_id, payment_id),
    )

    row = result.one()
    return bool(row["[applied]"])


def remove_payment_by_status(payment_status: str, user_id: UUID, payment_id: UUID):
    session = get_cassandra_session()
    delete_query = """
        DELETE FROM payment_by_status
        WHERE status = %s
        AND id = %s AND created_by = %s
        IF EXISTS
        """

    statements = SimpleStatement(
        delete_query
    )

    result = session.execute(
        statements,
        (payment_status, payment_id, user_id),
    )
    row = result.one()
    return bool(row["[applied]"])


def insert_payment_by_status(payment) -> bool:
    session = get_cassandra_session()
    result = session.execute(
        """
           INSERT INTO payment_by_status (
               id,
               amount,
               currency,
               execute_date,
               end_to_end_id,
               remittance,
               charge_bearer,
               debtor_name,
               debtor_bic,
               debtor_iban,
               creditor_name,
               creditor_bic,
               creditor_iban,
               created_at,
               updated_at,
               message_id,
               initial_party,
               transaction_no,
               code,
               invoice_number,
               created_by,
               updated_by,
               status)
       VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
       """,
        [payment["id"], payment["amount"], payment["currency"], payment["execute_date"],
         payment["end_to_end_id"], payment["remittance"], payment["charge_bearer"], payment["debtor_name"],
         payment["debtor_bic"],
         payment["debtor_iban"], payment["creditor_name"], payment["creditor_bic"], payment["creditor_iban"],
         payment["created_at"],
         payment["updated_at"], payment["message_id"], payment["initial_party"], payment["transaction_no"],
         payment["code"], payment["invoice_number"],
         payment["created_by"], payment["updated_by"], payment["status"]]
    )

    row = result.one()
    return bool(row["[applied]"])


def insert_payment_batch_by_id(payment_batch):
    session = get_cassandra_session()
    result = session.execute(
        """
           INSERT INTO payment_batch_message_by_id (
               id,
               batch_type,
               batch_id,
               batch_message,
               batch_name,
               created_at,
               updated_at,
               created_by,
               updated_by,
               payment_ids,
               total_amount)
       VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
       """,
        [payment_batch["id"], payment_batch["batch_type"], payment_batch["batch_id"],
         payment_batch["batch_message"], payment_batch["batch_name"],
         payment_batch["created_at"], payment_batch["updated_at"],
         payment_batch["created_by"], payment_batch["updated_by"],
         payment_batch["payment_ids"], payment_batch["total_amount"]]
    )

    row = result.one()
    return bool(row["[applied]"])



def get_payment_batch_by_user_id(user_id: UUID,
                      page_state: Optional[str],
                      size: int,) -> GetPaymentBatchResponse:
    session = get_cassandra_session()
    query = """ 
        SELECT * 
        FROM payment_batch_message_by_id
        where created_by = %s
        ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query,
        fetch_size=size
    )
    decoded_page_state = None
    if page_state:
        try:
            decoded_page_state = base64.b64decode(page_state)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid page_state")

    result = session.execute(
        statements,
        (user_id,),
        paging_state=decoded_page_state
    )
    for row in result.current_rows:
        print(row)

    items = []

    for row in result.current_rows:
        created_by_user = get_user_by_id(row["created_by"])
        updated_by_user = get_user_by_id(row["updated_by"])
        total_amount = get_amount_by_id(row["payment_ids"])
        items.append(
                PaymentBatchItem(
                id=str(row["id"]),
                batch_type=row["batch_type"],
                batch_id=str(row["batch_id"]),
                xml_content=row["batch_message"],
                batch_name=row["batch_name"],
                payment_ids=row["payment_ids"],
                total_amount=total_amount,
                created_at=row["created_at"].replace(tzinfo=timezone.utc)
                .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                updated_at=row["updated_at"].replace(tzinfo=timezone.utc)
                .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                created_by=created_by_user["full_name_en"],
                updated_by=updated_by_user["full_name_en"],
            )
        )

    next_page_state = None

    if result.has_more_pages:
        next_page_state = base64.b64encode(
            result.paging_state
        ).decode("utf-8")

    return GetPaymentBatchResponse(
        items=items,
        pagination=Pagination(
            page_size=size,
            count=len(items),
            next_page_state=next_page_state,
            has_next=result.has_more_pages,
        )
    )

def update_status_payment_by_id_by_ids(user_id: UUID, new_status: str, payment_ids: list[UUID]):
    session = get_cassandra_session()

    placeholders = ', '.join(['%s'] * len(payment_ids))
    # 1. Update payment to PENDING status
    query = f""" 
    UPDATE payment_by_id
    SET status = %s
    WHERE id IN ({placeholders})
    IF EXISTS
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (new_status, payment_ids),
    )
    row = result.one()
    return bool(row["[applied]"])

def update_status_payment_by_status_by_ids(user_id: UUID, new_status: str, payment_ids: list[UUID]):
    session = get_cassandra_session()

    placeholders = ', '.join(['%s'] * len(payment_ids))
    # 1. Update payment to PENDING status
    query = f""" 
    UPDATE payment_by_status
    SET status = %s
    WHERE id IN ({placeholders})
    IF EXISTS
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (new_status, payment_ids),
    )
    row = result.one()
    return bool(row["[applied]"])


def count_payment_batch_total_amount ():
    session = get_cassandra_session()

    query = """ 
    SELECT SUM(TOTAL_AMOUNT) as amount
    FROM payment_batch_message_by_id
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements
    )

    row = result.one()
    total_amount = row["amount"] if row and row["amount"] is not None else 0

    return total_amount


def count_payment_batch ():
    session = get_cassandra_session()

    query = """ 
    SELECT COUNT(*)
    FROM payment_batch_message_by_id
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements
    )

    row = result.one()
    return row["count"]

def count_total_amount_batch ():
    session = get_cassandra_session()
    query = """ 
    SELECT SUM(AMOUNT) as amount
    FROM payment_batch_message_by_id
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements
    )

    row = result.one()
    return row["amount"]


def count_payment_batch_by_type (batch_type: str):
    session = get_cassandra_session()

    query = """ 
    SELECT COUNT(*)
    FROM payment_batch_message_by_id
    WHERE batch_type = %s
    ALLOW FILTERING;
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (batch_type, )
    )

    row = result.one()
    return row["count"]

def get_amount_by_id(ids: list[UUID]):
    session = get_cassandra_session()
    placeholders = ', '.join(['%s'] * len(ids))

    query = f""" 
       SELECT SUM(AMOUNT) AS amount 
       FROM payment_by_id
       WHERE id IN ({placeholders})
       ALLOW FILTERING;
       """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        ids
    )
    row = result.one()
    total_amount = row["amount"] if row and row["amount"] is not None else 0

    return total_amount

def get_batch_by_batch_id(batch_id: str):
    session = get_cassandra_session()

    query = """ 
        SELECT *
        FROM payment_batch_message_by_id
        WHERE batch_id = %s
        ALLOW FILTERING;
        """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (batch_id,)
    )
    row = result.one()
    print (row)
    return row

def get_payment_by_ids(payment_ids: list[UUID], user_id: UUID):
        session = get_cassandra_session()

        placeholders = ', '.join(['%s'] * len(payment_ids))

        query = f""" 
           SELECT *
           FROM payment_by_id
           WHERE id IN ({placeholders})
           ALLOW FILTERING;
           """
        statements = SimpleStatement(
            query
        )
        result = session.execute(
            statements,
            payment_ids
        )
        items = []


        for row in result.current_rows:
            created_by_user = get_user_by_id(row["created_by"])
            updated_by_user = get_user_by_id(row["updated_by"])
            print("row", row)
            items.append(
                PaymentItem(
                    id=str(row["id"]),
                    status=row.get("status"),
                    created_at=row["created_at"].replace(tzinfo=timezone.utc)
                    .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                    amount=row["amount"],
                    currency=row["currency"],
                    execute_date=row["execute_date"].replace(tzinfo=timezone.utc)
                    .astimezone(ZoneInfo("Asia/Hong_Kong")).isoformat(),
                    end_to_end_id=row["end_to_end_id"],
                    remittance=row["remittance"],
                    charge_bearer=row["charge_bearer"],
                    debtor_name=row["debtor_name"],
                    debtor_bic=row["debtor_bic"],
                    debtor_iban=row["debtor_iban"],
                    creditor_name=row["creditor_name"],
                    creditor_bic=row["creditor_bic"],
                    creditor_iban=row["creditor_iban"],
                    created_by=created_by_user["full_name_en"],
                    updated_by=updated_by_user["full_name_en"],
                    transaction_no=row["transaction_no"],
                )
            )

        return items


