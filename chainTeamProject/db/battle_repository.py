# db/battle_repository.py
from .connection import get_connection

# def get_all_battles_with_demon_mission():
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   SELECT
#                       b.battle_id,
#                       b.mission_id,
#                       b.demon_id,
#                       d.name AS demon_name,
#                       b.started_at,
#                       b.ended_at,
#                       b.location,
#                       b.outcome,
#                       b.civilian_killed,
#                       b.civilian_injured,
#                       m.objective,
#                       m.status AS mission_status
#                   FROM Battle b
#                            JOIN Demon d ON b.demon_id = d.demon_id
#                            LEFT JOIN Mission m ON b.mission_id = m.mission_id
#                   ORDER BY b.started_at DESC \
#                   """
#             cursor.execute(sql)
#             return cursor.fetchall()
#     finally:
#         conn.close()

def get_all_battles_with_demon_mission():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT b.mission_id, b.battle_seq, b.demon_id, d.name AS demon_name, b.location, b.outcome, b.civilian_killed, b.civilian_injured, m.objective, m.state AS mission_state
                    FROM Battle b
                    JOIN Demon d ON b.demon_id = d.demon_id
                    LEFT JOIN Mission m ON b.mission_id = m.mission_id
                    ORDER BY b.mission_id DESC, b.battle_seq DESC;
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

# def get_battle_by_id(battle_id):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   SELECT
#                       b.*,
#                       d.name AS demon_name,
#                       d.bounty,
#                       m.objective,
#                       m.status AS mission_status
#                   FROM Battle b
#                            JOIN Demon d ON b.demon_id = d.demon_id
#                            LEFT JOIN Mission m ON b.mission_id = m.mission_id
#                   WHERE b.battle_id = %s \
#                   """
#             cursor.execute(sql, (battle_id,))
#             return cursor.fetchone()
#     finally:
#         conn.close()

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
            cursor.execute(sql, (battle_id, battle_seq))    # battle_seq를 추가함
            return cursor.fetchone()
    finally:
        conn.close()

# def get_distribution_for_battle(battle_id):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   SELECT
#                       dist.battle_id,
#                       dist.hunter_id,
#                       h.name AS hunter_name,
#                       h.status,
#                       dist.share_amount,
#                       dist.status AS dist_status
#                   FROM Distribution dist
#                            JOIN Human h ON dist.hunter_id = h.hunter_id
#                   WHERE dist.battle_id = %s \
#                   """
#             cursor.execute(sql, (battle_id,))
#             return cursor.fetchall()
#     finally:
#         conn.close()

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


# def get_distribution_for_battle(battle_id, battle_seq):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                     SELECT rd.reward_id, rd.hunter_id, h.name AS hunter_name, h.status AS hunter_status, rd.distributer_amount, rd.state AS distribution_state, rd.distributed_at
#                     FROM Reward r
#                     JOIN Reward_Distribution rd ON r.reward_id = rd.reward_id
#                     JOIN Hunter h ON rd.hunter_id = h.hunter_id
#                     WHERE r.mission_id = %s AND r.battle_seq = %s
#                 """
#             cursor.execute(sql, (battle_id, battle_seq))    # battle_seq를 추가함...
#                                                             # 아... 뭐지... 위에 동일하게 생긴 부분이랑 뭔가 요상
#                                                             # 일단 확실한건 bettle_seq랑 battel_service.py랑 뭔가 있어서 서비스 파일에서 문제 발생한다는 거임
#                                                             # sql에 이렇게 되있네.....   WHERE r.mission_id = %s AND r.battle_seq = %s
#             return cursor.fetchall()
#     finally:
#         conn.close()

# 뉴 코드 ~~~ ! 
def get_all_battles_with_demon_mission():
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



# def update_distribution_to_done(battle_id, share_amount):
#     """
#     모든 PENDING 분배를 DONE 처리하면서 share_amount 기록.
#     (실제로는 각 헌터별 share_amount를 별도로 계산해서 넣는게 이상적이지만,
#      지금은 동일 금액 분배 가정)
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   UPDATE Distribution
#                   SET share_amount = %s,
#                       status = 'DONE',
#                       distributed_at = NOW()
#                   WHERE battle_id = %s \
#                   """
#             cursor.execute(sql, (share_amount, battle_id))
#         conn.commit()
#     finally:
#         conn.close()

def update_distribution_to_done(battle_id, share_amount, battle_seq):       # 3개가 필요한거 같은데?
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
                """
            cursor.execute(sql, (share_amount, battle_id, battle_seq))      # 수정했으니 서비스 쪽도 봐야할듯..
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
