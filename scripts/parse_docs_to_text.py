import os
from glob import glob

import typer
from mair.pdf_parsing import parse
from tqdm import tqdm

data_sources = {"nesta": "nesta_ai_governance_docs", "oecd": "oecd_docs"}


def get_raw_path(source_name):
    return os.path.join("data", data_sources[source_name], "raw")


def get_text_path(source_name):
    return os.path.join("data", data_sources[source_name], "texts")


def main(source_name: str):
    raw_dir_path = get_raw_path(source_name)
    print(raw_dir_path)
    text_dir_path = get_text_path(source_name)
    os.makedirs(text_dir_path, exist_ok=True)

    pdf_paths = glob(os.path.join(raw_dir_path, "*.pdf"))
    for path in tqdm(pdf_paths):
        try:
            text = parse(path).full_text
        except Exception as e:
            print(f"error parsing {path} ({e}), passing...")
        text_filename = os.path.basename(path)[:-4] + ".txt"
        out_path = os.path.join(text_dir_path, text_filename)
        with open(out_path, "w") as f:
            f.write(text)


if __name__ == "__main__":
    typer.run(main)
