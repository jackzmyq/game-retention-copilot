from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hashlib
import json
import sqlite3
import os
from tempfile import TemporaryDirectory
from contextlib import closing
from uuid import uuid4
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from src.config import ROOT, RAW, DB, REPORTS
from src.statistics import compare, holm, srm, wilson, required_n
from src.provenance import verify_source


def validate(df):
    required = ["userid","version","sum_gamerounds","retention_1","retention_7"]
    if list(df.columns) != required:
        raise ValueError("Unexpected schema")
    if df.isna().any().any() or df.userid.duplicated().any():
        raise ValueError("Nulls or duplicate user IDs require source review")
    if set(df.version) != {"gate_30","gate_40"}:
        raise ValueError("Unexpected experiment arms")
    if not pd.api.types.is_integer_dtype(df.userid) or not df.userid.gt(0).all():
        raise ValueError("Player IDs must be positive integers")
    if not df.sum_gamerounds.ge(0).all() or not (df.sum_gamerounds % 1 == 0).all():
        raise ValueError("Game rounds must be nonnegative integers")
    if any(not df[c].isin([True,False,0,1]).all() for c in ["retention_1","retention_7"]):
        raise ValueError("Retention must be boolean")


def _build_to(con,reports):
    source_hash=verify_source(RAW.read_bytes())
    df = pd.read_csv(RAW)
    validate(df)
    reports.mkdir(parents=True,exist_ok=True)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript('''
      CREATE TABLE assignments(userid INTEGER PRIMARY KEY, version TEXT NOT NULL CHECK(version IN ('gate_30','gate_40')));
      CREATE TABLE outcomes(userid INTEGER PRIMARY KEY REFERENCES assignments(userid),sum_gamerounds INTEGER NOT NULL CHECK(sum_gamerounds>=0),retention_1 INTEGER NOT NULL CHECK(retention_1 IN (0,1)),retention_7 INTEGER NOT NULL CHECK(retention_7 IN (0,1)));
    ''')
    con.executemany("INSERT INTO assignments VALUES (?,?)", df[["userid","version"]].itertuples(index=False,name=None))
    rows = [(int(r.userid),int(r.sum_gamerounds),int(r.retention_1),int(r.retention_7)) for r in df.itertuples()]
    con.executemany("INSERT INTO outcomes VALUES (?,?,?,?)",rows)
    dfq = pd.DataFrame([
        ("rows",len(df),"PASS","One row per player; not session-level data"),
        ("missing_cells",int(df.isna().sum().sum()),"PASS","No imputation"),
        ("duplicate_ids",int(df.userid.duplicated().sum()),"PASS","Player-level primary key"),
        ("join_rows",len(rows),"PASS","Assignments and outcomes join 1:1"),
        ("max_observed_rounds",int(df.sum_gamerounds.max()),"REVIEW","Extreme value preserved; sensitivity analysis below"),
        ("d7_without_d1",int((df.retention_7 & ~df.retention_1).sum()),"INFO","D7 is not a subset of D1; not a sequential funnel"),
        ("dates_and_regions",0,"UNAVAILABLE","Daily trend, country and exposure checks not possible"),
    ],columns=["check_name","observed","status","note"])
    dfq.to_sql("quality_checks",con,index=False)
    pd.DataFrame([
        ("D1/D7 retention",1,"Provided outcome flags; denominator is all assigned players"),
        ("Experiment effect",1,"Randomized assignment documented by educational source; raw randomization/exposure not auditable"),
        ("Recorded-period engagement",1,"Post-treatment descriptive metric; cannot be an early-churn feature"),
        ("DAU/time anomaly",0,"No event timestamps or calendar dates"),
        ("Country/channel comparison",0,"No country, locale or acquisition channel fields"),
        ("Revenue/ROI",0,"No payment, acquisition cost or revenue fields"),
        ("Early churn prediction",0,"No strictly earlier observation window and later outcome window"),
    ],columns=["metric","available","reason"]).to_sql("capabilities",con,index=False)
    definitions = [
        ("D1", "Source-provided flag: returned one day after installation. All assigned players in denominator; no raw timestamps to re-audit."),
        ("D7", "Source-provided flag: returned seven days after installation, NOT cumulative days 1-7 retention; D7 users need not return on D1."),
        ("delta", "gate_40 minus gate_30. Rates stored as fractions; multiply by 100 for percentage points."),
        ("experiment", "Gate moved from level 30 to 40. Recorded-period rounds do not establish gate exposure or level reached."),
        ("round_band", "Recorded-period game-round grouping for descriptive exploration only; post-treatment and overlaps outcome window. Source text conflicts on 7 vs 14 days; horizon unverified."),
        ("causality", "ITT interpretation conditional on documented randomization, complete outcomes, no interference and consistent exposure; mechanism not identified."),
        ("inference", "Retrospective fixed-horizon two-sided test. D7 is project-selected main outcome, not verified preregistration; Holm over D1/D7."),
    ]
    pd.DataFrame(definitions,columns=["term","definition"]).to_sql("metric_definitions",con,index=False)
    # Install aggregate views after base tables exist; test_results view resolves after table is built.
    con.executescript((ROOT/"sql/metrics.sql").read_text(encoding="utf-8"))
    arms = pd.read_sql_query("SELECT * FROM v_arm_metrics ORDER BY version",con)
    join_n = con.execute("SELECT COUNT(*) FROM assignments JOIN outcomes USING(userid)").fetchone()[0]
    if join_n != len(df):
        raise AssertionError("Join multiplied or dropped players")
    # Independent pandas aggregation reconciles SQL grain and numerators.
    direct = df.groupby("version").agg(players=("userid","size"), retained_d1=("retention_1","sum"), retained_d7=("retention_7","sum"))
    for r in arms.itertuples():
        for key in ["players","retained_d1","retained_d7"]:
            assert int(getattr(r,key)) == int(direct.loc[r.version,key])
    c,t=arms.iloc[0],arms.iloc[1]
    tests=[]
    for metric,col in [("D1","retained_d1"),("D7","retained_d7")]:
        result=compare(int(c[col]),int(c.players),int(t[col]),int(t.players))
        tests.append({"metric":metric, **result})
    adjusted=holm([x["p_value"] for x in tests])
    for r,p in zip(tests,adjusted):
        r["holm_p"]=p
    pd.DataFrame(tests).to_sql("test_results",con,index=False)
    sampling=srm(int(c.players),int(t.players))
    diagnostics=[]
    for name,subset in [("All players",df),("Exclude global maximum (sensitivity only)",df[df.sum_gamerounds<df.sum_gamerounds.max()])]:
        g=subset.groupby("version")
        outcome=g.retention_7.agg(["sum","size"])
        effect=compare(int(outcome.loc["gate_30","sum"]),int(outcome.loc["gate_30","size"]),int(outcome.loc["gate_40","sum"]),int(outcome.loc["gate_40","size"]))
        for version,s in g:
            diagnostics.append({"sample":name,"version":version,"players":len(s),
                "mean_rounds":float(s.sum_gamerounds.mean()),"median_rounds":float(s.sum_gamerounds.median()),
                "p99_rounds":float(s.sum_gamerounds.quantile(.99)),"d7_rate":float(s.retention_7.mean()),
                "d7_delta":effect["delta"]})
    for r in arms.to_dict("records"):
        for day in [1,7]:
            low,high=wilson(r[f"retained_d{day}"],r["players"])
            arms.loc[arms.version==r["version"],f"d{day}_ci_low"]=low
            arms.loc[arms.version==r["version"],f"d{day}_ci_high"]=high
    bands=pd.read_sql_query("SELECT * FROM v_round_bands",con)
    transitions=pd.read_sql_query("SELECT * FROM v_retention_transitions",con)
    build_id=uuid4().hex
    con.execute("CREATE TABLE build_metadata(build_id TEXT NOT NULL,source_sha256 TEXT NOT NULL)")
    con.execute("INSERT INTO build_metadata VALUES (?,?)",(build_id,source_hash))
    summary={"build_id":build_id,"built_at_utc":datetime.now(timezone.utc).isoformat(),
      "source_sha256":source_hash,"rows":len(df),
      "arms":arms.to_dict("records"),"tests":tests,"srm":sampling,
      "quality":dfq.to_dict("records"),"sensitivity":diagnostics,
      "round_bands":bands.to_dict("records"),"transitions":transitions.to_dict("records"),
      "planning":{"baseline":float(c.d7_rate),"absolute_mde":.01,"power":.8,"alpha":.05,
                  "players_per_arm":required_n(float(c.d7_rate),.01)},
      "limitations":["No region, timestamps, revenue, acquisition or exposure logs",
                      "Source materials conflict on rounds horizon (7 vs 14 days); recorded total only, not a verified early-window feature",
                      "Historical tutorial experiment; not a live production feed or current industry benchmark",
                      "Equal allocation assumed, not source-verified; SRM is a screening check",
                      "Recorded-period rounds cannot establish an early causal driver or valid prospective churn predictor",
                      "D7 primary metric chosen retrospectively for this portfolio; experiment preregistration unavailable"]}
    (reports/"analysis.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    arms.to_csv(reports/"arm_metrics.csv",index=False)
    pd.DataFrame(tests).to_csv(reports/"experiment_tests.csv",index=False)
    pd.DataFrame(diagnostics).to_csv(reports/"sensitivity.csv",index=False)
    con.commit()
    return summary


def build():
    DB.parent.mkdir(parents=True,exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)
    # Build and validate away from the live files. A failed calculation preserves them.
    with TemporaryDirectory(prefix=".retention-build-",dir=DB.parent) as stage:
        staged_db=Path(stage)/"retention.sqlite"
        staged_reports=Path(stage)/"reports"
        with closing(sqlite3.connect(staged_db)) as con:
            summary=_build_to(con,staged_reports)
            if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                raise ValueError("Derived database failed integrity check")
        # Windows needs every staged connection closed before rename.
        os.replace(staged_db,DB)
        for report in staged_reports.iterdir():
            os.replace(report,REPORTS/report.name)
    print(json.dumps({"rows":summary["rows"],"build_id":summary["build_id"],"tests":summary["tests"],"srm":summary["srm"]},ensure_ascii=False,indent=2))
    return summary


if __name__ == "__main__":
    build()
