import itertools
import json
import os
import re
import pathos

import pandas as pd
import spacy

# CONFIG
USE_SPACY = False
MATCH_WINDOW_WIDTH = 500
USE_ENTIRE_AI_ARXIV = True  # use all AI papers from arxiv or only the XAI subset

# PATHS
OECD_TEXTS = "data/oecd_docs/texts"
NESTA_TEXTS = "data/nesta_ai_governance_docs/texts"
if USE_ENTIRE_AI_ARXIV:
    arxiv_ai_metadata_path = "data/citation_graph/arxiv-ai-metadata.json"
else:
    arxiv_ai_metadata_path = "data/arxiv_dump/search_results.json"
CITATION_MATCHES_PATH = 'data/citation_graph/documents_references.csv'
CITATION_GRAPH_PATH = 'data/citation_graph/citations_graph.csv'
PAPER_CITATIONS_CHECKPOINTS_PATH = "data/citation_graph/checkpoints"
PROCESSED_RICH_TEXTS_PATH = 'data/citation_graph/processed_documents'
OECD_METADATA_PATH = 'data/oecd_docs/meta.csv'
NESTA_METADATA_PATH = 'data/nesta_ai_governance_docs/meta.csv'

# REGEX
_ARXIV_ID_PATTERN = re.compile(r"\d{4}\.\d{4,5}") # TODO it works for >2007 papers only
_ONLY_ALPHANUMERIC = re.compile("\W+")


if USE_SPACY:
    # Load English NER and sentence tokenizer
    nlp = spacy.load("en_core_web_sm", disable=("parser"))
    sbd = nlp.create_pipe('sentencizer')
    # Add the component to the pipeline
    nlp.add_pipe(sbd)
    nlp.max_length = 5000000


def get_text(path):
    return open(path, 'r').read()


def process_text(text):
    return [str.lower(s) for s in text]


def match_titles(filepaths, meta, title_col, id_col):
    # match documents with titles
    titles = []
    for path in filepaths:
        path = path.split('.')[0]
        title = meta[meta[id_col] == path][title_col].iloc[0]
        titles.append(title)
    return titles


def build_match_entry(title, path, matched_fragment, match_context, arxiv_url, metadata, match_type, doc_type, match_confidence):
    return {
        'id_dest': path.split('.')[0],
        'id_source': arxiv_url.split('/')[-1].split('v')[0],  # TODO works for >2007 papers only
        'doc_type': doc_type,
        'dest_title': title,
        'source_title': metadata['title'],
        'dest_path': path,
        'source_arxiv_url': arxiv_url,
        'match_type': match_type,
        'matched_info': matched_fragment,
        'matched_text': match_context,
        'match_confidence': match_confidence
    }


def match_by_title(plain_title, title, plain_text):
    MINI_OFFSET = 50
    if plain_title in plain_text and len(title.split(' ')) > 3 and len(plain_title) > 12:
        match_obj = re.search(plain_title, plain_text)
        match_text = plain_text[max(0, match_obj.start() - MINI_OFFSET): match_obj.end() + MINI_OFFSET]
        return True, match_obj, match_text, 1
    else:
        return False, None, "", 0


def match_by_author(author_tokens, plain_text):
    return any(tok in plain_text for tok in author_tokens)


def search_arxiv_entry(title, rich_text, path, arxiv_url, metadata, doc_type):
    matches = []

    arxiv_id = metadata['id'].split('v')[0]

    # By arxiv ID
    for candidate_match in rich_text['arxiv_id_candidates']:
        matched_id, start, end = candidate_match
        if arxiv_id == matched_id:
            match_text = rich_text['text'][max(0, start - MATCH_WINDOW_WIDTH): end + MATCH_WINDOW_WIDTH]
            matches.append(build_match_entry(title, path, arxiv_id, match_text, arxiv_url, metadata,
                                             'by_arxiv_id', doc_type, match_confidence=1))


    # By a combo of title and authors
    plain_title = str.lower(_ONLY_ALPHANUMERIC.sub("", metadata['title']))

    is_match, match_obj, match_text, match_confidence = match_by_title(plain_title, metadata['title'], rich_text['plain_text'])

    if is_match:
        author_names = [m['name'] for m in metadata['authors']]
        name_tokens = [name.split(' ') for name in author_names]
        name_tokens = flatten(name_tokens)
        name_tokens = [str.lower(_ONLY_ALPHANUMERIC.sub("", tok)) for tok in name_tokens]
        name_tokens = [tok for tok in name_tokens if len(tok) > 3]

        if any(tok in match_text for tok in name_tokens):
            print("ACC: {}".format(plain_title))
            matches.append(
                build_match_entry(title, path, plain_title, match_text,
                                  arxiv_url, metadata, 'by_title', doc_type, match_confidence)
            )
        else:  # lower confidence
            print("ACC: {}".format(plain_title))
            matches.append(
                build_match_entry(title, path, plain_title, match_text,
                                  arxiv_url, metadata, 'by_title', doc_type, match_confidence * 0.8)
            )

    return matches


def flatten(ll):
    return list(itertools.chain.from_iterable(ll))


def build_rich_text_representation(text, name):
    name = name.split('.')[0] + '.json'
    cache_path = "{}/{}".format(PROCESSED_RICH_TEXTS_PATH, name)
    if os.path.exists(cache_path):  # Read from cache - it's compute heavy
        print('Reading {} rich information from cache'.format(name))
        with open(cache_path, 'rb') as f:
            return json.load(f)
    else:
        print('Computing enriched text information on {}'.format(name))

        # regex
        arxiv_id_candidates = [(m.group(0), m.start(), m.end()) for m in _ARXIV_ID_PATTERN.finditer(text)]

        rich_data = {
            'text': text,
            'plain_text': str.lower(_ONLY_ALPHANUMERIC.sub("", text)),
            'arxiv_id_candidates': arxiv_id_candidates,
        }

        if USE_SPACY:
            # SpaCy
            doc = nlp(text)
            people_names = []
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text) > 3 and len(ent.text.split(' ')) > 1:
                    people_names.append((ent.text, ent.start_char, ent.end_char))
            rich_data['people_name'] = people_names

        # Cache results
        with open(cache_path, 'w') as f:
            json.dump(rich_data, f, indent=2)
        return rich_data


if __name__ == "__main__":
    # oecd
    oecd_filepaths = os.listdir(OECD_TEXTS)
    oecd_texts = [get_text(os.path.join(OECD_TEXTS, path)) for path in oecd_filepaths]
    oecd_meta = pd.read_csv(OECD_METADATA_PATH)
    oecd_meta['oecdId'] = oecd_meta['oecdId'].astype(str)
    oecd_titles = match_titles(oecd_filepaths, oecd_meta, 'title', 'oecdId')
    oecd_rich_texts = [build_rich_text_representation(text, name) for text, name in zip(oecd_texts, oecd_filepaths)]

    # nesta
    nesta_filepaths = os.listdir(NESTA_TEXTS)
    nesta_texts = [get_text(os.path.join(NESTA_TEXTS, path)) for path in nesta_filepaths]
    nesta_meta = pd.read_csv(NESTA_METADATA_PATH)
    nesta_titles = match_titles(nesta_filepaths, nesta_meta, 'title', 'nestaId')
    nesta_rich_texts = [build_rich_text_representation(text, name) for text, name in zip(nesta_texts, nesta_filepaths)]

    # arxiv
    arxiv_metadata: dict = json.load(open(arxiv_ai_metadata_path))

    print(
        "Oecd documents: {}".format(len(oecd_titles)),
        "Nesta documents: {}".format(len(nesta_titles)),
        "Arxiv documents: {}".format(len(arxiv_metadata))
    )

    # search loop
    matched_records = []


    # oecd
    for i, (title, textl, path) in enumerate(zip(oecd_titles, oecd_rich_texts, oecd_filepaths)):
        print('{} out of {} OECD docs -- {}'.format(i + 1, len(oecd_titles), path))
        with pathos.multiprocessing.Pool(8) as p:
            new_records = p.map(lambda dict_item: search_arxiv_entry(title, textl, path, dict_item[0], dict_item[1], 'oecd'),
                                list(zip(arxiv_metadata.keys(), arxiv_metadata.values())))
            new_records = flatten(new_records)
            print(new_records)
            with open('{}/{}.json'.format(PAPER_CITATIONS_CHECKPOINTS_PATH, path.split('.')[0]), 'w') as f:
                json.dump(new_records, f, indent=2)
            matched_records.extend(new_records)




    # nesta
    for i, (title, textl, path) in enumerate(zip(nesta_titles, nesta_rich_texts, nesta_filepaths)):
        print('{} out of {} NESTA docs -- {}'.format(i + 1, len(nesta_titles), path))
        with pathos.multiprocessing.Pool(8) as p:
            new_records = p.map(lambda dict_item: search_arxiv_entry(title, textl, path, dict_item[0], dict_item[1], 'nesta'),
                                list(zip(arxiv_metadata.keys(), arxiv_metadata.values())))
            new_records = flatten(new_records)
            print(new_records)
            with open('{}/{}.json'.format(PAPER_CITATIONS_CHECKPOINTS_PATH, path.split('.')[0]), 'w') as f:
                json.dump(new_records, f, indent=2)
            matched_records.extend(new_records)

    graph_df = pd.DataFrame.from_records(matched_records)
    graph_df.to_csv(open(CITATION_MATCHES_PATH, 'w'))
    graph_df[graph_df['confidence' == 1]][['id_dest', 'id_source']].drop_duplicates().to_csv(open(CITATION_GRAPH_PATH, 'w'), index=False)
