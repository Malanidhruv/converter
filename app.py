import csv
import io
import re
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
TEMPLATE_DIR = APP_DIR / "templates"

# Zero-based columns copied from the old file into the new template.
# Columns 7 and 10 (Avc values) are deliberately retained from the new template.
TRANSFER_COLUMNS = (1, 2, 3, 4, 5, 6, 8, 9, 11, 12)
BLOCK_COLUMN = 0
FIRST_DATA_ROW = 21
EXPECTED_BLOCKS = 96
WIDTH = 13

TEMPLATES = {
    "DA": TEMPLATE_DIR / "wr_mrpl_tebhada_re_DA_Template.csv",
    "INTRADAY": TEMPLATE_DIR / "wr_mrpl_tebhada_re_INTRADAY_Template.csv",
}


def read_csv_bytes(data: bytes, filename: str):
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    try:
        rows = list(csv.reader(io.StringIO(text, newline="")))
    except csv.Error as exc:
        raise ValueError(f"{filename}: CSV could not be read: {exc}") from exc
    return rows


def normalize_rows(rows):
    return [list(row) + [""] * max(0, WIDTH - len(row)) for row in rows]


def revision_from_rows(rows):
    if len(rows) <= 3 or len(rows[3]) < 3:
        raise ValueError("Could not identify the revision. Expected DA or INTRADAY in row 4.")
    revision = rows[3][2].strip().upper()
    if revision not in TEMPLATES:
        raise ValueError(f"Unsupported revision '{revision}'. Only DA and INTRADAY are supported.")
    return revision


def convert(old_bytes: bytes, old_filename: str, template_bytes: bytes):
    old_rows = normalize_rows(read_csv_bytes(old_bytes, old_filename))
    template_rows = normalize_rows(read_csv_bytes(template_bytes, "template"))

    revision = revision_from_rows(old_rows)
    template_revision = revision_from_rows(template_rows)
    if revision != template_revision:
        raise ValueError(
            f"Revision mismatch: uploaded file is {revision}, but selected template is {template_revision}."
        )

    if len(old_rows) < FIRST_DATA_ROW + EXPECTED_BLOCKS:
        raise ValueError(
            f"Uploaded file has only {max(0, len(old_rows) - FIRST_DATA_ROW)} schedule rows; "
            f"{EXPECTED_BLOCKS} blocks are required."
        )
    if len(template_rows) < FIRST_DATA_ROW + EXPECTED_BLOCKS:
        raise ValueError("The selected template does not contain all 96 schedule blocks.")

    # Verify that the input and template both contain blocks 1 through 96 in order.
    for offset in range(EXPECTED_BLOCKS):
        row_index = FIRST_DATA_ROW + offset
        expected_block = str(offset + 1)
        old_block = old_rows[row_index][BLOCK_COLUMN].strip()
        new_block = template_rows[row_index][BLOCK_COLUMN].strip()
        if old_block != expected_block:
            raise ValueError(
                f"Input file: expected block {expected_block} at CSV row {row_index + 1}, "
                f"found '{old_block}'."
            )
        if new_block != expected_block:
            raise ValueError(
                f"Template: expected block {expected_block} at CSV row {row_index + 1}, "
                f"found '{new_block}'."
            )

    # Copy only the operational schedule values. Keep template metadata,
    # contract IDs, approval numbers, capacities and Avc columns unchanged.
    result = [row[:] for row in template_rows]
    for row_index in range(FIRST_DATA_ROW, FIRST_DATA_ROW + EXPECTED_BLOCKS):
        for col_index in TRANSFER_COLUMNS:
            result[row_index][col_index] = old_rows[row_index][col_index]

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(result)
    return output.getvalue().encode("utf-8"), revision


st.set_page_config(page_title="Schedule CSV Converter", page_icon="📄", layout="centered")
st.title("Schedule CSV Converter")
st.write("Convert the old REMC schedule CSV into the corresponding new template.")

st.info(
    "The converter transfers the 96-block schedule values and retains the new template's "
    "metadata, Contract IDs, Approval Numbers, capacities and Avc columns."
)

uploaded = st.file_uploader("Upload old-format CSV", type=["csv"])

if uploaded:
    try:
        input_rows = read_csv_bytes(uploaded.getvalue(), uploaded.name)
        detected_revision = revision_from_rows(input_rows)
        st.success(f"Detected revision: {detected_revision}")

        template_path = TEMPLATES[detected_revision]
        if not template_path.exists():
            st.error(f"Template file is missing: {template_path.name}")
        else:
            template_bytes = template_path.read_bytes()
            if st.button("Convert CSV", type="primary", use_container_width=True):
                output_bytes, revision = convert(
                    uploaded.getvalue(), uploaded.name, template_bytes
                )
                stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(uploaded.name).stem)
                output_name = f"{stem}_NEW_FORMAT_{revision}.csv"
                st.success("Conversion completed. All 96 schedule blocks passed validation.")
                st.download_button(
                    "Download converted CSV",
                    data=output_bytes,
                    file_name=output_name,
                    mime="text/csv",
                    use_container_width=True,
                )
    except ValueError as exc:
        st.error(str(exc))
else:
    st.caption("Supported input revisions: DA and INTRADAY.")
