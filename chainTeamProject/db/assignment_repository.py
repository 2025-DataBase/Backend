# db/assignment_repository.py
from .connection import get_connection


def insert_assignment(mission_id: int, team_id: int, assignment_status: str):
    """
    MissionAssignment 한 건 INSERT
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  INSERT INTO MissionAssignment (
                      mission_id,
                      team_id,
                      assignment_status
                  )
                  VALUES (%s, %s, %s) \
                  """
            cursor.execute(sql, (mission_id, team_id, assignment_status))
        conn.commit()
    finally:
        conn.close()


def find_assignment_by_mission_and_team(mission_id: int, team_id: int):
    """
    특정 (mission_id, team_id) 조합이 이미 있는지 확인
    UNIQUE uk_mission_team 검사용
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      assignment_id,
                      mission_id,
                      team_id,
                      assignment_status,
                      assigned_at
                  FROM MissionAssignment
                  WHERE mission_id = %s
                    AND team_id = %s \
                  """
            cursor.execute(sql, (mission_id, team_id))
            return cursor.fetchone()
    finally:
        conn.close()


def find_assignments_by_mission(mission_id: int):
    """
    특정 미션에 배정된 팀 목록 조회
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
                      ma.assigned_at,
                      t.team_name
                  FROM MissionAssignment ma
                           JOIN Team t ON ma.team_id = t.team_id
                  WHERE ma.mission_id = %s
                  ORDER BY ma.assigned_at DESC \
                  """
            cursor.execute(sql, (mission_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def find_all_assignments():
    """
    전체 임무 배정 목록 (Mission + Team 조인해서 목록용으로 사용)
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
                      ma.assigned_at,
                      m.objective AS mission_title,
                      t.team_name
                  FROM MissionAssignment ma
                           JOIN Mission m ON ma.mission_id = m.mission_id
                           JOIN Team t    ON ma.team_id    = t.team_id
                  ORDER BY ma.assigned_at DESC \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
