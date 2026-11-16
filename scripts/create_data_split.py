"""Create the chronological holdout once; refuse to overwrite an existing split."""

import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
CUTOFF = "2023-01-01"
SOURCES = (
    ("almond_monthly_2011_2025.csv", "month", "%Y-%m-%d"),
    ("GetDSCI.csv", "MapDate", "%Y%m%d"),
)


def encode_csv(header, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main():
    destinations = [DATA / "split_manifest.json"] + [
        DATA / subset / name
        for name, _, _ in SOURCES
        for subset in ("development", "reporting")
    ]
    if any(path.exists() for path in destinations):
        raise SystemExit("A split already exists. Refusing to overwrite the fixed reporting set.")

    manifest = {
        "method": "Chronological split with a shared calendar cutoff; no shuffling.",
        "reporting_start": CUTOFF,
        "reporting_target_fraction": 0.20,
        "datasets": {},
    }
    outputs = []
    for name, date_column, date_format in SOURCES:
        source = ROOT / name
        source_bytes = source.read_bytes()
        reader = csv.reader(io.StringIO(source_bytes.decode("utf-8-sig")))
        header = next(reader)
        rows = list(reader)
        date_index = header.index(date_column)
        development, reporting = [], []
        for row in rows:
            date = datetime.strptime(row[date_index], date_format).date().isoformat()
            (reporting if date >= CUTOFF else development).append(row)

        # The common cutoff must also produce 20%, rounded to a whole row,
        # for each source independently.
        assert len(reporting) == round(len(rows) * 0.20), name
        assert len(development) + len(reporting) == len(rows), name
        metadata = {
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "date_column": date_column,
            "total_rows": len(rows),
            "development_rows": len(development),
            "reporting_rows": len(reporting),
            "reporting_fraction": len(reporting) / len(rows),
        }
        for subset, subset_rows in (("development", development), ("reporting", reporting)):
            payload = encode_csv(header, subset_rows)
            outputs.append((DATA / subset / name, payload))
            metadata[f"{subset}_sha256"] = hashlib.sha256(payload).hexdigest()
        manifest["datasets"][name] = metadata

    for path, payload in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(payload)
        if path.parent.name == "reporting":
            path.chmod(0o444)

    with (DATA / "split_manifest.json").open("x") as output:
        json.dump(manifest, output, indent=2)
        output.write("\n")
    print("Created development and reporting sets. Reporting files are read-only.")
    for name, metadata in manifest["datasets"].items():
        print(f"{name}: {metadata['development_rows']} development, "
              f"{metadata['reporting_rows']} reporting rows")


if __name__ == "__main__":
    main()
