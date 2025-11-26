# db/hunter_repository.py
from .connection import get_connection


def find_all_humans():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.hunter_id,
                       h.name,
                       h.status,
                       h.team_id,
                       t.team_name,
                       t.region
                FROM Human h
                         LEFT JOIN Team t ON t.team_id = h.team_id
                ORDER BY h.hunter_id
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


def find_human_by_id(hunter_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.hunter_id,
                       h.name,
                       h.status,
                       h.team_id,
                       t.team_name,
                       t.region
                FROM Human h
                         LEFT JOIN Team t ON t.team_id = h.team_id
                WHERE h.hunter_id = %s
                """,
                (hunter_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def find_alive_hunters_by_team(team_id: int):
    """
    팀에 소속된, status != 'DEAD' 인 헌터 목록
    (분배 시 사용할 대상)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.hunter_id,
                       h.name,
                       h.status,
                       h.team_id,
                       t.team_name
                FROM Human h
                         LEFT JOIN Team t ON t.team_id = h.team_id
                WHERE h.team_id = %s
                  AND h.status <> 'DEAD'
                """,
                (team_id,),
            )
            return cursor.fetchall()
    finally:
        conn.close()
