__all__ = ["Database", "database"]

import re
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Callable, Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from inceptum import config


_ALIAS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RESERVED_ALIASES = {"main", "temp"}

# Key used in SQLAlchemy ConnectionRecord.info
_ATTACHED_CACHE_KEY = "ostryalis_sqlite_attached_aliases"

# Key used in SQLAlchemy ConnectionRecord.info
_UDF_CACHE_KEY = "ostryalis_sqlite_installed_udfs"

# Name validation for UDFs: keep it conservative and consistent with aliases.
_UDF_NAME_RE = _ALIAS_RE


class Database:
    """
    Database façade that owns engine/session/attachment/UDF state.

    Applications can use the module-level `database` instance, while tests can
    instantiate `Database()` freely for isolated state.
    """

    def __init__(self, *, config_getter: Callable[[str], object] | None = None):
        self._config = config_getter or config

        self._engine: Engine | None = None
        self._SessionLocal: sessionmaker | None = None

        # alias -> absolute path string
        self._attachments: dict[str, str] = {}

        # (name, arity) -> python callable
        self._udfs: dict[tuple[str, int], Callable[..., Any]] = {}

        self._lock = threading.RLock()

    # Public API

    @property
    def engine(self) -> Engine:
        return self._get_engine()

    @contextmanager
    def session_scope(
        self,
        session: Session | None = None,
        *,
        commit: bool = True,
        require_attached: Iterable[str] | None = None,
        require_functions: Iterable[tuple[str, int]] | None = None,
    ):
        """
        If `session` is provided, it is reused and never committed/rolled back/closed
        by this context manager.

        If `session` is not provided, a new session is created; it is committed if
        `commit=True`, rolled back on exception, and always closed.
        """
        if session is not None:
            self._ensure_required_attached(session, require_attached)
            self._ensure_required_functions(session, require_functions)
            yield session
            return

        factory = self._get_session_factory()
        new_session = factory()
        try:
            self._ensure_required_attached(new_session, require_attached)
            self._ensure_required_functions(new_session, require_functions)
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

        This only registers the mapping; actual ATTACH happens on connect
        and when `require_attached` is used.
        """
        alias = self._validate_alias(alias)
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

    def register_function(
        self,
        name: str,
        arity: int,
        func: Callable[..., Any],
    ) -> tuple[str, int]:
        """
        Register a SQLite user-defined function (UDF) by (name, arity).

        Registration is manager-level only; installation happens on engine connect
        and when `require_functions` is used.
        """
        name = self._validate_udf_name(name)
        arity = self._validate_udf_arity(arity)
        if not callable(func):
            raise ValueError("func must be callable.")

        key = (name, arity)
        with self._lock:
            # Idempotent: first one wins unless you explicitly change it.
            self._udfs.setdefault(key, func)
        return key

    # Private helpers

    def _get_engine(self) -> Engine:
        with self._lock:
            if self._engine is not None:
                return self._engine

            base_dir = self._base_dir()
            db_url = f"sqlite:///{base_dir / 'main.db'}"

            self._engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                future=True,
            )
            event.listen(self._engine, "connect", self._sqlite_on_connect)

            self._SessionLocal = sessionmaker(
                bind=self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                future=True,
            )
            return self._engine

    def _validate_alias(self, alias: str) -> str:
        if not isinstance(alias, str) or not alias.strip():
            raise ValueError("Database alias must be a non-empty string.")
        alias = alias.strip()
        if alias in _RESERVED_ALIASES:
            raise ValueError(f"Database alias '{alias}' is reserved by SQLite.")
        if not _ALIAS_RE.match(alias):
            raise ValueError("Database alias must match ^[A-Za-z_][A-Za-z0-9_]*$.")
        return alias

    def _validate_udf_name(self, name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Function name must be a non-empty string.")
        name = name.strip()
        if not _UDF_NAME_RE.match(name):
            raise ValueError("Function name must match ^[A-Za-z_][A-Za-z0-9_]*$.")
        return name

    def _validate_udf_arity(self, arity: int) -> int:
        if not isinstance(arity, int):
            raise ValueError("Function arity must be an integer.")
        # sqlite3.create_function supports -1 for varargs, but that collides with the
        # “overload by arity” requirement in confusing ways
        if arity < 0:
            raise ValueError("Function arity must be >= 0.")
        return arity

    def _base_dir(self) -> Path:
        base_dir = Path(str(self._config("ostryalis.directory"))).expanduser()
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def _escape_sqlite_string_literal(self, value: str) -> str:
        # SQLite string literal escaping: '' inside '...'
        return value.replace("'", "''")

    def _get_attached_cache(self, connection_record) -> set[str]:
        info = connection_record.info
        cache = info.get(_ATTACHED_CACHE_KEY)
        if cache is None:
            cache = set()
            info[_ATTACHED_CACHE_KEY] = cache
        return cache

    def _get_udf_cache(self, connection_record) -> set[tuple[str, int]]:
        info = connection_record.info
        cache = info.get(_UDF_CACHE_KEY)
        if cache is None:
            cache = set()
            info[_UDF_CACHE_KEY] = cache
        return cache

    def _sqlite_install_udfs(
        self,
        dbapi_connection,
        *,
        required: Iterable[tuple[str, int]],
        connection_record=None,
    ) -> None:
        cache: set[tuple[str, int]] | None = None
        if connection_record is not None:
            cache = self._get_udf_cache(connection_record)
            required = [k for k in required if k not in cache]
            if not required:
                return

        for (name, arity) in required:
            with self._lock:
                func = self._udfs.get((name, arity))
            if func is None:
                raise KeyError(
                    f"Function '{name}/{arity}' is not registered; call register_function() first."
                )
            dbapi_connection.create_function(name, arity, func)
            if cache is not None:
                cache.add((name, arity))

    def _sqlite_attach_aliases(
        self,
        dbapi_connection,
        *,
        aliases: Iterable[str],
        connection_record=None,
    ) -> None:
        cache: set[str] | None = None
        if connection_record is not None:
            cache = self._get_attached_cache(connection_record)
            aliases = [a for a in aliases if a not in cache]
            if not aliases:
                return

        cur = dbapi_connection.cursor()
        try:
            cur.execute("PRAGMA database_list")
            already = {row[1] for row in cur.fetchall()}

            for alias in aliases:
                if alias in already:
                    if cache is not None:
                        cache.add(alias)
                    continue

                with self._lock:
                    path = self._attachments.get(alias)
                if path is None:
                    raise KeyError(f"Alias '{alias}' is not registered; call attach() first.")

                path_sql = self._escape_sqlite_string_literal(path)
                cur.execute(f"ATTACH DATABASE '{path_sql}' AS {alias}")

                if cache is not None:
                    cache.add(alias)
        finally:
            cur.close()

    def _sqlite_on_connect(self, dbapi_connection, connection_record) -> None:
        with self._lock:
            aliases = list(self._attachments.keys())
            udf_keys = list(self._udfs.keys())

        if aliases:
            self._sqlite_attach_aliases(
                dbapi_connection,
                aliases=aliases,
                connection_record=connection_record,
            )

        if udf_keys:
            self._sqlite_install_udfs(
                dbapi_connection,
                required=udf_keys,
                connection_record=connection_record,
            )

    def _get_session_factory(self) -> sessionmaker:
        if self._SessionLocal is None:
            self._get_engine()
        assert self._SessionLocal is not None
        return self._SessionLocal

    def _get_connection_record_from_sa_connection(self, sa_connection) -> object | None:
        try:
            fairy = sa_connection.connection  # _ConnectionFairy
            return getattr(fairy, "_connection_record", None)
        except Exception:
            return None

    def _ensure_required_attached(
        self,
        session: Session,
        require_attached: Iterable[str] | None,
    ) -> None:
        if not require_attached:
            return
        for alias in require_attached:
            self.attach(alias)

        sa_conn = session.connection()
        record = self._get_connection_record_from_sa_connection(sa_conn)
        self._sqlite_attach_aliases(
            sa_conn.connection,
            aliases=[self._validate_alias(a) for a in require_attached],
            connection_record=record,
        )

    def _ensure_required_functions(
        self,
        session: Session,
        require_functions: Iterable[tuple[str, int]] | None,
    ) -> None:
        if not require_functions:
            return

        normalized: list[tuple[str, int]] = [
            (self._validate_udf_name(n), self._validate_udf_arity(a))
            for (n, a) in require_functions
        ]

        sa_conn = session.connection()
        record = self._get_connection_record_from_sa_connection(sa_conn)
        self._sqlite_install_udfs(
            sa_conn.connection,
            required=normalized,
            connection_record=record,
        )


# Application-global instance
database = Database()
