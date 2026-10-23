"""Train the outbreak / not-outbreak classifier.

TF-IDF + logistic regression. Character n-grams do most of the work on the
Swahili side (vifo / wamefariki / kipindupindu all share chunks, and people
mix English and Swahili in the same headline).

    python train.py                                 # your hand labels
    python train.py --use-weak                      # fill gaps with rule guesses
    python train.py --labels data/sample_labeled.csv
"""
import argparse
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import FeatureUnion, Pipeline


def make_model():
    return Pipeline([
        ("tfidf", FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)),
        ])),
        ("lr", LogisticRegression(C=4, class_weight="balanced", max_iter=2000)),
    ])


def strongest(model, n=12):
    tf = model.named_steps["tfidf"].transformer_list
    names = np.r_[tf[0][1].get_feature_names_out(), tf[1][1].get_feature_names_out()]
    coef = model.named_steps["lr"].coef_[0]
    order = coef.argsort()
    top = lambda idx: ", ".join(repr(str(names[i]).strip()) for i in idx)
    return f"pushes towards outbreak: {top(order[::-1][:n])}\npushes towards not:      {top(order[:n])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="data/labeled.csv")
    ap.add_argument("--use-weak", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.labels):
        raise SystemExit(f"no {args.labels} - label some articles with label.py first")
    df = pd.read_csv(args.labels).fillna({"title": "", "summary": ""})
    if "text" not in df:
        df["text"] = (df["title"] + ". " + df["summary"]).str.strip()
    df["text"] = df["text"].fillna("")
    hand = df["label"].notna()

    y = df["label"]
    if args.use_weak and "weak_label" in df:
        y = y.fillna(df["weak_label"])
    df = df[y.notna()].assign(y=y[y.notna()].astype(int))
    hand = hand[df.index]

    print(f"{len(df)} examples ({hand.sum()} hand-labeled): "
          f"{(df.y == 1).sum()} outbreak, {(df.y == 0).sum()} not")
    if df.y.value_counts().min() < 5:
        raise SystemExit("need at least 5 of each class - label some more first")

    k = min(5, df.y.value_counts().min())
    pred = cross_val_predict(make_model(), df.text, df.y,
                             cv=StratifiedKFold(k, shuffle=True, random_state=0))

    # rule-made labels are noisy, so grade on hand labels when there are enough
    graded = hand if hand.sum() >= 20 and df.y[hand].nunique() == 2 else pd.Series(True, index=df.index)
    report = classification_report(df.y[graded], pred[graded.values], target_names=["not", "outbreak"], digits=3)
    cm = confusion_matrix(df.y[graded], pred[graded.values])

    model = make_model().fit(df.text, df.y)
    out = (f"{k}-fold CV on {graded.sum()} {'hand-labeled' if graded is hand else ''} examples\n\n"
           f"{report}\nconfusion (rows = actual not/outbreak):\n{cm}\n\n{strongest(model)}\n")
    print("\n" + out)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/classifier.joblib")
    with open("models/metrics.txt", "w", encoding="utf-8") as f:
        f.write(out)

    wrong = df[df.y.values != pred]
    if len(wrong):
        print("some it got wrong (actual -> predicted):")
        for _, r in wrong.head(10).iterrows():
            print(f"  {r.y} -> {1 - r.y}  {r.title[:95]}")


if __name__ == "__main__":
    main()
