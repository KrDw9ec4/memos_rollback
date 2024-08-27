from database import connect_database, get_memo_record, upsert_memo_record
from utils import get_configured_logger

log = get_configured_logger()
old_conn_v0210, new_conn_v0171 = connect_database()

for memo_id in range(1,5508):
    memo_record = get_memo_record(
        memo_id=memo_id,
        db_connection=old_conn_v0210
    )
    id = memo_record["memo_id"]
    created_ts = memo_record["created_ts"]
    updated_ts = memo_record["updated_ts"]
    content = memo_record["content"]

    upsert_memo_record(
        memo_id=id,
        created_ts=created_ts,
        updated_ts=updated_ts,
        content=content,
        db_connection=new_conn_v0171
    )

    log.info(f"迁移 memo_id {memo_id} 完成。")
