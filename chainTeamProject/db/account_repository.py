# db/account_repository.py
from .connection import get_connection


def ensure_account_exists(hunter_id):
    """
    헌터 1명 = 계정 1개. 없으면 balance = 0으로 생성.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 계정 존재 여부 확인
            cursor.execute("""
                SELECT hunter_id FROM Account WHERE hunter_id = %s
            """, (hunter_id,))
            
            row = cursor.fetchone()
            if row:
                return hunter_id   # hunter_id 자체가 PK

            # 없으면 생성
            cursor.execute("""
                INSERT INTO Account (hunter_id, balance)
                VALUES (%s, 0)
            """, (hunter_id,))
        
        conn.commit()
        return hunter_id
    finally:
        conn.close()


def add_income(hunter_id, amount, desc=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Account
                SET balance = balance + %s
                WHERE hunter_id = %s
            """, (amount, hunter_id))
        conn.commit()
    finally:
        conn.close()



