__all__ = ['search']

from sqlalchemy import text
from .session import SessionManager

def search(q=None, session=None):
    with SessionManager().ensure_session(session) as session:
        rows = session.execute(
            text('''
                SELECT
                    *
                FROM
                    object
                LIMIT
                    100
            ''')
        )
        for row in rows:
            yield dict(row._mapping)
