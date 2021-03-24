import joblib
from flair.data import Sentence
from flair.embeddings import TransformerDocumentEmbeddings
from mair.data_loading import load_legal_documents
from tqdm import tqdm

OUT = "data/processed/docs-bert-embeddings.joblib"


embedder = TransformerDocumentEmbeddings("roberta-base")


def get_bert_embedding(text):
    sent = Sentence(text)
    sent = embedder.embed(sent)[0]
    return sent.embedding


data = load_legal_documents()

embeddings = dict()
for p, text in tqdm(data.items()):
    embeddings[p] = get_bert_embedding(text)

joblib.dump(embeddings, OUT)
