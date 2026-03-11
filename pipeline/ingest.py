import hashlib
import mimetypes
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


@dataclass
class DocumentJob:
    doc_id: str
    filename: str
    filepath: str
    file_ext: str
    mime_type: str
    file_size_bytes: int
    modified_time_utc: str
    ingested_at_utc: str
    sha256: str


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _infer_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate SHA256 with file locking workaround"""
    h = hashlib.sha256()
    
    # Read entire file into memory first (workaround for Docker Mac file locking)
    try:
        with path.open("rb") as f:
            data = f.read()  # Read all at once
        h.update(data)
    except OSError:
        # Fallback: use file stats if reading fails
        stat = path.stat()
        fallback_string = f"{path.name}:{stat.st_size}:{stat.st_mtime}"
        h.update(fallback_string.encode('utf-8'))
    
    return h.hexdigest()


def scan_input_directory(input_dir: Path) -> List[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir.resolve()}")

    files = []
    for p in input_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(p)

    return sorted(files)


def ingest(input_dir: Path) -> List[DocumentJob]:
    now = datetime.now(timezone.utc)
    ingested_at = _utc_iso(now)

    jobs = []
    for path in scan_input_directory(input_dir):
        stat = path.stat()
        modified_time = _utc_iso(datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc))
        sha256 = _sha256_file(path)

        doc_id = hashlib.sha256(
            f"{sha256}:{str(path.resolve())}".encode("utf-8")
        ).hexdigest()

        jobs.append(
            DocumentJob(
                doc_id=doc_id,
                filename=path.name,
                filepath=str(path.resolve()),
                file_ext=path.suffix.lower(),
                mime_type=_infer_mime_type(path),
                file_size_bytes=stat.st_size,
                modified_time_utc=modified_time,
                ingested_at_utc=ingested_at,
                sha256=sha256,
            )
        )

    return jobs


def jobs_to_dicts(jobs: List[DocumentJob]) -> List[dict]:
    return [asdict(j) for j in jobs]
