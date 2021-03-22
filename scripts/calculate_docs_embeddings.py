import joblib
from mair.data_loading import load_legal_documents
from tqdm import tqdm
from transformers import DistilBertTokenizer, TFDistilBertModel

OUT = "data/processed/docs-bert-embeddings.joblib"

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = TFDistilBertModel.from_pretrained("distilbert-base-uncased")


def get_bert_embedding(data_series):
    tokens = tokenizer(list(data_series), return_tensors="tf", padding=True)
    r = model(tokens)
    vectors = r.pooler_output.numpy()
    return vectors


texts = load_legal_documents()
embeddings = dict()
for p, text in tqdm(texts.items()):
    embeddings[p] = get_bert_embedding(text)

joblib.dump(embeddings, OUT)
