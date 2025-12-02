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
                      civilian_killed_total,
                      civilian_injured_total
                  FROM Demon
                  ORDER BY bounty DESC \
                  """
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
                  SET civilian_killed_total = %s,
                      civilian_injured_total = %s,
                      grade = %s,
                      bounty = %s
                  WHERE demon_id = %s \
                  """
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
                  """
            cursor.execute(sql, (demon_id,))
            row = cursor.fetchone()
            return row["killed_sum"], row["injured_sum"]
    finally:
        conn.close()
