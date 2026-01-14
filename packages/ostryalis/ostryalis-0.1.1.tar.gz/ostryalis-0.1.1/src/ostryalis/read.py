__all__ = ['read']

from sqlalchemy import text
from .session import SessionManager

def search(q=None, session=None):
    with SessionManager.ensure_session(session) as session:
        result = session.execute(
            text('''
                SELECT
                    *
                FROM
                    object
                LIMIT
                    100
            ''')
        )
        if row := result.one_or_none():
            return dict(row._mapping)

