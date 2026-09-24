import base64
from datetime import timezone
from typing import Optional, Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from cassandra.query import SimpleStatement
from fastapi import Query, HTTPException

from app.data.payment_constant import PaymentStatus
from app.db.cassandra import get_cassandra_session
from app.schemas.common import Pagination
from app.schemas.payment import GetPaymentResponse, PaymentItem


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
    print("insert by payment status: ",row)
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


def get_payment_by_id(payment_status: str,
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

    items = [
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
            created_by=str(row["created_by"]),
            updated_by=str(row["updated_by"]),
            transaction_no=row["transaction_no"],
        )

        for row in result.current_rows
    ]

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


def get_payment_by_status(payment_status: str, payment_id: UUID, user_id: UUID):
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


def update_payment_status_by_id(user_id: UUID, new_status: str, payment_id: UUID):
    session = get_cassandra_session()

    # 1. Update payment to PENDING status
    query = """ 
    UPDATE payment_by_id
    SET status = %s
    WHERE id = %s
    IF EXISTS
    """
    statements = SimpleStatement(
        query
    )
    result = session.execute(
        statements,
        (new_status, payment_id),
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
