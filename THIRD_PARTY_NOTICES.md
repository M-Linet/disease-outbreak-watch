# Third-party files

The project's own code is MIT licensed (see `LICENSE`). These bundled files are
not mine and keep their own licences.

## D3 — `site/vendor/d3.min.js`

Version 7, copyright 2010-2023 Mike Bostock. ISC licence.
https://github.com/d3/d3/blob/main/LICENSE

## Country outlines — in `site/vendor/geo.js`

Cut down from world-atlas 2 (`countries-50m.json`), copyright 2013-2019 Michael
Bostock, ISC licence: https://github.com/topojson/world-atlas
The underlying data is Natural Earth, which is in the public domain:
https://www.naturalearthdata.com/about/terms-of-use/

## Lake outlines — in `site/vendor/geo.js`

Cut down from geo-maps `earth-lakes-1km`, copyright 2017 Simone Primarosa, MIT
licence: https://github.com/simonepri/geo-maps

The data is © OpenStreetMap contributors and available under the Open Database
License (ODbL) 1.0: https://www.openstreetmap.org/copyright
The ODbL requires this attribution wherever the map is shown, which is why the
dashboard footer credits OpenStreetMap. If you redistribute the lake outlines
as a dataset in their own right, the ODbL's share-alike terms apply to that
dataset.

## News articles

Headlines and links collected by `collect.py` belong to their publishers. They
are kept out of the repository (`data/*.csv` is in `.gitignore`) and should
not be republished in bulk.
