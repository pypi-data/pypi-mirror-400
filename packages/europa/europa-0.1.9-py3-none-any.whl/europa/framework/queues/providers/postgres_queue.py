import json
from typing import Optional, Dict, Any

from europa.framework.queues.providers.api import BaseQueue, QueueItem

# import psycopg2
# from psycopg2.extras import RealDictCursor

class PostgresQueue(BaseQueue):
    def __init__(self, conn_params: Dict[str, Any], table_name: str):
        
        # Lazy load psycopg2 and RealDictCursor during initialization
        global psycopg2, RealDictCursor
        import psycopg2
        from psycopg2.extras import RealDictCursor

        self.conn_params = conn_params
        self.table_name = table_name
        self._ensure_table_exists()

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _ensure_table_exists(self):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id VARCHAR(36) PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL,
                    status INTEGER DEFAULT 0 NOT NULL,
                    payload JSONB NOT NULL,
                    metadata JSONB
                )
                """
                )
                conn.commit()

    def enqueue(self, item: QueueItem) -> str:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.table_name} (id, created_at, status, payload, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        item.id,
                        item.created_at,
                        0,  # status: 0 = pending
                        json.dumps(item.payload),
                        json.dumps(item.metadata),
                    ),
                )
                conn.commit()
        return item.id

    def dequeue(self) -> Optional[QueueItem]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    f"""
                    UPDATE {self.table_name}
                    SET status = 1
                    WHERE id = (
                        SELECT id
                        FROM {self.table_name}
                        WHERE status = 0
                        ORDER BY created_at
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    RETURNING id, created_at, payload, metadata
                    """
                )
                row = cursor.fetchone()
                conn.commit()

                if row:
                    return QueueItem.from_dict(
                        {
                            "id": row["id"],
                            "created_at": row["created_at"].isoformat(),
                            "payload": row["payload"],
                            "metadata": row["metadata"],
                        }
                    )
                return None

    def peek(self) -> Optional[QueueItem]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    f"""
                    SELECT id, created_at, payload, metadata
                    FROM {self.table_name}
                    WHERE status = 0
                    ORDER BY created_at
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()

                if row:
                    return QueueItem.from_dict(
                        {
                            "id": row["id"],
                            "created_at": row["created_at"].isoformat(),
                            "payload": json.loads(row["payload"]),
                            "metadata": json.loads(row["metadata"]),
                        }
                    )
                return None

    def size(self) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {self.table_name}
                    WHERE status = 0
                    """
                )
                return cursor.fetchone()[0]

    def clear(self) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {self.table_name}
                    WHERE status = 0
                    """
                )
                conn.commit()
