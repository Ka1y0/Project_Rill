# Rill · Chips Studio

Public product information for Rill. This repository contains static website materials only.

Website: https://ka1y0.github.io/Project_Rill/

## Publication

`Content/` is the text source. `site.json` selects the published pages and languages. `docs/` is generated.

Build and check with Python 3.9 or later:

```sh
python3 tools/build_site.py
python3 tools/build_site.py --check
```

GitHub Pages publishes `main` → `/docs`. No runtime JavaScript, package installation or external build service is needed. The website edition identifies this informational publication, not an App release or a privacy-policy effective date.
