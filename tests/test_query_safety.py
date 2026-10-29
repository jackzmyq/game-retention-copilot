import hashlib
import pytest
from src.config import DB
from src.queries import run_query,QueryRejected


@pytest.mark.parametrize("sql",[
    "DROP TABLE outcomes", "DELETE FROM outcomes", "PRAGMA table_info(outcomes)",
    "SELECT * FROM assignments", "SELECT userid FROM outcomes",
    "SELECT * FROM sqlite_master", "SELECT * FROM main.v_arm_metrics",
    "SELECT * FROM v_arm_metrics; DROP TABLE outcomes",
    "ATTACH DATABASE ':memory:' AS other", "VACUUM",
    "SELECT load_extension('x') FROM v_arm_metrics",
    "SELECT readfile('.env') FROM v_arm_metrics",
    "SELECT randomblob(999999999) FROM v_arm_metrics",
    "SELECT printf('%999999999s','x') FROM v_arm_metrics",
    "SELECT format('%999999999s','x') FROM v_arm_metrics",
    "WITH hidden AS (SELECT * FROM outcomes) SELECT * FROM hidden",
    "WITH RECURSIVE t(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM t) SELECT * FROM v_arm_metrics,t",
    "WITH v_arm_metrics AS (SELECT * FROM outcomes) SELECT * FROM v_arm_metrics",
    "SELECT 1 UNION SELECT 2", "", "SELECT 1",
])
def test_reject_unsafe_queries(sql):
    before=hashlib.sha256(DB.read_bytes()).hexdigest()
    with pytest.raises(QueryRejected):
        run_query(sql)
    assert hashlib.sha256(DB.read_bytes()).hexdigest()==before


def test_allowed_queries_and_cte():
    out=run_query("SELECT version,players,d7_rate FROM v_arm_metrics ORDER BY version")
    assert out["row_count"]==2
    assert sum(r["players"] for r in out["rows"])==90189
    assert run_query("WITH m AS (SELECT * FROM v_arm_metrics) SELECT SUM(players) AS n FROM m")["rows"][0]["n"]==90189
    assert run_query("SELECT * FROM v_test_results")["row_count"]==2
    assert run_query("SELECT * FROM v_definitions")["row_count"]>0


def test_result_limit_and_timeout():
    out=run_query("SELECT * FROM v_round_bands",max_rows=3)
    assert out["row_count"]==3 and out["truncated"]
    with pytest.raises(QueryRejected):
        run_query("SELECT count(*) FROM v_round_bands a CROSS JOIN v_round_bands b CROSS JOIN v_round_bands c CROSS JOIN v_round_bands d CROSS JOIN v_round_bands e CROSS JOIN v_round_bands f",timeout=.001)


@pytest.mark.parametrize("kwargs",[{"max_rows":-1},{"max_rows":1000000},{"timeout":float("nan")},{"timeout":30}])
def test_resource_caps_cannot_be_disabled(kwargs):
    with pytest.raises(QueryRejected):
        run_query("SELECT * FROM v_arm_metrics",**kwargs)
