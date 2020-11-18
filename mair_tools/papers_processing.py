import re
from typing import List


def clean_text(text: str):
    """Removes bibliography, newlines and references"""
    position = text.lower().rfind("references")
    text = text[:position]  # removing bibliography
    text = text.replace("\n", " ")  # removing newlines
    text = re.sub(r"\[[^\[^\]]*\]", "", text)  # removing references
    return text


def find_first(doc, searched_norms: List[str]) -> int:
    for token in doc:
        if token.norm_ in searched_norms:
            return token.i
    return 0


def get_lemmas(doc):
    return [word.lemma_.lower() for word in doc if not word.is_stop if word.is_alpha]
