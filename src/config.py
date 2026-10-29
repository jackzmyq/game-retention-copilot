from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/cookie_cats.csv"
DB = ROOT / "data/processed/retention.sqlite"
REPORTS = ROOT / "reports"
SOURCE_URL = "https://assets.datacamp.com/production/project_184/datasets/cookie_cats.csv"


def settings():
    """Only read the three documented keys; do not export or log credentials."""
    keys = {"DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "DEEPSEEK_BASE_URL"}
    values = {}
    local = ROOT / ".env"
    if local.exists():
        for line in local.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                if key.strip() in keys:
                    values[key.strip()] = value.strip().strip('\"').strip("'")
    values.update({k: os.environ[k] for k in keys if k in os.environ})
    return values
