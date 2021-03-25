"""Utilities for documents identifiers"""


def legal_doc_path_to_id(legal_doc_path):
    """Convert path to global document identifier"""
    suffix = legal_doc_path.split("/")[-1][:-4]
    if "oecd_docs" in legal_doc_path:
        prefix = "oecd|"
    elif "nesta_ai_governance_docs" in legal_doc_path:
        prefix = "nesta|"
    return prefix + suffix
