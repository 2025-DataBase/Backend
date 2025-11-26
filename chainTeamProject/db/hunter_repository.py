# db/hunter_repository.py
from .connection import get_connection

def get_all_hunters_with_team():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      h.hunter_id,
                      h.name,
                      h.status,
                      t.team_name,
                      t.region
                  FROM Human h
                           LEFT JOIN Team t ON h.team_id = t.team_id
                  ORDER BY t.team_name, h.name \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_hunter_by_id(hunter_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      h.hunter_id,
                      h.name,
                      h.status,
                      t.team_name,
                      a.balance,
                      a.total_income,
                      a.total_spent,
                      a.last_tx_type,
                      a.last_tx_amount,
                      a.last_tx_desc,
                      a.updated_at
                  FROM Human h
                           LEFT JOIN Team t ON h.team_id = t.team_id
                           LEFT JOIN Account a ON h.hunter_id = a.hunter_id
                  WHERE h.hunter_id = %s \
                  """
            cursor.execute(sql, (hunter_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_all_teams():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           SELECT team_id, team_name, region
                           FROM Team
                           ORDER BY team_id
                           """)
            return cursor.fetchall()
    finally:
        conn.close()

def create_hunter(name, status, team_id):
    """
    새 헌터 생성 후 hunter_id 반환.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  INSERT INTO Human (name, status, team_id)
                  VALUES (%s, %s, %s) \
                  """
            cursor.execute(sql, (name, status, team_id))
            hunter_id = cursor.lastrowid
        conn.commit()
        return hunter_id
    finally:
        conn.close()

def get_all_hunters_with_team():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      h.hunter_id,
                      h.name,
                      h.status,
                      h.team_id,          -- ★ 반드시 포함
                      t.team_name,
                      t.region
                  FROM Human h
                           LEFT JOIN Team t ON h.team_id = t.team_id
                  ORDER BY t.team_name, h.name \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def get_hunters_by_team(team_id):
    """
    특정 팀에 소속된 헌터 목록을 직접 DB에서 조회.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      h.hunter_id,
                      h.name,
                      h.status,
                      h.team_id,
                      t.team_name,
                      t.region
                  FROM Human h
                           JOIN Team t ON h.team_id = t.team_id
                  WHERE h.team_id = %s
                  ORDER BY h.name \
                  """
            cursor.execute(sql, (team_id,))
            return cursor.fetchall()
    finally:
        conn.close()