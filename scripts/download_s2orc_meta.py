"""Downloads papers filtered to specific field of study"""

import gzip
import io
import json
import os

import requests
from mair import s2orc_links
from tqdm import tqdm

METADATA_TEMP_DIR = "data/s2orc/metadata/tmp/"
METADATA_OUTPUT_DIR = "data/s2orc/metadata/comp_sci/"

FILTERED_FIELD_OF_STUDY = (
    "Computer Science"
)  # all names here: https://github.com/allenai/s2orc#download-instructions


def process_batch(batch: dict):
    # process single batch
    if os.path.exists(batch["tmp_metadata_path"]):
        print(f"File {batch['tmp_metadata_path']} already downloaded!")
    else:
        print(f"Downloading {batch['input_metadata_url']}...")
        r = requests.get(batch["input_metadata_url"])
        with open(batch["tmp_metadata_path"], "wb") as f:
            f.write(r.content)

    # filter metadata JSONL to only papers with a particular field of study.
    paper_ids_to_keep = set()
    if os.path.exists(batch["output_metadata_path"]):
        print(f"File {batch['output_metadata_path']} already processed!")
    else:
        with gzip.open(batch["tmp_metadata_path"], "rb") as gz, open(
            batch["output_metadata_path"], "wb"
        ) as f_out:
            f = io.BufferedReader(gz)
            for line in tqdm(f.readlines()):
                metadata_dict = json.loads(line)
                paper_id = metadata_dict["paper_id"]
                mag_field_of_study = metadata_dict["mag_field_of_study"]
                if mag_field_of_study and FILTERED_FIELD_OF_STUDY in mag_field_of_study:
                    paper_ids_to_keep.add(paper_id)
                    f_out.write(line)
        os.remove(batch["tmp_metadata_path"])


if __name__ == "__main__":
    os.makedirs(METADATA_TEMP_DIR, exist_ok=True)
    os.makedirs(METADATA_OUTPUT_DIR, exist_ok=True)

    batches = [
        {
            "input_metadata_url": download_links["metadata"],
            "tmp_metadata_path": os.path.join(
                METADATA_TEMP_DIR,
                os.path.basename(download_links["metadata"].split("?")[0]),
            ),
            "output_metadata_path": os.path.join(
                METADATA_OUTPUT_DIR,
                os.path.basename(download_links["metadata"].split("?")[0][:-3]),
            ),
        }
        for download_links in s2orc_links.links
    ]

    for batch in batches:
        process_batch(batch=batch)
