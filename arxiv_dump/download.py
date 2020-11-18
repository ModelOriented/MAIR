import os
import urllib.request as libreq
import feedparser
import requests
import json
import time
import re

from arxiv_dump.keywords import KEYWORDS

BASE_URL = 'http://export.arxiv.org/api/query'
KEYWORDS_FILE = 'keywords.txt'
CATEGORIES = 'arxiv_categories.txt'
PAPERS_DIR = 'papers'
SOURCES_DIR = 'sources'
SEARCH_RESULTS = 'search_results.json'

SOURCES = True
if SOURCES:
    FILES_DIR = SOURCES_DIR
else:
    FILES_DIR = PAPERS_DIR


def get_categories():
    categories = []
    with open(CATEGORIES, 'r') as f:
        for line in f:
            categories.append(line.split(' ')[0])
    return categories


def parse_entry(entry, keyword):
    links = entry['links']
    keyword_name = re.sub('"', '', keyword['name'])
    keyword_name = re.sub('\+', ' ', keyword_name)
    return {
        'id': entry['id'].split('/')[-1],
        'abs_id': entry['id'],
        'title': entry['title'],
        'published': entry['published'],
        'updated': entry['updated'],
        'summary': entry['summary'],
        'authors': entry['authors'],
        'journal_ref': entry['arxiv_journal_ref'] if 'arxiv_journal_ref' in entry else None,
        'links': links,
        'primary_category': entry['arxiv_primary_category']['term'],
        'keywords': [re.sub('"', '', keyword_name)],
    }


def parse_search_records(res, keyword):
    r = res.read()
    results_tree = feedparser.parse(r)
    entries = results_tree['entries']
    records = {entry['id']: parse_entry(entry, keyword) for entry in entries}
    return records


def keyword_string(field, keywords):
    keywords = [re.sub(' ', '+', k) for k in keywords]
    return '+AND+'.join(['{}:{}'.format(field, k) for k in keywords])


def wrap_apostrophes(s):
    return '"{}"'.format(s)


def url_generator(k, categories, step):
    k['name'] = re.sub(' ', '+', k['name'])
    filter_category = '+OR+'.join(['cat:{}'.format(cat) for cat in categories])
    if 'names' in k:
        if k['exact']:
            k['names'] = [wrap_apostrophes(s) for s in k['names']]
        print(keyword_string('abs', k['names']))
        search_url = '+OR+'.join(['({})'.format(keyword_string(f, k['names'])) for f in k['fields']])
    else:
        if k['exact']:
            k['name'] = wrap_apostrophes(k['name'])
        search_url = '+OR+'.join(['({})'.format(keyword_string(f, [k['name']])) for f in k['fields']])
    filter_url = '{}?search_query=(({})+AND({}))'.format(BASE_URL, search_url, filter_category)
    start = 0
    while True:
        yield '{}&start={}&max_results={}'.format(filter_url, start, step)
        start += step


def get_atom_results(k, categories, step=100):
    # fetch results
    records = dict()
    start = 0
    urls = url_generator(k, categories, step)
    while True:
        url = next(urls)
        with libreq.urlopen(url) as res:
            new_records = parse_search_records(res, k)
            print('Fetched info about {} for {}'.format(len(new_records), k))
            print('Together we have: {}'.format(len(records) + len(new_records)))
            records.update(new_records)
            if len(new_records) < step or not new_records:
                break
        start += step

    return records


def get_link_and_filename(record):
    if SOURCES:
        extension = 'tar.gz'
    else:
        extension = 'pdf'
    filename = os.path.join(FILES_DIR, record['id'] + '.{}'.format(extension))
    link = [r['href'] for r in record['links'] if r['type'] == 'application/pdf'][0]
    if SOURCES:
        link = re.sub('/pdf/', '/src/', link)
    return filename, link


def download_file(record):
    # TODO remove older versions when duplicated
    if not record['links']:
        print('Links unavailable for {}'.format(record['id']))
    filename, link = get_link_and_filename(record)
    if not os.path.exists(filename):
        while True:
            try:
                # sleep from time to time
                if hash(record['title']) % 20 == 0:
                    time.sleep(5)
                if hash(record['title']) + 1 % 100 == 0:
                    time.sleep(10)
                if link is None:
                    print('No matching link for download')
                    break
                # a mirror of arXiv for automated access
                print(link)
                response = requests.get(link)
                # print(len(response.content))
                print('Downloading {}'.format(record['title']))
                with open(filename, 'wb') as f:
                    f.write(response.content)
                break
            except ConnectionError as e:
                print(e)
                print('Retrying on download failure...')
                time.sleep(10)
                continue
    else:
        pass
        # print('{} already exists'.format(record['title']))


def download_files(records):
    for i, r in enumerate(records.values()):
        download_file(r)


def update_records(records, new_records):
    for key, v in new_records.items():
        if not key in records:
            records[key] = v
        else:
            records[key]['keywords'] = list(set(records[key]['keywords'] + new_records[key]['keywords']))


if __name__ == "__main__":
    categories = get_categories()
    if not os.path.exists(FILES_DIR):
        os.mkdir(FILES_DIR)

    records = dict()

    if os.path.exists(SEARCH_RESULTS):
        with open(SEARCH_RESULTS, 'r') as f:
            records = json.load(f)
    else:
        for k in KEYWORDS:
            print('Processing keyword: {}'.format(k['name']))
            new_records = get_atom_results(k, categories, step=1000)
            update_records(records, new_records)

        with open(SEARCH_RESULTS, 'w') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    download_files(records)
