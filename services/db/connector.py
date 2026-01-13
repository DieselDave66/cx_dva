from functools import lru_cache
from typing import Dict, List, Optional, Union, Any, Sequence
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config
import time
import logging

logger = logging.getLogger(__name__)

cfg = Config()

QUERY_TIMEOUT_SECONDS = 60

MARKERS = {
    "INVALID_STATE",
    "Invalid SessionHandle",
    "Session has been closed",
    "Cursor closed",
    "Session expired",
    "Endpoint is in a degraded state",
    "Temporarily Unavailable",
    "SERVICE_UNAVAILABLE",
}

@lru_cache(maxsize=1)
def get_connection(warehouse_id: str):

    http_path = f"/sql/1.0/warehouses/{warehouse_id}"
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def close_connections():
    get_connection.cache_clear()

def is_transient_session_error(e: Exception) -> bool:
    msg = str(e)
    return any(m in msg for m in MARKERS)


def query(
    sql_query: str, warehouse_id: str, params: Optional[Sequence[Any]] = None, *, as_dict: bool = True, wait_until_ready: bool = True, max_wait_seconds: float = 300.0, backoff_initial: float = 0.8, backoff_max: float = 5.0,
) -> Union[List[Dict], pd.DataFrame]:

    start = time.monotonic()
    attempt = 0

    while True:
        attempt +=1

        if time.monotonic() - start > QUERY_TIMEOUT_SECONDS:
            raise TimeoutError("Query execution exceeded timeout limit")

        try:

            conn = get_connection(warehouse_id)

            with conn.cursor() as cursor:

                if params is None:
                    cursor.execute(sql_query)
                else:
                    cursor.execute(sql_query, params)

                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description]

                if as_dict:
                    return [dict(zip(columns, row)) for row in result]
            
                else:
                    return pd.DataFrame(result, columns=columns)

        except Exception as e:
            if not wait_until_ready or not is_transient_session_error(e):
                raise
                
            elapsed = time.monotonic() - start
            if elapsed >= max_wait_seconds:
                logger.error(
                    "Timeour expired (%.1fs) waiting for the warehouse to be ready. Last error: %s",
                    elapsed, e
                )
                raise

            
            try:
                try:
                    conn.close()
                except Exception:
                    pass
                close_connections()
                conn = get_connection(warehouse_id)
            except Exception as rexc:
                logger.error("Failed recreating the connection: %s", rexc)

            sleep_s = min(backoff_initial * (2 ** (attempt - 1)), backoff_max)
            time.sleep(sleep_s)
            continue