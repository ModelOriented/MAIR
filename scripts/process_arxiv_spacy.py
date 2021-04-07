"""Process raw papers texts through spacy nlp engine, extracting trees and coreferences resolutions. Results are saved to OUT"""
import joblib
from mair import coreference_resulution
from mair.data_loading import load_arxiv_cleaned_texts
from mair.read_write_utilities import ensure_dirs_exist
from tqdm import tqdm

OUT = "data/processed/intermediate/parsed_arxiv_papers.joblib"
ensure_dirs_exist(OUT)


texts = load_arxiv_cleaned_texts()
results = {
    path: coreference_resulution.parse(text) for path, text in tqdm(texts.items())
}
joblib.dump(results, OUT)
