import json

import pandas as pd
import requests
from babelpy import babelfy
from tqdm import tqdm

IN_AFFILIATIONS_PATH = "data/arxiv_dump/affiliations.json"
OUT = "data/processed/affiliations_categories.csv"
API_KEY = "62cb486d-98aa-4f4b-b0cc-f1b6430491b4"
params = dict()
params["lang"] = "EN"
babel_client = babelfy.BabelfyClient(API_KEY, params)


def extract(aff_text):
    ents = []

    try:
        babel_client.babelfy(aff_text)
        ents_info = babel_client.merged_entities
        for ent in ents_info:
            if ent["score"] > 0 and ent is not None:
                entity_url = ent["DBpediaURL"]
                if entity_url != "":
                    ents.append(entity_url)
    except Exception as e:
        print("passing: ", e)

    return ents


def check_properties(link, params):
    a = str(requests.get(link).content)
    for param in params:
        i = a.find(param)
        if i != -1:
            return True
    return False


def check_academia(links):
    return any(
        [
            check_properties(
                l,
                [
                    "http://dbpedia.org/ontology/affiliation",
                    "http://dbpedia.org/ontology/almaMater",
                ],
            )
            for l in links
        ]
    )


def check_industry(links):
    return any(
        [
            check_properties(
                l,
                [
                    "http://dbpedia.org/ontology/industry",
                    "http://dbpedia.org/ontology/Company",
                ],
            )
            for l in links
        ]
    )


if __name__ == "__main__":
    affs = json.load(open(IN_AFFILIATIONS_PATH))
    affs = affs["affiliations"]

    affs2 = {"".join(key.split("v")[:-1]): " ".join(val) for key, val in affs.items()}

    id_to_bdpedia = {id: extract(text) for id, text in tqdm(affs2.items())}

    labels = dict()
    for id, aff_list in tqdm(id_to_bdpedia.items()):
        is_academia = check_academia(aff_list)
        is_industry = check_industry(aff_list)
        labels[id] = {"is_academia": is_academia, "is_industry": is_industry}
    df = pd.DataFrame.from_dict(labels, orient="index")
    df.to_csv(OUT)
