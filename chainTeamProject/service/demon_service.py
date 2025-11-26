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

def get_demon_risk_list():
    """
    1. Battle 기준으로 각 Demon의 killed/injured 합계를 계산하고
    2. grade, bounty를 재계산해서 Demon 테이블에 반영
    3. 화면에는 score까지 같이 내려줌
    """
    demons = demon_repository.get_all_demons()
    result = []

    for d in demons:
        demon_id = d["demon_id"]
        killed_sum, injured_sum = demon_repository.recalc_totals_from_battles(demon_id)
        grade, bounty, score = calculate_grade_and_bounty(killed_sum, injured_sum)

        # DB 값이랑 차이가 있으면 업데이트
        if (d["civilian_killed_total"] != killed_sum or
                d["civilian_injured_total"] != injured_sum or
                d["grade"] != grade or
                d["bounty"] != bounty):

            demon_repository.update_demon_totals_and_risk(
                demon_id, killed_sum, injured_sum, grade, bounty
            )

        result.append({
            "demon_id": demon_id,
            "name": d["name"],
            "grade": grade,
            "bounty": bounty,
            "killed_total": killed_sum,
            "injured_total": injured_sum,
            "score": score,
        })
    return result
