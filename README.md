# WizardWebb (Python)

WizardWebb is a small Flask web app that renders a YAML file of tools/links into a searchable, filterable directory.

## Run locally (Windows / macOS / Linux)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Then open: http://localhost:8000

## Edit the directory

Open `data/links.yml` and add/edit entries. Refresh the browser.

## Optional: point to a different YAML file

```bash
set LINKS_FILE=C:\path\to\my_links.yml
python app.py
```

(macOS/Linux: `export LINKS_FILE=/path/to/my_links.yml`)

## Deploy notes

This app listens on `PORT` when set (common on Railway/Render/Fly/etc).

## License

MIT — see `LICENSE`.
