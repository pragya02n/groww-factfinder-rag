"""
Source Loader Module
====================
Crawls the 8 official HDFC/AMFI URLs from sources.md and extracts text content.
Each page's text is returned alongside its source URL for citation tracking.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

# ── Headers to mimic a real browser request ──────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def parse_sources_md(filepath: str = "../sources.md") -> list[dict]:
    """
    Read the sources.md markdown table and extract scheme metadata + URLs.

    Returns a list of dicts:
        [{ "id": 1, "scheme": "...", "doc_type": "...", "url": "..." }, ...]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown table rows (skip header + separator rows)
    row_pattern = re.compile(
        r"\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[.*?\]\((https?://.*?)\)\s*\|"
    )

    sources = []
    for match in row_pattern.finditer(content):
        sources.append({
            "id": int(match.group(1)),
            "scheme": match.group(2).strip(),
            "doc_type": match.group(3).strip(),
            "url": match.group(4).strip(),
        })

    return sources


def scrape_url(url: str, timeout: int = 30) -> str:
    """
    Fetch a URL and extract clean text content from the page body.
    Strips navigation, scripts, styles, and other non-content elements.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        console.print(f"  [red]✗ Failed to fetch: {e}[/red]")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "form", "button", "iframe", "noscript", "svg"]):
        tag.decompose()

    # Extract text and clean whitespace
    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def load_all_sources(sources_path: str = "../sources.md") -> list[dict]:
    """
    Master function: parse sources.md, scrape each URL, return documents
    with metadata.

    Returns a list of dicts:
        [{
            "id": 1,
            "scheme": "HDFC Top 100",
            "doc_type": "SID (Exit Load/Fees)",
            "url": "https://...",
            "content": "... extracted text ...",
        }, ...]
    """
    sources = parse_sources_md(sources_path)

    if not sources:
        console.print("[red]✗ No sources found in sources.md![/red]")
        return []

    console.print(f"\n[bold cyan]📂 Found {len(sources)} sources to crawl[/bold cyan]\n")

    documents = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[bold green]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Crawling sources...", total=len(sources))

        for source in sources:
            progress.update(task, description=f"[cyan]Crawling: {source['scheme']}[/cyan]")

            content = scrape_url(source["url"])

            if content:
                documents.append({
                    "id": source["id"],
                    "scheme": source["scheme"],
                    "doc_type": source["doc_type"],
                    "url": source["url"],
                    "content": content,
                })
                console.print(
                    f"  [green]✓[/green] {source['scheme']} — "
                    f"[dim]{len(content):,} chars[/dim]"
                )
            else:
                console.print(f"  [yellow]⚠ {source['scheme']} — No content extracted[/yellow]")

            progress.advance(task)
            time.sleep(1)  # Polite crawl delay

    console.print(
        f"\n[bold green]✓ Successfully loaded {len(documents)}/{len(sources)} documents[/bold green]"
    )
    return documents


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    docs = load_all_sources()
    for doc in docs:
        console.print(f"\n[bold]{doc['scheme']}[/bold] ({doc['doc_type']})")
        console.print(f"  URL: [link]{doc['url']}[/link]")
        console.print(f"  Content length: {len(doc['content']):,} characters")
        console.print(f"  Preview: {doc['content'][:200]}...")
