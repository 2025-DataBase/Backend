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
        
        # Demon 테이블의 현재 값을 사용 (이미 Battle 기록이 반영된 값)
        # 전투 기록 생성 시마다 Demon 테이블이 업데이트되므로, 현재 값이 최신 상태
        killed_total = d["civilian_kills"]
        injured_total = d["civilian_injuries"]
        
        # 최종 값으로 등급/현상금 계산
        grade, bounty, score = calculate_grade_and_bounty(killed_total, injured_total)

        # DB 값이랑 차이가 있으면 업데이트 (등급/현상금만)
        if (d["grade"] != grade or d["bounty"] != bounty):
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
    
    # 위험 점수가 높은 순으로 정렬
    result.sort(key=lambda x: x["score"], reverse=True)
    return result
