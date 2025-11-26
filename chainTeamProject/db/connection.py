import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="kim20823097@@",
        database="chain_db",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )