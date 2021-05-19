"""Script downloading arxiv dump"""

import json
import os
import re
import time
import urllib.request as libreq

import feedparser
import requests
import typer
from mair.arxiv_dump.keywords import KEYWORDS

BASE_URL = "http://export.arxiv.org/api/query"
ARXIV_CATEGORIES_PATH_INPUT = "data/arxiv_dump/arxiv_categories.txt"
PAPERS_DIR_OUT = "data/arxiv_dump/papers"
SOURCES_DIR_OUT = "data/arxiv_dump/sources"
SEARCH_RESULTS_PATH_OUT = "data/arxiv_dump/search_results.json"


def get_categories():
    categories = []
    with open(ARXIV_CATEGORIES_PATH_INPUT, "r") as f:
        for line in f:
            categories.append(line.split(" ")[0])
    return categories


def parse_entry(entry, keyword):
    links = entry["links"]
    keyword_name = re.sub('"', "", keyword["name"])
    keyword_name = re.sub(r"\+", " ", keyword_name)
    try:
        affiliation = entry["arxiv_affiliation"]
    except KeyError:
        affiliation = None

    return {
        "id": entry["id"].split("/")[-1],
        "abs_id": entry["id"],
        "title": entry["title"],
        "published": entry["published"],
        "updated": entry["updated"],
        "summary": entry["summary"],
        "authors": entry["authors"],
        "journal_ref": entry["arxiv_journal_ref"]
        if "arxiv_journal_ref" in entry
        else None,
        "links": links,
        "affiliation": affiliation,
        "primary_category": entry["arxiv_primary_category"]["term"],
        "keywords": [re.sub('"', "", keyword_name)],
    }


def parse_search_records(res, keyword):
    r = res.read()
    results_tree = feedparser.parse(r)
    entries = results_tree["entries"]
    records = {entry["id"]: parse_entry(entry, keyword) for entry in entries}
    return records


def keyword_string(field, keywords):
    keywords = [re.sub(" ", "+", k) for k in keywords]
    return "+AND+".join(["{}:{}".format(field, k) for k in keywords])


def wrap_apostrophes(s):
    return '"{}"'.format(s)


def url_generator(k, categories, step):
    k["name"] = re.sub(" ", "+", k["name"])
    filter_category = "+OR+".join(["cat:{}".format(cat) for cat in categories])
    if "names" in k:
        if k["exact"]:
            k["names"] = [wrap_apostrophes(s) for s in k["names"]]
        print(keyword_string("abs", k["names"]))
        search_url = "+OR+".join(
            ["({})".format(keyword_string(f, k["names"])) for f in k["fields"]]
        )
    else:
        if k["exact"]:
            k["name"] = wrap_apostrophes(k["name"])
        search_url = "+OR+".join(
            ["({})".format(keyword_string(f, [k["name"]])) for f in k["fields"]]
        )
    filter_url = "{}?search_query=(({})+AND({}))".format(
        BASE_URL, search_url, filter_category
    )
    start = 0
    while True:
        yield "{}&start={}&max_results={}".format(filter_url, start, step)
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
            print("Fetched info about {} for {}".format(len(new_records), k))
            print("Together we have: {}".format(len(records) + len(new_records)))
            records.update(new_records)
            if len(new_records) < step or not new_records:
                break
        start += step

    return records


def get_link_and_filename(record, sources: bool, files_dir: str):
    link = [r["href"] for r in record["links"] if r["type"] == "application/pdf"][0]
    if sources:
        extension = "tar.gz"
    else:
        extension = "pdf"
    filename = os.path.join(files_dir, record["id"] + ".{}".format(extension))
    if sources:
        print(link)
        link = re.sub("/pdf/", "/src/", link)
    return filename, link


def download_file(record, sources: bool, files_dir):
    filename, link = get_link_and_filename(record, sources, files_dir)
    if not os.path.exists(filename):
        while True:
            try:
                # sleep from time to time
                if hash(record["title"]) % 20 == 0:
                    time.sleep(5)
                if hash(record["title"]) + 1 % 100 == 0:
                    time.sleep(10)
                if link is None:
                    print("No matching link for download")
                    break
                # a mirror of arXiv for automated access
                response = requests.get(link)
                # print(len(response.content))
                print("Downloading {}".format(record["title"]))
                with open(filename, "wb") as f:
                    f.write(response.content)
                break
            except ConnectionError as e:
                print(e)
                print("Retrying on download failure...")
                time.sleep(10)
                continue
    else:
        pass
        # print('{} already exists'.format(record['title']))


def download_files(records: dict, sources: bool, files_dir: str):
    for i, r in enumerate(records.values()):
        download_file(r, sources, files_dir)


def update_records(records, new_records):
    for key, v in new_records.items():
        if key not in records:
            records[key] = v
        else:
            records[key]["keywords"] = list(
                set(records[key]["keywords"] + new_records[key]["keywords"])
            )


def main(download_sources: bool = False, download_pdfs: bool = False):
    categories = get_categories()

    records = dict()

    if os.path.exists(SEARCH_RESULTS_PATH_OUT):
        with open(SEARCH_RESULTS_PATH_OUT, "r") as search_results_file:
            records = json.load(search_results_file)
    else:
        for k in KEYWORDS:
            print("Processing keyword: {}".format(k["name"]))
            new_records = get_atom_results(k, categories, step=1000)
            update_records(records, new_records)

        with open(SEARCH_RESULTS_PATH_OUT, "w") as search_results_file:
            json.dump(records, search_results_file, indent=2, ensure_ascii=False)
    if download_sources:
        if not os.path.exists(SOURCES_DIR_OUT):
            os.mkdir(SOURCES_DIR_OUT)
        download_files(records, True, SOURCES_DIR_OUT)
    if download_pdfs:
        if not os.path.exists(PAPERS_DIR_OUT):
            os.mkdir(PAPERS_DIR_OUT)
        download_files(records, False, PAPERS_DIR_OUT)


if __name__ == "__main__":
    typer.run(main)
