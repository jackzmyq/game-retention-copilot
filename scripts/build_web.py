"""Export only reviewed aggregate evidence for a GitHub Pages visitor app."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import shutil
from src.config import ROOT,REPORTS
from src.reporting import load_analysis
from src.queries import run_query
from src.statistics import required_n
from src.decision import allocation_check


def build():
    a=load_analysis()
    output=ROOT/"web/assets"
    output.mkdir(parents=True,exist_ok=True)
    queries={
        "arms":"SELECT * FROM v_arm_metrics ORDER BY version",
        "tests":"SELECT * FROM v_test_results ORDER BY metric",
        "quality":"SELECT * FROM v_quality",
        "capabilities":"SELECT * FROM v_capabilities",
        "definitions":"SELECT * FROM v_definitions",
        "transitions":"SELECT * FROM v_retention_transitions",
    }
    evidence={name:run_query(sql) for name,sql in queries.items()}
    data={"analysis":a,"evidence":evidence,
        "planning_grid":{f"{i/10:.1f}":required_n(a["arms"][0]["d7_rate"],i/1000) for i in range(5,21)},
        "allocation_grid":{f"{i/10:.1f}":allocation_check(a["arms"][0]["players"],a["arms"][1]["players"],i/1000) for i in range(490,511)},
        "mode":"browser_offline_rules","raw_players_included":False}
    def inspect(value):
        if isinstance(value,dict):
            if set(value)&{"userid","api_key","email","ip_address"}:
                raise ValueError("Player-level or credential field found in public export")
            for v in value.values():inspect(v)
        elif isinstance(value,list):
            for v in value:inspect(v)
    inspect(data)
    # A JS data assignment allows both GitHub Pages hosting and file:// review.
    payload=json.dumps(data,ensure_ascii=False,separators=(",",":"),allow_nan=False)
    (output/"evidence.js").write_text("window.RETENTION_EVIDENCE="+payload+";\n",encoding="utf-8")
    for lang in ["zh","en"]:
        shutil.copy2(REPORTS/f"decision_brief_{lang}.md",output/f"decision_brief_{lang}.md")
    pdf=ROOT/"output/马延青_游戏分析项目介绍.pdf"
    if pdf.exists():shutil.copy2(pdf,output/"project_brief.pdf")
    (ROOT/"web/.nojekyll").write_text("",encoding="utf-8")
    print("Visitor app exported with aggregate evidence only; no API, login, database service or chat persistence.")
    return data


if __name__=="__main__":build()
