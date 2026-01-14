__all__ = ['read']

from sqlalchemy import text
from .database import database

def search(q=None, session=None):
    with database.session_scope(session) as session:
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

