# service/battle_service.py
from typing import List, Dict, Optional


from db import (
    battle_repository,
    distribution_repository,
    account_repository,
)

from service import mission_service


def get_battle_by_id(battle_id: int) -> Optional[Dict]:
    row = battle_repository.find_battle_by_id(battle_id)
    if not row:
        return None

    # 총 보상금(합계)을 같이 내려주면 템플릿에서도 사용 가능
    total_reward = battle_repository.sum_bounty_by_battle(battle_id)

    return {
        "id": row["battle_id"],
        "mission_id": row["mission_id"],
        "demon_id": row["demon_id"],
        "demon_name": row["demon_name"],
        "location": row["location"],
        "started_at": row["started_at"],
        "ended_at": row["ended_at"],
        "outcome": row["outcome"],
        "civilian_killed": row["civilian_killed"],
        "civilian_injured": row["civilian_injured"],
        "reward": total_reward,   # claim 화면에서 battle.reward 로 사용
    }


def get_battles(demon_id: Optional[int] = None) -> List[Dict]:
    """
    전투 목록 조회
    - demon_id 가 None 이면 전체 전투
    - demon_id 가 있으면 해당 악마와 관련된 전투만
    """
    if demon_id is None:
        rows = battle_repository.find_all_battles()
    else:
        rows = battle_repository.find_battles_by_demon(demon_id)

    result: List[Dict] = []
    for r in rows:
        result.append(
            {
                "id": r["battle_id"],
                "demon_name": r["demon_name"],
                "hunter_name": r.get("hunter_name"),
                "location": r["location"],
                "outcome": r["outcome"],
                "civilian_killed": r["civilian_killed"],
                "civilian_injured": r["civilian_injured"],
                "reward": r.get("reward_amount") or r.get("amount") or 0,
                "is_paid": r.get("is_paid", 0),
            }
        )
    return result

def claim_reward(battle_id: int) -> bool:
    """
    전투 보상을 분배하고 Account/Distribution 갱신.
    단, 이 전투가 속한 임무의 MissionAssignment 중
    하나라도 DONE / CANCELLED 인 것이 있을 때만 수행.
    """
    # 0) 임무 배정 상태 확인
    if not mission_service.is_distributable_battle(battle_id):
        # 분배 불가
        return False

    # 1) 전투 기본 정보
    battle = battle_repository.find_battle_by_id(battle_id)
    if not battle:
        return False

    total_reward = battle["reward"]  # Demon.bounty 기준으로 설정해놨겠지
    if total_reward is None:
        total_reward = 0

    # 2) 전투에 참여한 팀 & 헌터 목록
    hunters = battle_repository.find_hunters_for_battle(battle_id)
    if not hunters:
        return False

    # 살아있는 헌터만 분배 대상
    alive_hunters = [h for h in hunters if h["status"] != "DEAD"]
    if not alive_hunters:
        return False

    # 팀 수 / 팀별 인원 수 계산
    team_ids = {h["team_id"] for h in alive_hunters}
    team_count = len(team_ids) if team_ids else 1

    share_per_team = total_reward // team_count

    # 팀별 인원
    hunters_by_team = {}
    for h in alive_hunters:
        hunters_by_team.setdefault(h["team_id"], []).append(h)

    # 3) 분배 + Account 업데이트
    for team_id, members in hunters_by_team.items():
        per_hunter = share_per_team // len(members)
        for h in members:
            hunter_id = h["hunter_id"]

            # Distribution 기록
            distribution_repository.insert_distribution(
                battle_id=battle_id,
                hunter_id=hunter_id,
                share_amount=per_hunter,
                is_dead_at_battle=(h["status"] == "DEAD"),
                status="DONE",
            )

            # Account 업데이트 (입금)
            account_repository.add_income(
                hunter_id=hunter_id,
                amount=per_hunter,
                desc=f"[전투 {battle_id}] 보상 분배",
            )

    # 4) 이 전투에 대한 BountyClaim 정리 (선택) + Battle 상태 변경 등
    #    필요하면 추가 로직 넣기 (예: 이미 분배된 전투는 다시 분배 못 하도록 플래그 저장 등)

    return True

def get_battles_for_hunter(hunter_id: int):
    """
    헌터 상세 화면에서 사용할,
    '이 헌터가 참여한 전투 목록' 조회용 서비스 함수.
    """
    rows = battle_repository.find_battles_for_hunter(hunter_id)
    result = []

    for r in rows:
        reward = r.get("reward_amount", 0)

        result.append(
            {
                "id": r["battle_id"],
                "battle_id": r["battle_id"],            # 혹시 템플릿에서 battle_id로 쓸 수도 있으니까 같이 줌
                "mission_title": r.get("mission_title"),
                "demon_name": r.get("demon_name"),
                "location": r.get("location"),
                "outcome": r.get("outcome"),
                "started_at": r.get("started_at"),
                "ended_at": r.get("ended_at"),
                "civilian_killed": r.get("civilian_killed", 0),
                "civilian_injured": r.get("civilian_injured", 0),
                "reward": reward,                       # 💡 템플릿에서 "{:,}".format(b.reward) 쓰면 여기 값 사용
            }
        )

    return result