# service/hunter_service.py
from db import hunter_repository, account_repository

def list_hunters():
    return hunter_repository.get_all_hunters_with_team()

def list_teams():
    return hunter_repository.get_all_teams()

def register_hunter(name, status):
    """
    헌터 등록 - DB 트리거가 자동으로 팀 배정
    """
    hunter_id = hunter_repository.create_hunter(name, status)
    account_repository.ensure_account_exists(hunter_id)
    return hunter_id

def get_hunter_detail(hunter_id):
    return hunter_repository.get_hunter_by_id(hunter_id)


def get_hunter_detail(hunter_id):
    return hunter_repository.get_hunter_detail_with_account(hunter_id)



