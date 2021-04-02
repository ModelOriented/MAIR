"""Process raw texts through spacy nlp engine, extracting trees and coreferences resolutions. Results are saved to OUT"""
import joblib
import neuralcoref
import spacy
from mair.data_loading import load_legal_documents
from mair.read_write_utilities import ensure_dirs_exist
from spacy.tokens import Token
from tqdm import tqdm

Token.set_extension("corefs", default=[])

# workaround, since neuralcoref breaks spacy's serialisation
def remove_unserializable_results(doc):
    doc._.coref_resolved = str(doc._.coref_resolved)
    for token in doc:
        token._.corefs = [str(cluster.main) for cluster in token._.coref_clusters]
        for x in dir(token._):
            if x not in ["get", "set", "has", "corefs"]:
                setattr(token._, x, None)

    for x in dir(doc._):
        if x not in ["get", "set", "has", "coref_resolved"]:
            setattr(doc._, x, None)
    for key in doc.user_data:
        _, name, _, _ = key
        if name in {"coref_scores", "coref_cluster"}:
            doc.user_data[key] = None

    return doc


OUT = "data/processed/intermediate/parsed_legal_texts.joblib"

ensure_dirs_exist(OUT)
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 3000000
neuralcoref.add_to_pipe(nlp)
nlp.add_pipe(remove_unserializable_results, last=True)

texts = load_legal_documents()
results = {t: nlp(text) for t, text in tqdm(texts.items())}
joblib.dump(results, OUT)
