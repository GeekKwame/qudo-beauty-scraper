# Veefyed Data Scraping and Enrichment Project

## Overview
This project provides a **generic and flexible** toolset for scraping product data from `qudobeauty.com` (or similar WooCommerce sites) and enriching it with external data via the **Google Custom Search API**. 

The tools are designed to be category-agnostic, allowing you to scrape any product category (e.g., Skincare, Hair Care) and enrich any CSV dataset.

## Files Included
1.  **`scrape_products.py`**: A generic CLI-based scraper.
2.  **`enrich_data.py`**: A generic CLI-based enrichment tool.
3.  **`skincare_1_raw.csv` / `skincare_2_enriched.csv`**: Sample data from the initial run.
4.  **`documentation.md`**: User guide (this file).

---

## Part 1: Generic Web Scraper

### Usage
Run the scraper from the command line by specifying the target category URL.

```bash
# Basic usage (defaults to 1 page, output: scraped_products.csv)
python scrape_products.py --url "https://qudobeauty.com/cat/wholesale-face-care/"

# Advanced usage
python scrape_products.py --url "https://qudobeauty.com/cat/wholesale-hair-products/" --pages 3 --output "hair_care.csv"
```

### Features
- **Dynamic Pagination**: Scrapes multiple pages as specified by `--pages`.
- **Category Agnostic**: Works on any product listing page.
- **Robust Extraction**: Helper methods to extract details like Ingredients and Size using multiple heuristics.

---

## Part 2: Data Enrichment

### Usage
Enrich any CSV file containing a "Product Name" (and optional "Brand") column.

```bash
# Basic usage
python enrich_data.py --input "hair_care.csv" --output "hair_care_enriched.csv"

# Advanced usage (limit rows, custom column name)
python enrich_data.py --input "my_data.csv" --limit 50 --column "Name"
```

### Features
- **Flexible Input**: Works with any CSV file.
- **Smart Querying**: Uses `{Brand} {Product Name} official site` for high-accuracy results.
- **Mock Mode**: Automatically falls back to mock data if API keys are missing.

---

## Setup & Requirements
- Python 3.x
- `requests`, `beautifulsoup4`, `pandas`
- Create a `.env` file with `GOOGLE_API_KEY` and `GOOGLE_CX` for real API usage.
