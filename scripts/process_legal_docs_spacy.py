"""Process raw texts through spacy nlp engine, extracting trees and coreferences resolutions. Results are saved to OUT"""
import joblib
import neuralcoref
import spacy
from mair.data_loading import load_legal_documents
from mair.read_write_utilities import ensure_dirs_exist
from tqdm import tqdm

OUT = "data/processed/intermediate/parsed_legal_texts.joblib"

ensure_dirs_exist(OUT)
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 3000000
coref = neuralcoref.NeuralCoref(nlp.vocab)
nlp.add_pipe(coref, name="neuralcoref")


texts = load_legal_documents()
results = {t: nlp(text) for t, text in tqdm(texts.items())}

joblib.dump(results, OUT)
