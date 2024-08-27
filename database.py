import sqlite3
from config import old_database_path_v0210, new_database_path_v0171, new_database_schema_path_v0171, creator_id
from utils import is_file_exists, ensure_directory_exists_for_file, get_configured_logger
from typing import Optional, List

log = get_configured_logger()


def create_database(
        db_path: str = new_database_path_v0171,
        schema_path: str = new_database_schema_path_v0171,
        overwrite: bool = False,  # 是否覆盖已存在的数据库文件
) -> None:
    """
    创建一个新的 SQLite 数据库，并使用给定的 SQL 文件初始化它。

    :param db_path: 新数据库的路径，默认为 new_database_path_v0171。
    :param schema_path: 包含 SQL 初始化脚本的文件，默认为 new_database_schema_path_v0171。
    :param overwrite: 如果数据库文件已存在，是否覆盖，默认为 False。
    """
    if is_file_exists(db_path) and not overwrite:
        log.info(f"数据库文件 {db_path} 已存在，继续使用。")
        return
    ensure_directory_exists_for_file(db_path)

    try:
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, 'r') as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            log.info(f"新数据库已创建：{db_path}")
    except sqlite3.Error as e:
        log.error(f"创建数据库时发生错误：{e}")


def connect_database(
        old_db_path: str = old_database_path_v0210,
        new_db_path: str = new_database_path_v0171,
) -> tuple[sqlite3.Connection, sqlite3.Connection]:
    """
    连接到两个 SQLite 数据库。

    :param old_db_path: 旧数据库的路径，默认为 old_database_path_v0210。
    :param new_db_path: 新数据库的路径，默认为 new_database_path_v0171。
    :return (old_conn, new_conn): 一个包含两个连接对象的元组(old_conn, new_conn)。如果连接失败，返回 None。
    """
    old_conn_v0210 = sqlite3.connect(old_db_path)
    new_conn_v0171 = sqlite3.connect(new_db_path)
    return old_conn_v0210, new_conn_v0171


def confirmed_memo_id(
        memo_id: int,
        db_connection: sqlite3.Connection = connect_database()[0],
        operation: str = "gte",  # "gte" - 大于等于 "lte" - 小于等于
) -> int:
    """
    检查 memo_id 是否存在于数据库的 memo 表中。如果不存在，则返回下一个存在的 memo_id。

    :param memo_id: memo_id
    :param db_connection: 已连接的 SQLite 数据库对象，默认为 old_conn_v0210。
    :param operation: 操作符，默认为 "gte"，表示大于等于。可选值有 "lte"，表示小于等于
    :return memo_id: 如果 memo_id 存在，返回原 memo_id；如果不存在，返回下一个存在的 memo_id；找不到就报错。
    """

    cursor = db_connection.cursor()

    if operation == "gte":
        # 查找大于等于给定 memo_id 的最小 id
        cursor.execute(
            """
            SELECT id
            FROM memo
            WHERE id >= ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (memo_id,)
        )
    elif operation == "lte":
        # 查找小于等于给定 memo_id 的最大 id
        cursor.execute(
            """
            SELECT id
            FROM memo
            WHERE id <= ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (memo_id,)
        )
    else:
        log.error(f"Invalid operation: {operation}")
        raise ValueError("Invalid operation.")

    result = cursor.fetchone()

    if result is None:
        log.error(f"No matching ID found for operation: {operation} with memo_id: {memo_id}")
        raise ValueError("No matching ID found.")

    return result[0]


def get_memo_record(
    memo_id: int,
    db_connection: sqlite3.Connection = connect_database()[0],
) -> dict:
    """
    获取指定 memo_id 的 memo 记录。

    :param memo_id: memo_id
    :param db_connection: 已连接的 SQLite 数据库对象，默认为 old_conn_v0210。
    :return memo_record: 包含 memo 记录的字典。
    """
    memo_id = confirmed_memo_id(memo_id, db_connection)

    cursor = db_connection.cursor()
    cursor.execute(
        """
        SELECT creator_id, created_ts, updated_ts, content
        FROM memo
        WHERE id = ?
        """,
        (memo_id,)
    )
    result = cursor.fetchone()

    return {
        "memo_id": memo_id,
        "creator_id": result[0],
        "created_ts": result[1],
        "updated_ts": result[2],
        "content": result[3],
    }


def upsert_memo_record(
    memo_id: int,
    created_ts: int,
    updated_ts: int,
    content: str,
    creator_id: int = creator_id,
    row_status: str = "NORMAL",
    visibility: str = "PRIVATE",
    db_connection: sqlite3.Connection = connect_database()[1],
) -> None:
    """
    插入或更新 memo 记录。

    :param memo_id: memo_id
    :param created_ts: 创建时间戳
    :param updated_ts: 更新时间戳
    :param content: 备忘录内容
    :param creator_id: 创建者 ID，默认在 config.py 给出。
    :param row_status: 行状态，默认为 "NORMAL"
    :param visibility: 可见性，默认为 "PRIVATE"
    :param db_connection: 已连接的 SQLite 数据库对象，默认为 new_conn_v0171。
    """
    cursor = db_connection.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO memo (id, created_ts, updated_ts, creator_id, row_status, visibility, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (memo_id, created_ts, updated_ts, creator_id, row_status, visibility, content)
    )
    db_connection.commit()


def get_resource_record(
    memo_id: int,
    version: str = "v0171",
    db_connection: sqlite3.Connection = connect_database()[1],
    another_db_connection: sqlite3.Connection = connect_database()[0],
) -> List[dict]:
    """
    获取指定 memo_id 的 resource 记录。

    :param memo_id: memo_id
    :param version: 数据库版本，默认为 "v0171"，注意与传入的 db_connection 对象相对应。
    :param db_connection: 已连接的 SQLite 数据库对象，默认为 new_conn_v0171。
    :param another_db_connection: 另一个数据库连接对象，默认为 old_conn_v0210，用于确认 memo_id 是否存在。
    :return resource_record_list: 包含 resource 记录的字典的列表。
    """
    memo_id = confirmed_memo_id(memo_id, another_db_connection)

    cursor = db_connection.cursor()
    if version == "v0171":
        cursor.execute(
            """
            SELECT creator_id, created_ts, updated_ts, filename, blob, external_link, type, size, internal_path
            FROM resource
            WHERE memo_id = ?
            ORDER BY id ASC
            """,
            (memo_id,)
        )
        result = cursor.fetchall()
        resource_record_list = [
            {
                "memo_id": memo_id,
                "creator_id": row[0],
                "created_ts": row[1],
                "updated_ts": row[2],
                "filename": row[3],
                "blob": row[4],
                "external_link": row[5],
                "type": row[6],
                "size": row[7],
                "internal_path": row[8],
            } for row in result
        ]
        return resource_record_list
    elif version == "v0210":
        cursor.execute(
            """
            SELECT creator_id, created_ts, updated_ts, filename, blob, type, size, storage_type, reference
            FROM resource
            WHERE memo_id = ?
            ORDER BY id ASC
            """,
            (memo_id,)
        )
        result = cursor.fetchall()
        resource_record_list = [
            {
                "memo_id": memo_id,
                "creator_id": row[0],
                "created_ts": row[1],
                "updated_ts": row[2],
                "filename": row[3],
                "blob": row[4],
                "type": row[5],
                "size": row[6],
                "storage_type": row[7],
                "reference": row[8],
            } for row in result
        ]
        return resource_record_list
    else:
        log.error(f"Invalid version: {version}")
        raise ValueError("Invalid version.")


def insert_resource_record(
    memo_id: int,
    created_ts: int,
    updated_ts: int,
    filename: int,
    blob: Optional[bytes] = None,
    external_link: str = "",
    resource_type: str = "",  # type 键，Python 保留字回避
    size: int = 0,
    internal_path: str = "",
    version: str = "v0171",
    db_connection: sqlite3.Connection = connect_database()[1],
) -> None:
    """
    插入 resource 记录。

    :param memo_id: memo_id
    :param created_ts: 创建时间戳
    :param updated_ts: 更新时间戳
    :param filename: 文件名
    :param blob: 二进制数据，默认为 None
    :param external_link: 外部链接地址，默认为 ""
    :param resource_type: 文件类型，默认为 ""
    :param size: 文件大小，默认为 0
    :param internal_path: 本地文件地址，默认为 ""
    :param version: 数据库版本，默认为 "v0171"，暂不支持 "v0210"。
    :param db_connection: 已连接的 SQLite 数据库对象，默认为 new_conn_v0171。
    """
    if version != "v0171":
        log.error(f"Invalid version: {version}")
        raise ValueError("Invalid version.")

    cursor = db_connection.cursor()
    cursor.execute(
        """
        INSERT INTO resource (memo_id, created_ts, updated_ts, filename, blob, external_link, type, size, internal_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (memo_id, created_ts, updated_ts, filename, blob, external_link, resource_type, size, internal_path)
    )
    db_connection.commit()
