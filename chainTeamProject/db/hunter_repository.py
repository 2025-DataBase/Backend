# db/hunter_repository.py
from .connection import get_connection


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
                      a.balance
                  FROM Hunter h
                       LEFT JOIN Team t ON h.team_id = t.team_id
                       LEFT JOIN Account a ON h.hunter_id = a.hunter_id
                  WHERE h.hunter_id = %s
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

def create_hunter(name, status):
    """
    새 헌터 생성 후 hunter_id 반환.
    team_id는 DB 트리거(trigger_random_team)가 자동으로 랜덤 배정함.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # team_id는 NULL로 넘기면 트리거가 자동으로 랜덤 팀 배정
            sql = """
                  INSERT INTO Hunter (name, status, team_id)
                  VALUES (%s, %s, NULL)
                  """
            cursor.execute(sql, (name, status))
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
                      h.team_id,
                      t.team_name,
                      t.region
                  FROM Hunter h
                           LEFT JOIN Team t ON h.team_id = t.team_id
                  ORDER BY h.hunter_id ASC
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
                  FROM Hunter h
                           JOIN Team t ON h.team_id = t.team_id
                  WHERE h.team_id = %s
                  ORDER BY h.name \
                  """           # From에서 Human -> Hunter
            cursor.execute(sql, (team_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_hunter_detail_with_account(hunter_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT h.hunter_id,
                   h.name,
                   h.status,
                   t.team_name,
                   a.balance,
                   IFNULL(SUM(rd.distributer_amount), 0) AS total_income,
                   IFNULL(h.contract_cost, 0) AS total_spent,
                   GREATEST(
                       COALESCE(MAX(rd.distributed_at), '1900-01-01'),
                       COALESCE(h.contract_date, '1900-01-01')
                   ) AS last_tx_date,
                   CASE 
                       WHEN h.contract_date >= COALESCE(MAX(rd.distributed_at), '1900-01-01') 
                       THEN h.contract_cost
                       ELSE MAX(rd.distributer_amount)
                   END AS last_tx_amount,
                   CASE 
                       WHEN h.contract_date >= COALESCE(MAX(rd.distributed_at), '1900-01-01') 
                       THEN 'CONTRACT'
                       WHEN MAX(rd.distributer_amount) IS NOT NULL THEN 'REWARD'
                       ELSE NULL
                   END AS last_tx_type,
                   CASE 
                       WHEN h.contract_date >= COALESCE(MAX(rd.distributed_at), '1900-01-01') 
                       THEN '계약 체결'
                       WHEN MAX(rd.distributer_amount) IS NOT NULL THEN '현상금 분배'
                       ELSE NULL
                   END AS last_tx_desc
            FROM Hunter h
            LEFT JOIN Team t ON h.team_id = t.team_id
            LEFT JOIN Account a ON h.hunter_id = a.hunter_id
            LEFT JOIN Reward_Distribution rd 
                   ON h.hunter_id = rd.hunter_id AND rd.state='SUCCESS'
            WHERE h.hunter_id = %s
            GROUP BY h.hunter_id, h.name, h.status, t.team_name, a.balance, h.contract_cost, h.contract_date
            """
            cursor.execute(sql, (hunter_id,))
            return cursor.fetchone()
    finally:
        conn.close()



# 계약 쪽 코드
def update_contract(hunter_id, demon_id, cost, power, date):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Hunter
                SET demon_id=%s, contract_cost=%s, contract_power=%s, contract_date=%s
                WHERE hunter_id=%s
            """, (demon_id, cost, power, date, hunter_id))
        conn.commit()
    finally:
        conn.close()

def get_contract_list():
    """
    계약 목록 조회 - 계약이 있는 모든 헌터(ALIVE/DEAD 포함) 반환
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT h.hunter_id, h.name AS hunter_name, h.status AS hunter_status,
                       d.demon_id, d.name AS demon_name,
                       h.contract_cost, h.contract_power, h.contract_date
                FROM Hunter h
                LEFT JOIN Demon d ON h.demon_id = d.demon_id
                WHERE h.demon_id IS NOT NULL
                ORDER BY h.contract_date DESC, h.hunter_id
            """)
            return cursor.fetchall()
    finally:
        conn.close()

