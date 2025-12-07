import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="1234",    # 여기 바꾸면 됨
        database="computer_2",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
