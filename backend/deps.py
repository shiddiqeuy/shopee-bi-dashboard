"""FastAPI dependencies — provides a per-request repository from the connection pool."""

from collections.abc import Generator

from database.connection import get_connection, release_connection
from database.repository import DuckDBRepository


def get_repo() -> Generator[DuckDBRepository, None, None]:
    """Yield a DuckDBRepository backed by a pooled connection.

    The connection is automatically returned to the pool when the request ends.
    """
    conn = get_connection()
    try:
        yield DuckDBRepository(conn)
    finally:
        release_connection(conn)
