import json
import os
import re

import pandas as pd

OECD_TEXTS = "data/oecd_docs/texts"
NESTA_TEXTS = "data/nesta_ai_governance_docs/texts"


def get_text(path):
    return open(path, 'r').read()


def process_text(text):
    return [str.lower(s) for s in text]


def match_titles(filepaths, meta, title_col, id_col):
    titles = []
    for path in filepaths:
        path = path.split('.')[0]
        title = meta[meta[id_col] == path][title_col].iloc[0]
        titles.append(title)
    return titles


def build_result_entry(title, path, matched_fragment, match_context, arxiv_url, metadata, match_type, doc_type):
    return {
        'doc_type': doc_type,
        'dest_title': title,
        'source_title': metadata['title'],
        'dest_path': path,
        'source_arxiv_url': arxiv_url,
        'match_type': match_type,
        'matched_info': matched_fragment,
        'matched_text': match_context,
    }


def search_arxiv_entry(title, text, path, arxiv_url, metadata, doc_type):
    OFFSET = 30
    matches = []

    arxiv_id = metadata['id'].split('v')[0]
    for match in re.finditer(arxiv_id, text):
        match_text = text[max(0, match.start() - OFFSET): match.end() + OFFSET]
        matches.append(build_result_entry(title, path, arxiv_id, match_text, arxiv_url, metadata, 'by_arxiv_id', doc_type))

    names = [m['name'] for m in metadata['authors']]
    names = [name for name in names if len(name.split(' ')) > 1]
    for name in names:
        for match in re.finditer('{}[$ \W]'.format(name), text):
            match_text = text[max(0, match.start() - OFFSET): match.end() + OFFSET]
            matches.append(
                build_result_entry(title, path, name, match_text, arxiv_url, metadata, 'by_author', doc_type))

    abbreviated_names = ['{}\. {}'.format(name[0], ' '.join(name.split(' ')[1:])) for name in names]
    for name in abbreviated_names:
        if len(name.split(' ')) > 1:
            for match in re.finditer(name + '[$ \W]', text):
                match_text = text[max(0, match.start() - OFFSET): match.end() + OFFSET]
                matches.append(
                    build_result_entry(title, path, name, match_text, arxiv_url, metadata, 'by_author_abbreviation', doc_type))

    return matches


if __name__ == "__main__":
    # oecd
    oecd_filepaths = os.listdir(OECD_TEXTS)
    oecd_texts = [get_text(os.path.join(OECD_TEXTS, path)) for path in oecd_filepaths]
    oecd_meta = pd.read_csv('data/oecd_docs/meta.csv')
    oecd_meta['oecdId'] = oecd_meta['oecdId'].astype(str)
    oecd_titles = match_titles(oecd_filepaths, oecd_meta, 'title', 'oecdId')
    # print(oecd_filepaths)
    # print(oecd_titles)

    # nesta
    nesta_filepaths = os.listdir(NESTA_TEXTS)
    nesta_texts = [get_text(os.path.join(NESTA_TEXTS, path)) for path in nesta_filepaths]
    nesta_meta = pd.read_csv('data/nesta_ai_governance_docs/meta.csv')
    nesta_titles = match_titles(nesta_filepaths, nesta_meta, 'title', 'nestaId')
    # print(nesta_filepaths)
    # print(nesta_titles)

    # arxiv
    arxiv_metadata = json.load(open('data/arxiv_dump/search_results.json'))

    # search loop
    matched_records = []

    # oecd
    for i, (title, textl, path) in enumerate(zip(oecd_titles, oecd_texts, oecd_filepaths)):
        print('{} out of {} OECD docs'.format(i + 1, len(oecd_titles)))
        for arxiv_id, metadata in arxiv_metadata.items():
            new_records = search_arxiv_entry(title, textl, path, arxiv_id, metadata, 'oecd')
            matched_records.extend(new_records)

    # nesta
    for i, (title, textl, path) in enumerate(zip(nesta_titles, nesta_texts, nesta_filepaths)):
        print('{} out of {} NESTA docs'.format(i + 1, len(nesta_titles)))
        for arxiv_id, metadata in arxiv_metadata.items():
            new_records = search_arxiv_entry(title, textl, path, arxiv_id, metadata, 'nesta')
            matched_records.extend(new_records)

    pd.DataFrame.from_records(matched_records).to_csv(open('data/documents_references.csv', 'w'))
