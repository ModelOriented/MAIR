import os
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup
from mair import downloading
from tqdm import tqdm

URL = "https://super-ai.diascreative.net/"
OUT_META_PATH = "data/nesta_ai_governance_docs/meta.csv"
OUT_DOCS_PATH = "data/nesta_ai_governance_docs/raw"


def get_document_link(link_to_page: str):
    text = urlopen(Request(link_to_page, headers={"User-Agent": "Mozilla/5.0"})).read()
    soup = BeautifulSoup(text)
    return (
        soup.find("div", "sub-page__copy")
        .find("div", attrs={"class": False})
        .find("a")["href"]
    )


def gather_document_data(article):
    href = article.find("a")["href"]
    try:
        document_link = get_document_link(urljoin(URL, href))
    except Exception:
        document_link = ""
    title = article.find("h1", "heading-4").text
    country = article.find("p", "sector-label-tag").text

    category, date_str = (
        text for text in article.find("span", "listings-topic").stripped_strings
    )
    (_, year) = date_str.split(",")
    try:
        document_type = article.find_all("p", "listings-text")[1].text.strip()
    except IndexError:
        document_type = ""
    actors = article.find("p", "listings-text").text
    data = {
        "nestaId": article["id"],
        "title": title,
        "country": country,
        "documentUrl": document_link,
        "year": int(year),
        "category": category,
        "documentType": document_type,
        "actors": actors,
    }
    return data


if __name__ == "__main__":
    Path(OUT_DOCS_PATH).mkdir(parents=True, exist_ok=True)

    page_url = URL
    text = urlopen(Request(page_url, headers={"User-Agent": "Mozilla/5.0"})).read()
    soup = BeautifulSoup(text)
    articles = soup.find_all("article")

    data = [gather_document_data(article) for article in tqdm(articles)]
    df = pd.DataFrame(data)
    df.to_csv(OUT_META_PATH, index=False)

    documents = df.to_dict(orient="records")
    for doc in tqdm(documents):
        link = doc["documentUrl"]
        doc_id = doc["id"]
        file_path = os.path.join(OUT_DOCS_PATH, f"{doc_id}.pdf")
        downloading.save_pdf_under_path(link, file_path)
