import json
import os
from glob import glob
from typing import Dict, List

import pandas as pd

ARXIV_DUMP_PATH_CLEANED_TEXT_PATH = "data/arxiv_dump/cleaned_texts"
ARXIV_DUMP_PATH_RAW_TEXT_PATH = "data/arxiv_dump/raw_extracted_texts"

ARXIV_GOLDEN_STANDARD_PATH = "data/golden_standard/papers_dbpedia_affiliations.json"
OECD_TEXTS_PATH = "data/oecd_docs/texts"
NESTA_TEXTS_PATH = "data/nesta_ai_governance_docs/texts"


def _load_text(path, id):
    with open(os.path.join(path, id + ".txt"), "r") as f:
        text = f.read()
    return text


def load_arxiv_cleaned_text(id: str) -> str:
    """Load cleaned text from given arxiv id"""
    return _load_text(ARXIV_DUMP_PATH_CLEANED_TEXT_PATH, id)


def load_arxiv_raw_text(id: str) -> str:
    """Loads raw text from given arxiv id"""
    return _load_text(ARXIV_DUMP_PATH_RAW_TEXT_PATH, id)


def load_golden_dataset() -> List[Dict[str, str]]:
    """Load list of golden standard annotated papers"""
    with open(ARXIV_GOLDEN_STANDARD_PATH, "r") as f:
        data = json.load(f)

    for id in data:
        try:
            text = load_arxiv_raw_text(data[id]["versioned_id"])
            data[id]["text"] = text
            data[id]["affiliations"] = data[id]["affiliations"]["names"]
        except FileNotFoundError as e:
            print(e, "passing...")
    return [d for d in data.values() if d.get("text")]


def load_legal_documents():
    """Load text extracted from nesta and oecd"""
    a = glob(os.path.join(OECD_TEXTS_PATH, "*")) + glob(
        os.path.join(NESTA_TEXTS_PATH, "*")
    )
    d = dict()
    for p in a:
        with open(p, "r") as f:
            d[p] = f.read()
    return d


def load_legal_documents_metadata() -> pd.DataFrame:
    meta_nesta = pd.read_csv("data/nesta_ai_governance_docs/meta.csv")
    meta_nesta["id"] = "nesta|" + meta_nesta["nestaId"]

    oecd_meta = pd.read_csv("data/oecd_docs/meta.csv")
    oecd_meta["id"] = "oecd|" + oecd_meta["oecdId"].astype("str")
    oecd_meta["year"] = oecd_meta["startDate"]
    df_meta = pd.concat([meta_nesta, oecd_meta])
    return df_meta
