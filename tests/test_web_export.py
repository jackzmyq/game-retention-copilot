from scripts.build_web import build
from src.reporting import load_analysis


def test_browser_export_uses_current_aggregate_build():
    data=build()
    a=load_analysis()
    assert data["analysis"]["build_id"]==a["build_id"]
    assert data["analysis"]["source_sha256"]==a["source_sha256"]
    assert data["raw_players_included"] is False
    assert sum(r["players"] for r in data["evidence"]["arms"]["rows"])==a["rows"]
    assert data["planning_grid"]["1.0"]==a["planning"]["players_per_arm"]
