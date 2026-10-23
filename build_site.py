"""Write site/data.js from the pipeline output so site/index.html can show it.

    python build_site.py
    then open site/index.html in a browser (double-click works, no server needed)
"""
import json
from datetime import date

import pandas as pd

from config import COUNTRY_CENTROIDS, DISEASES, PLACES


def split(s):
    return [x for x in str(s).split(";") if x and x != "nan"]


def num(x):
    return None if pd.isna(x) else int(x)


def main():
    sig = pd.read_csv("data/signals.csv", parse_dates=["published"])
    sig = sig[sig.published.notna()].fillna({"title": "", "source": "", "link": "", "places": "",
                                             "diseases": "", "countries": ""})
    try:
        alerts = pd.read_csv("data/alerts.csv")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        alerts = pd.DataFrame()

    articles = [{
        "date": r.published.strftime("%Y-%m-%d"),
        "title": r.title,
        "link": r.link,
        "source": r.source,
        "lang": r.language,
        "prob": float(r.prob_outbreak),
        "flagged": bool(r.is_outbreak),
        "diseases": split(r.diseases),
        "countries": split(r.countries),
        "places": split(r.places),
        "cases": num(r.cases),
        "deaths": num(r.deaths),
    } for r in sig.itertuples()]

    rising = []
    if len(alerts):
        for r in alerts[alerts.spike].itertuples():
            rising.append({
                "disease": r.disease, "country": r.country,
                "week": int(r.articles_last_7d), "usual": float(r.weekly_baseline_prev_4w),
                "cases": num(r.max_cases_reported), "deaths": num(r.max_deaths_reported),
                "places": [p.strip() for p in str(r.places).split(",") if p.strip() and p != "nan"],
                "headline": r.latest_headline, "link": r.latest_link,
            })

    data = {
        "asOf": sig.published.max().strftime("%Y-%m-%d"),
        "built": date.today().isoformat(),
        "demo": bool(sig.link.str.contains("example.org/demo").any()),
        "diseaseOrder": list(DISEASES),
        "places": {k: [v[1], v[2]] for k, v in PLACES.items()},
        "centroids": {k: list(v) for k, v in COUNTRY_CENTROIDS.items()},
        "rising": rising,
        "articles": articles,
    }
    with open("site/data.js", "w", encoding="utf-8") as f:
        f.write("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print(f"site/data.js: {len(articles)} articles, {len(rising)} rising signals")


if __name__ == "__main__":
    main()
