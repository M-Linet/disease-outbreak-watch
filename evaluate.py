"""Would this have caught real outbreaks, and how early?

Put outbreaks you know about in data/known_outbreaks.csv with the date of the
FIRST official report (WHO Disease Outbreak News, WHO AFRO bulletins, Africa
CDC weekly reports, MoH press releases):

    disease,country,official_report_date,source_url
    cholera,Kenya,2026-01-15,https://...

For each one this looks for the earliest flagged article on the same disease
and country, from 30 days before the official date to 14 days after.

    python evaluate.py
    python evaluate.py --known data/sample_known_outbreaks.csv
"""
import argparse

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--known", default="data/known_outbreaks.csv")
    args = ap.parse_args()

    known = pd.read_csv(args.known, parse_dates=["official_report_date"])
    if known.empty:
        raise SystemExit(f"{args.known} is empty - add some outbreaks first")
    sig = pd.read_csv("data/signals.csv", parse_dates=["published"]).fillna({"diseases": "", "countries": ""})
    sig = sig[sig.is_outbreak]

    rows = []
    for _, k in known.iterrows():
        d, c, when = k.disease.lower(), k.country, k.official_report_date
        m = sig[sig.diseases.str.split(";").map(lambda x: d in x)
                & sig.countries.str.split(";").map(lambda x: c in x)
                & sig.published.between(when - pd.Timedelta(days=30), when + pd.Timedelta(days=14))]
        first = m.published.min()
        rows.append({
            "disease": d, "country": c, "official": when.date(),
            "caught": not m.empty,
            "first_flagged": first.date() if not m.empty else None,
            "days_early": (when - first).days if not m.empty else None,
            "articles": len(m),
        })

    res = pd.DataFrame(rows)
    res.to_csv("data/evaluation.csv", index=False)
    print(res.to_string(index=False))

    caught = res[res.caught]
    print(f"\ncaught {len(caught)} of {len(res)}")
    if len(caught):
        print(f"{(caught.days_early > 0).sum()} before the official report, "
              f"median {caught.days_early.median():.0f} days early (negative = late)")


if __name__ == "__main__":
    main()
