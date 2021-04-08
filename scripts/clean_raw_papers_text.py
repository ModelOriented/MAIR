import os
from glob import glob

from mair import papers_processing_utils
from spacy.lang.en import English
from tqdm import tqdm

tqdm.pandas()
INPUT_FOLDER = "data/arxiv_dump/raw_extracted_texts/"
OUTPUT_FOLDER = "data/arxiv_dump/cleaned_texts/"
BEGINNING_WORDS = ["abstract", "summary"]  # , 'introduction']

MIN_PAPER_LEN = 100
tokeniser = English()


def cut_beggining(text: str) -> str:
    doc = tokeniser(text)
    beggining = papers_processing_utils.find_first(doc, BEGINNING_WORDS)
    stripped_text = doc[beggining:].text
    return stripped_text


def save(filename, text):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(file_path, "w") as f:
        f.write(text)


input_files_pattern = os.path.join(INPUT_FOLDER, "*.txt")
text_input_file_paths = glob(input_files_pattern)

texts = dict()
for path in text_input_file_paths:
    with open(path, "r") as text_file:
        text = text_file.read()
    if len(text) > MIN_PAPER_LEN:
        filename = os.path.basename(path)
        cleaned_text = papers_processing_utils.clean_text(text)
        texts[filename] = cut_beggining(cleaned_text)
    else:
        print(path, f"is to short ({len(text)}), passing...")

os.path.makedirs(OUTPUT_FOLDER, exist_ok=True)
for filename, text in texts.items():
    save(filename, text)

print(f"Saved {len(texts)} out of {len(text_input_file_paths)}")
