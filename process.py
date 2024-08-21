import sqlite3
from datetime import datetime
from database import connect_database
from utils import get_configured_logger

new_conn_v0171 = connect_database()[1]
log = get_configured_logger()


class Process:
    def __init__(
        self,
        db_connection: sqlite3.Connection = new_conn_v0171,
    ):
        self.db_connection = db_connection
        self.start_time = None
        self.start_memo_id = None

        # 创建表（如果不存在）
        self.create_table()

    def create_table(self):
        with self.db_connection:
            self.db_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memos_rollback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    start_memo_id INTEGER NOT NULL,
                    end_memo_id INTEGER,
                    elapsed_time_h REAL DEFAULT 0,
                    progress INTEGER DEFAULT 0,
                    efficiency REAL DEFAULT 0
                );
                """
            )

    def _get_last_memo_id(self) -> int:
        cursor = self.db_connection.cursor()

        # 查询表中是否有记录
        cursor.execute(
            """
            SELECT COUNT(*) FROM memos_rollback
            """
        )
        count = cursor.fetchone()[0]
        # 如果表为空，返回 0
        if count == 0:
            log.info("No records found in memos_rollback. Returning 0 as last end_memo_id.")
            return 0

        # 表不为空，获取最后一条记录的 start_memo_id 和 end_memo_id
        cursor.execute(
            """
            SELECT start_memo_id, end_memo_id
            FROM memos_rollback
            ORDER BY id DESC
            LIMIT 1
            """
        )
        result = cursor.fetchone()

        # 如果 start_memo_id 等于 end_memo_id，说明上一次并没有进行操作
        if result[0] == result[1]:
            log.info("Last operation has not been completed. Returning start_memo_id - 1 as last end_memo_id.")
            return result[0] - 1
        else:
            return result[1]

    def start(self) -> int:
        """记录开始时间和开始 memo_id，初始化结束时间和结束 memo_id 为当前值。"""
        last_end_memo_id = self._get_last_memo_id()
        self.start_memo_id = last_end_memo_id + 1
        self.start_time = datetime.now()
        self.end_mem_id = self.start_memo_id
        self.end_time = self.start_time

        with self.db_connection:
            self.db_connection.execute(
                """
                INSERT INTO memos_rollback (start_time, end_time, start_memo_id, end_memo_id)
                VALUES (?, ?, ?, ?)
                """,
                (self.start_time, self.end_time, self.start_memo_id, self.end_mem_id),
            )

        log.info(f"Process started at {self.start_time} with memo_id: {self.start_memo_id}.")

        return self.start_memo_id

    def update(self, end_memo_id: int):
        """更新结束时间和结束 memo_id，并计算相关值。"""
        self.end_time = datetime.now()
        self.end_memo_id = end_memo_id

        elapsed_time_h = (self.end_time - self.start_time).total_seconds() / 3600
        progress = self.end_memo_id - self.start_memo_id
        efficiency = progress / elapsed_time_h if elapsed_time_h > 0 else 0

        with self.db_connection:
            self.db_connection.execute(
                """
                UPDATE memos_rollback
                SET end_time = ?, end_memo_id = ?, elapsed_time_h = ?, progress = ?, efficiency = ?
                WHERE id = (
                    SELECT id FROM memos_rollback
                    ORDER BY id DESC
                    LIMIT 1
                )
                """,
                (self.end_time, self.end_memo_id, elapsed_time_h, progress, efficiency),
            )

        log.info(f"Process updated at {self.end_time} with memo_id: {self.end_memo_id}.")
