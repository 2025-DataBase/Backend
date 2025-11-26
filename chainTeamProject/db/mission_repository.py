# db/mission_repository.py
from .connection import get_connection


def find_all_missions():
    """
    Mission + Team 조인해서 목록 조회
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT m.mission_id,
                       m.objective,
                       m.target_desc,
                       m.status,
                       m.created_at,
                       m.due_date,
                       t.team_name
                FROM Mission m
                         JOIN Team t ON m.team_id = t.team_id
                ORDER BY m.created_at DESC
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


def find_mission_by_id(mission_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT m.mission_id,
                       m.objective,
                       m.target_desc,
                       m.status,
                       m.created_at,
                       m.due_date,
                       t.team_name
                FROM Mission m
                         JOIN Team t ON m.team_id = t.team_id
                WHERE m.mission_id = %s
                """,
                (mission_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()

def find_assignments_for_battle(battle_id: int):
    """
    Battle → Mission → MissionAssignment를 타고,
    해당 전투가 속한 임무의 배정 상태들을 가져온다.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      ma.assignment_id,
                      ma.mission_id,
                      ma.team_id,
                      ma.assignment_status,
                      ma.assigned_at
                  FROM Battle b
                           JOIN MissionAssignment ma
                                ON ma.mission_id = b.mission_id
                  WHERE b.battle_id = %s \
                  """
            cursor.execute(sql, (battle_id,))
            return cursor.fetchall()
    finally:
        conn.close()