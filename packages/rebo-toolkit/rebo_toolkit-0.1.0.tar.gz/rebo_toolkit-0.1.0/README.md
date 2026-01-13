# rebo (repo bootstrap + repo utilities)

A small, practical CLI that helps you:
- **init**: bootstrap a new repo from templates (py-lib / node-lib / c-lib / minimal)
- **doctor**: check repo hygiene (and optionally auto-fix missing basics)
- **md2pdf**: convert Markdown to a clean PDF (subset of Markdown, no external tools)
- **jsondiff**: structural diff for JSON files (text / json / html output)
- **index**: generate a command index (Makefile / package.json scripts / common scripts)

## Install (dev / editable)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate
pip install -e ".[dev]"
```

## Quickstart

```bash
rebo --help
rebo init my-lib --profile py-lib --author "Your Name" --email "you@example.com" --github-user "your-id" --with-ci
rebo doctor my-lib
rebo doctor my-lib --fix
rebo md2pdf README.md out.pdf
rebo jsondiff old.json new.json --format html --out diff.html
rebo index .
```

## Why this exists

A lot of GitHub repos look "empty" to strangers because they don't have a quick button to press.
This tool tries to create that button.

## License

MIT
