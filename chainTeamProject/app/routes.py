# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash

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

# 2. 헌터 목록 페이지 + 등록 폼
@bp.route("/hunters")
def hunter_list():
    hunters = hunter_service.list_hunters()
    return render_template("hunter_list.html", hunters=hunters)

@bp.route("/hunters/new", methods=["GET", "POST"])
def hunter_new():
    if request.method == "POST":
        name = request.form.get("name")
        # 상태는 입력받지 않고 항상 ACTIVE로 시작
        status = "ACTIVE"

        if not name:
            flash("이름은 필수입니다.", "danger")
            return redirect(url_for("main.hunter_new"))

        # team_id는 DB 트리거에서 자동으로 랜덤 배정되므로 NULL로 저장
        hunter_id = hunter_service.register_hunter(name, status, None)

        # 방금 배정된 팀 정보를 조회해서 메시지로 보여준다.
        hunter = hunter_service.get_hunter_detail(hunter_id)
        team_name = hunter.get("team_name") if hunter else None

        if team_name:
            flash(f"헌터가 등록되었습니다. 자동 배정된 팀: {team_name}", "success")
        else:
            flash("헌터가 등록되었습니다. (소속 팀 없음)", "success")

        return redirect(url_for("main.hunter_detail", hunter_id=hunter_id))

    # GET 요청: 이름만 입력받고, 팀/상태는 자동 처리 안내만 표시
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
    show_all = request.args.get("all") == "1"
    missions = mission_service.get_mission_list(active_only=not show_all)
    return render_template("mission_list.html",
                           missions=missions,
                           show_all=show_all)

# 4. 미션 생성 + 팀 할당 페이지
@bp.route("/missions/assign", methods=["GET", "POST"])
def mission_assign():
    if request.method == "POST":
        team_id = int(request.form.get("team_id"))
        objective = request.form.get("objective")
        target_desc = request.form.get("target_desc")
        created_at = request.form.get("created_at")
        due_date = request.form.get("due_date")

        if not (team_id and objective and target_desc and created_at and due_date):
            flash("모든 필드를 입력하세요.", "danger")
            return redirect(url_for("main.mission_assign"))

        mission_id = mission_service.create_mission(
            team_id, objective, target_desc, created_at, due_date
        )

        try:
            mission_service.assign_team(mission_id, team_id)
            flash("미션이 생성되고 팀이 배정되었습니다.", "success")
        except ValueError as e:
            flash(str(e), "danger")

        return redirect(url_for("main.mission_list"))

    teams = hunter_service.list_teams()
    return render_template("mission_assign.html", teams=teams)

# 5. 전투 기록 페이지
@bp.route("/battles")
def battle_list():
    battles = battle_service.list_battles()
    return render_template("battle_list.html", battles=battles)

@bp.route("/battles/<int:battle_id>/distribute", methods=["POST"])
def battle_distribute(battle_id):
    try:
        share, n = battle_service.distribute_bounty(battle_id)
        flash(f"{n}명의 헌터에게 각 {share}원씩 분배했습니다.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("main.battle_list"))
