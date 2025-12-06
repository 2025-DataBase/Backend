# db/mission_repository.py
from .connection import get_connection

# def get_active_missions():
#     """
#     SUCCESS(=DONE) 아닌 미션 목록
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   SELECT
#                       m.mission_id,
#                       m.objective,
#                       m.state,
#                       m.created_at,
#                       m.due_date,
#                       t.team_name
#                   FROM Mission m
#                            JOIN Team t ON m.team_id = t.team_id
#                   WHERE m.state != 'SUCCESS'
#                   ORDER BY m.created_at DESC \
#                   """           # m.target_desc, 해당 부분 삭제, status에서 state 바뀜
#             cursor.execute(sql)
#             return cursor.fetchall()
#     finally:
#         conn.close()

def get_active_missions():
    """
    SUCCESS 아닌 미션 목록 - 마감일 긴박한 순으로 정렬
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    WHERE m.state != 'SUCCESS'
                    ORDER BY m.due_date ASC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

# def get_all_missions():
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   SELECT
#                       m.mission_id,
#                       m.objective,
                      
#                       m.state,
#                       m.created_at,
#                       m.due_date,
#                       t.team_name
#                   FROM Mission m
#                            JOIN Team t ON m.team_id = t.team_id
#                   ORDER BY m.created_at DESC \
#                   """
#             cursor.execute(sql)
#             return cursor.fetchall()
#     finally:
#         conn.close()

def get_all_missions():
    """
    전체 미션 목록 - 마감일 긴박한 순으로 정렬
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    ORDER BY m.due_date ASC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

# def create_mission(team_id, objective, 
#                    created_at, due_date):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   INSERT INTO Mission(
#                       team_id, objective, 
#                       state, created_at, due_date
#                   ) VALUES (%s, %s, %s, 'PLANNED', %s, %s) \
#                   """
#             cursor.execute(sql, (team_id, objective, 
#                                  created_at, due_date))
#             mission_id = cursor.lastrowid
#         conn.commit()
#         return mission_id
#     finally:
#         conn.close()

def create_mission(objective, created_at, due_date):
    """
    미션 생성
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    INSERT INTO Mission(objective, state, created_at, due_date) 
                    VALUES (%s, 'PLANNED', %s, %s)
                """
            cursor.execute(sql, (objective, created_at, due_date))
            mission_id = cursor.lastrowid
        conn.commit()
        return mission_id
    finally:
        conn.close()

# def assign_team_to_mission(mission_id, team_id):
#     """
#     MissionAssignment에 팀 배정 (중복 배정은 UNIQUE로 막힘)
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                   INSERT INTO MissionAssignment(
#                       mission_id, team_id, assignment_status
#                   ) VALUES (%s, %s, 'PLANNED') \
#                   """
#             cursor.execute(sql, (mission_id, team_id))
#         conn.commit()
#     finally:
#         conn.close()

def assign_team_to_mission(mission_id, team_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    INSERT INTO Mission_assignment (mission_id, team_id) VALUES (%s, %s)
                """
            cursor.execute(sql, (mission_id, team_id))
        conn.commit()
    finally:
        conn.close()

        

def update_mission_status(mission_id, new_state):
    """
    미션 상태 업데이트
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           UPDATE Mission
                           SET state = %s
                           WHERE mission_id = %s
                           """, (new_state, mission_id))
        conn.commit()
    finally:
        conn.close()

def get_mission_team_id(mission_id):
    """
    미션에 할당된 팀 ID 조회
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT team_id 
                FROM Mission_assignment 
                WHERE mission_id = %s 
                LIMIT 1
            """
            cursor.execute(sql, (mission_id,))
            result = cursor.fetchone()
            return result['team_id'] if result else None
    finally:
        conn.close()

def get_completed_missions():
    """
    완료된 미션 (SUCCESS + FAIL) - 최신순
    분배 완료된 전투가 있는 미션은 제외
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT DISTINCT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    WHERE m.state IN ('SUCCESS', 'FAIL')
                      AND m.mission_id NOT IN (
                          -- 분배 완료된 전투가 있는 미션 제외
                          SELECT DISTINCT r.mission_id
                          FROM Reward r
                          JOIN Reward_Distribution rd ON r.reward_id = rd.reward_id
                          WHERE rd.state = 'SUCCESS'
                      )
                    ORDER BY m.due_date DESC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_in_progress_missions():
    """
    진행중인 미션 (IN_PROGRESS만) - 마감일 긴박한 순
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    WHERE m.state = 'IN_PROGRESS'
                    ORDER BY m.due_date ASC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_success_missions():
    """
    완료된 미션 (SUCCESS) - 최신순
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    WHERE m.state = 'SUCCESS'
                    ORDER BY m.due_date DESC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_fail_missions():
    """
    실패한 미션 (FAIL) - 최신순
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT m.mission_id, m.objective, m.state, m.created_at, m.due_date, 
                           t.team_name
                    FROM Mission m
                    LEFT JOIN Mission_assignment ma ON m.mission_id = ma.mission_id
                    LEFT JOIN Team t ON ma.team_id = t.team_id
                    WHERE m.state = 'FAIL'
                    ORDER BY m.due_date DESC
                """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
