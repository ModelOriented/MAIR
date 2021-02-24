from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

URL = "https://super-ai.diascreative.net/"
OUT_TABLE_PATH = "data/ai_governance_meta.csv"
page_url = URL

text = urlopen(Request(page_url, headers={"User-Agent": "Mozilla/5.0"})).read()
soup = BeautifulSoup(text)
articles = soup.find_all("article")


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
        "title": title,
        "country": country,
        "documentLink": document_link,
        "year": int(year),
        "category": category,
        "documentType": document_type,
        "actors": actors,
    }
    return data


if __name__ == "__main__":
    data = [gather_document_data(article) for article in tqdm(articles)]
    df = pd.DataFrame(data)
    df.to_csv(OUT_TABLE_PATH)
