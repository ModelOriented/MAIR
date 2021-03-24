import os

import joblib
from flair.data import Sentence
from flair.embeddings import TransformerDocumentEmbeddings
from mair.data_loading import load_legal_documents
from tqdm import tqdm

OUT_DIR = "data/processed"
OUT_FILE = "docs-bert-embeddings.joblib"
out_path = os.path.join(OUT_DIR, OUT_FILE)

embedder = TransformerDocumentEmbeddings("roberta-base")
os.makedirs(OUT_DIR, exist_ok=True)


def get_bert_embedding(text):
    sent = Sentence(text)
    sent = embedder.embed(sent)[0]
    return sent.embedding


data = load_legal_documents()

embeddings = dict()
for p, text in tqdm(data.items()):
    embeddings[p] = get_bert_embedding(text)

joblib.dump(embeddings, out_path)
