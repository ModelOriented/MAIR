import glob
import os

from mair.pdf_parsing import parse
from tqdm import tqdm

INPUT_FOLDER = "data/arxiv_dump/papers/"
OUTPUT_FOLDER = "data/arxiv_dump/raw_extracted_texts/"

pdfs_path = os.path.join(INPUT_FOLDER, "*.pdf")

# Parsing articles

pdfs = dict()
for filepath in tqdm(list(glob.glob(pdfs_path))):
    filename = filepath.split("/")[-1]
    try:
        pdf = parse(filepath)
        pdfs[filename] = pdf
    except Exception as e:
        print(f"Error parsing ({filename}):", e)


if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

for name, doc in tqdm(pdfs.items()):
    file_path = os.path.join(OUTPUT_FOLDER, name).replace(".pdf", ".txt")
    text = doc.full_text
    with open(file_path, "w") as f:
        f.write(text)
