# service/hunter_service.py
from typing import Optional, Dict, List

from db import hunter_repository, account_repository


def get_hunters() -> List[Dict]:
    rows = hunter_repository.find_all_humans()
    result: List[Dict] = []
    for r in rows:
        result.append(
            {
                "id": r["hunter_id"],
                "name": r["name"],
                "status": r["status"],
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "region": r["region"],
            }
        )
    return result


def get_hunter_by_id(hunter_id: int) -> Optional[Dict]:
    r = hunter_repository.find_human_by_id(hunter_id)
    if not r:
        return None

    acc = account_repository.find_account_by_hunter_id(hunter_id)

    return {
        "id": r["hunter_id"],
        "name": r["name"],
        "status": r["status"],
        "team_id": r["team_id"],
        "team_name": r["team_name"],
        "region": r["region"],
        "account": acc,
    }
