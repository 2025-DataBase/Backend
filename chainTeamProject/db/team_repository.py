# db/team_repository.py
from .connection import get_connection

def find_all_teams():
    """
    팀 전체 목록 조회
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      team_id,
                      team_name,
                      region
                  FROM Team
                  ORDER BY team_id
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
