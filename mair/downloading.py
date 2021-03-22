"""Module with downloading utilities"""

import requests


def save_pdf_under_path(pdf_url, path):
    if ".pdf" not in pdf_url:
        print(f"{pdf_url} is not a pdf, skipping...")
    else:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(pdf_url, headers=headers, allow_redirects=True)
            with open(path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"\nError downloading ({pdf_url}):{e}, skipping")
