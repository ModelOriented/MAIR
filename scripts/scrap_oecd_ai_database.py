import json
import os
import ssl
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from mair import downloading
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context

URL = "https://www.oecd.ai/ws/AIPO/API/dashboards/policyInitiatives.xqy?conceptUris=undefined"
OUT_DOCS_PATH = "data/oecd_docs/raw"
OUT_META_PATH = "data/oecd_docs/meta.csv"


# TODO: download metadata from https://www.oecd.ai/ws/AIPO/API/dashboards/policyInitiative.xqy?uri=http://stip.oecd.org/...
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
        "title": name,
        "description": description,
        "country": country,
        "documentUrl": document_url,
        "startDate": start_date,
        "endDate": end_date,
        "oecdId": oecd_id,
    }
    return document_info


if __name__ == "__main__":
    data = json.load(urlopen(URL))

    df = pd.DataFrame([parse_result_dict(result) for result in data["results"]])
    dff = df[~df["documentUrl"].isna()]
    dff2 = dff[dff.documentUrl.str.endswith("pdf")]
    # create dir if not exist
    Path(OUT_DOCS_PATH).mkdir(parents=True, exist_ok=True)

    dff.to_csv(OUT_META_PATH, index=False)
    for _, (name, link) in tqdm(list(dff2[["oecdId", "documentUrl"]].iterrows())):
        file_path = os.path.join(OUT_DOCS_PATH, f"{name}.pdf")
        downloading.save_pdf_under_path(link, file_path)
