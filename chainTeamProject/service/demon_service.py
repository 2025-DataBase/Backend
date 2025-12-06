# service/demon_service.py
from db import demon_repository

def calculate_grade_and_bounty(killed_total, injured_total):
    score = killed_total * 10 + injured_total * 3

    if score < 50:
        grade = 'C'
        bounty = 200_000
    elif score < 150:
        grade = 'B'
        bounty = 500_000
    elif score < 300:
        grade = 'A'
        bounty = 800_000
    elif score < 600:
        grade = 'S'
        bounty = 1_200_000
    else:
        grade = 'SS'
        bounty = 1_500_000

    return grade, bounty, score

def register_demon(name, civilian_kills, civilian_injuries):
    """
    악마 등록 - 등급과 현상금 자동 계산
    """
    grade, bounty, score = calculate_grade_and_bounty(civilian_kills, civilian_injuries)
    demon_id = demon_repository.create_demon(name, grade, bounty, civilian_kills, civilian_injuries)
    
    return {
        'demon_id': demon_id,
        'name': name,
        'grade': grade,
        'bounty': bounty,
        'civilian_kills': civilian_kills,
        'civilian_injuries': civilian_injuries,
        'score': score
    }

def get_demon_risk_list():
    """
    1. Battle 기준으로 각 Demon의 killed/injured 합계를 계산하고
    2. Demon 테이블의 원본 값과 비교하여 더 큰 값 사용
    3. grade, bounty를 재계산해서 Demon 테이블에 반영
    4. 화면에는 score까지 같이 내려줌
    """
    demons = demon_repository.get_all_demons()
    result = []

    for d in demons:
        demon_id = d["demon_id"]
        
        # Battle 테이블에서 집계한 값
        battle_killed, battle_injured = demon_repository.recalc_totals_from_battles(demon_id)
        
        # Demon 테이블 원본 값과 Battle 집계 값 중 더 큰 값 사용
        # (Battle 기록이 없으면 원본 값 유지, Battle 기록이 있으면 Battle 값 우선)
        killed_total = max(d["civilian_kills"], battle_killed)
        injured_total = max(d["civilian_injuries"], battle_injured)
        
        # 최종 값으로 등급/현상금 계산
        grade, bounty, score = calculate_grade_and_bounty(killed_total, injured_total)

        # DB 값이랑 차이가 있으면 업데이트
        if (d["civilian_kills"] != killed_total or
                d["civilian_injuries"] != injured_total or
                d["grade"] != grade or
                d["bounty"] != bounty):
            
            demon_repository.update_demon_totals_and_risk(
                demon_id, killed_total, injured_total, grade, bounty
            )

        result.append({
            "demon_id": demon_id,
            "name": d["name"],
            "status": d["status"],
            "grade": grade,
            "bounty": bounty,
            "killed_total": killed_total,
            "injured_total": injured_total,
            "score": score,
        })
    return result
