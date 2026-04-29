# Divar Scraper

A simple Selenium-based scraper for collecting ad URLs and titles from [Divar](https://divar.ir) search result pages. Handles infinite scrolling and the "آگهی‌های بیشتر" button automatically, and saves results to a CSV file.

## Features

- Scrape any Divar search URL (city, category, filters. ANYTHING)
- Configurable limits: max ads, max scrolls, any number of pages
- Deduplicates ads by URL
- Outputs a clean CSV with `URL` and `Title` columns
- Returns a pandas DataFrame for further processing
- Usable as a CLI tool or as a Python class

## Requirements

- Python 3.8+
- Google Chrome installed
- ChromeDriver (auto-managed by recent Selenium versions)

## Installation

```bash
git clone https://github.com/bardiaegz/divar-scraper.git
cd divar-scraper
pip install -r requirements.txt
```

## Usage

### As a CLI

Run with the default URL (Tehran):

```bash
python divar_scraper.py
```

Pass your own URL and options:

```bash
python divar_scraper.py "https://divar.ir/s/tehran" --max-ads 200 --max-pages 5 --output tehran_ads.csv
```

### CLI Options

| Argument | Default | Description |
|---|---|---|
| `url` | Tehran search URL | Divar search results URL to scrape |
| `--max-ads` | `100` | Stop after collecting this many unique ads |
| `--max-scrolls` | `60` | Max consecutive scrolls in the page. |
| `--max-pages` | `3` | Max number of "load more" pages to traverse |
| `--output` | `divar_ads.csv` | Output CSV file path |

### As a Python class

```python
from divar_scraper import DivarScraper

scraper = DivarScraper(
    url="https://divar.ir/s/tehran",
    max_ads=100,
    max_pages=5,
    output_file="tehran_ads.csv",
)

df = scraper.scrape()
print(df.head())
```

## Output

A CSV file like:

| URL | Title |
|---|---|
| https://divar.ir/v/... | آپارتمان ۹۰ متری در مرکز شهر |
| https://divar.ir/v/... | فروش خودرو پراید مدل ۹۵ |
| ... | ... |

## How It Works

1. Opens the given Divar URL in a Chrome window via Selenium.
2. Scrolls to the bottom of the page repeatedly, collecting ad cards as they load.
3. When the page stops growing, looks for a "آگهی‌های بیشتر" button and clicks it.
4. Repeats until one of the stop conditions is met:
   - `max_ads` collected
   - `max_pages` reached
   - `max_scrolls` scrolls without finding new content
   - No more "آگهی‌های بیشتر" button on the page
5. Saves results to CSV and closes the browser.

## Notes

- This is a learning/personal-use scraper. Be respectful of Divar's servers — don't run it in tight loops or at scale.
- Divar's CSS class names (like `kt-post-card__action` and the "load more" button selector) change every now and then. If the scraper suddenly stops finding ads, open the search page in Chrome, right-click an ad card → **Inspect**, and grab the new class name. Then update the selector constants at the top of the `DivarScraper` class:

```python
  CARD_CLASS = "kt-post-card__action"
  LOAD_MORE_SELECTOR = "#post-list-container-id > div.post-list__bottom-container-cac2f > div > button"
```

- If you figure out the new selectors before I do, **PRs are very welcome!** Open a pull request with the updated values and I'll merge it. Same goes for any other improvement, bug fixes, ANYTHING.