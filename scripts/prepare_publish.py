"""Prepare an explicit publication file list; never glob the whole workspace."""
from pathlib import Path
import json
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]


def prepare():
    files=[ROOT/name for name in ["README.md","app.py","requirements.txt","requirements-lock.txt","pytest.ini",".gitignore",".env.example","setup.ps1","start.ps1","configure_api.ps1",".streamlit/config.toml"]]
    suffixes={".py",".md",".sql",".png",".css",".js",".cjs",".json",".html",".pdf",".yml",".yaml"}
    for name in ["src","scripts","sql","tests","docs","web",".github"]:
        files.extend(p for p in (ROOT/name).rglob("*") if p.is_file() and (p.suffix in suffixes or p.name==".nojekyll") and "__pycache__" not in p.parts)
    files.extend(p for p in (ROOT/"reports").glob("*") if p.suffix in {".md",".csv",".json"})
    files.extend(ROOT/"output"/name for name in ["HR项目介绍.html","马延青_游戏分析项目介绍.pdf","HR_review_pack.zip"])
    groups=defaultdict(list)
    for path in sorted(set(files)):
        relative=path.relative_to(ROOT).as_posix()
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError(relative)
        if relative.startswith(("data/",".cache/",".venv/","reports/agent_runs/")) or path.name==".env":raise ValueError(relative)
        if path.stat().st_size>20_000_000:raise ValueError("Large file requires review: "+relative)
        groups[path.parent.relative_to(ROOT).as_posix()].append(str(path.resolve()))
    # Workflows go last so no action runs against a partially uploaded repository.
    ordered=[{"directory":key,"files":value} for key,value in sorted(groups.items(),key=lambda x:(x[0].startswith('.github'),x[0]))]
    out=ROOT/".cache/publish_manifest.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(ordered,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Prepared {sum(len(g['files']) for g in ordered)} public files in {len(ordered)} directory batches")
    return ordered


if __name__=="__main__":prepare()
