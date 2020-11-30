import glob
import json
import os

import requests
from tqdm import tqdm

PARSE_ENDPOINT = "http://localhost:8080/v1"
INPUT_FOLDER = "../data/arxiv_dump/papers/"
OUTPUT_FOLDER = "../data/arxiv_dump/sci-parse_output/"
pdfs_path = os.path.join(INPUT_FOLDER, "*.pdf")


def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    for pdf_filepath in tqdm(list(glob.glob(pdfs_path))):
        try:
            with open(pdf_filepath, "rb") as f:
                data = f.read()
            res = requests.post(
                url=PARSE_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/pdf"},
            )
            parsed_data = res.json()
        except Exception as e:
            print(f"Error parsing ({pdf_filepath}):", e)
        else:
            try:
                pdf_filename = pdf_filepath.split("/")[-1]
                out_file_path = os.path.join(OUTPUT_FOLDER, pdf_filename).replace(
                    ".pdf", ".json"
                )
                with open(out_file_path, "w") as f:
                    json.dump(parsed_data, f)
            except Exception as e:
                print(f"Error saving ({out_file_path}):", e)


if __name__ == "__main__":
    main()
