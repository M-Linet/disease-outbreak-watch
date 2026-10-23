"""Label articles: 1 = reports an actual outbreak, 0 = doesn't.

    python label.py --weak     # rule-based guess for every article
    python label.py            # go through them by hand (1 / 0 / enter / s / q)
    python label.py --stats

What I count as 1: new or ongoing cases/deaths, spread, or an official
outbreak declaration, in a specific place.
What's 0: vaccination drives, research, funding, awareness days, opinion
pieces, prevention tips, old stories, or the word used for something else.

Answers save as you go, so quitting halfway is fine.
"""
import argparse
import os

import pandas as pd

from config import NON_OUTBREAK_SIGNALS, OUTBREAK_SIGNALS
from extract import extract_all

RAW = "data/raw_articles.csv"
LABELS = "data/labeled.csv"


def guess(text):
    """Keyword rules. Returns 1, 0, or None when it can't tell."""
    t = text.lower()
    facts = extract_all(text)
    if not facts["diseases"]:
        return 0
    has_count = facts["cases"] is not None or facts["deaths"] is not None
    pos = sum(w in t for w in OUTBREAK_SIGNALS)
    neg = sum(w in t for w in NON_OUTBREAK_SIGNALS)
    if neg == 0 and (has_count or pos >= 2):
        return 1
    if neg and not has_count:
        return 0
    return None


def read_raw():
    if not os.path.exists(RAW):
        raise SystemExit(f"no {RAW} yet - run collect.py first")
    df = pd.read_csv(RAW).fillna("")
    df["text"] = (df["title"] + ". " + df["summary"]).str.strip()
    return df


def read_labels():
    if os.path.exists(LABELS):
        return pd.read_csv(LABELS).fillna({"summary": "", "source": ""})
    df = read_raw()
    df["weak_label"] = pd.NA
    df["label"] = pd.NA
    return df


def weak():
    df = read_labels()
    fresh = read_raw()
    fresh = fresh[~fresh["link"].isin(df["link"])]  # anything collected since last time
    df = pd.concat([df, fresh.assign(weak_label=pd.NA, label=pd.NA)], ignore_index=True)
    df["weak_label"] = df["text"].apply(guess).astype("Int64")
    df.to_csv(LABELS, index=False)
    c = df["weak_label"].value_counts(dropna=False)
    print(f"{len(df)} articles ({len(fresh)} new): {c.get(1, 0)} outbreak, "
          f"{c.get(0, 0)} not, {df['weak_label'].isna().sum()} unsure")


def stats():
    df = read_labels()
    done = df[df["label"].notna()]
    print(f"labeled {len(done)} of {len(df)}")
    if len(done):
        print(f"  outbreak: {(done['label'] == 1).sum()}   not: {(done['label'] == 0).sum()}")
        both = done[done["weak_label"].notna()]
        if len(both):
            agree = (both["label"].astype(int) == both["weak_label"].astype(int)).mean()
            print(f"  rules agree with you {agree:.0%} of the time")


def by_hand():
    df = read_labels()
    if df["weak_label"].isna().all():
        print("(run with --weak first if you want suggestions)\n")

    # unsure ones first - those are the ones the model learns most from
    todo = df[df["label"].isna()]
    todo = todo.loc[todo["weak_label"].map({1: 1, 0: 2}).fillna(0).sort_values().index]

    print("1 = outbreak, 0 = not, enter = take the suggestion, s = skip, q = quit\n")
    for i, row in todo.iterrows():
        g = row["weak_label"]
        hint = "unsure" if pd.isna(g) else ("outbreak" if g == 1 else "not")
        print(f"\n{row['published']}  {row['source']}  [{row['language']}]")
        print(f"  {row['title']}")
        if row["summary"] and row["summary"] != row["title"]:
            print(f"  {row['summary'][:300]}")
        ans = input(f"  ({hint}) > ").strip().lower()
        while ans not in {"1", "0", "s", "q", ""}:
            ans = input("  1/0/s/q > ").strip().lower()
        if ans == "q":
            break
        if ans == "" and not pd.isna(g):
            ans = str(int(g))
        if ans in ("1", "0"):
            df.at[i, "label"] = int(ans)
            df.to_csv(LABELS, index=False)
    print()
    stats()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--weak", action="store_true")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    weak() if a.weak else stats() if a.stats else by_hand()
