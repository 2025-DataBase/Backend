# chainTeamProject/service/devil_service.py

from db import demon_repository


def _calculate_risk_score(killed: int, injured: int) -> int:
    killed = killed or 0
    injured = injured or 0
    return killed * 3 + injured


def _score_to_grade(score: int) -> str:
    if score >= 80:  return "SS"
    if score >= 70:  return "S"
    if score >= 60:  return "A"
    if score >= 50:  return "B"
    return "C"


def get_demon_risk_list(update_rank: bool = False):
    devils = demon_repository.find_all_devils()
    result = []

    for d in devils:
        score = _calculate_risk_score(
            d["civilian_killed_total"],
            d["civilian_injured_total"]
        )
        rank = _score_to_grade(score)

        if update_rank:
            demon_repository.update_devil_rank(d["demon_id"], rank)

        result.append({
            "id": d["demon_id"],
            "name": d["name"],
            "bounty": d["bounty"],
            "civilian_killed_total": d["civilian_killed_total"],
            "civilian_injured_total": d["civilian_injured_total"],
            "rank": rank,
            "risk_score": score
        })

    return result


def get_demon_by_id(demon_id: int):
    for d in get_demon_risk_list(update_rank=False):
        if d["id"] == demon_id:
            return d
    return None
