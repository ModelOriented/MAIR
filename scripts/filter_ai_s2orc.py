import glob
import os

import pandas as pd
import spacy.lang.en
from spacy.matcher import PhraseMatcher
from tqdm import tqdm

S2_ORC_INPUT_PATHS = "data/s2orc/metadata/comp_sci/*.jsonl"
AI_PAPERS_OUT_PATH = "data/s2orc/ai_papers_meta.csv"

tqdm.pandas()
AI_PAPER_PATTERNS = [
"Transfer Learning", 
"Gradient Boosting", 
"Adversarial Learning", 
"Feature Learning", 
"Generative Adversarial Net*", 
"Representation Learning", 
("Multiagent Learning", 
"Multi‑agent Learning"), 
"Reservoir Computing", 
"Co‑training", 
("Pac Learning", 
"Probabl* Approximate* Correct Learning"), 
"Extreme Learning Machine*", 
"Ensemble Learning", 
"Machine* Intelli‑gen*", 
("Neuro fuzzy", 
"Neurofuzzy"), 
"Lazy Learning", 
("Multi* instance Learning", 
"Multi‑instance Learning"), 
("Multi* task Learning", 
"Multitask Learning"), 
"Computation* Intelligen*", 
"Neural Model*", 
("Multi* label Learning", 
"Multilabel Learning"), 
"Similarity Learning", 
"Statistical Relation* Learning", 
"Support* Vector* Regression", 
"Manifold Regulari?ation", 
"Decision Forest*", 
"Generali?ation Error*", 
"Transductive Learning", 
("Neurorobotic*", 
"Neuro‑robotic*"), 
"Inductive Logic Programming", 
"Natural Language Understanding", 
("Ada‑boost*", 
"Adaptive Boosting"), 
"Incremental Learning", 
"Random Forest*", 
"Metric Learning", 
"Neural Gas", 
"Grammatical Inference", 
"Support* Vector* Machine*", 
("Multi* label Clas‑sification", 
"Multilabel Classification"), 
"Conditional Random Field*", 
("Multi* class Classifica‑tion", 
"Multiclass Classification"), 
"Mixture Of Expert*", 
"Concept* Drift", 
"Genetic Program‑ming", 
"String Kernel*", 
("Learning To Rank*", 
"Machine‑learned Ranking"), 
"Boosting Algorithm$", 
"Robot* Learning", 
"Relevance Vector* Machine*", 
"Connectionis*", 
("Multi* Kernel$ Learning", 
"Multikernel$ Learning"), 
"Graph Learning", 
"Naive bayes* Classifi*", 
"Rule‑based System$", 
"Classification Algorithm*", 
"Graph* Kernel*", 
"Rule* induction", 
"Manifold Learning", 
"Label Propagation", 
"Hypergraph* Learning", 
"One class Classifi*", 
"Intelligent Algorithm*"
]

en = spacy.lang.en.English()
ai_papers_index = dict()


def find_ai_papers(df, matcher):
    df["cleaned_abstract"] = df["abstract"].str.replace("\n", " ")

    text_to_search = df.apply(
        lambda row: str(row["title"]) + " " + str(row["cleaned_abstract"]), axis=1
    ).str.lower()

    docs = text_to_search.apply(en)

    foundings = docs.apply(matcher)
    ai_papers_ids = list(df[foundings.str.len() != 0].paper_id)
    return ai_papers_ids


def prepare_matcher():
    matcher = PhraseMatcher(en.vocab, attr="NORM")  # TODO: change to lemma
    for pattern in AI_PAPER_PATTERNS:
        matcher.add(pattern, None, en(pattern))
    return matcher


if __name__ == "__main__":
    matcher = prepare_matcher()

    s2orc_paths = glob.glob(S2_ORC_INPUT_PATHS)
    for path in tqdm(s2orc_paths):
        filename = os.path.basename(path)
        if filename in ai_papers_index.keys():
            print(f"Already filtered ({filename}), skipping...", flush=True)
        else:
            df = pd.read_json(path, lines=True)
            ai_papers_ids = find_ai_papers(df, matcher)

            ai_papers_index[filename] = ai_papers_ids
    ai_papers = pd.DataFrame()
    for path in tqdm(s2orc_paths):
        filename = os.path.basename(path)
        df2 = pd.read_json(path, lines=True)
        df_filtered = df2[df2["paper_id"].isin(ai_papers_index[filename])]
        ai_papers = ai_papers.append(df_filtered)
    ai_papers.to_csv(AI_PAPERS_OUT_PATH, index=False)
