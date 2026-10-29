import sqlite3
import pandas as pd
import pytest
from scipy.stats import chi2_contingency
from src.config import RAW,DB
from src.statistics import compare,holm,wilson,required_n,srm
from src.reporting import load_analysis
from scripts.build_pipeline import validate


def test_counts_and_independent_test():
    df=pd.read_csv(RAW)
    a=load_analysis()
    assert len(df)==90189
    assert df.userid.nunique()==len(df)
    c=df[df.version=="gate_30"]
    t=df[df.version=="gate_40"]
    assert (len(c),len(t))==(44700,45489)
    assert (int(c.retention_7.sum()),int(t.retention_7.sum()))==(8502,8279)
    for day in [1,7]:
        metric=f"retention_{day}"
        k0,k1=int(c[metric].sum()),int(t[metric].sum())
        result=compare(k0,len(c),k1,len(t))
        independent=chi2_contingency([[k0,len(c)-k0],[k1,len(t)-k1]],correction=False)
        assert result["p_value"]==pytest.approx(independent.pvalue,rel=1e-10)
        assert result["delta"]==pytest.approx(t[metric].mean()-c[metric].mean())
    assert a["tests"][1]["ci_low"]<a["tests"][1]["delta"]<a["tests"][1]["ci_high"]<0
    assert a["tests"][0]["ci_low"]<0<a["tests"][0]["ci_high"]
    assert a["tests"][1]["holm_p"]==pytest.approx(.00310849995)


def test_sql_join_preserves_grain():
    con=sqlite3.connect(DB)
    assert con.execute("PRAGMA foreign_key_check").fetchall()==[]
    assert con.execute("SELECT COUNT(*) FROM assignments JOIN outcomes USING(userid)").fetchone()[0]==90189
    assert con.execute("SELECT SUM(players) FROM v_arm_metrics").fetchone()[0]==90189
    assert con.execute("SELECT SUM(players) FROM v_round_bands").fetchone()[0]==90189
    assert con.execute("SELECT SUM(players) FROM v_retention_transitions").fetchone()[0]==90189
    con.close()


def test_sensitivity_not_main_exclusion():
    a=load_analysis()
    full=[r for r in a["sensitivity"] if r["sample"]=="All players"]
    trimmed=[r for r in a["sensitivity"] if r["sample"]!="All players"]
    assert sum(r["players"] for r in full)==90189
    assert sum(r["players"] for r in trimmed)==90188
    assert abs(full[0]["d7_delta"]-trimmed[0]["d7_delta"])<.0001
    assert full[0]["mean_rounds"]-trimmed[0]["mean_rounds"]>1
    assert a["srm"]["p_value"]<.01
    assert a["srm"]["allocation_verified"] is False


def test_edge_cases_and_schema():
    lo,hi=wilson(0,10)
    assert lo==pytest.approx(0,abs=1e-15) and 0<hi<1
    lo,hi=wilson(10,10)
    assert 0<lo<1 and hi==pytest.approx(1)
    assert holm([.04,.001])==pytest.approx([.04,.002])
    assert srm(100,100)["p_value"]==1
    assert required_n(.19,.005)>required_n(.19,.01)
    df=pd.read_csv(RAW,nrows=10)
    with pytest.raises(ValueError):
        validate(pd.concat([df,df.iloc[[0]]]))
    with pytest.raises(ValueError):
        validate(df.drop(columns="retention_7"))
