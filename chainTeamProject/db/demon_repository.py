# db/demon_repository.py
from .connection import get_connection

def find_all_devils():
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
                  FROM Demon \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
