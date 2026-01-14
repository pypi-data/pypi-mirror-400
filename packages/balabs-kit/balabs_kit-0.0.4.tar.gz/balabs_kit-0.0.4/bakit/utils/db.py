import logging
from contextlib import asynccontextmanager

from tortoise.connection import connections

log = logging.getLogger(__name__)


def _convert_named_placeholders(sql, sql_vars):
    sql_vars = sql_vars or []
    if isinstance(sql_vars, dict):
        # Convert named placeholders (%(key)s) to $1, $2, ...
        param_count = 1
        for key in sql_vars:
            sql = sql.replace(f"%({key})s", f"${param_count}")
            param_count += 1
        sql_vars = list(sql_vars.values())
    return sql, sql_vars


async def fetch_one_sql(sql, sql_vars=None, db_alias="default"):
    sql, sql_vars = _convert_named_placeholders(sql, sql_vars)
    conn = connections.get(db_alias)
    rows = await conn.execute_query_dict(sql, sql_vars)
    return rows[0] if rows else {}


async def fetch_all_sql(sql, sql_vars=None, db_alias="default"):
    sql, sql_vars = _convert_named_placeholders(sql, sql_vars)
    conn = connections.get(db_alias)
    rows = await conn.execute_query_dict(sql, sql_vars)
    return rows


@asynccontextmanager
async def streaming_fetch_all_sql(
    sql, sql_vars=None, db_alias="default", prefetch=2000
):
    """
    Example usage:
        async with streaming_fetch_all_sql(sql) as cursor:
            async for record in cursor:
                print(record)
    """
    sql_vars = sql_vars or []
    sql, sql_vars = _convert_named_placeholders(sql, sql_vars)
    db_client = connections.get(db_alias)

    async with db_client.acquire_connection() as con, con.transaction():
        cursor = con.cursor(sql, *sql_vars, prefetch=prefetch)
        yield cursor
