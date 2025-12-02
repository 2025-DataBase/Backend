# service/battle_service.py
from db import battle_repository

def list_battles():
    return battle_repository.get_all_battles_with_demon_mission()

def get_battle_detail_with_distribution(battle_id):
    battle = battle_repository.get_battle_by_id(battle_id)
    distributions = battle_repository.get_distribution_for_battle(battle_id)
    return battle, distributions

def distribute_bounty(battle_id):
    """
    분배/보상 처리를 DB 저장 프로시저 distribute_bounty에 위임.
    프로시저가 내부에서 각종 검증 및 Account/Mission/Distribution 업데이트를 수행한다.
    """
    share, n = battle_repository.call_distribute_bounty(battle_id)
    return share, n
