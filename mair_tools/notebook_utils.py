"""Functions to be used in notebooks"""

import glob
import os.path
from typing import List

from mair_tools import pdf_processing


def parse_all_files_from_path(path: str) -> List[pdf_processing.Pdf]:
    pdfs = []

    for filename in glob.glob(os.path.join(path, "*.pdf")):
        try:
            pdf = pdf_processing.parse(filename)
            pdfs.append(pdf)
        except Exception as e:
            print(f"Error parsing ({filename}):", e)
    return pdfs
