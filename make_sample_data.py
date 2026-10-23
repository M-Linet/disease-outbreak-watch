"""Fake data for trying the pipeline before you have real articles.

Headlines are generated from templates (outlets are made up, links go to
example.org), with a cholera spike planted in western Kenya in the last week
so there's something to find. Don't quote any numbers you get from this.

    python make_sample_data.py
"""

import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(7)
END = date(2026, 10, 20)
DAYS = 70

OUTBREAK_EN = [
    "{d} outbreak confirmed in {p} as {n} cases reported",
    "{p} health officials report {n} new {d} cases, {k} deaths",
    "{d} spreads in {p}: {n} people hospitalised",
    "Death toll from {d} in {p} rises to {k}",
    "{c} declares {d} outbreak after {n} suspected cases in {p}",
    "Surge in {d} infections in {p} with {n} cases this week",
]
OUTBREAK_SW = [
    "Mlipuko wa {d} {p}: visa {n} vimethibitishwa",
    "Watu {k} wamefariki kutokana na {d} {p}",
    "Wagonjwa {n} wa {d} walazwa hospitalini {p}",
    "Wizara ya Afya yatoa tahadhari ya {d} {p}, visa vipya {n}",
]
NOT_EN = [
    "Government launches {d} vaccination campaign in {p}",
    "New study finds progress in {d} research in {c}",
    "World Health Day: experts discuss {d} awareness in {c}",
    "Donors pledge funding to fight {d} in {c}",
    "How to prevent {d}: tips for families in {p}",
    "Opinion: {c} must invest more in {d} preparedness",
    "{c} certified free of {d} transmission, officials say",
]
NOT_SW = [
    "Utafiti mpya kuhusu {d} wazinduliwa {c}",
    "Mkutano wa wataalamu kuhusu {d} wafanyika {p}",
    "Elimu kuhusu kujikinga na {d} yatolewa {p}",
]

SW_NAMES = {"cholera": "kipindupindu", "measles": "surua", "malaria": "malaria",
            "mpox": "mpox", "dengue": "homa ya dengue", "anthrax": "kimeta"}
PLACES = {
    "Kenya": ["Kisumu", "Migori", "Garissa", "Nairobi", "Mombasa", "Turkana", "Homa Bay"],
    "Uganda": ["Kampala", "Mbale", "Kasese"],
    "Tanzania": ["Dar es Salaam", "Mwanza", "Arusha"],
    "Ethiopia": ["Addis Ababa", "Gambella"],
    "Somalia": ["Mogadishu", "Baidoa"],
}


def make_row(day: date, outbreak: bool, lang: str, disease: str, country: str, place: str):
    n, k = random.randint(5, 300), random.randint(1, 20)
    d = SW_NAMES.get(disease, disease) if lang == "sw" else disease
    pool = {(True, "en"): OUTBREAK_EN, (True, "sw"): OUTBREAK_SW,
            (False, "en"): NOT_EN, (False, "sw"): NOT_SW}[(outbreak, lang)]
    title = random.choice(pool).format(d=d, p=place, c=country, n=n, k=k)
    title = title[0].upper() + title[1:]
    return {
        "title": title,
        "summary": "",
        "link": f"https://example.org/demo/{random.getrandbits(48):x}",
        "published": day.isoformat(),
        "source": random.choice(["Demo Wire", "Sample Daily", "Gazeti la Mfano", "Test Radio", "Placeholder Post"]),
        "language": lang,
        "query_keyword": disease,
        "query_country": country,
        "label": int(outbreak),
    }


def main():
    rows = []
    for i in range(DAYS):
        day = END - timedelta(days=DAYS - 1 - i)
        for _ in range(random.randint(2, 5)):  # background news
            country = random.choice(list(PLACES))
            disease = random.choice(list(SW_NAMES))
            lang = "sw" if country in {"Kenya", "Tanzania"} and random.random() < 0.35 else "en"
            rows.append(make_row(day, random.random() < 0.35, lang, disease, country,
                                 random.choice(PLACES[country])))
        if i >= DAYS - 7:  # the injected spike: cholera in western Kenya, last week
            for _ in range(random.randint(2, 4)):
                lang = random.choice(["en", "en", "sw"])
                rows.append(make_row(day, True, lang, "cholera", "Kenya",
                                     random.choice(["Kisumu", "Migori", "Homa Bay"])))

    df = pd.DataFrame(rows).drop_duplicates("title")
    os.makedirs("data", exist_ok=True)
    df.drop(columns=["label"]).to_csv("data/sample_articles.csv", index=False)
    labeled = df.copy()
    labeled["text"] = labeled["title"]
    labeled["weak_label"] = pd.NA
    labeled.to_csv("data/sample_labeled.csv", index=False)
    pd.DataFrame([
        # Fictional "official reports" for the demo backtest.
        {"disease": "cholera", "country": "Kenya", "official_report_date": "2026-10-19",
         "source_url": "https://example.org/demo-official-report"},
        {"disease": "dengue", "country": "Somalia", "official_report_date": "2026-09-10",
         "source_url": "https://example.org/demo-official-report-2"},
    ]).to_csv("data/sample_known_outbreaks.csv", index=False)
    print(f"Wrote {len(df)} fictional articles to data/sample_articles.csv "
          f"and data/sample_labeled.csv ({df['label'].mean():.0%} outbreak reports)")


if __name__ == "__main__":
    main()
