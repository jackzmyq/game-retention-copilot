import hashlib
import json
import sqlite3
from pathlib import Path
import pytest
from src.config import RAW
from src.provenance import verify_source, EvidenceError, SOURCE_SHA256
from src.reporting import load_analysis
from scripts import download_data, build_pipeline


def test_pinned_source_rejects_modified_bytes():
    payload=RAW.read_bytes()
    assert verify_source(payload)==SOURCE_SHA256
    with pytest.raises(EvidenceError,match="SHA-256"):
        verify_source(payload+b"\n")


def test_cached_source_cannot_silently_reset_manifest(tmp_path,monkeypatch):
    raw=tmp_path/"cookie_cats.csv"
    raw.write_bytes(RAW.read_bytes()+b"\n")
    manifest=tmp_path/"manifest.json"
    manifest.write_text('{"prior":"evidence"}',encoding="utf-8")
    monkeypatch.setattr(download_data,"RAW",raw)
    with pytest.raises(EvidenceError):
        download_data.download()
    assert json.loads(manifest.read_text())=={"prior":"evidence"}


def test_failed_staged_build_keeps_prior_database_and_report(tmp_path,monkeypatch):
    database=tmp_path/"retention.sqlite"
    reports=tmp_path/"reports"
    reports.mkdir()
    with sqlite3.connect(database) as con:
        con.execute("CREATE TABLE old_result(value INTEGER)")
        con.execute("INSERT INTO old_result VALUES (123)")
    baseline=hashlib.sha256(database.read_bytes()).hexdigest()
    old=reports/"analysis.json"
    old.write_text('{"old":true}',encoding="utf-8")
    monkeypatch.setattr(build_pipeline,"DB",database)
    monkeypatch.setattr(build_pipeline,"REPORTS",reports)
    def fail(con,staged_reports):
        con.execute("CREATE TABLE partial(value INTEGER)")
        staged_reports.mkdir()
        (staged_reports/"analysis.json").write_text('{"partial":true}')
        raise ValueError("Intentional calculation failure")
    monkeypatch.setattr(build_pipeline,"_build_to",fail)
    with pytest.raises(ValueError,match="Intentional"):
        build_pipeline.build()
    assert hashlib.sha256(database.read_bytes()).hexdigest()==baseline
    assert json.loads(old.read_text())=={"old":True}
    assert not list(tmp_path.glob(".retention-build-*"))


def test_mixed_builds_are_not_served(tmp_path):
    database=tmp_path/"retention.sqlite"
    with sqlite3.connect(database) as con:
        con.execute("CREATE TABLE build_metadata(build_id TEXT,source_sha256 TEXT)")
        con.execute("INSERT INTO build_metadata VALUES ('new','source')")
    (tmp_path/"analysis.json").write_text(json.dumps({"build_id":"old","source_sha256":"source"}))
    with pytest.raises(EvidenceError,match="different builds"):
        load_analysis(tmp_path,database)


def test_all_deliverables_are_generated_by_the_report_command():
    from src.config import REPORTS
    for name in ["decision_brief_zh.md","decision_brief_en.md","decision_scenario_zh.md","decision_scenario_en.md","offline_demo_evidence.json","unsupported_question_example.json"]:
        assert (REPORTS/name).is_file()
    scenario=(REPORTS/"decision_scenario_zh.md").read_text(encoding="utf-8")
    assert "overlaps_tolerance" not in scenario
    assert "区间跨越容忍边界" in scenario
