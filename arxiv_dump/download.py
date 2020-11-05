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
SEARCH_RESULTS_DIR = 'search_results'


def get_categories():
    categories = []
    with open(CATEGORIES, 'r') as f:
        for line in f:
            categories.append(line.split(' ')[0])
    return categories


def parse_entry(entry, keyword):
    links = [link['href'] for link in entry['links'] if 'title' in link and link['type'] == 'application/pdf']
    if links:
        link = links[0]
    else:
        link = None
    return {
        'id': entry['id'].split('/')[-1],
        'abs_id': entry['id'],
        'title': entry['title'],
        'published': entry['published'],
        'updated': entry['updated'],
        'summary': entry['summary'],
        'authors': entry['authors'],
        'journal_ref': entry['arxiv_journal_ref'] if 'arxiv_journal_ref' in entry else None,
        'link': link,
        'primary_category': entry['arxiv_primary_category']['term'],
        'keyword': re.sub('"', '', keyword['name']),
    }


def parse_search_records(res, keyword):
    r = res.read()
    results_tree = feedparser.parse(r)
    entries = results_tree['entries']
    records = [parse_entry(entry, keyword) for entry in entries]
    return records


def url_generator(k, categories, step):
    k['name'] = re.sub(' ', '+', k['name'])
    if k['exact']:
        k['name'] = '"{}"'.format(k['name'])
    filter_category = '+OR+'.join(['cat:{}'.format(cat) for cat in categories])
    search_url = '+OR+'.join(['{}:{}'.format(f, k['name']) for f in k['fields']])
    filter_url = '{}?search_query=({})&({})'.format(BASE_URL, search_url, filter_category)
    start = 0
    while True:
        yield '{}&start={}&max_results={}'.format(filter_url, start, step)
        start += step


def get_atom_results(k, categories, use_cache=True, step=100):
    filename = os.path.join(SEARCH_RESULTS_DIR, 'search_results_{}.json'.format(k['name']))

    # read from cache
    if os.path.exists(filename) and use_cache:
        with open(filename, 'r') as f:
            return json.load(f)

    # fetch results
    records = []
    start = 0
    urls = url_generator(k, categories, step)
    while True:
        url = next(urls)
        with libreq.urlopen(url) as res:
            new_records = parse_search_records(res, k)
            print('Fetched info about {} for {}'.format(len(new_records), k))
            print('Together we have: {}'.format(len(records) + len(new_records)))
            records.extend(new_records)
            if len(new_records) < step or not new_records:
                break
        start += step

    # cache the result
    with open(filename, 'w') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return records


def download_pdf(record):
    # TODO remove older versions when duplicated

    if not record['link']:
        print('Link unavailable for {}'.format(record['id']))
    filename = os.path.join(PAPERS_DIR, record['keyword'], record['id'] + '.pdf')
    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            while True:
                try:
                    # sleep from time to time
                    if hash(record['title']) % 20 == 0:
                        time.sleep(5)
                    if hash(record['title']) + 1 % 100 == 0:
                        time.sleep(10)

                    # a mirror of arXiv for automated access
                    link = record['link'][:7] + 'export.' + record['link'][7:]
                    print(link)
                    response = requests.get(link)
                    # print(len(response.content))
                    print('Downloading {}'.format(record['title']))
                    f.write(response.content)
                    break
                except Exception as e:
                    print(e)
                    print('Retrying on download failure...')
                    time.sleep(10)
                    continue
    else:
        pass
        # print('{} already exists'.format(record['title']))


def download_files(records):
    for i, r in enumerate(records):
        download_pdf(r)


if __name__ == "__main__":
    categories = get_categories()
    if not os.path.exists(PAPERS_DIR):
        os.mkdir(PAPERS_DIR)
    if not os.path.exists(SEARCH_RESULTS_DIR):
        os.mkdir(SEARCH_RESULTS_DIR)

    for k in KEYWORDS:
        if not os.path.exists(os.path.join(PAPERS_DIR, k['name'])):
            os.mkdir(os.path.join(PAPERS_DIR, k['name']))

        print('Processing keyword: {}'.format(k['name']))
        records = get_atom_results(k, categories, use_cache=False, step=100)
        download_files(records)
