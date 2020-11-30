import re

import pandas as pd

UNI_LIST_PATH = "world-universities.csv"


uni_phrases = {
    "universit",
    "school",
    "college",
    "institut",
    "academy",
    "universidad",
    "polyte",
    "schule",
    "ecole",
    "escuela",
}


def get_unis():
    df = pd.read_csv(UNI_LIST_PATH)
    print(df.head())
    return set(df["name"])


def match(text):
    for u in uni_phrases:
        if re.search(u, text):
            return True
    return False


def find_phrases():
    unis = get_unis()
    all_count = len(unis)
    unmatched = 0
    for u in unis:
        if not match(u.lower()):
            unmatched += 1
            print(u)
    print("{} / {}".format(unmatched, all_count))
