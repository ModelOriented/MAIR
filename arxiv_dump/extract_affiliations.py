import json
import os
import re
import spacy
from collections import Counter

from arxiv_dump.utils import uni_phrases

SOURCE_DIR = 'sources'
nlp = spacy.load('en_core_web_sm')


def clean_text(text, prune_document=True):
    pos = text.find('\\begin{abstract}')
    if pos >= 0:
        text = text[:pos]
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


def cleanup(text):
    text = re.sub('\\\[a-zA-z]+?{', '', text)
    text = re.sub('[a-zA-z0-9]+@.+?\.[a-z]+?', '', text)  # remove emails
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = re.sub('\s+', ' ', text)
    text = re.sub('[\\\\%\{\}\(\)\[\]\~\$\^\*]', '', text)
    return text


def is_academic_match(text):
    for u in uni_phrases:
        if re.search(u, text):
            return True
    return False


def retrieve_ner(cand, confidence):
    cand = cleanup(cand)
    if len(cand) < 3:
        return []
    doc = nlp(cand)
    orgs = []
    for ent in doc.ents:
        if is_academic_match(ent.text.lower()):
            orgs.append(ent.text)
        elif ent.label_ == 'ORG' and len(ent.text) > 2:
            orgs.append(ent.text)
    return orgs


def extract_affiliations_from_text(text):
    affiliations = set()

    # list of patterns TODO optimize this
    patterns = {
        '\\\icmlaffiliation *{.*?}{': 1,
        '\\\institution *{': 1,
        '\\\\affil(iation)?.*?(\[.*?\])?{': 1,
        '\\\institute *{': 1,
        '\\\\AFF *{': 1,
        '\\\IEEEauthorblockA *{': 1,
        '\\\\address\[.*?\] *{': 0,
        '\\\\affiliations *{': 0,
        '\\\\aistatsaddress{': 0,
        '\\\\author *{': 0,  # TOO broad might cover some other tags
    }

    for pattern in patterns.keys():
        compiled_pattern = re.compile(pattern)
        for m in compiled_pattern.finditer(text, re.DOTALL):
            cand = extract_candidate_affiliation(text, m.end())
            affs = retrieve_ner(cand, patterns[pattern])
            if affs:
                affiliations.update(affs)
        if affiliations:
            return affiliations

    if affiliations:
        return affiliations

    # last case resort
    retrieve_ner(text, confidence=-1)

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


def generate_stats(results):
    affiliations = results['affiliations']
    academic = 0
    companies_count = Counter()
    companies_set = {'google', 'apple', 'netflix', 'microsoft', 'ibm', 'facebook', 'amazon'}

    for aff in affiliations.values():
        if any(is_academic_match(text.lower()) for text in aff):
            academic += 1
        else:
            pass
            #print(aff)

    for aff in affiliations.values():
        merge = ' '.join(aff)
        for c in companies_set:
            if c in merge.lower():
                companies_count[c] += 1

    print('Academic: {} / {} / {}'.format(academic, results['matched_count'], results['all_count']))
    print(companies_count)


if __name__ == "__main__":
    sources = [f for f in os.listdir(SOURCE_DIR) if not f.endswith('tar.gz')]
    # results = generate_results(sources, 'affiliations.json')
    results = json.load(open('affiliations.json', 'r'))
    generate_stats(results)