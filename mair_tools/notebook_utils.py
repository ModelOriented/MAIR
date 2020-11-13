"""Functions to be used in notebooks"""

import glob
import os.path
from typing import List

import pandas as pd

from mair_tools import pdf_processing


def parse_all_files_from_path(path: str) -> List[pdf_processing.Pdf]:
    pdfs = []

    for filename in glob.glob(os.path.join(path, "*.pdf")):
        try:
            pdf = pdf_processing.parse(filename)
            pdfs.append(pdf)
        except Exception as e:
            print(f"Error parsing ({filename}):", e)
    return pdfs


def load_texts_as_df(input_file_pattarn: str) -> pd.DataFrame:
    texts = dict()
    for filepath in glob.glob(input_file_pattarn):
        filename = filepath.split("/")[-1]
        name = os.path.splitext(filename)[0]
        with open(filepath, "r") as file:
            text = file.read()
        texts[name] = text

    df = pd.DataFrame({"text": pd.Series(texts)})

    return df


def save_texts_series_to_dir(texts: pd.Series, dir_path: str) -> None:
    """Saves text from series as .txt files in selected directory"""
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    for key, text in texts.items():
        file_path = os.path.join(dir_path, key) + ".txt"
        with open(file_path, "w") as file:
            file.write(text)
