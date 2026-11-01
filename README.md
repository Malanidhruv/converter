# Schedule CSV Converter

A small Streamlit application that converts the old REMC schedule CSV format into the supplied new DA or INTRADAY template.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL printed by Streamlit, upload an old-format CSV, and download the converted file.

## Free hosting on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, `README.md`, and the complete `templates` folder.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select the repository, branch, and `app.py`.
5. Deploy.

Keep the two template CSV files in the `templates` folder. The app depends on them.

## Conversion rules

- Detects `DA` or `INTRADAY` from row 4 of the uploaded file.
- Uses the matching new-format template.
- Copies columns B–G and I–J and L–M for blocks 1–96 (CSV rows 22–117).
- Retains the new template's metadata, Contract IDs, Approval Numbers, capacities, and Avc columns H and K.
- Validates the revision and all 96 block numbers before producing an output.
- Does not upload or store files on a separate server. The app processes the uploaded CSV in memory.

## Important

The column mapping is based on the four example files supplied with this project. Before using converted files for an actual market submission, verify the result against the receiving software's requirements and a known-good sample.
