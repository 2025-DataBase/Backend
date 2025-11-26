# db/battle_repository.py
from .connection import get_connection

def get_all_battles_with_demon_mission():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      b.battle_id,
                      b.mission_id,
                      b.demon_id,
                      d.name AS demon_name,
                      b.started_at,
                      b.ended_at,
                      b.location,
                      b.outcome,
                      b.civilian_killed,
                      b.civilian_injured,
                      m.objective,
                      m.status AS mission_status
                  FROM Battle b
                           JOIN Demon d ON b.demon_id = d.demon_id
                           LEFT JOIN Mission m ON b.mission_id = m.mission_id
                  ORDER BY b.started_at DESC \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_battle_by_id(battle_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      b.*,
                      d.name AS demon_name,
                      d.bounty,
                      m.objective,
                      m.status AS mission_status
                  FROM Battle b
                           JOIN Demon d ON b.demon_id = d.demon_id
                           LEFT JOIN Mission m ON b.mission_id = m.mission_id
                  WHERE b.battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_distribution_for_battle(battle_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      dist.battle_id,
                      dist.hunter_id,
                      h.name AS hunter_name,
                      h.status,
                      dist.share_amount,
                      dist.status AS dist_status
                  FROM Distribution dist
                           JOIN Human h ON dist.hunter_id = h.hunter_id
                  WHERE dist.battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def update_distribution_to_done(battle_id, share_amount):
    """
    모든 PENDING 분배를 DONE 처리하면서 share_amount 기록.
    (실제로는 각 헌터별 share_amount를 별도로 계산해서 넣는게 이상적이지만,
     지금은 동일 금액 분배 가정)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  UPDATE Distribution
                  SET share_amount = %s,
                      status = 'DONE',
                      distributed_at = NOW()
                  WHERE battle_id = %s \
                  """
            cursor.execute(sql, (share_amount, battle_id))
        conn.commit()
    finally:
        conn.close()
