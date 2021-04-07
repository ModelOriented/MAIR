import json
import os
from glob import glob
from typing import Dict, List

import joblib
import pandas as pd

# importing to set spacy's extensions
import mair.coreference_resulution  # noqa: F401

ARXIV_DUMP_PATH_CLEANED_TEXT_PATH = "data/arxiv_dump/cleaned_texts"
ARXIV_DUMP_PATH_RAW_TEXT_PATH = "data/arxiv_dump/raw_extracted_texts"

ARXIV_GOLDEN_STANDARD_PATH = "data/golden_standard/papers_dbpedia_affiliations.json"
OECD_TEXTS_PATH = "data/oecd_docs/texts"
NESTA_TEXTS_PATH = "data/nesta_ai_governance_docs/texts"


def _load_text(path):
    with open(os.path.join(path), "r") as f:
        text = f.read()
    return text


def _load_text_by_id(path, id):
    return _load_text(os.path.join(path, id + ".txt"))


def load_arxiv_raw_text_by_id(id: str) -> str:
    """Load cleaned text from given arxiv id"""
    return _load_text_by_id(ARXIV_DUMP_PATH_RAW_TEXT_PATH, id)


def load_arxiv_cleaned_texts() -> dict:
    input_files_pattern = os.path.join(ARXIV_DUMP_PATH_CLEANED_TEXT_PATH, "*.txt")
    text_input_file_paths = glob(input_files_pattern)
    d = dict()
    for path in text_input_file_paths:
        d[path] = _load_text(path)
    return d


def load_golden_dataset() -> List[Dict[str, str]]:
    """Load list of golden standard annotated papers"""
    with open(ARXIV_GOLDEN_STANDARD_PATH, "r") as f:
        data = json.load(f)

    for id in data:
        try:
            text = load_arxiv_raw_text_by_id(data[id]["versioned_id"])
            data[id]["text"] = text
            data[id]["affiliations"] = data[id]["affiliations"]["names"]
        except FileNotFoundError as e:
            print(e, "passing...")
    return [d for d in data.values() if d.get("text")]


def load_legal_documents() -> dict:
    """Load text extracted from nesta and oecd"""
    a = glob(os.path.join(OECD_TEXTS_PATH, "*")) + glob(
        os.path.join(NESTA_TEXTS_PATH, "*")
    )
    d = dict()
    for p in a:
        d[p] = _load_text(p)
    return d


def load_legal_documents_metadata() -> pd.DataFrame:
    nesta_path = "data/nesta_ai_governance_docs/meta.csv"
    oecd_path = "data/oecd_docs/meta.csv"

    meta_nesta = pd.read_csv(nesta_path)
    meta_nesta["id"] = "nesta|" + meta_nesta["nestaId"]
    oecd_meta = pd.read_csv(oecd_path)
    oecd_meta["id"] = "oecd|" + oecd_meta["oecdId"].astype("str")
    oecd_meta["year"] = oecd_meta["startDate"]
    df_meta = pd.concat([meta_nesta, oecd_meta])
    return df_meta


def load_parsed_legal_documents() -> pd.Series:
    r = joblib.load("data/processed/intermediate/parsed_legal_texts.joblib")
    df = pd.Series(r, name="doc")
    df = df.reset_index()
    df = df.set_index("index")
    docs = df["doc"]

    return docs
