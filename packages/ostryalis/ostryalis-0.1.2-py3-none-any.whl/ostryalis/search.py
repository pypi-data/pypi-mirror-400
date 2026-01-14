__all__ = ['search']

from sqlalchemy import text
from .database import Database

def search(q=None, session=None):
    with Database().session_scope(session) as session:
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
