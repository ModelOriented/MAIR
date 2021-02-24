import json
import os
import ssl
import urllib.error
from urllib.request import urlopen

import pandas as pd
import wget
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context

URL = "https://www.oecd.ai/ws/AIPO/API/dashboards/policyInitiatives.xqy?conceptUris=undefined"
OUT_DIR_PATH = "data/oecd_docs/"
OUT_META_PATH = "data/oecd_meta.csv"
data = json.load(urlopen(URL))


def parse_result_dict(result):
    name = result["label"]
    oecd_id = result["uri"].split("/")[-1]
    description = result["description"]
    for field in result["fields"]:
        key = field["key"]
        value = field["value"]
        if key == "Country":
            country = value
        elif key == "Public access URL":
            document_url = value
        elif key == "Cover start date":
            start_date = value
        elif key == "Cover end date":
            end_date = value

    document_info = {
        "name": name,
        "description": description,
        "country": country,
        "documentUrl": document_url,
        "startDate": start_date,
        "endDate": end_date,
        "oecdId": oecd_id,
    }
    return document_info


df = pd.DataFrame([parse_result_dict(result) for result in data["results"]])
dff = df[~df["documentUrl"].isna()]
dff2 = dff[dff.documentUrl.str.endswith("pdf")]

dff.to_csv(OUT_META_PATH)
for _, (name, link) in dff2[["oecdId", "documentUrl"]].iterrows():
    file_path = os.path.join(OUT_DIR_PATH, f"{name}.pdf")
    if os.path.isfile(file_path):
        print(f"{file_path} exist, skipping")
    else:
        try:
            wget.download(link, file_path)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print(f"Error downloading ({link}):{e}, skipping")
