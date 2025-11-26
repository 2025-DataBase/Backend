# db/account_repository.py
from .connection import get_connection


def add_income(hunter_id: int, amount: int, desc: str) -> None:
    """
    특정 헌터의 Account에 수입을 추가.
    - 없으면 새 row INSERT
    - 있으면 balance/total_income만 증가
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1) 기존 계정 조회
            cursor.execute(
                "SELECT account_id, balance, total_income FROM Account WHERE hunter_id = %s",
                (hunter_id,),
            )
            row = cursor.fetchone()

            if row:
                # UPDATE
                new_balance = row["balance"] + amount
                new_total_income = row["total_income"] + amount
                sql = """
                      UPDATE Account
                      SET balance = %s,
                          total_income = %s,
                          last_tx_type = 'IN',
                          last_tx_amount = %s,
                          last_tx_desc = %s,
                          updated_at = NOW()
                      WHERE account_id = %s \
                      """
                cursor.execute(
                    sql,
                    (
                        new_balance,
                        new_total_income,
                        amount,
                        desc,
                        row["account_id"],
                    ),
                )
            else:
                # INSERT
                sql = """
                      INSERT INTO Account (
                          hunter_id, balance, total_income, total_spent,
                          last_tx_type, last_tx_amount, last_tx_desc, updated_at
                      )
                      VALUES (%s, %s, %s, 0, 'IN', %s, %s, NOW()) \
                      """
                cursor.execute(
                    sql,
                    (hunter_id, amount, amount, amount, desc),
                )

        conn.commit()
    finally:
        conn.close()

def find_account_by_hunter_id(hunter_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Account WHERE hunter_id = %s",
                (hunter_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def upsert_account_for_income(hunter_id: int, amount: int, desc: str):
    """
    보상(+수입)을 Account 에 반영.
    없으면 새로 생성.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT account_id FROM Account WHERE hunter_id = %s",
                (hunter_id,),
            )
            acc = cursor.fetchone()

            if acc:
                cursor.execute(
                    """
                    UPDATE Account
                    SET balance      = balance + %s,
                        total_income = total_income + %s,
                        last_tx_type = 'IN',
                        last_tx_amount = %s,
                        last_tx_desc = %s,
                        updated_at = NOW()
                    WHERE hunter_id = %s
                    """,
                    (amount, amount, amount, desc, hunter_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO Account
                    (hunter_id, balance, total_income, total_spent,
                     last_tx_type, last_tx_amount, last_tx_desc, history, updated_at)
                    VALUES
                        (%s, %s, %s, 0,
                         'IN', %s, %s, NULL, NOW())
                    """,
                    (hunter_id, amount, amount, amount, desc),
                )
        conn.commit()
    finally:
        conn.close()
