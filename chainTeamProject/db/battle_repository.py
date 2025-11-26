from .connection import get_connection


def find_battle_by_id(battle_id: int):
    """
    전투 한 건 상세 조회.
    Demon, Mission까지 JOIN해서 이름 정도는 가져온다고 가정.
    """
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
                      b.civilian_injured
                  FROM Battle b
                           JOIN Demon d ON b.demon_id = d.demon_id
                  WHERE b.battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def find_all_battles():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      b.battle_id,
                      b.mission_id,
                      m.objective AS mission_title,
                      b.demon_id,
                      d.name AS demon_name,
                      b.location,
                      b.outcome,
                      b.started_at,
                      b.ended_at,
                      b.civilian_killed,
                      b.civilian_injured,

                      -- 보상금 계산
                      COALESCE(SUM(bc.amount), 0) AS reward_amount

                  FROM Battle b
                           LEFT JOIN Demon d ON b.demon_id = d.demon_id
                           LEFT JOIN Mission m ON b.mission_id = m.mission_id
                           LEFT JOIN BountyClaim bc ON bc.battle_id = b.battle_id

                  GROUP BY
                      b.battle_id, b.mission_id, m.objective,
                      b.demon_id, d.name, b.location, b.outcome,
                      b.started_at, b.ended_at, b.civilian_killed, b.civilian_injured

                  ORDER BY b.started_at DESC \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def find_battles_by_demon(demon_id: int):
    """
    특정 악마(demon_id)와 관련된 전투만 조회
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      b.battle_id,
                      d.name      AS demon_name,
                      b.location,
                      b.outcome,
                      b.civilian_killed,
                      b.civilian_injured,
                      COALESCE(SUM(bc.amount), 0) AS reward_amount
                  FROM Battle b
                           JOIN Demon d ON b.demon_id = d.demon_id
                           LEFT JOIN BountyClaim bc ON b.battle_id = bc.battle_id
                  WHERE b.demon_id = %s
                  GROUP BY
                      b.battle_id, d.name, b.location,
                      b.outcome, b.civilian_killed, b.civilian_injured
                  ORDER BY b.started_at DESC \
                  """
            cursor.execute(sql, (demon_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def find_hunters_for_battle(battle_id: int):
    """
    해당 전투에 참여한 헌터 목록 (팀/상태 포함)
    BountyClaim 기준으로 참여자 판단.
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
                      t.team_name
                  FROM BountyClaim bc
                           JOIN Human h ON h.hunter_id = bc.hunter_id
                           LEFT JOIN Team t ON t.team_id = h.team_id
                  WHERE bc.battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def find_battles_for_hunter(hunter_id: int):
    """
    특정 헌터가 참여한 전투 목록 조회.
    BountyClaim 를 기준으로 Battle / Demon / Mission 을 조인해서 가져온다.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      b.battle_id,
                      b.mission_id,
                      m.objective AS mission_title,
                      b.demon_id,
                      d.name AS demon_name,
                      b.location,
                      b.outcome,
                      b.started_at,
                      b.ended_at,
                      b.civilian_killed,
                      b.civilian_injured,
                      COALESCE(SUM(bc.amount), 0) AS reward_amount
                  FROM BountyClaim bc
                           JOIN Battle b ON bc.battle_id = b.battle_id
                           JOIN Demon d ON b.demon_id = d.demon_id
                           LEFT JOIN Mission m ON b.mission_id = m.mission_id
                  WHERE bc.hunter_id = %s
                  GROUP BY
                      b.battle_id,
                      b.mission_id,
                      m.objective,
                      b.demon_id,
                      d.name,
                      b.location,
                      b.outcome,
                      b.started_at,
                      b.ended_at,
                      b.civilian_killed,
                      b.civilian_injured
                  ORDER BY b.started_at DESC \
                  """
            cursor.execute(sql, (hunter_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def sum_bounty_by_battle(battle_id: int) -> int:
    """
    해당 전투의 총 보상금 (BountyClaim.amount 합계 기준)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT COALESCE(SUM(amount), 0) AS total_amount
                  FROM BountyClaim
                  WHERE battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            row = cursor.fetchone()
            return row["total_amount"] if row else 0
    finally:
        conn.close()


def delete_claims_for_battle(battle_id: int):
    """
    보상 지급 후, 이 전투에 대한 청구(BountyClaim) 목록 삭제
    -> 화면에서 자동으로 사라지도록
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM BountyClaim WHERE battle_id = %s",
                (battle_id,),
            )
        conn.commit()
    finally:
        conn.close()