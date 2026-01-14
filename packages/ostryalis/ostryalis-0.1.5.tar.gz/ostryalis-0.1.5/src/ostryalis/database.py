__all__ = ['database']

from contextlib import contextmanager
from pathlib import Path
import threading
from typing import Iterable, Callable, Any

import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from inceptum import config


class Database:
    def __init__(self):
        self._engine: Engine | None = None
        self._attachments: dict[str, str] = {}
        self._lock = threading.RLock()

    @property
    def engine(self) -> Engine:
        return self._get_engine()

    @contextmanager
    def use_session(self, session: Session | None = None, *, commit: bool = True):
        """
        If `session` is provided, it is reused and never committed/rolled back/closed
        by this context manager.

        If `session` is not provided, a new session is created; it is committed if
        `commit=True`, rolled back on exception, and always closed.
        """
        if session is not None:
            yield session
            return

        self._get_engine() # make sure there is a self._session_factory
        new_session = self._session_factory()
        try:
            yield new_session
            if commit:
                new_session.commit()
        except Exception:
            new_session.rollback()
            raise
        finally:
            new_session.close()

    def attach(self, alias: str, path: str | Path | None = None) -> str:
        """
        Register an attachment alias.

        If `path` is not provided, uses `{base_dir}/{alias}.db`.

        This only registers the mapping; actual ATTACH happens on connect.
        """
        # alias = self._validate_alias(alias)
        if path is None:
            db_path = self._base_dir() / f"{alias}.db"
        else:
            db_path = Path(path).expanduser()
            if not db_path.is_absolute():
                # Relative paths become relative to base dir for predictability.
                db_path = self._base_dir() / db_path

        # Do not create the file here; ATTACH will create it if needed.
        db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            self._attachments.setdefault(alias, str(db_path))
        return alias

    def _get_engine(self) -> Engine:
        with self._lock:
            if self._engine is not None:
                return self._engine

            base_dir = self._base_dir()
            db_url = f"sqlite:///{base_dir / 'main.db'}"

            self._engine = sqlalchemy.create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                future=True,
            )
            sqlalchemy.event.listen(self._engine, "connect", self._sqlite_on_connect)

            self._session_factory = sessionmaker(
                bind=self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                future=True,
            )
            return self._engine

    def _sqlite_on_connect(self, connection, connection_record) -> None:
        with self._lock:
            aliases = list(self._attachments.keys())

        if aliases:
            self._sqlite_attach_aliases(connection, aliases=aliases)

    def _sqlite_attach_aliases(self, connection, *, aliases: Iterable[str]) -> None:
        cur = connection.cursor()
        try:
            cur.execute("PRAGMA database_list")
            already = {row[1] for row in cur.fetchall()}

            for alias in aliases:
                if alias in already:
                    continue

                with self._lock:
                    path = self._attachments.get(alias)
                if path is None:
                    raise KeyError(f"Alias '{alias}' is not registered; call attach() first.")

                path_sql = path.replace("'", "''") # prevent SQL injection
                print(alias, path_sql)
                cur.execute(f"ATTACH DATABASE '{path_sql}' AS {alias}")
        finally:
            cur.close()

    def _base_dir(self) -> Path:
        base_dir = Path(str(config("ostryalis.directory"))).expanduser()
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir


database = Database()
