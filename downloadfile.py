#!/usr/bin/env python3
import requests

# Direct download URL obtained from an external Issuu downloader tool.
url = "https://seomagnifier.com/download/XlXT3oeNf3w/url.pdf"
output_filename = "5-mower_parts.pdf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

print("Downloading PDF from Issuu...")
with requests.get(url, headers=headers, stream=True) as r:
    r.raise_for_status()  # Raise an error if the download fails
    with open(output_filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print(f"Download complete. File saved as: {output_filename}")
