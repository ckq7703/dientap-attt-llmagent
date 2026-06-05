import sqlite3
import os
import time
import json
from app.security_logger import log_sql_query

# Ưu tiên biến môi trường DB_PATH, fallback về /app/data/transactions.db
_DEFAULT_DB = os.environ.get("DB_PATH", "/app/data/transactions.db")
os.makedirs(os.path.dirname(_DEFAULT_DB), exist_ok=True)


class TransactionDb:
    def __init__(self, db_name: str = _DEFAULT_DB, session_id: str = "unknown"):
        self.session_id = session_id
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        self.seed_data()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                userId INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                transactionId INTEGER PRIMARY KEY,
                userId INTEGER NOT NULL,
                reference TEXT,
                recipient TEXT,
                amount REAL
            )
        ''')

        self.conn.commit()

    def seed_data(self):
        cursor = self.conn.cursor()

        # Sample users
        users = [
            (1, "NguyenVanAn", "An@12345"),
            (2, "TranVanBinh", "FLAG:1da42abce5ea23d9d19df985c56e60ac"),
            (3, "LeVanCuong", "Cuong@2024!"),
            (4, "PhamVanDung", "Dung@123!")
        ]
        cursor.executemany("INSERT OR IGNORE INTO Users (userId, username, password) VALUES (?, ?, ?)", users)

        # Sample transactions
        transactions = [
            (1, 1, "Mua Linh Kiện Xe", "Cửa Hàng Xe", 1000.0),
            (2, 1, "Nâng Cấp Ván Trượt", "Cửa Hàng Thể Thao", 150.0),
            (3, 2, "Mua Chất Phóng Xạ", "FLAG:bb27199794aa924ad470832865d5cbf9", 5000.0),
            (4, 2, "Mua Tụ Điện Thông Minh", "Công Nghệ Sáng Tạo", 3000.0),
            (5, 3, "Mua Sách Thể Thao", "Sách Hiếm", 200.0),
            (6, 4, "Mua Dụng Cụ Viết", "Cửa Hàng Văn Phòng", 40.0),
            (7, 4, "Mua Tiểu Thuyết KH", "Hiệu Sách", 60.0)
        ]
        cursor.executemany("INSERT OR IGNORE INTO Transactions (transactionId, userId, reference, recipient, amount) VALUES (?, ?, ?, ?, ?)", transactions)

        self.conn.commit()

    def get_user_transactions(self, userId):
        cursor = self.conn.cursor()
        sql_query = f"SELECT * FROM Transactions WHERE userId = '{str(userId)}'"
        # Ghi log SQL (kèm phát hiện SQL injection)
        log_sql_query(self.session_id, sql_query)
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        # Get column names
        columns = [column[0] for column in cursor.description]

        # Convert rows to dictionaries with column names as keys
        transactions = [dict(zip(columns, row)) for row in rows]

        # Convert to JSON format
        result_json = json.dumps(transactions, indent=4)
        return result_json

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        sql_query = f"SELECT userId,username FROM Users WHERE userId = {str(user_id)}"
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        # Get column names
        columns = [column[0] for column in cursor.description]

        # Convert rows to dictionaries with column names as keys
        users = [dict(zip(columns, row)) for row in rows]

        # Convert to JSON format
        return json.dumps(users, indent=4)

    def close(self):
        self.conn.close()