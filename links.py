"""Swap Google News redirect links for the real article address.

Each lookup is a separate request to Google, so this only does the articles
the dashboard actually shows (newest first, a capped number per run) and saves
what it finds to data/real_links.csv as it goes. Next run, anything already
looked up is instant, and stopping halfway with Ctrl+C loses nothing.

Links that can't be looked up keep their Google address, which still opens the
story in a normal browser.
"""
import csv
import os

CACHE = "data/real_links.csv"
BATCH = 10


def is_google(url):
    return "news.google.com" in str(url or "")


def load_cache():
    if not os.path.exists(CACHE):
        return {}
    with open(CACHE, encoding="utf-8") as f:
        return {r["google_link"]: r["real_link"] for r in csv.DictReader(f) if r.get("real_link")}


def _append(pairs):
    new_file = not os.path.exists(CACHE)
    with open(CACHE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["google_link", "real_link"])
        w.writerows(pairs)


def look_up(urls, limit=150, pause=0.5):
    """Find real links for up to `limit` of `urls` that aren't cached yet.
    Returns the full {google_link: real_link} cache."""
    cache = load_cache()
    todo = [u for u in dict.fromkeys(urls) if is_google(u) and u not in cache][:limit]
    if not todo:
        return cache
    try:
        from googlenewsdecoder import gnewsdecoder
    except ImportError:
        print("skipping link lookup: run  pip install googlenewsdecoder  to turn it on")
        return cache

    print(f"looking up real links for {len(todo)} articles (about {len(todo) * 1.5 / 60:.0f} min, "
          f"Ctrl+C is safe)...")
    found, misses_in_a_row = 0, 0
    try:
        for start in range(0, len(todo), BATCH):
            batch = todo[start:start + BATCH]
            try:
                results = gnewsdecoder(batch, interval=pause, timeout=8)
            except Exception:
                results = [{}] * len(batch)
            pairs = [(u, r["decoded_url"]) for u, r in zip(batch, results)
                     if r.get("success") and r.get("decoded_url")]
            if pairs:
                _append(pairs)
                cache.update(pairs)
                found += len(pairs)
                misses_in_a_row = 0
            else:
                misses_in_a_row += 1
                if misses_in_a_row >= 3:  # Google is refusing for now - don't sit here for hours
                    print("  Google isn't answering link lookups right now, so stopping early. "
                          "The rest keep their Google links; try again later.")
                    break
            print(f"  {found} found so far ({min(start + BATCH, len(todo))}/{len(todo)} tried)")
    except KeyboardInterrupt:
        print(f"\n  stopped - kept the {found} links found so far, building the page with those")
    return cache
