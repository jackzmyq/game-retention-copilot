"""Pin the reviewed source; never silently replace the evidence baseline."""
import hashlib

SOURCE_SHA256 = "5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd"
SOURCE_HEADER = b"userid,version,sum_gamerounds,retention_1,retention_7"


class EvidenceError(ValueError):
    pass


def verify_source(payload):
    if not payload.startswith(SOURCE_HEADER):
        raise EvidenceError("Source schema changed; inspect before importing")
    actual=hashlib.sha256(payload).hexdigest()
    if actual != SOURCE_SHA256:
        raise EvidenceError("Source differs from the reviewed SHA-256. Restore the original or review the new version explicitly; no baseline was updated.")
    return actual
