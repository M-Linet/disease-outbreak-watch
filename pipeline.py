"""Classify every article, pull out the facts, and flag what's rising.

"Rising" = a disease/country pair with 2+ reports in the last 7 days and at
least double its weekly average over the 4 weeks before that. Crude, but it's a
triage list for a person to check, not a diagnosis.

    python pipeline.py
    python pipeline.py --input data/sample_articles.csv --threshold 0.6
"""
import argparse
import os

import joblib
import pandas as pd

from extract import extract_all
from label import guess


def score(texts):
    if os.path.exists("models/classifier.joblib"):
        model = joblib.load("models/classifier.joblib")
        return model.predict_proba(texts)[:, 1]
    print("no model yet (run train.py) - using the keyword rules instead")
    return texts.map(lambda t: {1: 0.9, 0: 0.1}.get(guess(t), 0.5)).values


def run(df, threshold):
    df = df.fillna({"title": "", "summary": "", "source": ""}).copy()
    text = (df["title"] + ". " + df["summary"]).str.strip()
    df["prob_outbreak"] = score(text).round(3)
    df["is_outbreak"] = df["prob_outbreak"] >= threshold

    facts = pd.DataFrame(list(text.map(extract_all)), index=df.index)
    for col in ("diseases", "countries", "places"):
        df[col] = facts[col].map(";".join)
    df["cases"] = facts["cases"].astype("Int64")
    df["deaths"] = facts["deaths"].astype("Int64")

    # no country in the text -> assume the one we searched for
    if "query_country" in df:
        empty = df["countries"] == ""
        df.loc[empty, "countries"] = df.loc[empty, "query_country"].fillna("")

    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    return df


def rising(df, today):
    hits = df[df.is_outbreak & (df.diseases != "") & df.published.notna()].copy()
    if hits.empty:
        return pd.DataFrame()
    # one row per disease x country mentioned
    hits = hits.assign(disease=hits.diseases.str.split(";"), country=hits.countries.str.split(";"))
    hits = hits.explode("disease").explode("country")
    hits = hits[hits.country != ""]

    week_ago = today - pd.Timedelta(days=7)
    month_before = week_ago - pd.Timedelta(days=28)

    out = []
    for (disease, country), g in hits.groupby(["disease", "country"]):
        this_week = g[(g.published > week_ago) & (g.published <= today)]
        before = g[(g.published > month_before) & (g.published <= week_ago)]
        usual = len(before) / 4
        if not len(this_week) and not len(before):
            continue
        # nothing in the previous month at all counts as "new" (ratio left empty)
        ratio = round(len(this_week) / usual, 1) if usual else None
        last = g.sort_values("published").iloc[-1]
        out.append({
            "disease": disease,
            "country": country,
            "articles_last_7d": len(this_week),
            "weekly_baseline_prev_4w": usual,
            "spike_ratio": ratio,
            "spike": len(this_week) >= 2 and (ratio is None or ratio >= 2),
            "max_cases_reported": g.cases.max(),
            "max_deaths_reported": g.deaths.max(),
            "places": ", ".join(sorted({p for ps in g.places for p in ps.split(";") if p})),
            "latest_date": last.published.date(),
            "latest_headline": last.title,
            "latest_link": last.link,
        })
    return pd.DataFrame(out).sort_values(["spike", "articles_last_7d"], ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/raw_articles.csv")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--as-of", help="YYYY-MM-DD, defaults to the newest article")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        raise SystemExit(f"no {args.input} - run collect.py first (or use --input data/sample_articles.csv)")
    signals = run(pd.read_csv(args.input), args.threshold)
    today = pd.Timestamp(args.as_of) if args.as_of else signals.published.max()
    alerts = rising(signals, today)

    signals.to_csv("data/signals.csv", index=False)
    alerts.to_csv("data/alerts.csv", index=False)

    print(f"{len(signals)} articles, {signals.is_outbreak.sum()} look like outbreak reports "
          f"(week ending {today:%d %b %Y})")
    up = alerts[alerts.spike] if len(alerts) else alerts
    for _, a in up.iterrows():
        usual = f"usually {a.weekly_baseline_prev_4w:g}/wk" if pd.notna(a.spike_ratio) else "new"
        print(f"  rising: {a.disease} in {a.country}, {a.articles_last_7d} reports this week ({usual})")
    if up.empty:
        print("  nothing rising this week")


if __name__ == "__main__":
    main()
