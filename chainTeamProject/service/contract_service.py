from db import hunter_repository, demon_repository, account_repository

def list_contracts():
    return hunter_repository.get_contract_list()

def set_contract(hunter_id, demon_id, cost, power, date):
    hunter = hunter_repository.get_hunter_by_id(hunter_id)
    demon = demon_repository.get_demon_by_id(demon_id)
    if not hunter or not demon:
        raise ValueError("존재하지 않는 헌터 또는 악마입니다.")
    
    # 계좌에서 계약 비용 차감
    account_repository.add_expense(hunter_id, cost, "계약 체결")
    
    # 계약 정보 업데이트
    hunter_repository.update_contract(hunter_id, demon_id, cost, power, date)