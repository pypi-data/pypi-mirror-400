# Adoc Link Checker (adocx)

Adoc Link Checker is a command-line tool to detect broken HTTP and HTTPS links
in AsciiDoc (`.adoc`) files.

It is designed to be:
- reliable (HEAD request with GET fallback),
- fast (parallel processing with caching),
- explicit (JSON report, no implicit output),
- CI-friendly.

---

## Why Adoc Link Checker?

- AsciiDoc / Antora projects often contain hundreds of external links
- Broken links silently degrade documentation quality
- CI pipelines rarely validate link integrity
- This tool provides a deterministic, cache-aware, CI-friendly solution

---

## Features

- Checks HTTP and HTTPS links
- Supports YouTube IDs (`video::ID[]`)
- Parallel processing (configurable)
- URL and domain exclusion
- Structured JSON report
- Works on a single file or a directory
- Built-in request caching
- Suitable for CI pipelines

---

## Installation

### Requirements
- Python 3.8+
- pip

### Install from PyPI

```bash
pip install adoc-link-checker
```

This installs the CLI command:

```bash
adocx
```

---

## Quick usage

### Check a single AsciiDoc file

```bash
adocx check-links README.adoc --output report.json
```

### Check a directory

```bash
adocx check-links ./docs --output report.json
```

⚠️ **WARNING**  
The `--output` option is mandatory.  
No report is generated without it.

---

## Main options

```
FILE_OR_DIR
    .adoc file or directory to scan (required)

--output
    JSON output file (required)

--timeout
    HTTP timeout in seconds (default: 15)

--max-workers
    Number of parallel threads (default: 5)

--delay
    Delay between requests in seconds (default: 0.5)

--blacklist
    Domain to ignore (repeatable)

--exclude-from
    File containing URLs to exclude

--fail-on-broken
    Exit with non-zero status code if broken links are found

-v / -vv
    Verbosity (INFO / DEBUG)

--quiet
    Errors only
```

---

## Excluding URLs

You can exclude specific URLs using a text file.

Example `exclude_urls.txt`:

```
# Comments are allowed
https://example.com/temp
https://dev.example.com
```

Usage:

```bash
adocx check-links ./docs --exclude-from exclude_urls.txt --output report.json
```

Rules:
- one URL per line
- empty lines are ignored
- lines starting with `#` are ignored
- URLs are normalized automatically

---

## JSON report format

Only files containing broken links appear in the report.

Example:

```json
{
  "docs/page.adoc": [
    ["https://example.com/broken", "URL not accessible"]
  ]
}
```

---

## HTTP behavior

- HEAD request first
- Automatic fallback to GET
- Redirects followed
- Realistic User-Agent
- Automatic retries on server errors
- Shared cache to avoid duplicate requests

---

## CI usage

Typical usage in CI pipelines:

```bash
adocx check-links ./docs --output broken_links.json --fail-on-broken
```

Exit codes:
- `0`: no broken links
- `1`: broken links detected

Designed for CI:
- deterministic JSON output
- no implicit stdout noise
- configurable failure behavior

---

## Development

Clone the repository:

```bash
git clone https://github.com/dhrions/adoc-link-checker.git
cd adoc-link-checker
```

Install in editable mode:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest --cov=.
```

---

## License

This project is licensed under the MIT License.  
See the LICENSE file for details.
