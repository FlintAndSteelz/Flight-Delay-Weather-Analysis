"""Download monthly BTS On-Time Performance archives for 2022–2025.

Run from the root of Flight-Delay-Weather-Analysis:
    python download_bts_2022_2025.py --pilot
    python download_bts_2022_2025.py

Requires only the Python standard library (compatible with Python 3.13).
Original BTS ZIPs are preserved in data/raw/bts/; CSV files remain inside.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

BASE = "https://transtats.bts.gov/PREZIP/"
ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "data" / "raw" / "bts"
CHUNK_SIZE = 1024 * 1024
RETRIES = 3


def has_csv_in_zip(path: Path, *, check_crc: bool = False) -> bool:
    """Check archive structure; optionally fully verify member CRCs."""
    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            if not any(name.lower().endswith(".csv") for name in names):
                return False
            if check_crc and archive.testzip() is not None:
                return False
        return True
    except (BadZipFile, OSError, EOFError, ValueError):
        return False


def download_month(year: int, month: int) -> bool:
    name = f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
    target = OUT_DIR / name
    partial = OUT_DIR / f"{name}.part"
    url = BASE + name
    label = f"{year}-{month:02d}"

    if target.exists() and has_csv_in_zip(target):
        print(f"[SKIP] {label}: Valid ZIP already exists")
        return True
    if target.exists():
        print(f"[RETRY] {label}: Invalid ZIP found; downloading again")

    for attempt in range(1, RETRIES + 1):
        try:
            partial.unlink(missing_ok=True)
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 (academic data download)"})
            with urlopen(request, timeout=120) as response, partial.open("wb") as output:
                while block := response.read(CHUNK_SIZE):
                    output.write(block)

            if not has_csv_in_zip(partial, check_crc=True):
                raise ValueError("Downloaded file is not a complete ZIP with a readable CSV")
            partial.replace(target)
            print(f"[OK]   {label}: {target.stat().st_size / 1_000_000:.1f} MB")
            return True

        except (HTTPError, URLError, OSError, ValueError, EOFError, BadZipFile) as exc:
            partial.unlink(missing_ok=True)
            print(f"[FAIL] {label}: attempt {attempt}/{RETRIES}: {exc}")
            if attempt < RETRIES:
                time.sleep(3 * attempt)

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Download BTS monthly flight data: 2022–2025")
    parser.add_argument(
        "--pilot", action="store_true", help="Download only January 2025 as a test"
    )
    parser.add_argument(
        "--year", type=int, choices=range(2022, 2026), metavar="YYYY",
        help="Download only one year (2022, 2023, 2024, or 2025)"
    )
    args = parser.parse_args()
    if args.pilot and args.year is not None:
        parser.error("Choose --pilot OR --year, not both")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    months = (
        [(2025, 1)] if args.pilot
        else [(args.year, month) for month in range(1, 13)] if args.year is not None
        else [(year, month) for year in range(2022, 2026) for month in range(1, 13)]
    )

    print(f"Downloading {len(months)} monthly BTS archives to: {OUT_DIR}\n")
    failed = [(year, month) for year, month in months if not download_month(year, month)]
    done = len(months) - len(failed)
    print(f"\nCompleted: {done}/{len(months)} month(s).")
    if failed:
        print("Failed months:", ", ".join(f"{y}-{m:02d}" for y, m in failed))
        print("You may rerun this script; successfully downloaded files will be skipped.")
        return 1
    print("All requested ZIPs are ready. The original CSVs are inside the ZIP files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
