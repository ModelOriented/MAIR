import os

import pandas as pd
from mair.data_loading import load_legal_documents_metadata

IN_ANNOTATION = "data/golden_standard/policy_docs_categories.csv"
OUT_MERGED_META = "data/policy_docs_all/metadata.csv"
categories_map = {
    "A": "diagnosis",
    "B": "principles",
    "C": "strategy",
    "D": "pre-regulation",
    "E": "regulation",
    "F": "body",
}


def get_author(s):
    if type(s) != str:
        return "other"
    if ".org" in s:
        return "organisation"
    if ".gov" in s:
        return "government"
    if ".com" in s:
        return "company"
    else:
        return "other"


if __name__ == "__main__":
    os.makedirs("data/policy_docs_all/", exist_ok=True)
    df_categories = pd.read_csv(IN_ANNOTATION)

    df_meta = load_legal_documents_metadata()

    df_merged = df_meta.merge(df_categories, on="id", how="left")

    df_merged["documentFunction"] = df_merged["consensusCategory"].map(categories_map)
    df_merged["author"] = df_merged.documentUrl.apply(get_author)
    df_merged.loc[
        (df_merged.country.str.split(",").str.len() > 1)
        & (df_merged.author == "other"),
        "author",
    ] = "international"
    df_merged.loc[
        (df_merged.country != "Global") & (df_merged.author == "other"), "author"
    ] = "government"
    df_merged.to_csv(OUT_MERGED_META, index=False)
