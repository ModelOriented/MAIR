"""Module for extraction coreferences and syntax trees from texts"""
import neuralcoref
import spacy
from spacy.tokens import Token

Token.set_extension("corefs", default=[])

# workaround, since neuralcoref breaks spacy's serialisation
def _remove_unserializable_results(doc):
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


_nlp = spacy.load("en_core_web_sm")
_nlp.max_length = 3000000
neuralcoref.add_to_pipe(_nlp)
_nlp.add_pipe(_remove_unserializable_results, last=True)


def parse(text: str):
    """Process text through spacy nlp engine and neural coref"""
    return _nlp(text)
