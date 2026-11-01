import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import convert

ROOT = Path(__file__).resolve().parents[1]
DATA = Path("/mnt/data")

cases = [
    ("wr_mrpl_tebhada_re_DA_02-11-2026_REMC.csv", "wr_mrpl_tebhada_re_DA_Template.csv", "DA"),
    ("wr_mrpl_tebhada_re_ID_01-11-2026_REMC.csv", "wr_mrpl_tebhada_re_INTRADAY_Template.csv", "INTRADAY"),
]

for old_name, template_name, expected_revision in cases:
    result, revision = convert(
        (DATA / old_name).read_bytes(),
        old_name,
        (ROOT / "templates" / template_name).read_bytes(),
    )
    assert revision == expected_revision
    rows = list(csv.reader(result.decode("utf-8").splitlines()))
    assert len(rows) == 117
    assert rows[21][0] == "1" and rows[116][0] == "96"
    print(f"PASS: {old_name} -> {revision}, 96 blocks")

