"""Pull disease, place and case/death numbers out of a headline + summary.

Plain regex and word lists, no model. Off-the-shelf NER doesn't know Swahili
phrases like "watu 3 wamefariki" or most county names, and rules are easier to
debug when something gets pulled out wrong.

    python extract.py "Cholera outbreak in Kisumu: 120 cases and 4 deaths confirmed"
"""
import re
import sys

from config import COUNTRIES, DISEASES, NUMBER_WORDS, SUBNATIONAL


def _patterns(mapping):
    # longest alias first, otherwise "sudan" matches inside "south sudan"
    pairs = sorted(((a, name) for name, aliases in mapping.items() for a in aliases),
                   key=lambda p: -len(p[0]))
    return [(re.compile(r"\b" + re.escape(a) + r"\b", re.I), name) for a, name in pairs]


DISEASE_RX = _patterns(DISEASES)
COUNTRY_RX = _patterns(COUNTRIES)
PLACE_RX = _patterns({p: [p] for p in SUBNATIONAL})


def _find(text, patterns):
    found = []
    for rx, name in patterns:
        if rx.search(text):
            if name not in found:
                found.append(name)
            text = rx.sub(" ", text)  # blank it out so a shorter alias can't match it again
    return found


def diseases(text):
    return _find(text, DISEASE_RX)


def locations(text):
    places = _find(text, PLACE_RX)
    countries = _find(text, COUNTRY_RX)
    for p in places:  # "Kisumu" implies Kenya even if Kenya isn't mentioned
        if SUBNATIONAL[p] not in countries:
            countries.append(SUBNATIONAL[p])
    return countries, places


# numbers: digits ("1,200") or a few spelled-out ones in either language
NUM = r"\b(\d{1,3}(?:,\d{3})+|\d+|" + "|".join(NUMBER_WORDS) + r")\b"

CASES = [
    # "120 cases", "120 new suspected cholera cases"
    rf"{NUM}\s+(?:new\s+|more\s+|confirmed\s+|suspected\s+|additional\s+)*(?:[a-z-]+\s+){{0,3}}?(?:cases|infections|patients)",
    rf"{NUM}\s+(?:people|persons|residents|children)\s+(?:have\s+been\s+|were\s+)?(?:infected|hospitali[sz]ed|admitted)",
    rf"cases\s+(?:rose|risen|climbed|increased|jumped)\s+to\s+{NUM}",
    rf"visa\s+(?:vipya\s+|zaidi\s+ya\s+)?{NUM}",          # visa vipya 45
    rf"wagonjwa\s+(?:wapya\s+)?{NUM}",                     # wagonjwa 30
    rf"watu\s+{NUM}\s+(?:wameambukizwa|wamelazwa)",
]
DEATHS = [
    rf"{NUM}\s+(?:people\s+|persons\s+|more\s+|new\s+)?(?:deaths|dead|fatalities|lives)",
    rf"{NUM}\s+(?:people|persons|residents|children)\s+(?:have\s+)?(?:died|dead|killed|succumbed)",
    rf"(?:killed|claimed\s+the\s+lives\s+of)\s+{NUM}",
    # "death toll from cholera in Kisumu rises to 12"
    rf"death\s+toll\b[^.;]{{0,60}}?\b(?:rises|rose|climbs|climbed|hits|hit|reaches|reached|stands|jumps)\s+(?:to\s+|at\s+)?{NUM}",
    rf"vifo\s+(?:vya\s+watu\s+)?{NUM}",                    # vifo 3
    rf"watu\s+{NUM}\s+(?:wamefariki|wamekufa|wamepoteza\s+maisha)",
]
CASES = [re.compile(p, re.I) for p in CASES]
DEATHS = [re.compile(p, re.I) for p in DEATHS]


def _to_int(s):
    s = s.lower()
    if s in NUMBER_WORDS:
        return NUMBER_WORDS[s]
    s = s.replace(",", "")
    return int(s) if s.isdigit() else None


def _biggest(text, regexes):
    nums = []
    for rx in regexes:
        for m in rx.finditer(text):
            n = _to_int(m.group(1))
            if n is not None and not 1900 <= n <= 2100 and n < 10_000_000:  # skip years
                nums.append(n)
    return max(nums) if nums else None


def extract_all(text):
    countries, places = locations(text)
    return {
        "diseases": diseases(text),
        "countries": countries,
        "places": places,
        "cases": _biggest(text, CASES),
        "deaths": _biggest(text, DEATHS),
    }


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "Cholera outbreak in Kisumu and Migori: 120 new cases and 4 deaths confirmed"
    print(text)
    for k, v in extract_all(text).items():
        print(f"  {k:<9} {v}")
