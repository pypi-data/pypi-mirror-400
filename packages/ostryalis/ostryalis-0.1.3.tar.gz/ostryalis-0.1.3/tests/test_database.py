import threading

import pytest
import sqlalchemy as sa


@pytest.fixture()
def mgr(tmp_path):
    """
    Provide an isolated Database instance per test by injecting its config getter.
    This avoids monkeypatching and avoids any test-only methods.
    """
    from ostryalis.database import Database

    m = Database(config_getter=lambda key: str(tmp_path))
    yield m

    # Not strictly required for isolation (new object per test), but helps release handles.
    try:
        if getattr(m, "_engine", None) is not None:
            m._engine.dispose()
    except Exception:
        pass


def _attached_aliases_via_pragma(dbapi_conn):
    cur = dbapi_conn.cursor()
    try:
        cur.execute("PRAGMA database_list")
        return {row[1] for row in cur.fetchall()}
    finally:
        cur.close()


def test_validate_alias_rejects_empty(mgr):
    with pytest.raises(ValueError):
        mgr._validate_alias("")
    with pytest.raises(ValueError):
        mgr._validate_alias("   ")


def test_validate_alias_rejects_reserved(mgr):
    with pytest.raises(ValueError):
        mgr._validate_alias("main")
    with pytest.raises(ValueError):
        mgr._validate_alias("temp")


def test_validate_alias_rejects_invalid_identifier(mgr):
    with pytest.raises(ValueError):
        mgr._validate_alias("1abc")
    with pytest.raises(ValueError):
        mgr._validate_alias("foo-bar")
    with pytest.raises(ValueError):
        mgr._validate_alias("foo bar")


def test_validate_alias_normalizes_whitespace(mgr):
    assert mgr._validate_alias("  abc_123  ") == "abc_123"


def test_register_required_aliases_creates_dir_and_paths(mgr, tmp_path):
    aliases = [mgr.attach("a"), mgr.attach("b_2")]
    assert aliases == ["a", "b_2"]

    assert tmp_path.exists()
    assert mgr._attachments["a"] == str(tmp_path / "a.db")
    assert mgr._attachments["b_2"] == str(tmp_path / "b_2.db")


def test_get_engine_creates_main_db_and_session_factory(mgr, tmp_path):
    engine = mgr.engine
    assert engine is not None

    expected = tmp_path / "main.db"
    with engine.connect():
        pass
    assert expected.exists()


def test_sqlite_on_connect_attaches_known_aliases(mgr):
    mgr.attach("alpha")
    mgr.attach("beta")
    engine = mgr.engine

    with engine.connect() as conn:
        dbapi = conn.connection
        names = _attached_aliases_via_pragma(dbapi)
        assert "alpha" in names
        assert "beta" in names


def test_session_scope_commit_true_persists_changes(mgr):
    engine = mgr.engine

    with mgr.session_scope(commit=True) as s:
        s.execute(sa.text("CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, v TEXT)"))
        s.execute(sa.text("DELETE FROM t"))
        s.execute(sa.text("INSERT INTO t (v) VALUES ('x')"))

    with engine.connect() as c:
        row = c.execute(sa.text("SELECT COUNT(*) FROM t")).scalar_one()
        assert row == 1


def test_session_scope_commit_false_does_not_commit(mgr):
    engine = mgr.engine
    with engine.begin() as c:
        c.execute(sa.text("CREATE TABLE IF NOT EXISTS t2 (id INTEGER PRIMARY KEY, v TEXT)"))
        c.execute(sa.text("DELETE FROM t2"))

    with mgr.session_scope(commit=False) as s:
        s.execute(sa.text("INSERT INTO t2 (v) VALUES ('y')"))

    with engine.connect() as c:
        row = c.execute(sa.text("SELECT COUNT(*) FROM t2")).scalar_one()
        assert row == 0


def test_session_scope_rollback_on_exception(mgr):
    engine = mgr.engine
    with engine.begin() as c:
        c.execute(sa.text("CREATE TABLE IF NOT EXISTS t3 (id INTEGER PRIMARY KEY, v TEXT)"))
        c.execute(sa.text("DELETE FROM t3"))

    with pytest.raises(RuntimeError):
        with mgr.session_scope(commit=True) as s:
            s.execute(sa.text("INSERT INTO t3 (v) VALUES ('z')"))
            raise RuntimeError("boom")

    with engine.connect() as c:
        row = c.execute(sa.text("SELECT COUNT(*) FROM t3")).scalar_one()
        assert row == 0


def test_session_scope_with_existing_session_does_not_close_it(mgr):
    factory = mgr._get_session_factory()
    s = factory()
    try:
        with mgr.session_scope(s, require_attached=["xalias"]) as s2:
            assert s2 is s
            sa_conn = s2.connection()
            names = _attached_aliases_via_pragma(sa_conn.connection)
            assert "xalias" in names

        s.execute(sa.text("SELECT 1")).scalar_one()
    finally:
        s.close()


def test_attachment_cache_skips_repeated_pragma_calls(mgr, monkeypatch):
    _ = mgr.engine

    real = mgr._sqlite_attach_aliases
    pragma_counter = {"count": 0}

    def wrapped(dbapi_connection, *, aliases, connection_record=None):
        if not hasattr(dbapi_connection, "set_trace_callback"):
            pytest.skip("DB-API connection does not support set_trace_callback; cannot count PRAGMA.")

        def trace_cb(stmt: str):
            if stmt.strip().lower() == "pragma database_list":
                pragma_counter["count"] += 1

        prev = dbapi_connection.set_trace_callback(trace_cb)
        try:
            return real(dbapi_connection, aliases=aliases, connection_record=connection_record)
        finally:
            dbapi_connection.set_trace_callback(prev)

    monkeypatch.setattr(mgr, "_sqlite_attach_aliases", wrapped)

    with mgr.session_scope(require_attached=["cachetest"]) as s:
        sa_conn = s.connection()
        names = _attached_aliases_via_pragma(sa_conn.connection)
        assert "cachetest" in names

    first = pragma_counter["count"]
    assert first >= 1

    with mgr.session_scope(require_attached=["cachetest"]) as s:
        sa_conn = s.connection()
        names = _attached_aliases_via_pragma(sa_conn.connection)
        assert "cachetest" in names

    second = pragma_counter["count"]
    assert second == first


def test_attachment_cache_is_per_connection(mgr, monkeypatch, tmp_path):
    engine = mgr.engine

    pragma_counter = {"count": 0}
    real = mgr._sqlite_attach_aliases

    def traced(dbapi_connection, *, aliases, connection_record=None):
        cb_count = {"n": 0}

        def trace_cb(stmt):
            if stmt.strip().lower() == "pragma database_list":
                cb_count["n"] += 1

        prev = None
        if hasattr(dbapi_connection, "set_trace_callback"):
            prev = dbapi_connection.set_trace_callback(trace_cb)
        try:
            return real(dbapi_connection, aliases=aliases, connection_record=connection_record)
        finally:
            if hasattr(dbapi_connection, "set_trace_callback"):
                dbapi_connection.set_trace_callback(prev)
            pragma_counter["count"] += cb_count["n"]

    monkeypatch.setattr(mgr, "_sqlite_attach_aliases", traced)

    with mgr.session_scope(require_attached=["perconn"]) as s:
        pass

    first = pragma_counter["count"]
    assert first >= 1

    engine.dispose()

    from ostryalis.database import Database
    mgr2 = Database(config_getter=lambda key: str(tmp_path))
    monkeypatch.setattr(mgr2, "_sqlite_attach_aliases", traced)
    _ = mgr2.engine

    with mgr2.session_scope(require_attached=["perconn"]) as s:
        pass

    second = pragma_counter["count"]
    assert second > first


def test_concurrency_register_required_aliases_is_thread_safe(mgr):
    names = [f"a{i}" for i in range(20)]
    errors = []
    barrier = threading.Barrier(parties=10)

    def worker(tid: int):
        try:
            barrier.wait()
            local = names[tid % 5 : tid % 5 + 10]
            for a in local:
                mgr.attach(a)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors: {errors!r}"

    for alias, path in mgr._attachments.items():
        assert path.endswith(f"{alias}.db")


def test_concurrency_session_scope_require_attached_no_exceptions(mgr):
    _ = mgr.engine
    mgr.attach("conc")

    errors = []
    barrier = threading.Barrier(parties=10)

    def worker():
        try:
            barrier.wait()
            with mgr.session_scope(require_attached=["conc"], commit=False) as s:
                s.execute(sa.text("SELECT 1")).scalar_one()
                sa_conn = s.connection()
                cur = sa_conn.connection.cursor()
                try:
                    cur.execute("PRAGMA database_list")
                    names = {row[1] for row in cur.fetchall()}
                finally:
                    cur.close()
                assert "conc" in names
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors: {errors!r}"


def test_concurrency_mixed_alias_registration_and_attachment(mgr):
    _ = mgr.engine

    aliases = [f"m{i}" for i in range(10)]
    errors = []
    barrier = threading.Barrier(parties=20)

    def registrar(i: int):
        try:
            barrier.wait()
            mgr.attach(aliases[i])
        except Exception as e:
            errors.append(e)

    def attacher(i: int):
        try:
            barrier.wait()
            with mgr.session_scope(require_attached=[aliases[i]], commit=False) as s:
                s.execute(sa.text("SELECT 1")).scalar_one()
        except Exception as e:
            errors.append(e)

    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=registrar, args=(i,)))
        threads.append(threading.Thread(target=attacher, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors: {errors!r}"
    for a in aliases:
        assert a in mgr._attachments


# -----------------------
# SQLite UDF tests
# -----------------------

def test_validate_udf_name_rejects_empty(mgr):
    with pytest.raises(ValueError):
        mgr._validate_udf_name("")
    with pytest.raises(ValueError):
        mgr._validate_udf_name("   ")


def test_validate_udf_name_rejects_invalid_identifier(mgr):
    with pytest.raises(ValueError):
        mgr._validate_udf_name("1abc")
    with pytest.raises(ValueError):
        mgr._validate_udf_name("foo-bar")
    with pytest.raises(ValueError):
        mgr._validate_udf_name("foo bar")


def test_validate_udf_arity_rejects_negative(mgr):
    with pytest.raises(ValueError):
        mgr._validate_udf_arity(-1)


def test_register_function_and_require_functions_installs_and_executes(mgr):
    _ = mgr.engine

    def add1(x):
        return x + 1

    mgr.register_function("add1", 1, add1)

    with mgr.session_scope(require_functions=[("add1", 1)], commit=False) as s:
        v = s.execute(sa.text("SELECT add1(41)")).scalar_one()
        assert v == 42


def test_udf_overload_by_arity_works(mgr):
    _ = mgr.engine

    def f1(x):
        return x + 10

    def f2(x, y):
        return x + y + 100

    mgr.register_function("ovl", 1, f1)
    mgr.register_function("ovl", 2, f2)

    with mgr.session_scope(require_functions=[("ovl", 1), ("ovl", 2)], commit=False) as s:
        a = s.execute(sa.text("SELECT ovl(5)")).scalar_one()
        b = s.execute(sa.text("SELECT ovl(5, 7)")).scalar_one()
        assert a == 15
        assert b == 112


def test_sqlite_on_connect_installs_registered_udfs(mgr):
    def mul2(x):
        return x * 2

    mgr.register_function("mul2", 1, mul2)
    engine = mgr.engine

    with engine.connect() as c:
        v = c.execute(sa.text("SELECT mul2(21)")).scalar_one()
        assert v == 42


def test_require_functions_missing_registration_raises_keyerror(mgr):
    _ = mgr.engine
    with pytest.raises(KeyError):
        with mgr.session_scope(require_functions=[("nope", 1)], commit=False):
            pass


def test_udf_cache_is_per_connection(mgr, monkeypatch, tmp_path):
    engine = mgr.engine

    def inc(x):
        return x + 1

    mgr.register_function("inc", 1, inc)

    real = mgr._sqlite_install_udfs
    counter = {"count": 0}

    def wrapped(dbapi_connection, *, required, connection_record=None):
        counter["count"] += 1
        return real(dbapi_connection, required=required, connection_record=connection_record)

    monkeypatch.setattr(mgr, "_sqlite_install_udfs", wrapped)

    with mgr.session_scope(require_functions=[("inc", 1)], commit=False):
        pass

    first = counter["count"]
    assert first >= 1

    engine.dispose()

    from ostryalis.database import Database
    mgr2 = Database(config_getter=lambda key: str(tmp_path))
    _ = mgr2.engine
    mgr2.register_function("inc", 1, inc)
    monkeypatch.setattr(mgr2, "_sqlite_install_udfs", wrapped)

    with mgr2.session_scope(require_functions=[("inc", 1)], commit=False):
        pass

    second = counter["count"]
    assert second > first


def test_concurrency_register_function_is_thread_safe(mgr):
    _ = mgr.engine
    errors = []
    barrier = threading.Barrier(parties=10)

    def make_func(k):
        return lambda x, _k=k: x + _k

    def worker(i: int):
        try:
            barrier.wait()
            mgr.register_function("cf", i % 3, make_func(i))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors: {errors!r}"
    assert len([k for k in mgr._udfs.keys() if k[0] == "cf"]) <= 3


def test_concurrency_session_scope_require_functions_no_exceptions(mgr):
    _ = mgr.engine

    def inc(x):
        return x + 1

    mgr.register_function("inc", 1, inc)

    errors = []
    barrier = threading.Barrier(parties=10)

    def worker():
        try:
            barrier.wait()
            with mgr.session_scope(require_functions=[("inc", 1)], commit=False) as s:
                assert s.execute(sa.text("SELECT inc(41)")).scalar_one() == 42
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors: {errors!r}"
