# db/distribution_repository.py
from .connection import get_connection
from datetime import datetime


def exists_distribution_for_battle(battle_id: int) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM Distribution WHERE battle_id = %s",
                (battle_id,),
            )
            row = cursor.fetchone()
            return row["cnt"] > 0
    finally:
        conn.close()

def insert_distribution(battle_id: int,
                        hunter_id: int,
                        share_amount: int,
                        is_dead_at_battle: bool):
    """
    Distribution 테이블에 한 건 INSERT.
    - is_dead_at_battle: 전투 시점에 사망 여부 (True/False)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  INSERT INTO Distribution(
                      battle_id,
                      hunter_id,
                      share_amount,
                      is_dead_at_battle,
                      distributed_at,
                      status
                  )
                  VALUES (%s, %s, %s, %s, NOW(), 'DONE') \
                  """
            cursor.execute(
                sql,
                (
                    battle_id,
                    hunter_id,
                    share_amount,
                    1 if is_dead_at_battle else 0,
                ),
            )
        conn.commit()
    finally:
        conn.close()

def delete_by_battle(battle_id: int) -> None:
    """
    같은 battle_id에 대해 기존 분배 기록이 있다면 삭제
    (중복 지급 방지용 – 필요 없으면 사용 안 해도 됨)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM Distribution WHERE battle_id = %s"
            cursor.execute(sql, (battle_id,))
        conn.commit()
    finally:
        conn.close()
