# db/demon_repository.py
from .connection import get_connection

def get_all_demons():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      demon_id,
                      name,
                      grade,
                      bounty,
                      civilian_kills,
                      civilian_injuries
                  FROM Demon
                  ORDER BY bounty DESC \
                  """                               # 시민에 대한 테이블 속성 이름 수정 반영
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def update_demon_totals_and_risk(demon_id, killed_total, injured_total,
                                 grade, bounty):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  UPDATE Demon
                  SET civilian_kills = %s,
                      civilian_injuries = %s,
                      grade = %s,
                      bounty = %s
                  WHERE demon_id = %s \
                  """                           # 시민에 대한 테이블 속성 이름 수정 반영
            cursor.execute(sql, (killed_total, injured_total,
                                 grade, bounty, demon_id))
        conn.commit()
    finally:
        conn.close()

def recalc_totals_from_battles(demon_id):
    """
    Battle 테이블에서 해당 demon_id의 killed/injured 합계를 구해 돌려줌.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      COALESCE(SUM(civilian_killed), 0) AS killed_sum,
                      COALESCE(SUM(civilian_injured), 0) AS injured_sum
                  FROM Battle
                  WHERE demon_id = %s \
                  """                       # 여긴 왜 시민에 대한 테이블 속성 이름 수정 반영된거지? .... 작동 안 되었을텐데..?
            cursor.execute(sql, (demon_id,))
            row = cursor.fetchone()
            return row["killed_sum"], row["injured_sum"]
    finally:
        conn.close()
