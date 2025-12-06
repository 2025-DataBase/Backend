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


def distribute_bounty(mission_id, battle_seq):
    """
    현상금 분배 - Python 코드로 처리
    """
    battle = battle_repository.get_battle_by_id(mission_id, battle_seq)
    if not battle:
        raise ValueError("존재하지 않는 전투입니다.")

    if battle["outcome"] != "HUNTER_WIN":
        raise ValueError("HUNTER_WIN 전투만 분배할 수 있습니다.")

    # Reward 조회
    reward = battle_repository.get_reward_for_battle(mission_id, battle_seq)
    if not reward:
        raise ValueError("해당 전투에 대한 Reward가 없습니다.")

    # Reward_Distribution에서 IN_PROGRESS 상태이고 ALIVE인 헌터 조회
    distributions = battle_repository.get_distribution_for_battle(mission_id, battle_seq)
    active_participants = [
        d for d in distributions 
        if d.get('distribution_state') == 'IN_PROGRESS' 
        and d.get('hunter_status') == 'ALIVE'
    ]

    n = len(active_participants)
    if n == 0:
        raise ValueError("전투에 참여한 ALIVE 헌터가 없어 보상을 지급할 수 없습니다.")

    # 이미 분배된 헌터가 있는지 확인
    done_count = sum(1 for d in distributions if d.get('distribution_state') == 'SUCCESS')
    if done_count > 0:
        raise ValueError("이미 보상 지급이 완료된 전투입니다.")

    total_amount = reward["total_amount"]
    share = total_amount // n

    # Account 업데이트 및 Reward_Distribution 상태 변경
    # 각 헌터의 계좌에 분배 금액 추가
    for d in active_participants:
        hunter_id = d["hunter_id"]
        # 계좌가 없으면 생성
        account_repository.ensure_account_exists(hunter_id)
        # 계좌 잔액 업데이트
        account_repository.add_income(
            hunter_id,
            share,
            f"전투 {mission_id}-{battle_seq} 보상 분배"
        )

    # Reward_Distribution 상태 SUCCESS + share_amount 기록 (IN_PROGRESS 상태인 헌터들만)
    battle_repository.update_distribution_to_done(mission_id, share, battle_seq)

    return share, n


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
            
            # 등급과 현상금 재계산
            from service.demon_service import calculate_grade_and_bounty
            grade, bounty, score = calculate_grade_and_bounty(new_killed, new_injured)
            
            # Demon 테이블 업데이트 (민간인 피해 추가 + 등급/현상금 재계산)
            demon_repository.update_demon_totals_and_risk(
                demon_id, new_killed, new_injured, grade, bounty
            )
    else:
        # DEMON_WIN이거나 다른 경우에도 악마 위험도 업데이트 (Battle 기록 반영)
        battle_killed, battle_injured = demon_repository.recalc_totals_from_battles(demon_id)
        
        # 등급과 현상금 재계산
        from service.demon_service import calculate_grade_and_bounty
        grade, bounty, score = calculate_grade_and_bounty(battle_killed, battle_injured)
        
        # Demon 테이블 업데이트
        demon_repository.update_demon_totals_and_risk(
            demon_id, battle_killed, battle_injured, grade, bounty
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