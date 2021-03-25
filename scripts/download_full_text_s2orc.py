import gzip
import io
import json
import os

import pandas as pd
import requests
from mair import s2orc_links
from tqdm import tqdm

FILTERED_AI_PAPERS_META_INPUT = "data/s2orc/ai_papers_meta.csv"
PDF_PARSES_TMP_DIR = "data/s2orc/pdf_parses/tmp/"
PDF_PARSES_OUTPUT_DIR = "data/s2orc/pdf_parses/ai/"

paper_ids_to_keep = list(pd.read_csv(FILTERED_AI_PAPERS_META_INPUT)["paper_id"])


def process_batch(batch: dict):
    # get full texts
    print(f"Downloading {batch['input_pdf_parses_url']}...")
    r = requests.get(batch["input_pdf_parses_url"])
    with open(batch["input_pdf_parses_path"], "wb") as f:
        f.write(r.content)

    with gzip.open(batch["input_pdf_parses_path"], "rb") as gz, open(
        batch["output_pdf_parses_path"], "wb"
    ) as f_out:
        f = io.BufferedReader(gz)
        for line in tqdm(f.readlines()):
            metadata_dict = json.loads(line)
            paper_id = metadata_dict["paper_id"]
            if paper_id in paper_ids_to_keep:
                f_out.write(line)
    print("Papers number after filtering:", len(paper_ids_to_keep))
    # now delete the raw files to clear up space for other batches
    # os.remove(batch["input_metadata_path"])
    os.remove(batch["input_pdf_parses_path"])


if __name__ == "__main__":
    os.makedirs(PDF_PARSES_TMP_DIR, exist_ok=True)
    os.makedirs(PDF_PARSES_OUTPUT_DIR, exist_ok=True)

    batches = [
        {
            "input_pdf_parses_url": download_links["pdf_parses"],
            "input_pdf_parses_path": os.path.join(
                PDF_PARSES_TMP_DIR,
                os.path.basename(download_links["pdf_parses"].split("?")[0]),
            ),
            "output_pdf_parses_path": os.path.join(
                PDF_PARSES_OUTPUT_DIR,
                os.path.basename(download_links["pdf_parses"].split("?")[0]),
            ),
        }
        for download_links in s2orc_links.links
    ]
    for batch in batches:
        process_batch(batch=batch)
