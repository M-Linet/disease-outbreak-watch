# Disease Outbreak Watch

Picks up early signs of disease outbreaks in East African news, in English and Kiswahili.

It pulls health stories from Google News, works out which ones actually report
an outbreak (as opposed to a vaccination drive or a research grant), pulls out
the disease, place and case numbers, and flags disease/country pairs that are
getting more coverage than usual. The results go into a single web page with a
map, epidemic curves and a searchable list of articles.

The idea comes from WHO's EIOS (Epidemic Intelligence from Open Sources), which
does this kind of media monitoring at a much bigger scale. I wanted to see how
far a small, transparent version could get, especially for Kiswahili coverage
that general tools tend to skip.

Anything it flags is a lead to check against official reports, not a confirmed outbreak.

## Running it

Needs Python 3.10+.

```bash
pip install -r requirements.txt

python collect.py          # fetch articles (~2 min). Run it daily, it appends.
python label.py --weak     # rule-based guess for each article
python label.py            # go through them yourself: 1 / 0 / enter / s / q
python train.py            # train the classifier on your labels
python pipeline.py         # classify + extract + find what's rising
python build_site.py       # export for the web page (also looks up real article links)
```

Then open `site/index.html` in a browser. No server needed.

The page in the repo already has fake demo data in it so you can see what it
looks like straight away. To regenerate that demo from scratch:

```bash
python make_sample_data.py
python train.py --labels data/sample_labeled.csv
python pipeline.py --input data/sample_articles.csv
python build_site.py
```

(The demo model scores 100% because the fake headlines come from a handful of
templates. Real news is much messier.)

## How it works

**Collecting** (`collect.py`). Google News RSS search, about 120 queries: 12
disease terms across 8 countries (including DR Congo) in English, plus Kiswahili terms like
*kipindupindu* (cholera), *surua* (measles) and *homa ya bonde la ufa* (Rift
Valley fever) for Kenya, Tanzania and Uganda. Duplicates are dropped by link and
by title, since wire stories get republished under different URLs.

Google News only gives out its own redirect links, so `build_site.py` swaps them
for the real article address. Each one takes a request to Google, so it does the
newest 150 flagged articles per run and remembers them in `data/real_links.csv`.

**Labelling** (`label.py`). Keyword rules make a first guess, then you confirm
or correct each one by hand. The unsure ones come up first because they're
the most useful to label. I count something as an outbreak report if it
describes new or ongoing cases, deaths or spread in a specific place, or an
official outbreak declaration.

**Classifier** (`train.py`). TF-IDF + logistic regression, using both word
n-grams and character n-grams. The character n-grams help a lot with Kiswahili,
where one root shows up in many forms (*vifo*, *wamefariki*, *wamekufa*) and
headlines often mix both languages. It reports cross-validated precision and
recall and lists the features that push hardest each way, which is a quick way
to spot labelling mistakes.

**Extraction** (`extract.py`). Regex and word lists rather than a model.
Off-the-shelf NER doesn't handle phrases like *watu 3 wamefariki* ("3 people
have died") or most Kenyan county names. It knows all 47 counties plus the
main towns in the region.

**Rising signals** (`pipeline.py`). For each disease and country, reports this
week are compared with the weekly average over the four weeks before. Two or
more reports and at least double the usual counts as rising.

**The page** (`site/index.html`). A map of the region with Lake Victoria and the
other big lakes, rising signals in red, epidemic curves per disease, a
disease-by-country heatmap, the English/Kiswahili split, largest case counts,
news sources, the classifier's confidence spread, and a sortable, searchable
table of every flagged article. Everything filters by disease, country,
language and time period. Built with D3. Country outlines are from Natural Earth and lake outlines from OpenStreetMap (see `THIRD_PARTY_NOTICES.md`).

## Checking it against real outbreaks

`evaluate.py` takes a list of outbreaks you know about (`data/known_outbreaks.csv`)
with the date each was first officially reported. Good sources are WHO Disease
Outbreak News, WHO AFRO weekly bulletins and Africa CDC's weekly reports. For each
one it checks whether the system flagged it and how many days before or after the
official report.

This needs collected data covering those dates. Google News search only goes
back so far, so collection has to run regularly for a few weeks first.

## Known problems

- Google News misses a lot: local radio, community health worker reports and
  anything on WhatsApp.
- More coverage doesn't mean more disease. Nairobi and big outbreaks get far
  more articles than rural areas.
- An article covering two diseases can get the wrong number attached to one of them.
- The rising-signal rule is a simple ratio, not a statistical test.
- There's much less Kiswahili training data than English.

## Things I'd like to add

- Compare against a fine-tuned multilingual transformer (XLM-R or AfroXLMR) on
  the same labels
- More sources: ministry of health releases, ReliefWeb, ProMED
- County-level shading on the map
- A proper anomaly test (EARS C2 or Poisson) instead of the ratio
- Run collection on a schedule and send a weekly digest

## Files

```
collect.py           fetch articles
label.py             weak labels + labelling tool
train.py             classifier
extract.py           disease / place / number extraction
pipeline.py          run everything, find rising signals
build_site.py        export results to site/data.js
links.py             swap Google News redirect links for real ones (cached)
evaluate.py          backtest against known outbreaks
make_sample_data.py  fake data for the demo
config.py            word lists and place coordinates
site/index.html      the dashboard page
site/vendor/         d3 and the map outlines
```

## Licence

MIT for my code (see `LICENSE`). Bundled third-party files keep their own licences, listed in `THIRD_PARTY_NOTICES.md`.
