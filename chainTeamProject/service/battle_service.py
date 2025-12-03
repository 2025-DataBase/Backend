# service/battle_service.py
from db import battle_repository, mission_repository, account_repository

# def list_battles():
#     return battle_repository.get_all_battles_with_demon_mission()
# def list_battles():
#     battles = battle_repository.get_all_battles_with_demon_mission()
def list_battles():
    battles = battle_repository.get_all_battles_with_demon_mission()

    # for b in battles:
    #     distributions = battle_repository.get_distribution_for_battle(
    #         b['mission_id'], b['battle_seq']
    #     )
    #     b['active_hunters'] = sum(1 for d in distributions if d['state'] == 'IN_PROGRESS')
    for b in battles:
        distributions = battle_repository.get_distribution_for_battle(b['mission_id'], b['battle_seq'])
        b['active_hunters'] = sum(1 for d in distributions if d['distribution_state'] == 'IN_PROGRESS')

    return battles

# 우씌 잠만... 스파게티 코드 됨 .... 이게 문제가 아닌가? html ㄱㄱ


    # # 각 배틀별 active 헌터 수 계산
    # for b in battles:
    #     distributions = battle_repository.get_distribution_for_battle(b['mission_id'], b['battle_seq'])
    #     b['active_hunters'] = sum(1 for d in distributions if d['state'] == 'IN_PROGRESS')

    # return battles


def get_battle_detail_with_distribution(battle_id):
    battle = battle_repository.get_battle_by_id(battle_id)
    distributions = battle_repository.get_distribution_for_battle(battle_id)
    return battle, distributions

def distribute_bounty(battle_id, battle_seq):
    """
    1. battle 읽기
    2. outcome = HUMAN_WIN 인지 확인
    3. Distribution에서 참여 헌터 목록 가져오기
    4. n분의 1로 분배하여 Account 업데이트
    5. Distribution 상태 DONE
    6. Mission 상태 SUCCESS 로 변경
    """
    battle = battle_repository.get_battle_by_id(battle_id, battle_seq)
    if not battle:
        raise ValueError("존재하지 않는 전투입니다.")

    if battle["outcome"] != "HUNTER_WIN":
        raise ValueError("HUNTER_WIN 전투만 분배할 수 있습니다.")    # HUMAN에서 HUNTER로 교체

    # demon_bounty = battle["bounty"]      demon에 bounty가 없는뎅? vscode 고양이 귀엽다
    mission_id = battle["mission_id"]

    distributions = battle_repository.get_distribution_for_battle(battle_id, battle_seq)
    # active_participants = [d for d in distributions if d["state"] == "IN_PROGRESS"]     # status에서 state로 
                        # 잠만 .... active가 맞나? 에헤이 강아지 이쁘다 ... 굿!
                        # -- 돈이 지급중인지, 지급 완료 되었는지 나타내는 state가 추가되었습니다.  `state` ENUM('IN_PROGRESS', 'SUCCESS') NOT NULL , 라는데?
                        # 일단 IN_PROGRESS로 변경해보자..... 스읍... 맞나?  CALL 911~ 코드에 불이 났어~~

    active_participants = [d for d in distributions if d["distribution_state"] == "IN_PROGRESS"]



    n = len(active_participants)
    if n == 0:
        raise ValueError("참여한 ACTIVE 헌터가 없어 분배할 수 없습니다.")

    # share = demon_bounty // n         위에 내가 날려서 일단 주석 처리
    # reward = battle_repository.get_reward_for_battle(battle_id, share, state="SUCCESS")
    reward = battle_repository.get_reward_for_battle(mission_id, battle_seq)
    total_amount = reward["total_amount"]
    share = total_amount // n
    # 새롭게 반영해 본건데 맞으려나?
    # 이게 맞나?


    # 4. Account 업데이트
    for d in active_participants:
        hunter_id = d["hunter_id"]
        account_repository.add_income(
            hunter_id,
            share,
            f"전투 {battle_id} 보상 분배"
        )

    # 5. Distribution 상태 DONE + share_amount 기록
    # battle_repository.update_distribution_to_done(battle_id, share, state="SUCCESS")        # 'IN_PROGRESS', 'SUCCESS' 둘 중 하나요, 그리고 요소 3개용
    battle_repository.update_distribution_to_done(battle_id, share, battle_seq)

    # 6. 미션 상태 SUCCESS로 변경 (DONE 의미)
    # if mission_id is not None:
    #     mission_repository.update_mission_status(mission_id, "SUCCESS")          # 'PLANNED', 'IN_PROGRESS', 'SUCCESS', 'FAIL' 4개 중 하나입니다.

    # return share, n


    # 6. 미션 상태 SUCCESS로 변경 (DONE 의미)
    if mission_id is not None:
        # 문제 4 핵심: Mission 상태를 바로 SUCCESS로 바꿔버림
        # 현재 로직:
        #   - 단일 배틀이 HUNTER_WIN이면 바로 SUCCESS 처리
        # 잠재적 문제:
        #   - 하나의 Mission에 여러 Battle이 존재할 수 있음
        #   - 모든 Battle이 완료되지 않았는데 Mission을 SUCCESS로 바꾸면 잘못된 상태가 됨
        mission_repository.update_mission_status(mission_id, "SUCCESS")  
        # → 주석으로 표시:
        # TODO: Mission 상태 업데이트를 '모든 배틀 완료 후'로 변경 필요
        # ex) 해당 mission_id의 모든 battle outcome 확인 후, 모두 HUNTER_WIN이면 SUCCESS, 
        #     하나라도 DEMON_WIN이면 FAIL, 진행중인 배틀이 있으면 IN_PROGRESS 유지


