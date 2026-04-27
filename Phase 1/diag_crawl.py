import os
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def parse_sources(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    row_pattern = re.compile(r"\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[.*?\]\((https?://.*?)\)\s*\|")
    return [{"id": int(m.group(1)), "scheme": m.group(2).strip(), "url": m.group(4).strip()} for m in row_pattern.finditer(content)]

def crawl():
    sources = parse_sources("sources.md")
    os.makedirs("crawled_data", exist_ok=True)
    for s in sources:
        print(f"Crawling {s['scheme']}...")
        try:
            r = requests.get(s["url"], headers=HEADERS, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                with open(f"crawled_data/src_{s['id']}.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"  Saved {len(text)} bytes.")
            else:
                print(f"  Error: {r.status_code}")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    crawl()
