# db/account_repository.py
from .connection import get_connection

# def ensure_account_exists(hunter_id):
#     """
#     헌터 등록 시 계정도 하나씩 있는게 편하므로,
#     없으면 새로 만든다.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("""
#                            SELECT account_id FROM Account WHERE hunter_id = %s
#                            """, (hunter_id,))
#             row = cursor.fetchone()
#             if row:
#                 return row["account_id"]

#             sql = """
#                   INSERT INTO Account(
#                       hunter_id, balance, total_income, total_spent,
#                       last_tx_type, last_tx_amount, last_tx_desc, updated_at
#                   ) VALUES (%s, 0, 0, 0, NULL, NULL, NULL, NOW()) \
#                   """
#             cursor.execute(sql, (hunter_id,))
#             account_id = cursor.lastrowid
#         conn.commit()
#         return account_id
#     finally:
#         conn.close()

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



# def add_income(hunter_id, amount, desc):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   UPDATE Account
#                   SET balance = balance + %s,
#                       total_income = total_income + %s,
#                       last_tx_type = 'IN',
#                       last_tx_amount = %s,
#                       last_tx_desc = %s,
#                       updated_at = NOW()
#                   WHERE hunter_id = %s \
#                   """
#             cursor.execute(sql, (amount, amount, amount, desc, hunter_id))
#         conn.commit()
#     finally:
#         conn.close()

# def add_income(hunter_id, amount):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("""
#                 UPDATE Account
#                 SET balance = balance + %s
#                 WHERE hunter_id = %s
#             """, (amount, hunter_id))
#         conn.commit()
#     finally:
#         conn.close()
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


# 해당 파일은 오류 가능성 존재
# 무슨 내용인지 잘 파악은 안되지만 현 DB에 맞게 수정 완료
