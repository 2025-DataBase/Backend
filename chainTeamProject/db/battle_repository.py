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

def call_distribute_bounty(battle_id):
    """
    저장 프로시저 distribute_bounty를 호출하여
    1/n 분배 로직을 DB에서 수행하고 결과(1인당 share, 참여 인원 수)를 반환.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # IN 파라미터 한 개(battle_id)를 전달하여 프로시저 호출
            cursor.callproc("distribute_bounty", (battle_id,))
            # 프로시저 마지막 SELECT 결과를 한 행으로 받는다.
            row = cursor.fetchone()
            if not row:
                return 0, 0
            return row.get("share", 0), row.get("participant_count", 0)
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
