"""Build a source-only shareable package from an explicit allowlist."""
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/game_retention_copilot_source.zip"


def package():
    files=[]
    for name in ["README.md","app.py","requirements.txt","requirements-lock.txt",
                 "pytest.ini",".gitignore",".env.example","setup.ps1","start.ps1","configure_api.ps1",
                 ".streamlit/config.toml"]:
        files.append(ROOT/name)
    for folder in ["src","scripts","sql","docs","tests","web",".github"]:
        files.extend(p for p in (ROOT/folder).rglob("*")
                     if p.is_file() and (p.suffix in {".py",".md",".sql",".png",".json",".css",".js",".cjs",".html",".pdf",".yml"} or p.name==".nojekyll")
                     and "__pycache__" not in p.parts)
    files.extend(p for p in (ROOT/"reports").glob("*") if p.suffix in {".md",".csv",".json"})
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(files)):
            archive.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUT) as archive:
        names=archive.namelist()
        assert all(not n.startswith((".venv/",".cache/","data/","reports/agent_runs/")) for n in names)
        assert ".env" not in names and ".streamlit/secrets.toml" not in names
    print(f"Packaged {len(names)} files, {OUT.stat().st_size:,} bytes: {OUT}")


if __name__=="__main__":
    package()
