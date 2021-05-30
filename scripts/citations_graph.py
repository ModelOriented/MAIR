# get all arxiv ids
# fetch metadata from Semantic Scholar for all of them and dump it
# visualize the citation graph
# what is most cited?
# What are the most frequent authors by name/id?

import json
import os
import time
from collections import Counter

import semanticscholar as sch

GRAPH_JSON = "../data/arxiv_dump/citations_graph.json"
SEMANTIC_SCHOLAR_PAPER_BASE_URL = "https://api.semanticscholar.org/arXiv"
PAPERS_METADATA_PATH = "../data/arxiv_dump/semantic_scholar.json"


def get_paper_ids():
    sources = "../data/arxiv_dump/sources"
    paper_ids = set(os.listdir(sources))
    paper_ids = set(filter(lambda s: not s.endswith("tar.gz"), paper_ids))
    paper_ids = set(s.split("v")[0] for s in paper_ids)
    return paper_ids


def fetch_paper_information(arxiv_id):
    print("Fetching: {}".format(arxiv_id))
    time.sleep(2.5)
    paper = sch.paper(
        "arXiv:{}".format(arxiv_id), timeout=10, include_unknown_references=True
    )
    try:
        return paper, [
            p["arxivId"] for p in paper["references"] if p["arxivId"] is not None
        ]
    except KeyError:
        return paper, []


def build_citations_graph(paper_ids):
    graph = dict()
    papers_data = dict()
    for i, arxiv_id in enumerate(paper_ids):
        if i % 20 == 19:
            print("Fetched {}/{} documents".format(i, len(paper_ids)))
        papers_data[arxiv_id], graph[arxiv_id] = fetch_paper_information(arxiv_id)
    with open(GRAPH_JSON, "w") as f:
        json.dump(graph, f, indent=2)
    with open(PAPERS_METADATA_PATH, "w") as f:
        json.dump(papers_data, f, indent=2)


def calculate_graph_stats():
    with open(GRAPH_JSON, "r") as f:
        graph = json.load(f)
    with open(PAPERS_METADATA_PATH, "r") as f:
        metadata = json.load(f)
    c = Counter()
    for g in graph.values():
        c.update(g)
    for id_, count in c.most_common():
        if count > 10:
            title = ""
            if id_ in metadata:
                title = metadata[id_]["title"]
            print(id_, count, id_ in graph, title)


if __name__ == "__main__":
    paper_ids = get_paper_ids()
    # build_citations_graph(list(paper_ids))
    calculate_graph_stats()
