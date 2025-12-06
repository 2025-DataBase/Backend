# db/battle_repository.py
from .connection import get_connection

def get_all_battles_with_demon_mission():
    """
    전투 기록 - 모든 전투 표시
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    b.mission_id, b.battle_seq, b.demon_id, 
                    d.name AS demon_name, 
                    b.location, b.outcome, 
                    b.civilian_killed, b.civilian_injured, 
                    m.objective, m.state AS mission_state
                FROM Battle b
                JOIN Demon d ON b.demon_id = d.demon_id
                LEFT JOIN Mission m ON b.mission_id = m.mission_id
                ORDER BY b.mission_id DESC, b.battle_seq DESC;
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_battle_by_id(battle_id, battle_seq):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT b.*, d.name AS demon_name, d.bounty, m.objective, m.state AS mission_state
                    FROM Battle b
                    JOIN Demon d ON b.demon_id = d.demon_id
                    LEFT JOIN Mission m ON b.mission_id = m.mission_id
                    WHERE b.mission_id = %s AND b.battle_seq = %s
                """
            cursor.execute(sql, (battle_id, battle_seq))
            return cursor.fetchone()
    finally:
        conn.close()

def get_distribution_for_battle(mission_id, battle_seq):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT rd.reward_id, rd.hunter_id, h.name AS hunter_name, h.status AS hunter_status,
                       rd.distributer_amount, rd.state AS distribution_state, rd.distributed_at
                FROM Reward r
                JOIN Reward_Distribution rd ON r.reward_id = rd.reward_id
                JOIN Hunter h ON rd.hunter_id = h.hunter_id
                WHERE r.mission_id = %s AND r.battle_seq = %s
            """
            cursor.execute(sql, (mission_id, battle_seq))
            return cursor.fetchall()
    finally:
        conn.close()

def update_distribution_to_done(mission_id, share_amount, battle_seq):
    """
    Reward_Distribution 상태를 SUCCESS로 변경하고 분배 금액 기록
    IN_PROGRESS 상태인 헌터들만 업데이트
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    UPDATE Reward_Distribution rd
                    JOIN Reward r ON rd.reward_id = r.reward_id
                    SET
                        rd.distributer_amount = %s,
                        rd.state = 'SUCCESS',
                        rd.distributed_at = NOW()
                    WHERE r.mission_id = %s
                    AND r.battle_seq = %s
                    AND rd.state = 'IN_PROGRESS'
                """
            cursor.execute(sql, (share_amount, mission_id, battle_seq))
        conn.commit()
    finally:
        conn.close()

def get_reward_for_battle(mission_id, battle_seq):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT *
                FROM Reward
                WHERE mission_id = %s AND battle_seq = %s
            """
            cursor.execute(sql, (mission_id, battle_seq))
            return cursor.fetchone()
    finally:
        conn.close()

def create_battle(mission_id, battle_seq, demon_id, outcome, location, civilian_killed, civilian_injured):
    """
    전투 기록 생성 - 모든 필드 포함
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Battle (mission_id, battle_seq, demon_id, outcome, location, civilian_killed, civilian_injured)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (mission_id, battle_seq, demon_id, outcome, location, civilian_killed, civilian_injured))
        conn.commit()
        return True
    finally:
        conn.close()

def get_next_battle_seq(mission_id):
    """
    해당 미션의 다음 battle_seq 번호 조회
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT COALESCE(MAX(battle_seq), 0) + 1 as next_seq
                FROM Battle
                WHERE mission_id = %s
            """
            cursor.execute(sql, (mission_id,))
            result = cursor.fetchone()
            return result['next_seq'] if result else 1
    finally:
        conn.close()

def update_demon_status_to_dead(demon_id):
    """
    악마 상태를 DEAD로 변경
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE Demon SET status = 'DEAD' WHERE demon_id = %s"
            cursor.execute(sql, (demon_id,))
        conn.commit()
    finally:
        conn.close()

def update_hunter_status_to_dead(hunter_id):
    """
    헌터 상태를 DEAD로 변경
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE Hunter SET status = 'DEAD' WHERE hunter_id = %s"
            cursor.execute(sql, (hunter_id,))
        conn.commit()
    finally:
        conn.close()

def create_battle_participation(mission_id, battle_seq, hunter_id, participated_status):
    """
    전투 참여 기록 생성 (Battle_Participaton 테이블)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Battle_Participaton (mission_id, battle_seq, hunter_id, participated_status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (mission_id, battle_seq, hunter_id, participated_status))
        conn.commit()
    finally:
        conn.close()

def create_reward(mission_id, battle_seq, team_id, total_amount):
    """
    Reward 생성
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Reward (mission_id, battle_seq, team_id, total_amount)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (mission_id, battle_seq, team_id, total_amount))
            reward_id = cursor.lastrowid
        conn.commit()
        return reward_id
    finally:
        conn.close()

def create_reward_distribution(reward_id, hunter_id):
    """
    Reward_Distribution 생성 (IN_PROGRESS 상태로)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Reward_Distribution (reward_id, hunter_id, state, distributer_amount, distributed_at)
                VALUES (%s, %s, 'IN_PROGRESS', 0, NOW())
            """
            cursor.execute(sql, (reward_id, hunter_id))
        conn.commit()
    finally:
        conn.close()

def call_distribute_bounty_procedure(mission_id, battle_seq):
    """
    SQL 프로시저를 호출하여 현상금 분배
    프로시저는 mission_id와 battle_seq를 받아서 처리합니다.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 프로시저 호출 (mission_id, battle_seq 순서)
            cursor.callproc('distribute_bounty', [mission_id, battle_seq])
            # 결과 가져오기
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            conn.commit()
            if results:
                return results[0]
            return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()