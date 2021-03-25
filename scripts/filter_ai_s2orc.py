import glob
import os

import pandas as pd
import spacy.lang.en
from spacy.matcher import PhraseMatcher
from tqdm import tqdm

S2_ORC_INPUT_PATHS = "data/s2orc/metadata/comp_sci/*.jsonl"
AI_PAPERS_OUT_PATH = "data/s2orc/ai_papers_meta.csv"

tqdm.pandas()
AI_PAPER_PATTERNS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "classifier",
    "neural network",
    "deep learning",
    "data science",
    "nlp",
    "machine-learning",
    "computer vision",
]

en = spacy.lang.en.English()
ai_papers_index = dict()


def find_ai_papers(df, matcher):
    df["cleaned_abstract"] = df["abstract"].str.replace("\n", " ")

    text_to_search = df.apply(
        lambda row: str(row["title"]) + " " + str(row["cleaned_abstract"]), axis=1
    ).str.lower()

    docs = text_to_search.apply(en)

    foundings = docs.apply(matcher)
    ai_papers_ids = list(df[foundings.str.len() != 0].paper_id)
    return ai_papers_ids


def prepare_matcher():
    matcher = PhraseMatcher(en.vocab, attr="NORM")  # TODO: change to lemma
    for pattern in AI_PAPER_PATTERNS:
        matcher.add(pattern, None, en(pattern))
    return matcher


if __name__ == "__main__":
    matcher = prepare_matcher()

    s2orc_paths = glob.glob(S2_ORC_INPUT_PATHS)
    for path in tqdm(s2orc_paths):
        filename = os.path.basename(path)
        if filename in ai_papers_index.keys():
            print(f"Already filtered ({filename}), skipping...", flush=True)
        else:
            df = pd.read_json(path, lines=True)
            ai_papers_ids = find_ai_papers(df, matcher)

            ai_papers_index[filename] = ai_papers_ids
    ai_papers = pd.DataFrame()
    for path in tqdm(s2orc_paths):
        filename = os.path.basename(path)
        df2 = pd.read_json(path, lines=True)
        df_filtered = df2[df2["paper_id"].isin(ai_papers_index[filename])]
        ai_papers = ai_papers.append(df_filtered)
    ai_papers.to_csv(AI_PAPERS_OUT_PATH, index=False)
