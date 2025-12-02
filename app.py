# app.py
from flask import Flask, render_template, request, redirect, url_for, abort
from db import get_connection

app = Flask(__name__)

# ============================================
# INDEX
# ============================================
@app.route("/")
def index():
    return redirect(url_for("battle_list"))


# ============================================
# BATTLE LIST
# ============================================
@app.route("/battles")
def battle_list():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM v_battle_summary")
            battles = cur.fetchall()
        return render_template("battle_list.html", battles=battles)
    finally:
        conn.close()


# ============================================
# BATTLE DETAIL
# ============================================
@app.route("/battles/<int:battle_id>")
def battle_detail(battle_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM v_battle_distribution_detail
                        WHERE battle_id = %s
                        """, (battle_id,))
            rows = cur.fetchall()

        battle = rows[0] if rows else None
        return render_template("battle_detail.html", battle=battle, participants=rows)
    finally:
        conn.close()


# ============================================
# PREPARE DISTRIBUTION (자동 초기 등록)
# ============================================
@app.route("/battles/<int:battle_id>/prepare-distribution")
def prepare_distribution(battle_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # battle → mission_id
            cur.execute("SELECT mission_id FROM Battle WHERE battle_id = %s", (battle_id,))
            b = cur.fetchone()

            if not b or b["mission_id"] is None:
                return redirect(url_for("battle_detail", battle_id=battle_id))

            mission_id = b["mission_id"]

            # 배정된 헌터 찾기
            cur.execute("""
                        SELECT hunter_id
                        FROM MissionAssignment
                        WHERE mission_id = %s
                          AND assignment_status IN ('CONFIRMED','IN_PROGRESS','DONE')
                        """, (mission_id,))
            hunters = cur.fetchall()

            for h in hunters:
                cur.execute("""
                            INSERT IGNORE INTO Distribution (
                        battle_id, hunter_id, share_amount, status
                    ) VALUES (%s, %s, 1, 'PENDING')
                            """, (battle_id, h["hunter_id"]))

        conn.commit()
        return redirect(url_for("battle_detail", battle_id=battle_id))

    finally:
        conn.close()


# ============================================
# BATTLE DISTRIBUTE (최종 리팩토링)
# ============================================
@app.route("/battles/<int:battle_id>/distribute", methods=["POST"])
def battle_distribute(battle_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # 1) 총 청구 금액
            cur.execute("""
                        SELECT IFNULL(SUM(amount),0) AS total
                        FROM BountyClaim
                        WHERE battle_id = %s
                        """, (battle_id,))
            total = int(cur.fetchone()["total"])

            # 없으면 Demon.bounty로 대체
            if total == 0:
                cur.execute("""
                            SELECT d.bounty
                            FROM Battle b
                                     JOIN Demon d ON b.demon_id = d.demon_id
                            WHERE b.battle_id = %s
                            """, (battle_id,))
                r = cur.fetchone()
                total = int(r["bounty"]) if r else 0

            # 2) 분배 대상 (PENDING)
            cur.execute("""
                        SELECT hunter_id, share_amount AS weight
                        FROM Distribution
                        WHERE battle_id = %s AND status='PENDING'
                        """, (battle_id,))
            dist = cur.fetchall()

            if not dist or total <= 0:
                return redirect(url_for("battle_detail", battle_id=battle_id))

            total_weight = sum(row["weight"] for row in dist) or 1

            # 3) 지급
            for row in dist:
                hunter_id = row["hunter_id"]
                weight = row["weight"]
                pay = int(total * (weight / total_weight))

                # 계좌 갱신
                cur.execute("""
                            INSERT INTO Account (
                                hunter_id, balance, total_income, total_spent,
                                last_tx_type, last_tx_amount, last_tx_desc, updated_at
                            ) VALUES (
                                         %s, %s, %s, 0,
                                         'IN', %s,
                                         CONCAT('Battle ', %s, ' 분배금 입금'),
                                         NOW()
                                     )
                                ON DUPLICATE KEY UPDATE
                                                     balance = balance + VALUES(balance),
                                                     total_income = total_income + VALUES(balance),
                                                     last_tx_type='IN',
                                                     last_tx_amount=VALUES(balance),
                                                     last_tx_desc=VALUES(last_tx_desc),
                                                     updated_at=NOW()
                            """, (hunter_id, pay, pay, pay, battle_id))

                # Distribution 확정
                cur.execute("""
                            UPDATE Distribution
                            SET status='DONE',
                                distributed_at=NOW(),
                                share_amount=%s
                            WHERE battle_id=%s AND hunter_id=%s
                            """, (pay, battle_id, hunter_id))

        conn.commit()
        return redirect(url_for("battle_detail", battle_id=battle_id))

    finally:
        conn.close()


# ============================================
# BOUNTY CLAIM
# ============================================
@app.route("/battles/<int:battle_id>/claim", methods=["POST"])
def bounty_claim(battle_id):
    hunter_id = request.form["hunter_id"]
    demon_id = request.form["demon_id"]
    amount = request.form["amount"]
    notes = request.form.get("notes","")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO BountyClaim (
                            battle_id, demon_id, hunter_id, amount, claim_date, notes
                        ) VALUES (%s,%s,%s,%s,NOW(),%s)
                        """, (battle_id, demon_id, hunter_id, amount, notes))
        conn.commit()
        return redirect(url_for("battle_detail", battle_id=battle_id))
    finally:
        conn.close()


# ============================================
# MISSION LIST
# ============================================
@app.route("/missions")
def mission_list():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM v_mission_overview ORDER BY due_date")
            missions = cur.fetchall()
        return render_template("mission_list.html", missions=missions)
    finally:
        conn.close()


# ============================================
# MISSION CREATE
# ============================================
@app.route("/missions/create", methods=["GET","POST"])
def mission_create():
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            if request.method == "GET":
                cur.execute("SELECT team_id, team_name FROM Team ORDER BY team_name")
                teams = cur.fetchall()
                return render_template("mission_create.html", teams=teams)

            # POST
            team_id = request.form["team_id"]
            objective = request.form["objective"]
            target_desc = request.form["target_desc"]
            due_date = request.form["due_date"]

            cur.execute("""
                        INSERT INTO Mission (
                            team_id, objective, target_desc, status, created_at, due_date
                        ) VALUES (%s,%s,%s,'PLANNED',CURDATE(),%s)
                        """, (team_id, objective, target_desc, due_date))
            conn.commit()
            return redirect(url_for("mission_list"))

    finally:
        conn.close()


# ============================================
# MISSION ASSIGN
# ============================================
@app.route("/missions/<int:mission_id>/assign", methods=["GET","POST"])
def mission_assign(mission_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # ---------------------
            # POST = 헌터 배정
            # ---------------------
            if request.method == "POST":
                hunter_id = request.form.get("hunter_id")

                if hunter_id:
                    # 배정 기록 저장
                    cur.execute("""
                                INSERT INTO MissionAssignment (mission_id, hunter_id, assignment_status)
                                VALUES (%s,%s,'CONFIRMED')
                                    ON DUPLICATE KEY UPDATE assignment_status='CONFIRMED'
                                """, (mission_id, hunter_id))

                    # 미션 내 모든 전투 가져오기
                    cur.execute("SELECT battle_id FROM Battle WHERE mission_id = %s", (mission_id,))
                    battles = cur.fetchall()

                    # 전투별 Distribution 행 자동 생성
                    for b in battles:
                        cur.execute("""
                                    INSERT IGNORE INTO Distribution (
                                battle_id, hunter_id, share_amount, status
                            ) VALUES (%s,%s,1,'PENDING')
                                    """, (b["battle_id"], hunter_id))

                    conn.commit()

                return redirect(url_for("mission_assign", mission_id=mission_id))


            # ---------------------
            # GET = 화면 표시
            # ---------------------

            # 미션 조회
            cur.execute("""
                        SELECT m.*, t.team_name
                        FROM Mission m
                                 JOIN Team t ON m.team_id = t.team_id
                        WHERE mission_id=%s
                        """, (mission_id,))
            mission = cur.fetchone()
            if not mission:
                abort(404)

            # 배정된 헌터
            cur.execute("""
                        SELECT
                            ma.assignment_id,
                            ma.hunter_id,
                            ma.assignment_status,
                            ma.assigned_at,
                            h.name AS hunter_name,
                            h.status AS hunter_status,
                            t.team_name AS hunter_team
                        FROM MissionAssignment ma
                                 JOIN Human h ON ma.hunter_id = h.hunter_id
                                 LEFT JOIN Team t ON h.team_id = t.team_id
                        WHERE ma.mission_id = %s
                          AND (ma.assignment_status <> 'CANCELLED'
                            OR ma.assignment_status IS NULL)
                        ORDER BY h.name
                        """, (mission_id,))
            assigned = cur.fetchall()

            # 배정되지 않은 ACTIVE 헌터 목록
            cur.execute("""
                        SELECT h.hunter_id, h.name AS hunter_name, h.status AS hunter_status,
                               t.team_name AS hunter_team
                        FROM Human h
                                 LEFT JOIN Team t ON h.team_id = t.team_id
                        WHERE h.status='ACTIVE'
                          AND h.hunter_id NOT IN (
                            SELECT hunter_id
                            FROM MissionAssignment
                            WHERE mission_id=%s
                              AND (assignment_status <> 'CANCELLED'
                                OR assignment_status IS NULL)
                        )
                        ORDER BY h.name
                        """, (mission_id,))
            candidates = cur.fetchall()

            return render_template("mission_assign.html",
                                   mission=mission,
                                   assigned=assigned,
                                   candidates=candidates)

    finally:
        conn.close()



# ============================================
# DELETE / UPDATE MISSION ASSIGNMENT
# ============================================
@app.route("/missions/assignment/<int:assignment_id>/delete")
def mission_assignment_delete(assignment_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # mission_id + hunter_id 가져오기
            cur.execute("""
                        SELECT mission_id, hunter_id
                        FROM MissionAssignment
                        WHERE assignment_id=%s
                        """, (assignment_id,))
            row = cur.fetchone()

            if not row:
                return redirect(url_for("assignment_list"))

            mission_id = row["mission_id"]
            hunter_id = row["hunter_id"]

            # 관련 Distribution 삭제
            cur.execute("""
                DELETE dist
                FROM Distribution dist
                JOIN Battle b ON dist.battle_id = b.battle_id
                WHERE b.mission_id=%s AND dist.hunter_id=%s
            """, (mission_id, hunter_id))

            # 배정 자체 삭제
            cur.execute("DELETE FROM MissionAssignment WHERE assignment_id=%s", (assignment_id,))

        conn.commit()
        return redirect(url_for("mission_assign", mission_id=mission_id))

    finally:
        conn.close()


# ============================================
# DEMON DASHBOARD
# ============================================
@app.route("/demons")
def demon_dashboard():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM v_demon_dashboard
                        ORDER BY
                            CASE risk_level
                                WHEN 'EXTREME' THEN 1
                                WHEN 'DANGER' THEN 2
                                WHEN 'WARNING' THEN 3
                                ELSE 4
                                END,
                            battle_count DESC
                        """)
            demons = cur.fetchall()

        total = len(demons)
        extreme = sum(1 for d in demons if d["risk_level"]=="EXTREME")
        danger  = sum(1 for d in demons if d["risk_level"]=="DANGER")
        warning = sum(1 for d in demons if d["risk_level"]=="WARNING")

        return render_template(
            "demons_dashboard.html",
            demons=demons,
            total=total,
            extreme=extreme,
            danger=danger,
            warning=warning
        )
    finally:
        conn.close()



# ============================================
# DEMON RECALC FINAL (전투 기반 일관 재계산)
# ============================================
@app.route("/demons/recalc", methods=["POST"])
def demon_recalc():
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # 1) 악마 + 전투데이터 조회
            cur.execute("""
                        SELECT
                            d.demon_id,
                            d.base_bounty,
                            d.grade,
                            d.base_civilian_killed,
                            d.base_civilian_injured,

                            COALESCE(SUM(b.civilian_killed),0) AS battle_killed,
                            COALESCE(SUM(b.civilian_injured),0) AS battle_injured
                        FROM Demon d
                                 LEFT JOIN Battle b ON d.demon_id = b.demon_id
                        GROUP BY d.demon_id
                        """)
            demons = cur.fetchall()

            # 등급 매핑
            grade_to_level = {"C":1,"B":2,"A":3,"S":4,"SS":5}
            level_to_grade = {v:k for k,v in grade_to_level.items()}

            for d in demons:
                demon_id = d["demon_id"]

                killed  = d["base_civilian_killed"]  + d["battle_killed"]
                injured = d["base_civilian_injured"] + d["battle_injured"]
                damage = killed + injured

                base_bounty = d["base_bounty"]

                # 2) 위험수준별 배수
                if damage >= 80:
                    risk_factor = 4
                elif damage >= 40:
                    risk_factor = 3
                elif damage >= 20:
                    risk_factor = 2
                else:
                    risk_factor = 1

                # 3) 피해량 기반 고정 보너스
                casualty_bonus = killed * 50000 + injured * 10000

                new_bounty = int(base_bounty * risk_factor + casualty_bonus)

                # 4) 등급 재계산
                base_grade = d["grade"] or "C"
                base_level = grade_to_level[base_grade]

                if damage >= 150:
                    damage_level = 5
                elif damage >= 80:
                    damage_level = 4
                elif damage >= 40:
                    damage_level = 3
                elif damage >= 20:
                    damage_level = 2
                else:
                    damage_level = 1

                final_grade = level_to_grade[max(base_level, damage_level)]

                # 5) DB 갱신
                cur.execute("""
                            UPDATE Demon
                            SET bounty=%s,
                                grade=%s,
                                civilian_killed_total=%s,
                                civilian_injured_total=%s
                            WHERE demon_id=%s
                            """, (new_bounty, final_grade, killed, injured, demon_id))

        conn.commit()
        return redirect(url_for("demon_dashboard"))

    finally:
        conn.close()



# ============================================
# HUNTER LIST / DETAIL
# ============================================
@app.route("/hunters")
def hunter_list():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM v_hunter_financials
                        ORDER BY
                            CASE hunter_status
                                WHEN 'ACTIVE' THEN 1
                                WHEN 'INACTIVE' THEN 2
                                WHEN 'RETIRED' THEN 3
                                WHEN 'DEAD' THEN 4
                                ELSE 5
                                END,
                            hunter_name
                        """)
            hunters = cur.fetchall()
        return render_template("hunters_list.html", hunters=hunters)
    finally:
        conn.close()


@app.route("/hunters/<int:hunter_id>")
def hunter_detail(hunter_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM v_hunter_financials
                        WHERE hunter_id=%s
                        """, (hunter_id,))
            hunter = cur.fetchone()
        return render_template("hunter_detail.html", hunter=hunter)
    finally:
        conn.close()


# ============================================
# BATTLE CREATE
# ============================================
@app.route("/battles/create", methods=["GET","POST"])
def battle_create():
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            if request.method == "POST":
                mission_id = request.form.get("mission_id") or None
                demon_id = request.form.get("demon_id")
                started_at = request.form.get("started_at")
                ended_at = request.form.get("ended_at")
                location = request.form.get("location")
                outcome = request.form.get("outcome")
                killed = request.form.get("civilian_killed") or 0
                injured = request.form.get("civilian_injured") or 0
                notes = request.form.get("notes") or None

                # datetime-local 처리
                if started_at:
                    started_at = started_at.replace("T"," ")
                if ended_at:
                    ended_at = ended_at.replace("T"," ")

                cur.execute("""
                            INSERT INTO Battle (
                                mission_id, demon_id, started_at, ended_at,
                                location, outcome, civilian_killed,
                                civilian_injured, notes
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (
                                mission_id, demon_id, started_at, ended_at,
                                location, outcome, killed, injured, notes
                            ))

                conn.commit()
                return redirect(url_for("battle_list"))

            # GET: 선택 목록
            cur.execute("SELECT mission_id, objective FROM Mission ORDER BY mission_id")
            missions = cur.fetchall()

            cur.execute("SELECT demon_id, name FROM Demon ORDER BY demon_id")
            demons = cur.fetchall()

        return render_template("battle_create.html", missions=missions, demons=demons)

    finally:
        conn.close()



# ============================================
# ASSIGNMENT LIST
# ============================================
@app.route("/assignments")
def assignment_list():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM v_mission_assignment_detail
                        ORDER BY mission_id, assigned_at DESC
                        """)
            assignments = cur.fetchall()

        return render_template("assignments_list.html", assignments=assignments)

    finally:
        conn.close()



# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    app.run(port=5001)
