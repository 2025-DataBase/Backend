# service/mission_service.py
from db import mission_repository, hunter_repository


def get_mission_list(active_only=True):
    if active_only:
        return mission_repository.get_active_missions()
    return mission_repository.get_all_missions()

def create_mission(team_id, objective, created_at, due_date):          # target_desc는 테이블에 없고... 뭐 작성되도 없어서 작동 안해서 의미없음
    return mission_repository.create_mission(
        team_id, objective, created_at, due_date
    )

def assign_team(mission_id, team_id):
    """
    팀 단위 배정.
    해당 팀에 ACTIVE 헌터가 한 명도 없으면 예외 발생.
    """
    hunters = hunter_repository.get_hunters_by_team(team_id)
    active_count = sum(1 for h in hunters if h["status"] == "ALIVE")        # ALIVE로 수정함

    if active_count == 0:
        raise ValueError("해당 팀에 ACTIVE 상태인 헌터가 한 명도 없어 미션에 배정할 수 없습니다.")

    # 실제 배정
    mission_repository.assign_team_to_mission(mission_id, team_id)

def get_hunters_by_team(team_id):
    """
    간단히 모든 헌터 조회 후 team_id filter.
    (규모 작으니 편하게)
    """
    all_hunters = hunter_repository.get_all_hunters_with_team()
    return [h for h in all_hunters if h["team_name"] and h["team_name"] != '' and h.get("team_id") == team_id]
