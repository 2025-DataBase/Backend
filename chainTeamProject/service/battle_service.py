# service/battle_service.py
from db import battle_repository, mission_repository, account_repository

def list_battles():
    battles = battle_repository.get_all_battles_with_demon_mission()
    for b in battles:
        distributions = battle_repository.get_distribution_for_battle(b['mission_id'], b['battle_seq'])
        b['active_hunters'] = sum(1 for d in distributions if d['distribution_state'] == 'IN_PROGRESS')
        # 분배 완료 여부 확인 (SUCCESS 상태가 하나라도 있으면 분배 완료)
        b['distributed'] = any(d['distribution_state'] == 'SUCCESS' for d in distributions)
    return battles


def get_battle_detail_with_distribution(battle_id):
    battle = battle_repository.get_battle_by_id(battle_id)
    distributions = battle_repository.get_distribution_for_battle(battle_id)
    return battle, distributions



def create_battle_record(mission_id, demon_id, outcome, location, civilian_killed, civilian_injured,
                         participant_hunter_ids, dead_hunter_ids):
    """
    전투 기록 생성 - 완전판
    participant_hunter_ids: 전투에 참여한 헌터 ID 리스트
    dead_hunter_ids: 사망한 헌터 ID 리스트
    """
    from db import demon_repository, mission_repository
    
    # 다음 battle_seq 번호 가져오기
    battle_seq = battle_repository.get_next_battle_seq(mission_id)

    # Battle 레코드 생성
    battle_repository.create_battle(
        mission_id, battle_seq, demon_id, outcome, location,
        civilian_killed, civilian_injured
    )

    # HUNTER_WIN이면 악마 상태를 DEAD로 변경하고 민간인 피해를 바로 추가
    if outcome == 'HUNTER_WIN':
        battle_repository.update_demon_status_to_dead(demon_id)
        
        # 현재 악마의 민간인 피해 수치 가져오기
        current_demon = demon_repository.get_demon_by_id(demon_id)
        
        if current_demon:
            # 민간인 피해를 바로 추가
            new_killed = current_demon['civilian_kills'] + civilian_killed
            new_injured = current_demon['civilian_injuries'] + civilian_injured
            
            # 등급/현상금 재계산
            from service.demon_service import calculate_grade_and_bounty
            grade, bounty, score = calculate_grade_and_bounty(new_killed, new_injured)
            
            # Demon 테이블 업데이트 (민간인 피해 추가 + 등급/현상금 재계산)
            demon_repository.update_demon_totals_and_risk(
                demon_id, new_killed, new_injured, grade, bounty
            )
    else:
        # DEMON_WIN이거나 다른 경우에도 악마 위험도 업데이트 (Battle 기록 반영)
        # 현재 악마의 민간인 피해 수치 가져오기
        current_demon = demon_repository.get_demon_by_id(demon_id)
        
        if current_demon:
            # 현재 전투의 민간인 피해를 바로 추가 (Battle 테이블 합계가 아닌 현재 전투만)
            new_killed = current_demon['civilian_kills'] + civilian_killed
            new_injured = current_demon['civilian_injuries'] + civilian_injured
            
            # 등급/현상금 재계산
            from service.demon_service import calculate_grade_and_bounty
            grade, bounty, score = calculate_grade_and_bounty(new_killed, new_injured)
            
            # Demon 테이블 업데이트 (민간인 피해 추가 + 등급/현상금 재계산)
            demon_repository.update_demon_totals_and_risk(
                demon_id, new_killed, new_injured, grade, bounty
            )

    # 참여한 헌터들의 전투 참여 기록 생성
    for hunter_id in participant_hunter_ids:
        # 사망자 목록에 있으면 DEAD, 없으면 ALIVE
        status = 'DEAD' if hunter_id in dead_hunter_ids else 'ALIVE'
        battle_repository.create_battle_participation(mission_id, battle_seq, hunter_id, status)

    # 사망한 헌터들의 상태를 DEAD로 변경
    for hunter_id in dead_hunter_ids:
        battle_repository.update_hunter_status_to_dead(hunter_id)

    # HUNTER_WIN이고 참여 헌터가 있으면 Reward와 Reward_Distribution 생성
    if outcome == 'HUNTER_WIN' and len(participant_hunter_ids) > 0:
        # 미션의 팀 ID 가져오기
        team_id = mission_repository.get_mission_team_id(mission_id)
        if team_id:
            # 악마의 현상금 가져오기 (업데이트된 현상금)
            current_demon = demon_repository.get_demon_by_id(demon_id)
            bounty = current_demon['bounty'] if current_demon else 0
            
            # Reward 생성
            reward_id = battle_repository.create_reward(mission_id, battle_seq, team_id, bounty)
            
            # Reward_Distribution 생성 (사망자가 아닌 헌터만)
            alive_hunter_ids = [hid for hid in participant_hunter_ids if hid not in dead_hunter_ids]
            for hunter_id in alive_hunter_ids:
                battle_repository.create_reward_distribution(reward_id, hunter_id)

    return battle_seq

def distribute_bounty(mission_id, battle_seq):
    """
    현상금 분배 - SQL 프로시저를 사용하여 처리
    """
    try:
        # SQL 프로시저 호출
        result = battle_repository.call_distribute_bounty_procedure(mission_id, battle_seq)
        if result:
            share = result.get('share', 0)
            participant_count = result.get('participant_count', 0)
            return share, participant_count
        else:
            raise ValueError("프로시저 실행 결과를 받을 수 없습니다.")
    except Exception as e:
        # 프로시저에서 발생한 오류를 그대로 전달
        raise ValueError(str(e))