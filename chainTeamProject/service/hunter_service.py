# service/hunter_service.py
from db import hunter_repository, account_repository

def list_hunters():
    return hunter_repository.get_all_hunters_with_team()

def list_teams():
    return hunter_repository.get_all_teams()

def register_hunter(name, status, team_id):
    hunter_id = hunter_repository.create_hunter(name, status, team_id)
    account_repository.ensure_account_exists(hunter_id)
    return hunter_id

def get_hunter_detail(hunter_id):
    return hunter_repository.get_hunter_by_id(hunter_id)
