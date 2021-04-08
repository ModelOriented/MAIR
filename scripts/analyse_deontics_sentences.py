import mair.deontics
import mair.doc_ids
import pandas as pd
from mair.data_loading import load_legal_documents_metadata, load_parsed_legal_documents

# INPUTS:   "data/nesta_ai_governance_docs/meta.csv"
#           "data/oecd_docs/meta.csv"
#           "data/processed/intermediate/parsed_legal_texts.joblib"

OUT = "data/processed/deontics.csv"
if __name__ == "__main__":
    df_meta = load_legal_documents_metadata()
    parsed_documents = load_parsed_legal_documents()

    result_df = mair.deontics.get_deontic_sentences_table(parsed_documents)

    final_df = pd.DataFrame()
    final_df["id"] = result_df["raw_text_path"].apply(mair.doc_ids.legal_doc_path_to_id)
    final_df["verb"] = result_df["verb"].apply(lambda t: t.lemma_.lower())
    final_df["subject"] = result_df.apply(
        lambda row: mair.deontics.final_subjects(row["subject"], row["subjectCoref"]),
        axis=1,
    )
    final_df["sent"] = result_df["sent"].apply(
        lambda sent: sent.text.replace("\n", " ")
    )
    final_df["modal"] = result_df["modal"]
    final_df["isQuestion"] = result_df["isQuestion"]
    final_df["negated"] = result_df["negated"]

    final_df = final_df.merge(df_meta, on="id")
    final_df = final_df.explode("subject")  # convert lists to multiple rows}

    final_df.to_csv(OUT, index=False)
