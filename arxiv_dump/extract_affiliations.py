"""
GOALS
* extract affiliations
* generate a list of unmatched papers
* generate a list of papers without sources
* utility for returning all tex files
* dump results in json format
* improve and clean, regular regex doesn't work! (prune some latex syntax, parse no of brackets etc.)
"""

import json
import os
import re
import spacy

SOURCE_DIR = 'sources'


def clean_text(text):
    lines = text.split('\n')
    lines = [l for l in lines if not l.startswith('%')]
    return '\n'.join(lines)


def get_text(path):
    with open(path, 'r') as f:
        try:
            return f.read()
        except UnicodeDecodeError as e:
            #print('Failed to read the file {}'.format(path))
            return ""


def get_all_files(s):
    paper_dir = os.path.join(SOURCE_DIR, s)
    return [os.path.join(paper_dir, f) for f in os.listdir(paper_dir)]


def get_tex_files(s):
    return [f for f in get_all_files(s) if f.endswith('.tex')]


def extract_candidate_affiliation(text, start):
    pos = start
    open = 1
    while open > 0:
        if text[pos] == '{':
            open += 1
        elif text[pos] == '}':
            open -= 1
        pos += 1
    return text[start:pos - 1]


def retrieve_ner(cand):


    return {}


def extract_affiliations_from_text(text):
    affiliations = set()

    # list of patterns TODO optimize this
    patterns = [
        '\\\icmlaffiliation *{.*?}{',
        '\\\institution *{',
        '\\\\affil(iation)?.*?(\[.*?\])?{',
        '\\\institute *{',
        '\\\\AFF *{',
        '\\\IEEEauthorblockA *{',
        '\\\\address\[.*?\] *{',
        '\\\\affiliations *{',
        '\\\\aistatsaddress{',
        '\\\\author *{',  # TOO broad???
    ]

    for pattern in patterns:
        compiled_pattern = re.compile(pattern)
        for m in compiled_pattern.finditer(text, re.DOTALL):
            cand = extract_candidate_affiliation(text, m.end())
            affs = retrieve_ner(cand)
            if aff:
                affiliations.update(aff)
        if affiliations:
            return affiliations

    for m in re.finditer('\$\^\{\d+?\}\$(.*)', text):
        affiliations.add(m.group()[0])
    if affiliations:
        return affiliations

    return affiliations


def get_paper_affiliations(s):
    tex_files = get_tex_files(s)
    affiliations = set()
    for f in tex_files:
        text = get_text(f)
        text = clean_text(text)
        affiliations.update(extract_affiliations_from_text(text))
    return affiliations, len(tex_files) > 0


def generate_results(sources, path):
    unmatched = []
    notex = []
    affiliations_dict = {}
    for s in sources:
        aff, latex = get_paper_affiliations(s)
        if aff:
            affiliations_dict[s] = list(aff)
        else:
            if latex:
                unmatched.append(s)
            else:
                notex.append(s)
    results = {
        'unmatched_count': len(unmatched),
        'all_count': len(unmatched) + len(notex) + len(affiliations_dict),
        'notex_count': len(notex),
        'matched_count': len(affiliations_dict),
        'unmatched': unmatched,
        'notex': notex,
        'affiliations': affiliations_dict
    }
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    sources = [f for f in os.listdir(SOURCE_DIR) if not f.endswith('tar.gz')]
    results = generate_results(sources, 'affiliations.json')
    # some postprocessing (answering questions, report, stats)