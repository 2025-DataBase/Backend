# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify

from service import demon_service, hunter_service, mission_service, battle_service

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return redirect(url_for("main.demon_list"))

# 1. 악마 위험도 표시 페이지
@bp.route("/demons")
def demon_list():
    demons = demon_service.get_demon_risk_list()
    return render_template("demon_list.html", demons=demons)

# 악마 등록 페이지
@bp.route("/demons/new", methods=["GET", "POST"])
def demon_new():
    if request.method == "POST":
        name = request.form.get("name")
        civilian_kills = int(request.form.get("civilian_kills", 0))
        civilian_injuries = int(request.form.get("civilian_injuries", 0))

        if not name:
            flash("악마 이름은 필수입니다.", "danger")
            return redirect(url_for("main.demon_new"))

        # 자동으로 등급과 현상금 계산
        result = demon_service.register_demon(name, civilian_kills, civilian_injuries)
        
        flash(f"악마 '{result['name']}'이(가) 등록되었습니다. "
              f"등급: {result['grade']}, 현상금: {result['bounty']:,}원", "success")
        return redirect(url_for("main.demon_list"))

    return render_template("demon_form.html")

# 2. 헌터 목록 페이지 + 등록 폼
@bp.route("/hunters")
def hunter_list():
    hunters = hunter_service.list_hunters()
    return render_template("hunter_list.html", hunters=hunters)

@bp.route("/hunters/new", methods=["GET", "POST"])
def hunter_new():
    if request.method == "POST":
        name = request.form.get("name")
        
        if not name:
            flash("이름은 필수입니다.", "danger")
            return redirect(url_for("main.hunter_new"))

        # 상태는 자동으로 ALIVE, 트리거가 자동으로 팀을 배정
        hunter_id = hunter_service.register_hunter(name, "ALIVE")
        flash(f"헌터 '{name}'이(가) 등록되었습니다. 팀은 자동으로 배정되었습니다.", "success")
        return redirect(url_for("main.hunter_list"))

    # GET 요청 시
    return render_template("hunter_form.html")

@bp.route("/hunters/<int:hunter_id>")
def hunter_detail(hunter_id):
    hunter = hunter_service.get_hunter_detail(hunter_id)
    if not hunter:
        flash("존재하지 않는 헌터입니다.", "danger")
        return redirect(url_for("main.hunter_list"))
    return render_template("hunter_detail.html", hunter=hunter)

# 3. 미션 목록 페이지
@bp.route("/missions")
def mission_list():
    filter_type = request.args.get("filter", "all")
    missions = mission_service.get_mission_list(filter_type)
    return render_template("mission_list.html",
                           missions=missions,
                           filter_type=filter_type)

# 4. 미션 생성 + 팀 할당 페이지
@bp.route("/missions/assign", methods=["GET", "POST"])
def mission_assign():
    if request.method == "POST":
        team_id = int(request.form.get("team_id"))
        demon_id = int(request.form.get("demon_id"))  # 받기만 하고 저장은 안함 (나중에 사용)
        objective = request.form.get("objective")
        created_at = request.form.get("created_at")
        due_date = request.form.get("due_date")

        if not (team_id and demon_id and objective and created_at and due_date):
            flash("모든 필드를 입력하세요.", "danger")
            return redirect(url_for("main.mission_assign"))

        # 미션 생성
        mission_id = mission_service.create_mission(
            objective, created_at, due_date
        )

        try:
            mission_service.assign_team(mission_id, team_id)
            flash(f"미션이 생성되고 팀이 배정되었습니다.", "success")
        except ValueError as e:
            flash(str(e), "danger")

        return redirect(url_for("main.mission_list"))

    # GET 요청 시 - 팀 목록과 악마 목록 전달
    teams = hunter_service.list_teams()
    demons = demon_service.get_demon_risk_list()
    return render_template("mission_assign.html", teams=teams, demons=demons)

# 미션 상태 변경
@bp.route("/missions/<int:mission_id>/update_state", methods=["POST"])
def mission_update_state(mission_id):
    new_state = request.form.get("state")
    
    if new_state not in ['PLANNED', 'IN_PROGRESS', 'SUCCESS', 'FAIL']:
        flash("잘못된 상태값입니다.", "danger")
        return redirect(url_for("main.mission_list"))
    
    try:
        mission_service.update_mission_state(mission_id, new_state)
        flash(f"미션 상태가 '{new_state}'로 변경되었습니다.", "success")
    except Exception as e:
        flash(f"상태 변경 실패: {str(e)}", "danger")
    
    return redirect(url_for("main.mission_list"))

# 5. 전투 기록 페이지
@bp.route("/battles")
def battle_list():
    battles = battle_service.list_battles()
    return render_template("battle_list.html", battles=battles)

# @bp.route("/battles/<int:battle_id>/distribute", methods=["POST"])
# def battle_distribute(battle_id):
#     try:
#         share, n = battle_service.distribute_bounty(battle_id)
#         flash(f"{n}명의 헌터에게 각 {share}원씩 분배했습니다.", "success")
#     except ValueError as e:
#         flash(str(e), "danger")

#     return redirect(url_for("main.battle_list"))

@bp.route('/battle_distribute/<int:mission_id>/<int:battle_seq>', methods=['POST'])
def battle_distribute(mission_id, battle_seq):
    try:
        share, n = battle_service.distribute_bounty(mission_id, battle_seq)
        flash(f"분배 완료! {n}명의 헌터에게 각 {share:,}원씩 분배되었습니다.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('main.battle_list'))

# 전투 기록 등록 페이지
@bp.route("/battles/new", methods=["GET", "POST"])
def battle_new():
    if request.method == "POST":
        mission_id = int(request.form.get("mission_id"))
        demon_id = int(request.form.get("demon_id"))
        outcome = request.form.get("outcome")
        location = request.form.get("location")
        civilian_killed = int(request.form.get("civilian_killed", 0))
        civilian_injured = int(request.form.get("civilian_injured", 0))
        
        participant_hunter_ids = request.form.getlist("participant_hunters")  # 참여 헌터
        dead_hunter_ids = request.form.getlist("dead_hunters")  # 사망 헌터
        
        participant_hunter_ids = [int(hid) for hid in participant_hunter_ids if hid]
        dead_hunter_ids = [int(hid) for hid in dead_hunter_ids if hid]
        
        if not all([mission_id, demon_id, outcome, location]):
            flash("필수 필드를 모두 입력하세요.", "danger")
            return redirect(url_for("main.battle_new"))
        
        try:
            battle_seq = battle_service.create_battle_record(
                mission_id, demon_id, outcome, location, 
                civilian_killed, civilian_injured,
                participant_hunter_ids, dead_hunter_ids
            )
            flash(f"전투 기록이 등록되었습니다. (미션 {mission_id} - 전투 {battle_seq})", "success")
            return redirect(url_for("main.battle_list"))
        except Exception as e:
            flash(f"등록 실패: {str(e)}", "danger")
            return redirect(url_for("main.battle_new"))
    
    # GET 요청 - SUCCESS/FAIL 상태 미션 목록과 악마 목록 전달
    completed_missions = mission_service.get_mission_list('completed')
    demons = demon_service.get_demon_risk_list()
    
    return render_template("battle_form.html", missions=completed_missions, demons=demons)

# 미션의 팀원 조회 (AJAX)
@bp.route("/missions/<int:mission_id>/hunters")
def get_mission_hunters(mission_id):
    try:
        from db import mission_repository, hunter_repository
        team_id = mission_repository.get_mission_team_id(mission_id)
        
        if team_id:
            # hunter_repository에서 직접 조회
            hunters = hunter_repository.get_hunters_by_team(team_id)
            # ALIVE 헌터만 필터링
            alive_hunters = [h for h in hunters if h.get('status') == 'ALIVE']
            return jsonify({"hunters": alive_hunters})
        return jsonify({"hunters": []})
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in get_mission_hunters: {error_msg}")
        return jsonify({"error": str(e), "hunters": []}), 500

# 팀의 ALIVE 헌터 수 확인 (AJAX)
@bp.route("/teams/<int:team_id>/hunters/count")
def get_team_hunters_count(team_id):
    try:
        from db import hunter_repository
        hunters = hunter_repository.get_hunters_by_team(team_id)
        alive_count = sum(1 for h in hunters if h.get('status') == 'ALIVE')
        return jsonify({
            "alive_count": alive_count, 
            "total_count": len(hunters),
            "hunters": [{"hunter_id": h.get("hunter_id"), "name": h.get("name"), "status": h.get("status")} for h in hunters]
        })
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in get_team_hunters_count: {error_msg}")
        return jsonify({"error": str(e), "alive_count": 0, "total_count": 0}), 500


