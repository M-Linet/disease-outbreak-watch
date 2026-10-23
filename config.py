# Word lists the rest of the project uses. Add to these when you see
# something get missed in the labeled data.

DISEASES = {
    # canonical name: everything I've seen it called (lowercase, EN + SW)
    "cholera": ["cholera", "kipindupindu", "acute watery diarrhoea", "acute watery diarrhea"],
    "measles": ["measles", "surua", "rubeola"],
    "malaria": ["malaria", "maleria"],
    "mpox": ["mpox", "monkeypox", "homa ya nyani"],
    "ebola": ["ebola", "ebola virus disease", "sudan virus", "bundibugyo"],
    "marburg": ["marburg"],
    "dengue": ["dengue", "homa ya dengue", "dengi"],
    "anthrax": ["anthrax", "kimeta"],
    "rift valley fever": ["rift valley fever", "homa ya bonde la ufa"],
    "polio": ["polio", "poliomyelitis", "vaccine-derived poliovirus", "kupooza"],
    "yellow fever": ["yellow fever", "homa ya manjano"],
    "meningitis": ["meningitis", "homa ya uti wa mgongo"],
    "chikungunya": ["chikungunya"],
    "typhoid": ["typhoid", "homa ya matumbo"],
    "covid-19": ["covid-19", "covid", "coronavirus", "korona"],
}

COUNTRIES = {
    "Kenya": ["kenya"],
    "Uganda": ["uganda"],
    "Tanzania": ["tanzania", "zanzibar"],
    "Rwanda": ["rwanda"],
    "Burundi": ["burundi"],
    "Ethiopia": ["ethiopia", "ethiopian"],
    "Somalia": ["somalia", "somali"],
    "South Sudan": ["south sudan"],
    "DR Congo": ["dr congo", "drc", "democratic republic of congo", "democratic republic of the congo", "kongo"],
    "Sudan": ["sudan"],
}

# place: (country, lat, lon). Kenyan counties use the county town.
# Coordinates are approximate - good enough for a regional map, not for routing.
PLACES = {
    "Mombasa": ("Kenya", -4.04, 39.67), "Kwale": ("Kenya", -4.17, 39.45),
    "Kilifi": ("Kenya", -3.63, 39.85), "Tana River": ("Kenya", -1.50, 40.03),
    "Lamu": ("Kenya", -2.27, 40.90), "Taita Taveta": ("Kenya", -3.40, 38.56),
    "Garissa": ("Kenya", -0.45, 39.65), "Wajir": ("Kenya", 1.75, 40.06),
    "Mandera": ("Kenya", 3.94, 41.86), "Marsabit": ("Kenya", 2.33, 37.99),
    "Isiolo": ("Kenya", 0.35, 37.58), "Meru": ("Kenya", 0.05, 37.65),
    "Tharaka Nithi": ("Kenya", -0.33, 37.65), "Embu": ("Kenya", -0.53, 37.45),
    "Kitui": ("Kenya", -1.37, 38.01), "Machakos": ("Kenya", -1.52, 37.26),
    "Makueni": ("Kenya", -1.78, 37.63), "Nyandarua": ("Kenya", -0.27, 36.38),
    "Nyeri": ("Kenya", -0.42, 36.95), "Kirinyaga": ("Kenya", -0.50, 37.28),
    "Murang'a": ("Kenya", -0.72, 37.15), "Kiambu": ("Kenya", -1.17, 36.83),
    "Turkana": ("Kenya", 3.12, 35.60), "West Pokot": ("Kenya", 1.24, 35.11),
    "Samburu": ("Kenya", 1.10, 36.70), "Trans Nzoia": ("Kenya", 1.02, 35.00),
    "Uasin Gishu": ("Kenya", 0.51, 35.27), "Elgeyo Marakwet": ("Kenya", 0.67, 35.51),
    "Nandi": ("Kenya", 0.20, 35.10), "Baringo": ("Kenya", 0.49, 35.74),
    "Laikipia": ("Kenya", 0.01, 37.07), "Nakuru": ("Kenya", -0.30, 36.07),
    "Narok": ("Kenya", -1.08, 35.87), "Kajiado": ("Kenya", -1.85, 36.78),
    "Kericho": ("Kenya", -0.37, 35.28), "Bomet": ("Kenya", -0.78, 35.34),
    "Kakamega": ("Kenya", 0.28, 34.75), "Vihiga": ("Kenya", 0.08, 34.72),
    "Bungoma": ("Kenya", 0.56, 34.56), "Busia": ("Kenya", 0.46, 34.11),
    "Siaya": ("Kenya", 0.06, 34.29), "Kisumu": ("Kenya", -0.09, 34.77),
    "Homa Bay": ("Kenya", -0.53, 34.46), "Migori": ("Kenya", -1.06, 34.47),
    "Kisii": ("Kenya", -0.68, 34.77), "Nyamira": ("Kenya", -0.57, 34.94),
    "Nairobi": ("Kenya", -1.29, 36.82), "Eldoret": ("Kenya", 0.51, 35.27),
    "Dadaab": ("Kenya", 0.06, 40.31), "Kakuma": ("Kenya", 3.72, 34.86),
    "Kampala": ("Uganda", 0.35, 32.58), "Mbale": ("Uganda", 1.08, 34.18),
    "Gulu": ("Uganda", 2.77, 32.30), "Kasese": ("Uganda", 0.18, 30.08),
    "Mubende": ("Uganda", 0.56, 31.39), "Arua": ("Uganda", 3.02, 30.91),
    "Jinja": ("Uganda", 0.44, 33.20), "Wakiso": ("Uganda", 0.40, 32.48),
    "Dar es Salaam": ("Tanzania", -6.79, 39.21), "Dodoma": ("Tanzania", -6.16, 35.75),
    "Arusha": ("Tanzania", -3.37, 36.68), "Mwanza": ("Tanzania", -2.52, 32.90),
    "Kagera": ("Tanzania", -1.33, 31.81), "Mbeya": ("Tanzania", -8.91, 33.46),
    "Tanga": ("Tanzania", -5.07, 39.10),
    "Kigali": ("Rwanda", -1.95, 30.06), "Bujumbura": ("Burundi", -3.38, 29.36),
    "Addis Ababa": ("Ethiopia", 9.03, 38.74), "Gambella": ("Ethiopia", 8.25, 34.59),
    "Mogadishu": ("Somalia", 2.05, 45.32), "Baidoa": ("Somalia", 3.11, 43.65),
    "Juba": ("South Sudan", 4.85, 31.58), "Goma": ("DR Congo", -1.68, 29.22),
    "Khartoum": ("Sudan", 15.50, 32.56),
}
SUBNATIONAL = {name: v[0] for name, v in PLACES.items()}

# rough middle of each country, used on the map when a story names no town
COUNTRY_CENTROIDS = {
    "Kenya": (0.2, 37.9), "Uganda": (1.4, 32.4), "Tanzania": (-6.3, 34.9),
    "Rwanda": (-2.0, 29.9), "Burundi": (-3.4, 29.9), "Ethiopia": (8.6, 39.6),
    "Somalia": (4.8, 45.3), "South Sudan": (7.3, 30.3), "DR Congo": (-1.5, 27.5),
    "Sudan": (14.0, 30.5),
}

# words that show up in actual outbreak reporting
OUTBREAK_SIGNALS = [
    "outbreak", "cases", "confirmed", "suspected", "deaths", "died", "dead",
    "killed", "fatalities", "spike", "surge", "rise in", "spread", "spreading",
    "infected", "infections", "hospitalised", "hospitalized", "admitted",
    "quarantine", "isolation", "declared", "alert", "epidemic", "death toll",
    "mlipuko", "visa", "wagonjwa", "vifo", "wamefariki", "wamekufa",
    "kuenea", "imethibitishwa", "maambukizi", "tahadhari",
]

# words that usually mean the story is about something else
# (vaccine drives, research, awareness days...)
NON_OUTBREAK_SIGNALS = [
    "vaccine trial", "research", "study finds", "funding", "grant", "donates",
    "awareness", "world malaria day", "world health day", "anniversary",
    "conference", "summit", "opinion", "op-ed", "how to prevent", "tips",
    "eradicated", "free of", "certified", "launches campaign", "budget",
    "utafiti", "mkutano", "elimu kuhusu", "siku ya malaria duniani",
]

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100,
    "moja": 1, "mbili": 2, "tatu": 3, "nne": 4, "tano": 5, "sita": 6, "saba": 7,
    "nane": 8, "tisa": 9, "kumi": 10, "ishirini": 20, "thelathini": 30, "hamsini": 50,
}
