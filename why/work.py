import pymysql
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "hello world!"

def get_connection():
    conn = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="kim20823097@@",
        database="chain_db",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return conn

def calc_threat_score(killed: int, injured: int) -> int:
    return killed * 5 + injured * 2

def calc_rank(score: int) -> str:
    if score >= 250:
        return "SS"
    elif score >= 200:
        return "S"
    elif score >= 120:
        return "B"
    else:
        return "C"

def get_ranked_demons():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                  SELECT
                      demon_id,
                      name,
                      bounty,
                      civilian_killed_total,
                      civilian_injured_total
                  FROM Demon \
                  """
            cursor.execute(sql)
            demons = cursor.fetchall()

        # Python에서 threat_score + rank 계산
        for d in demons:
            killed = d["civilian_killed_total"] or 0
            injured = d["civilian_injured_total"] or 0
            score = calc_threat_score(killed, injured)
            d["threat_score"] = score
            d["rank"] = calc_rank(score)

        # 위험도 높은 순으로 정렬
        demons_sorted = sorted(
            demons,
            key=lambda x: (-x["threat_score"], -x["bounty"])
        )
        return demons_sorted
    finally:
        conn.close()

def get_top5_demons():
    demons_sorted = get_ranked_demons()
    return demons_sorted[:5]

def print_top5_demons():
    top5 = get_top5_demons()

    print("\n===== 위험도 TOP 5 악마 랭킹 (rank 동적 계산) =====\n")
    for i, d in enumerate(top5, start=1):
        print(f"{i}. {d['name']} | Rank: {d['rank']}")
        print(f"   - 현상금: {d['bounty']:,}")
        print(f"   - 사망자: {d['civilian_killed_total']} | 부상자: {d['civilian_injured_total']}")
        print(f"   - 위협 점수: {d['threat_score']}")
        print("")
    print("======================================================\n")


if __name__ == "__main__":
    app.run(debug=True)