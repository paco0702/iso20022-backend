from app.db.cassandra import get_cassandra_session


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
                updated_by)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) IF NOT EXISTs     
        """,
        [payment["id"], payment["amount"], payment["currency"], payment["execute_date"],
         payment["end_to_end_id"], payment["remittance"], payment["charge_bearer"], payment["debtor_name"], payment["debtor_bic"],
         payment["debtor_iban"], payment["creditor_name"], payment["creditor_bic"], payment["creditor_iban"], payment["created_at"],
         payment["updated_at"], payment["message_id"], payment["initial_party"], payment["transaction_no"], payment["code"], payment["invoice_number"],
         payment["created_by"], payment["updated_by"]]
    )
    row = result.one()
    print("Payment was successfully inserted", row)
    return bool(row["[applied]"])