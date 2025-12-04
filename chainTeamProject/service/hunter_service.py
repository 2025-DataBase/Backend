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

# 추가... 헌터 디테일에서 계좌 수입, 지출 등이 안보여서..
# def get_hunter_detail(hunter_id):
#     query = """
#     SELECT h.hunter_id,
#            h.name,
#            h.status,
#            t.team_name,
#            a.balance,
#            IFNULL(SUM(rd.distributer_amount), 0) AS total_income,
#            0 AS total_spent,  -- 지출은 아직 테이블 없으므로 0
#            MAX(rd.distributed_at) AS last_tx_date,
#            MAX(rd.distributer_amount) AS last_tx_amount,
#            'REWARD' AS last_tx_type,
#            '현상금 분배' AS last_tx_desc
#     FROM Hunter h
#     LEFT JOIN Team t ON h.team_id = t.team_id
#     LEFT JOIN Account a ON h.hunter_id = a.hunter_id
#     LEFT JOIN Reward_Distribution rd 
#            ON h.hunter_id = rd.hunter_id AND rd.state='SUCCESS'
#     WHERE h.hunter_id = %s
#     GROUP BY h.hunter_id, h.name, h.status, t.team_name, a.balance;
#     """
#     result = db.session.execute(query, (hunter_id,)).mappings().fetchone()
#     return result
def get_hunter_detail(hunter_id):
    return hunter_repository.get_hunter_detail_with_account(hunter_id)



