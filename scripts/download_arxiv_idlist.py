import pandas as pd
import requests
import time
import os

# paths
CITATION_GRAPH_PATH = "../data/citation_graph/citations_graph.csv"
SOURCES_DEST_PATH = "../data/citation_graph/arxiv_sources"

BASE_URL = "http://export.arxiv.org/"


def get_arxiv_ids():
    citation_graph_df = pd.read_csv(CITATION_GRAPH_PATH, dtype={'id_source': str})
    return set(citation_graph_df['id_source'])

def _download_file(filename, link, id_, type_):
    if not os.path.exists(filename):
        while True:
            try:
                # sleep from time to time
                if hash(link) % 40 == 0:
                    time.sleep(1)
                if hash(link) + 1 % 100 == 0:
                    time.sleep(3)
                # a mirror of arXiv for automated access
                response = requests.get(link)
                # print(len(response.content))
                print("Downloading {} {}".format(id_, type_))
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


def download_paper(arxiv_id: str):
    filename_source = os.path.join(SOURCES_DEST_PATH, 'sources', arxiv_id + '.tar.gz')
    filename_pdf = os.path.join(SOURCES_DEST_PATH, 'pdfs', arxiv_id + '.pdf')

    link_source = '{}/src/{}'.format(BASE_URL, arxiv_id)
    link_pdf = '{}/pdf/{}'.format(BASE_URL, arxiv_id)

    _download_file(filename_source, link_source, arxiv_id, 'sources')
    _download_file(filename_pdf, link_pdf, arxiv_id, 'pdf')


def download_arxiv_sources(ids: set):
    for arxiv_id in ids:
        download_paper(arxiv_id)


if __name__ == "__main__":
    arxiv_ids = get_arxiv_ids()
    download_arxiv_sources(arxiv_ids)