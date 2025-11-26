# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, Response, abort

from service import demon_service
from service import battle_service
from service import mission_service
from service import hunter_service


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")


# =========================
# ① 악마 위험도 대시보드
# =========================
@bp.route("/devils/risk-page")
def devil_risk_page():
    devils = demon_service.get_demon_risk_list(update_rank=False)
    return render_template("demon_risk.html", devils=devils)

@bp.route("/demons/<int:demon_id>")
def demon_detail(demon_id):
    # 1) 악마 기본 정보 (위험도/등급 포함)
    demon = demon_service.get_demon_by_id(demon_id)
    if demon is None:
        abort(404)

    # 2) 해당 악마와 관련된 전투 목록
    battles = battle_service.get_battles(demon_id=demon_id)

    # 3) 템플릿으로 전달
    return render_template("demon_detail.html",
                           demon=demon,
                           battles=battles)
# =========================
# ② 전투 & 보상 시나리오
# =========================
@bp.route("/battles")
def battle_list():
    battles = battle_service.get_battles()
    return render_template("battle_list.html", battles=battles)

@bp.route("/battles/<int:battle_id>")
def battle_detail(battle_id):
    battle = battle_service.get_battle_by_id(battle_id)
    if not battle:
        abort(404)
    return render_template("battle_detail.html", battle=battle)

@bp.route("/claim/<int:battle_id>", methods=["GET", "POST"])
def claim_page(battle_id):
    battle = battle_service.get_battle_by_id(battle_id)
    if not battle:
        abort(404)

    if request.method == "POST":
        ok = battle_service.claim_reward(battle_id)
        return render_template("claim.html", battle=battle, success=ok)

    return render_template("claim.html", battle=battle, success=None)

# =========================
# ③ 임무 할당 시나리오
# =========================
@bp.route("/missions")
def mission_list():
    missions = mission_service.get_missions()
    return render_template("mission_list.html", missions=missions)

@bp.route("/missions/<int:mission_id>")
def mission_detail(mission_id):
    mission = mission_service.get_mission_by_id(mission_id)
    if not mission:
        abort(404)
    hunters = mission_service.get_hunters_for_mission(mission_id)
    return render_template("mission_detail.html", mission=mission, hunters=hunters)

@bp.route("/hunters")
def hunter_list():
    hunters = hunter_service.get_hunters()
    return render_template("hunter_list.html", hunters=hunters)

@bp.route("/hunters/<int:hunter_id>")
def hunter_detail(hunter_id):
    hunter = hunter_service.get_hunter_by_id(hunter_id)
    if not hunter:
        abort(404)

    battles = battle_service.get_battles_for_hunter(hunter_id)

    return render_template("hunter_detail.html",
                           hunter=hunter,
                           battles=battles)

# =========================
# ④ 임무 할당 시나리오
# =========================
@bp.route("/assignments/new", methods=["GET", "POST"])
def assignment_new():
    if request.method == "POST":
        mission_id = int(request.form["mission_id"])
        team_id = int(request.form["team_id"])
        status = request.form.get("status", "CONFIRMED")

        mission_service.create_assignment(mission_id, team_id, status)
        # 생성 후 목록 페이지로 이동
        return redirect(url_for("main.assignment_list"))

    # GET: 폼에 필요한 데이터 로딩
    data = mission_service.get_assignment_form_data()
    return render_template(
        "assignment_form.html",
        missions=data["missions"],
        teams=data["teams"],
    )


@bp.route("/assignments")
def assignment_list():
    assignments = mission_service.get_assignments()
    return render_template("assignment_list.html", assignments=assignments)
