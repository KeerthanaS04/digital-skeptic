from typing import Optional, Dict
from .types import FetchResult
from .utils import clean_text

def _try_trafilatura(url: str):
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        art = trafilatura.extract(downloaded, include_comments=False, include_tables=False, favor_recall=True, output="json")
        if not art:
            return None
        import json
        data = json.loads(art)
        text = data.get("text")
        if not text:
            return None
        return {
        "title": data.get("title"),
        "text": text,
        "byline": data.get("author"),
        "published": data.get("date"),
        "meta": {k: v for k, v in data.items() if isinstance(v, str)}
        }
    except Exception:
        return None




def _try_newspaper(url: str):
    try:
        from newspaper import Article
        art = Article(url)
        art.download()
        art.parse()
        return {
            "title": art.title or None,
            "text": art.text or "",
            "byline": ", ".join(art.authors) if art.authors else None,
            "published": art.publish_date.isoformat() if art.publish_date else None,
            "meta": {}
        }
    except Exception:
        return None




def _try_bs4(url: str):
    try:
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # crude extraction: concatenate paragraph text
        ps = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None
        text = "\n".join(ps)
        return {
            "title": title,
            "text": text,
            "byline": None,
            "published": None,
            "meta": {}
        }
    except Exception:
        return None




def fetch_article(url: str) -> FetchResult:
    for fn in (_try_trafilatura, _try_newspaper, _try_bs4):
        data = fn(url)
        if data and data.get("text"):
            return FetchResult(
                url=url,
                title=data.get("title") or "Untitled",
                text=clean_text(data.get("text", "")),
                byline=data.get("byline"),
                published=data.get("published"),
                meta=data.get("meta", {}),
            )
    # If everything fails
    return FetchResult(url=url, title="Untitled", text="", byline=None, published=None, meta={})