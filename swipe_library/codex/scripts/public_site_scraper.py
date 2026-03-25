#!/usr/bin/env python3
"""Scrape public pages from approved domains into a local swipe-file archive."""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree


USER_AGENT = "Mozilla/5.0 (compatible; CodexSwipeScraper/1.0; +https://openai.com)"
REQUEST_TIMEOUT = 20


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip += 1
        elif tag in {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1
        elif tag in {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "page"


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def extract_text(html: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(html)
    parser.close()
    return normalize_text("".join(parser.parts))


def same_domain(url: str, allowed_domains: set[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains)


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="", query="")
    return cleaned.geturl().rstrip("/") or parsed.geturl()


def discover_sitemap_urls(session: requests.Session, root_url: str) -> list[str]:
    candidates = []
    parsed = urlparse(root_url)
    candidates.append(f"{parsed.scheme}://{parsed.netloc}/sitemap.xml")
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        response = session.get(robots_url, timeout=REQUEST_TIMEOUT)
        if response.ok:
            for line in response.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    candidates.append(line.split(":", 1)[1].strip())
    except requests.RequestException:
        pass
    return list(dict.fromkeys(candidates))


def parse_sitemap(session: requests.Session, sitemap_url: str, allowed_domains: set[str]) -> list[str]:
    try:
        response = session.get(sitemap_url, timeout=REQUEST_TIMEOUT)
        if not response.ok:
            return []
        root = ElementTree.fromstring(response.content)
    except Exception:
        return []

    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}")[0] + "}"

    urls: list[str] = []
    if root.tag.endswith("sitemapindex"):
        for node in root.findall(f"{namespace}sitemap/{namespace}loc"):
            child = (node.text or "").strip()
            if child:
                urls.extend(parse_sitemap(session, child, allowed_domains))
        return urls

    for node in root.findall(f"{namespace}url/{namespace}loc"):
        loc = (node.text or "").strip()
        if loc and same_domain(loc, allowed_domains):
            urls.append(clean_url(loc))
    return urls


def allow_by_robots(root_url: str, user_agent: str, url: str) -> bool:
    parsed = urlparse(root_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def collect_links(base_url: str, html: str, allowed_domains: set[str]) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all("a", href=True):
        href = urljoin(base_url, node["href"])
        href = clean_url(href)
        if same_domain(href, allowed_domains):
            yield href


def fetch_pages(
    roots: list[str],
    allowed_domains: set[str],
    include_patterns: list[str],
    exclude_patterns: list[str],
    max_pages: int,
    delay_seconds: float,
    respect_robots: bool,
) -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    url_queue: deque[str] = deque()
    seen: set[str] = set()
    pages: list[dict] = []

    for root in roots:
        url_queue.append(clean_url(root))
        for sitemap_url in discover_sitemap_urls(session, root):
            for discovered in parse_sitemap(session, sitemap_url, allowed_domains):
                url_queue.append(discovered)

    include_regexes = [re.compile(pattern) for pattern in include_patterns]
    exclude_regexes = [re.compile(pattern) for pattern in exclude_patterns]

    while url_queue and len(pages) < max_pages:
        url = clean_url(url_queue.popleft())
        if url in seen:
            continue
        seen.add(url)

        if include_regexes and not any(regex.search(url) for regex in include_regexes):
            continue
        if any(regex.search(url) for regex in exclude_regexes):
            continue
        if respect_robots and not allow_by_robots(roots[0], USER_AGENT, url):
            continue

        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException:
            continue
        if not response.ok:
            continue
        if "text/html" not in response.headers.get("content-type", ""):
            continue

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        title = normalize_text(soup.title.get_text(" ", strip=True)) if soup.title else ""
        text = extract_text(html)
        meta_description = ""
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            meta_description = normalize_text(desc["content"])

        pages.append(
            {
                "url": url,
                "title": title,
                "meta_description": meta_description,
                "word_count": len(text.split()),
                "text": text,
                "html": html,
            }
        )

        for link in collect_links(url, html, allowed_domains):
            if link not in seen:
                url_queue.append(link)

        time.sleep(delay_seconds)

    return pages


def write_archive(output_dir: Path, pages: list[dict], config: dict) -> None:
    raw_dir = output_dir / "raw_html"
    text_dir = output_dir / "text"
    raw_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": config["name"],
        "roots": config["roots"],
        "allowed_domains": config["allowed_domains"],
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "page_count": len(pages),
        "pages": [],
    }

    for index, page in enumerate(pages, start=1):
        slug = f"{index:03d}-{slugify(urlparse(page['url']).path or 'home')}"
        raw_path = raw_dir / f"{slug}.html"
        text_path = text_dir / f"{slug}.txt"
        raw_path.write_text(page["html"], encoding="utf-8")
        text_path.write_text(page["text"], encoding="utf-8")
        manifest["pages"].append(
            {
                "url": page["url"],
                "title": page["title"],
                "meta_description": page["meta_description"],
                "word_count": page["word_count"],
                "raw_html": str(raw_path.relative_to(output_dir)),
                "text_file": str(text_path.relative_to(output_dir)),
            }
        )

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary_lines = [
        f"# {config['name']} Public Web Archive",
        "",
        f"- Scraped pages: {len(pages)}",
        f"- Roots: {', '.join(config['roots'])}",
        f"- Allowed domains: {', '.join(config['allowed_domains'])}",
        "",
    ]
    for page in manifest["pages"]:
        summary_lines.append(f"## {page['title'] or page['url']}")
        summary_lines.append(page["url"])
        if page["meta_description"]:
            summary_lines.append(page["meta_description"])
        summary_lines.append(f"Word count: {page['word_count']}")
        summary_lines.append("")
    (output_dir / "README.md").write_text("\n".join(summary_lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape public pages for one copywriter archive.")
    parser.add_argument("config", help="Path to a JSON config file.")
    parser.add_argument("output_dir", help="Path to output directory.")
    args = parser.parse_args()

    config_path = Path(args.config)
    output_dir = Path(args.output_dir)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pages = fetch_pages(
        roots=config["roots"],
        allowed_domains=set(config["allowed_domains"]),
        include_patterns=config.get("include_patterns", ["."]),
        exclude_patterns=config.get("exclude_patterns", []),
        max_pages=int(config.get("max_pages", 50)),
        delay_seconds=float(config.get("delay_seconds", 0.5)),
        respect_robots=bool(config.get("respect_robots", False)),
    )
    write_archive(output_dir, pages, config)
    print(f"Scraped {len(pages)} pages into {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
