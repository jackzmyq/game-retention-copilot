"""Fetch the unmodified educational source; retain original SHA-256 lineage."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import urlopen
from src.config import RAW, SOURCE_URL
from src.provenance import verify_source


def download():
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists():
        payload = RAW.read_bytes()
    else:
        with urlopen(SOURCE_URL, timeout=45) as response:
            payload = response.read()
        verify_source(payload)
        RAW.write_bytes(payload)
    source_hash=verify_source(payload) # Cached files must pass the same check as downloads.
    manifest = {"source_url":SOURCE_URL,"sha256":source_hash,
                "bytes":len(payload), "verified_at_utc":datetime.now(timezone.utc).isoformat(),
                "source_kind":"Public educational release of Cookie Cats A/B experiment",
                "rights":"No explicit redistribution license verified. Raw CSV excluded from repository; fetched from publisher.",
                "limitation":"No raw events, dates, country, acquisition, revenue or exposure logs."}
    (RAW.parent / "manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Source ready: {len(payload):,} bytes; SHA256 {manifest['sha256']}")


if __name__ == "__main__":
    download()
