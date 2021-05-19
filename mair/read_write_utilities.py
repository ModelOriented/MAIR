"""Saving and loading utilities"""

import glob
import os

import pandas as pd


def ensure_dirs_exist(path):
    """Create all directories that lead to file if they dont exist"""
    os.makedirs(os.path.dirname(path), exist_ok=True)


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
