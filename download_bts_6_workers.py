r"""Download BTS on-time performance monthly ZIP files (2022–2025).

Python 3.13; standard library only. Defaults to 6 concurrent downloads.

Examples (from the project root):
    python .\download_bts_6_workers.py --pilot
    python .\download_bts_6_workers.py
    python .\download_bts_6_workers.py --year 2024
    python .\download_bts_6_workers.py --workers 3

Valid ZIPs already in data/raw/bts/ are preserved and skipped.
"""
from __future__ import annotations

import argparse
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

BASE_URL = "https://transtats.bts.gov/PREZIP/"
DATA_DIR = Path(__file__).resolve().parent / "data" / "raw" / "bts"
CHUNK_SIZE = 1024 * 1024  # 1 MiB per read
PROGRESS_EVERY = 20 * 1024 * 1024  # Print roughly every 20 MiB per file
MAX_ATTEMPTS = 3
PRINT_LOCK = threading.Lock()
STOP = threading.Event()


def log(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def archive_is_valid(path: Path) -> bool:
    """Verify ZIP structure, that it contains a CSV, and members' CRCs."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        with ZipFile(path) as zf:
            if not any(entry.filename.lower().endswith(".csv") for entry in zf.infolist()):
                return False
            return zf.testzip() is None
    except (BadZipFile, OSError, EOFError, ValueError, RuntimeError):
        return False


def download_one(year: int, month: int) -> tuple[str, str]:
    label = f"{year}-{month:02d}"
    filename = (
        f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
    )
    target = DATA_DIR / filename
    temporary = DATA_DIR / (filename + ".part")

    if STOP.is_set():
        return label, "cancelled"

    if archive_is_valid(target):
        log(f"[SKIP] {label} | ZIP already complete and valid")
        return label, "skipped"

    if target.exists():
        log(f"[WARN] {label} | Existing ZIP is invalid; will replace after download")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if STOP.is_set():
            temporary.unlink(missing_ok=True)
            return label, "cancelled"
        try:
            # An old .part file is safe to delete only when no other downloader is running.
            temporary.unlink(missing_ok=True)
            log(f"[START] {label} | attempt {attempt}/{MAX_ATTEMPTS}")
            request = Request(
                BASE_URL + filename,
                headers={"User-Agent": "Mozilla/5.0 (research project; BTS download)"},
            )
            with urlopen(request, timeout=60) as response, temporary.open("wb") as out:
                expected = int(response.headers.get("Content-Length") or "0")
                received = 0
                next_update = PROGRESS_EVERY
                while True:
                    if STOP.is_set():
                        raise InterruptedError("Download stopped")
                    block = response.read(CHUNK_SIZE)
                    if not block:
                        break
                    out.write(block)
                    received += len(block)
                    if received >= next_update:
                        expected_mb = f" / {expected/1_000_000:.1f} MB" if expected else ""
                        log(f"[PROGRESS] {label} | {received/1_000_000:.1f}{expected_mb} MB")
                        next_update += PROGRESS_EVERY
                if expected and received != expected:
                    raise ValueError(f"Incomplete transfer: {received}/{expected} bytes")

            if not archive_is_valid(temporary):
                raise ValueError("ZIP is invalid, damaged, or contains no CSV")
            # Only replace an existing target after the new file is fully validated.
            temporary.replace(target)
            log(f"[OK] {label} | {target.stat().st_size / 1_000_000:.1f} MB")
            return label, "downloaded"

        except (HTTPError, URLError, TimeoutError, OSError, EOFError,
                BadZipFile, ValueError, RuntimeError, InterruptedError) as exc:
            temporary.unlink(missing_ok=True)
            if STOP.is_set():
                return label, "cancelled"
            log(f"[ERROR] {label} | {type(exc).__name__}: {exc}")
            if attempt < MAX_ATTEMPTS:
                # Interruptible backoff: avoid hammering the server if it is throttling.
                delay = 5 * attempt
                log(f"[RETRY] {label} | retry in {delay} seconds")
                if STOP.wait(delay):
                    return label, "cancelled"

    log(f"[FAIL] {label} | failed after {MAX_ATTEMPTS} attempts")
    return label, "failed"


def on_interrupt(signum: int, frame: object) -> None:
    log("\n[STOP] Stop requested. Finishing active requests and cleaning .part files...")
    STOP.set()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download BTS 2022–2025 ZIPs with 6 workers")
    parser.add_argument("--pilot", action="store_true", help="Download only January 2025")
    parser.add_argument("--year", type=int, choices=range(2022, 2026), metavar="YYYY",
                        help="Download only one year (2022, 2023, 2024, or 2025)")
    parser.add_argument("--workers", type=int, choices=range(1, 7), default=6, metavar="N",
                        help="Concurrent downloads: 1–6 (default: 6)")
    args = parser.parse_args()
    if args.pilot and args.year:
        parser.error("Choose either --pilot or --year")

    months = (
        [(2025, 1)] if args.pilot
        else [(args.year, m) for m in range(1, 13)] if args.year
        else [(year, month) for year in range(2022, 2026) for month in range(1, 13)]
    )
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGINT, on_interrupt)

    log(f"Folder : {DATA_DIR}")
    log(f"Files  : {len(months)} requested")
    log(f"Workers: {min(args.workers, len(months))} parallel downloads")
    log("Note   : Valid existing ZIPs will be skipped; never run two downloaders together.")

    results: dict[str, int] = {"skipped": 0, "downloaded": 0, "failed": 0, "cancelled": 0}
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(download_one, year, month) for year, month in months]
        for index, future in enumerate(as_completed(futures), start=1):
            label, status = future.result()
            results[status] += 1
            if status == "failed":
                failures.append(label)
            log(f"[TOTAL] {index}/{len(months)} checked | OK new: {results['downloaded']}"
                f" | SKIP: {results['skipped']} | FAIL: {results['failed']}")

    log("[SUMMARY] " + ", ".join(f"{key}={value}" for key, value in results.items()))
    if failures:
        log("[FAILED MONTHS] " + ", ".join(sorted(failures)))
        log("Run the same command again: valid ZIPs will be skipped.")
        return 1
    if STOP.is_set():
        log("[INTERRUPTED] Some months not processed; run again to continue.")
        return 130
    log("[DONE] All requested BTS ZIPs are present and passed validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
