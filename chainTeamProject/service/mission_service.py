# service/mission_service.py
from db import mission_repository, hunter_repository


def get_mission_list(filter_type='all'):
    """
    필터 타입에 따른 미션 목록 반환
    - 'all': 전체 (마감일 긴박한 순)
    - 'in_progress': 진행중 (마감일 긴박한 순)
    - 'success': 완료 (최신순)
    - 'fail': 실패 (최신순)
    - 'completed': SUCCESS + FAIL (전투 기록 등록용)
    """
    if filter_type == 'in_progress':
        return mission_repository.get_in_progress_missions()
    elif filter_type == 'success':
        return mission_repository.get_success_missions()
    elif filter_type == 'fail':
        return mission_repository.get_fail_missions()
    elif filter_type == 'completed':
        return mission_repository.get_completed_missions()
    else:  # 'all'
        return mission_repository.get_all_missions()

def create_mission(objective, created_at, due_date):
    """
    미션 생성
    """
    return mission_repository.create_mission(
        objective, created_at, due_date
    )

def update_mission_state(mission_id, new_state):
    """
    미션 상태 업데이트
    """
    mission_repository.update_mission_status(mission_id, new_state)

def assign_team(mission_id, team_id):
    """
    팀 단위 배정.
    해당 팀에 ALIVE 헌터가 한 명도 없으면 예외 발생.
    """
    hunters = hunter_repository.get_hunters_by_team(team_id)
    active_count = sum(1 for h in hunters if h["status"] == "ALIVE")

    if active_count == 0:
        raise ValueError("해당 팀에 ALIVE 상태인 헌터가 한 명도 없어 미션에 배정할 수 없습니다.")

    # 실제 배정
    mission_repository.assign_team_to_mission(mission_id, team_id)

def get_hunters_by_team(team_id):
    """
    간단히 모든 헌터 조회 후 team_id filter.
    (규모 작으니 편하게)
    """
    all_hunters = hunter_repository.get_all_hunters_with_team()
    return [h for h in all_hunters if h["team_name"] and h["team_name"] != '' and h.get("team_id") == team_id]
