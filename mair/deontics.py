from dataclasses import dataclass

import pandas as pd
import spacy.tokens

# importing to set spacy's extensions
import mair.coreference_resulution  # noqa:F401


@dataclass
class EmptyToken:
    lemma_ = ""
    children = []

    def __len__(self):
        return 0


nlp = spacy.load("en_core_web_sm")


EMPTY_TOKEN = EmptyToken()

COULD = "can"
SHOULD = "shall"
MUST = "must"
MODAL_VERBS_MAPPING = {
    "can": COULD,
    "could": COULD,
    "may": COULD,
    "might": COULD,
    "shall": SHOULD,
    "should": SHOULD,
    "must": MUST,
}


def _get_all_conjucted_tokens(token):
    tokens = []
    for child in token.children:
        if child.dep_ == "conj":
            tokens.append(child)
    return tokens


def _find_subjects(verb: spacy.tokens.Token, modal: spacy.tokens.Token):
    subject = [child for child in verb.children if child.dep_ == "nsubj"]
    passive_subject = [child for child in verb.children if child.dep_ == "nsubjpass"]
    csubj = [
        c
        for child in verb.children
        if child.dep_ == "csubj"
        for c in child.children
        if c.dep_ == "nsubj"
    ]

    if len(subject) == 0 and len(passive_subject) == 0:
        # if no subject found, check if there is conjunction on verb, and add subjects of conjucted verb
        if verb.dep_ == "conj":
            head = verb.head
            subject = [child for child in head.children if child.dep_ == "nsubj"]
            passive_subject = [
                child for child in head.children if child.dep_ == "nsubjpass"
            ]
    if len(subject) == 0 and len(passive_subject) == 0:
        subject = [child for child in modal.children if child.dep_ == "nsubj"]
        passive_subject = [
            child for child in modal.children if child.dep_ == "nsubjpass"
        ]

    if len(subject) != 0:
        subject += _get_all_conjucted_tokens(subject[0])
        # check conjucted subjects, and add them to subjects

    return subject, passive_subject, csubj


def _get_coref_text(tokens):
    if len(tokens) == 0:
        return ""
    token = tokens[0]
    corefs = token._.corefs
    if len(corefs) == 0 or token.pos_ != "PRON":
        return ""
    return corefs[0]


def _get_subjects_from_noun_phrase(text):
    """Get all subjects from noun phrase"""
    if text == "":
        return []
    doc = nlp(text)
    root = None
    for t in doc:
        if t.dep_ == "ROOT":
            root = t
            break
    if not root:
        return []
    subjects = [root] + _get_all_conjucted_tokens(root)

    return subjects


def get_deontic_sentences_table(docs: pd.Series) -> pd.DataFrame:
    """Produce table with analysed sentences with deontics from series of parsed texts
    Index of series is path of raw text"""
    results = []
    for id, doc in docs.iteritems():
        for token in doc:
            modal = token.lemma_.lower()
            if modal_category := MODAL_VERBS_MAPPING.get(modal):
                verb = next(token.ancestors, EMPTY_TOKEN)
                if len(verb) != 0:
                    subject, passive_subject, clausal_subject = _find_subjects(
                        verb, token
                    )
                    negated = any([c.dep_ == "neg" for c in verb.children])
                else:
                    subject = []
                    passive_subject = []
                    clausal_subject = []
                    negated = False
                is_question = token.sent[-1].norm_ == "?" or token.sent[-2].norm_ == "?"
                subject_coref_text = _get_coref_text(subject)
                subject_coref = _get_subjects_from_noun_phrase(subject_coref_text)
                result = {
                    "modal": modal_category,
                    "sent": token.sent,  # .text.replace('\n', ' '),
                    "raw_text_path": id,
                    "verb": verb,
                    "subject": subject,
                    "passiveSubject": passive_subject,
                    "clausalSubject": clausal_subject,
                    "token": token,
                    "isQuestion": is_question,
                    "negated": negated,
                    "subjectCorefText": subject_coref_text,
                    "subjectCoref": subject_coref,
                }
                results.append(result)
    result_df = pd.DataFrame(results)

    return result_df


def final_subjects(subjects, coref_subjects):
    """Merges coreference subjects with normal subjects.
    If normal subject is pronoun, replace it with coreferenced"""
    results = []
    append_coref = False
    for s in subjects:
        if s.pos_ == "PRON":
            append_coref = True
        else:
            results.append(s.lemma_.lower())

    if append_coref:
        for s in coref_subjects:
            results.append(s.lemma_.lower())
    return results
