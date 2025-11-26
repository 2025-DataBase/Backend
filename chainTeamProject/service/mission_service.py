# service/mission_service.py
from typing import List, Dict, Optional

from db import mission_repository, assignment_repository, hunter_repository, team_repository
import pymysql

def get_missions() -> List[Dict]:
    rows = mission_repository.find_all_missions()
    result: List[Dict] = []
    for r in rows:
        result.append(
            {
                "id": r["mission_id"],
                "title": r["objective"],
                "target_desc": r["target_desc"],
                "status": r["status"],
                "created_at": r["created_at"],
                "due_date": r["due_date"],
                "team_name": r["team_name"],
            }
        )
    return result


def get_mission_by_id(mission_id: int) -> Optional[Dict]:
    row = mission_repository.find_mission_by_id(mission_id)
    if not row:
        return None

    assignments = assignment_repository.find_assignments_by_mission(mission_id)
    assigned_teams = [
        {
            "assignment_id": a["assignment_id"],
            "team_id": a["team_id"],
            "team_name": a["team_name"],
            "status": a["assignment_status"],
            "assigned_at": a["assigned_at"],
        }
        for a in assignments
    ]

    return {
        "id": row["mission_id"],
        "title": row["objective"],
        "objective": row["objective"],
        "target_desc": row["target_desc"],
        "status": row["status"],
        "created_at": row["created_at"],
        "due_date": row["due_date"],
        "team_name": row["team_name"],
        "assigned_teams": assigned_teams,
    }


def get_hunters_for_mission(mission_id: int) -> List[Dict]:
    """
    미션과 연결된 전투(Battle) → BountyClaim → Human 으로 참여 헌터 조회.
    (이미 기존에 쓰던 쿼리가 있다면 그대로 사용해도 됨)
    """
    # 단순하게는 hunter_repository.find_all_humans() 를 써도 되고,
    # 필요하면 별도 repository 함수로 교체 가능.
    return []

def get_assignment_form_data() -> Dict[str, List[Dict]]:
    """
    임무 할당 폼에서 사용할 선택 목록 데이터:
    - missions: 선택 가능한 임무 목록
    - teams   : 선택 가능한 팀 목록
    """
    missions_raw = mission_repository.find_all_missions()
    teams_raw = team_repository.find_all_teams()

    missions: List[Dict] = []
    for m in missions_raw:
        missions.append(
            {
                "id": m["mission_id"],
                "title": m["objective"],     # 화면에 보이는 제목
                "status": m["status"],
                "due_date": m["due_date"],
            }
        )

    teams: List[Dict] = []
    for t in teams_raw:
        teams.append(
            {
                "id": t["team_id"],
                "name": t["team_name"],
                "region": t["region"],
            }
        )

    return {
        "missions": missions,
        "teams": teams,
    }



def create_assignment(mission_id: int, team_id: int, assignment_status: str = "PLANNED") -> bool:
    """
    MissionAssignment 테이블에 한 건 INSERT.
    - 동일 (mission_id, team_id)는 UNIQUE 제약이 있어서,
      이미 있으면 DB IntegrityError가 발생한다.
    - 여기서 미리 체크하고, 혹시 에러가 나도 False 리턴으로 막아준다.
    """

    # 1) 이미 같은 조합이 있는지 먼저 조회해서 막기 (권장)
    existing = assignment_repository.find_assignment_by_mission_and_team(mission_id, team_id)
    if existing:
        # 이미 배정된 조합이면 그냥 아무 것도 안 하고 False 반환
        return False

    # 2) 혹시 동시성 / 예외 상황 대비해서 try/except 로 한 번 더 안전장치
    try:
        assignment_repository.insert_assignment(
            mission_id=mission_id,
            team_id=team_id,
            assignment_status=assignment_status,
        )
        return True
    except pymysql.err.IntegrityError:
        # 여기까지 왔다는 건 UNIQUE 제약에 걸렸다는 뜻이니,
        # 서비스 레벨에서는 조용히 False만 돌려주자.
        return False

def get_assignments() -> List[Dict]:
    """
    MissionAssignment 전체 목록 조회.
    assignment_repository.find_all_assignments() 가
    Mission + Team 을 JOIN 해서 넘겨준다는 전제.
    """
    rows = assignment_repository.find_all_assignments()
    result: List[Dict] = []

    for r in rows:
        result.append(
            {
                "assignment_id": r["assignment_id"],
                "mission_id": r["mission_id"],
                # Mission.objective 를 제목처럼 사용
                "mission_title": r.get("mission_title") or r.get("objective"),
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "status": r["assignment_status"],
                "assigned_at": r["assigned_at"],
            }
        )

    return result

def is_distributable_battle(battle_id: int) -> bool:
    """
    battle_id 기준으로 연결된 MissionAssignment 들을 조회해서
    상태가 DONE 또는 CANCELLED 인 것이 하나라도 있으면
    '보상 분배 가능'으로 본다.
    """
    rows = mission_repository.find_assignments_for_battle(battle_id)
    if not rows:
        # 임무에 연결되지 않았거나, 아직 배정이 안 되어 있으면 분배 X
        return False

    for r in rows:
        status = r["assignment_status"]
        if status in ("DONE", "CANCELLED"):
            return True

    return False

def find_assignment_by_mission_and_team(mission_id: int, team_id: int):
    """
    특정 (mission_id, team_id) 조합이 이미 존재하는지 확인
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

