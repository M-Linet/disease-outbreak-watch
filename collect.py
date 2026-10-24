"""Grab health news for East Africa from Google News RSS (English + Swahili).

No API key needed. Each run adds to data/raw_articles.csv instead of replacing
it, so run it daily and the history builds up. Real article links are looked
up later, by build_site.py, and only for the articles the dashboard shows.

    python collect.py
"""
import csv
import html
import os
import re
import time
from datetime import datetime
from urllib.parse import quote_plus

import feedparser

# DR Congo is in because the 2026 Ebola outbreak started there and spread east
COUNTRIES = ["Kenya", "Uganda", "Tanzania", "Rwanda", "Ethiopia", "Somalia", "South Sudan", "DR Congo"]

KEYWORDS_EN = [
    "cholera", "measles", "malaria outbreak", "mpox", "ebola", "marburg",
    "dengue", "anthrax", "rift valley fever", "polio", "outbreak", "epidemic",
]
# kipindupindu = cholera, surua = measles, mlipuko wa ugonjwa = disease outbreak,
# homa ya bonde la ufa = rift valley fever
KEYWORDS_SW = [
    "kipindupindu", "surua", "mlipuko wa ugonjwa", "homa ya dengue",
    "ebola", "mpox", "malaria", "homa ya bonde la ufa",
]
SW_COUNTRIES = ["Kenya", "Tanzania", "Uganda"]  # where Swahili press actually exists

FEED_PARAMS = {
    "en": "hl=en-KE&gl=KE&ceid=KE:en",
    "sw": "hl=sw&gl=TZ&ceid=TZ:sw",
}

OUT = "data/raw_articles.csv"
FIELDS = ["title", "summary", "link", "published", "source", "language", "query_keyword",
          "query_country", "google_link"]


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")  # summaries come back as HTML
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def search(query, lang):
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&{FEED_PARAMS[lang]}"
    feed = feedparser.parse(url)
    # feedparser swallows connection errors and just returns nothing
    if feed.get("bozo") and not feed.entries:
        raise RuntimeError(feed.get("bozo_exception", "couldn't read feed"))
    return feed.entries


def to_row(entry, lang, keyword, country):
    published = ""
    if entry.get("published_parsed"):
        published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
    source = entry.get("source")
    outlet = source.get("title", "") if isinstance(source, dict) else ""
    title = clean(entry.get("title"))
    if outlet and title.endswith(" - " + outlet):  # Google appends " - Outlet" to every title
        title = title[: -len(outlet) - 3]
    return {
        "title": title,
        "summary": clean(entry.get("summary")),
        "link": entry.get("link", ""),
        "google_link": entry.get("link", ""),
        "published": published,
        "source": outlet,
        "language": lang,
        "query_keyword": keyword,
        "query_country": country,
    }


def save(rows):
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs("data", exist_ok=True)
    old = []
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = list(csv.DictReader(f))
    # compare on Google's link, since that's what the feed gives us next time
    links = {r.get("google_link") or r["link"] for r in old}
    titles = {r["title"].lower() for r in old}
    print(f"{len(old)} articles already saved")

    queries = [(k, c, "en") for k in KEYWORDS_EN for c in COUNTRIES]
    queries += [(k, c, "sw") for k in KEYWORDS_SW for c in SW_COUNTRIES]

    new = []
    for i, (kw, country, lang) in enumerate(queries, 1):
        q = f"{kw} {country}"
        try:
            entries = search(q, lang)
        except Exception as e:
            print(f"{i:>3}/{len(queries)}  failed: {q} ({e})")
            continue
        added = 0
        for e in entries:
            row = to_row(e, lang, kw, country)
            # the same wire story turns up under several links, so check titles too
            if not row["link"] or row["link"] in links or row["title"].lower() in titles:
                continue
            links.add(row["link"])
            titles.add(row["title"].lower())
            new.append(row)
            added += 1
        print(f"{i:>3}/{len(queries)}  {q:<38} {len(entries):>3} found, {added} new")
        time.sleep(1)  # don't hammer Google

    save(old + new)

    sw = sum(r["language"] == "sw" for r in new)
    print(f"\n+{len(new)} new ({sw} Swahili), {len(old) + len(new)} total in {OUT}")


if __name__ == "__main__":
    main()
