# service/battle_service.py
from db import battle_repository, mission_repository, account_repository

def list_battles():
    return battle_repository.get_all_battles_with_demon_mission()

def get_battle_detail_with_distribution(battle_id):
    battle = battle_repository.get_battle_by_id(battle_id)
    distributions = battle_repository.get_distribution_for_battle(battle_id)
    return battle, distributions

def distribute_bounty(battle_id):
    """
    1. battle 읽기
    2. outcome = HUMAN_WIN 인지 확인
    3. Distribution에서 참여 헌터 목록 가져오기
    4. n분의 1로 분배하여 Account 업데이트
    5. Distribution 상태 DONE
    6. Mission 상태 SUCCESS 로 변경
    """
    battle = battle_repository.get_battle_by_id(battle_id)
    if not battle:
        raise ValueError("존재하지 않는 전투입니다.")

    if battle["outcome"] != "HUMAN_WIN":
        raise ValueError("HUMAN_WIN 전투만 분배할 수 있습니다.")

    demon_bounty = battle["bounty"]
    mission_id = battle["mission_id"]

    distributions = battle_repository.get_distribution_for_battle(battle_id)
    active_participants = [d for d in distributions if d["status"] == "ACTIVE"]

    n = len(active_participants)
    if n == 0:
        raise ValueError("참여한 ACTIVE 헌터가 없어 분배할 수 없습니다.")

    share = demon_bounty // n

    # 4. Account 업데이트
    for d in active_participants:
        hunter_id = d["hunter_id"]
        account_repository.add_income(
            hunter_id,
            share,
            f"전투 {battle_id} 보상 분배"
        )

    # 5. Distribution 상태 DONE + share_amount 기록
    battle_repository.update_distribution_to_done(battle_id, share)

    # 6. 미션 상태 SUCCESS로 변경 (DONE 의미)
    if mission_id is not None:
        mission_repository.update_mission_status(mission_id, "SUCCESS")

    return share, n
