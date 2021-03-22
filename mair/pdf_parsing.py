"""Functions for parsing raw pdf to text"""

import glob
import os
from dataclasses import dataclass
from typing import List

import pdfminer.converter
import pdfminer.layout
import pdfminer.pdfinterp
import pdfminer.pdfpage


@dataclass
class PdfMeta:
    author: str
    creator: str
    title: str
    filename: str


@dataclass
class Pdf:
    # metadata: PdfMeta
    pages: List[List[str]]
    empty_pages: list
    full_text: str


def parse_all_files_from_path(path: str) -> List[Pdf]:
    pdfs = []

    for filename in glob.glob(os.path.join(path, "*.pdf")):
        try:
            pdf = parse(filename)
            pdfs.append(pdf)
        except Exception as e:
            print(f"Error parsing ({filename}):", e)
    return pdfs


def parse(path: str) -> Pdf:
    """Extracts text and metadata from *.pdf file"""
    file_name = os.path.splitext(os.path.basename(path))[0]
    empty_pages = []
    separated_text = []
    all_text = ""
    page_no = 0
    document = open(path, "rb")
    # pdf_info = PyPDF2.PdfFileReader(document).getDocumentInfo()
    # pdf_metadata = PdfMeta(pdf_info.author, pdf_info.creator, pdf_info.title, file_name)
    rsrcmgr = pdfminer.pdfinterp.PDFResourceManager()
    laparams = pdfminer.layout.LAParams()
    device = pdfminer.converter.PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = pdfminer.pdfinterp.PDFPageInterpreter(rsrcmgr, device)
    for page in pdfminer.pdfpage.PDFPage.get_pages(document):
        text_on_page = []
        interpreter.process_page(page)
        layout = device.get_result()
        for element in layout:
            if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                text_on_page.append(element.get_text())
                all_text += element.get_text()
        if len(text_on_page) == 0:
            empty_pages.append(page_no)
        separated_text.append(text_on_page)
        page_no += 1
    document.close()

    return Pdf(separated_text, empty_pages, all_text)
