"""Read-only aggregate SQL boundary for untrusted model output."""
import sqlite3
import time
import math
import sqlglot
from sqlglot import exp
from src.config import DB

ALLOWED_VIEWS = {
    "v_arm_metrics", "v_round_bands", "v_retention_transitions", "v_quality",
    "v_capabilities", "v_test_results", "v_definitions",
}
ALLOWED_FUNCTIONS = {"count","sum","avg","min","max","round","abs","coalesce",
    "nullif","ifnull","lower","upper","length","like","glob","typeof",
    "substr","substring","trim","cast","total"}


class QueryRejected(ValueError):
    pass


def validate_sql(sql):
    if not isinstance(sql,str) or not sql.strip() or len(sql)>6000:
        raise QueryRejected("SQL must be a nonempty query of at most 6,000 characters")
    try:
        trees=sqlglot.parse(sql,read="sqlite")
    except Exception as exc:
        raise QueryRejected("SQL could not be parsed") from exc
    if len(trees)!=1 or not isinstance(trees[0],exp.Select):
        raise QueryRejected("Exactly one SELECT statement is allowed")
    tree=trees[0]
    forbidden=(exp.Insert,exp.Update,exp.Delete,exp.Create,exp.Drop,exp.Alter,
               exp.Command,exp.Pragma,exp.Attach,exp.Detach)
    if any(isinstance(node,forbidden) for node in tree.walk()):
        raise QueryRejected("Only read-only SELECT is allowed")
    if tree.find(exp.With) and tree.find(exp.With).args.get("recursive"):
        raise QueryRejected("Recursive queries are not allowed")
    ctes={c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}
    references=list(tree.find_all(exp.Table))
    if not references:
        raise QueryRejected("Query must read an approved evidence view")
    # Reject CTE aliases that shadow real views and external/database-qualified tables.
    if ctes & ALLOWED_VIEWS:
        raise QueryRejected("CTE names cannot shadow evidence views")
    if not any(t.name.lower() in ALLOWED_VIEWS for t in references):
        raise QueryRejected("Query must read an approved evidence view")
    for table in references:
        if table.db or table.catalog or table.name.lower() not in ALLOWED_VIEWS|ctes:
            raise QueryRejected("Only approved aggregate evidence views may be queried")
    return tree.sql(dialect="sqlite")


def run_query(sql, db_path=DB, max_rows=200, timeout=3):
    if type(max_rows) is not int or not 1<=max_rows<=200:
        raise QueryRejected("Row limit must be an integer from 1 to 200")
    if type(timeout) not in (float,int) or not math.isfinite(timeout) or not 0<timeout<=3:
        raise QueryRejected("Timeout must be greater than zero and no more than 3 seconds")
    normalized=validate_sql(sql)
    started=time.monotonic()
    uri=db_path.resolve().as_uri()+"?mode=ro"
    connection=sqlite3.connect(uri,uri=True,timeout=timeout)
    connection.execute("PRAGMA query_only=ON")
    connection.enable_load_extension(False)
    # Bound a single SQL value/output row in addition to the wall-clock and row caps.
    connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH,1_000_000)
    connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH,7000)
    connection.setlimit(sqlite3.SQLITE_LIMIT_COLUMN,100)
    connection.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH,64)
    connection.setlimit(sqlite3.SQLITE_LIMIT_COMPOUND_SELECT,8)

    def authorize(action,arg1,arg2,database,source):
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            # Internal base reads are permitted only through an allowed view.
            return sqlite3.SQLITE_OK if (arg1 in ALLOWED_VIEWS or source in ALLOWED_VIEWS) else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if (arg2 or "").lower() in ALLOWED_FUNCTIONS else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_DENY

    connection.set_authorizer(authorize)
    connection.set_progress_handler(lambda:int(time.monotonic()-started>timeout),1000)
    try:
        cursor=connection.execute(f"SELECT * FROM ({normalized}) LIMIT {max_rows+1}")
        columns=[d[0] for d in cursor.description]
        data=cursor.fetchmany(max_rows+1)
        return {"sql":normalized,"columns":columns,
                "rows":[dict(zip(columns,row)) for row in data[:max_rows]],
                "row_count":min(len(data),max_rows),"truncated":len(data)>max_rows,
                "elapsed_ms":round((time.monotonic()-started)*1000,2)}
    except sqlite3.Error as exc:
        raise QueryRejected("Query failed validation or execution: "+str(exc)) from exc
    finally:
        connection.close()


def schema_description(db_path=DB):
    con=sqlite3.connect(db_path.resolve().as_uri()+"?mode=ro",uri=True)
    result={view:[{"name":r[1],"type":r[2]} for r in con.execute(f"PRAGMA table_info({view})")]
            for view in sorted(ALLOWED_VIEWS)}
    con.close()
    return result
