# Veefyed Qudo Beauty Scraper


## Overview

This toolkit provides a flexible, modular solution for scraping product data from WooCommerce-based e-commerce sites (specifically tailored for [Qudo Beauty](https://qudobeauty.com)) and enriching that data using Google's Custom Search API.

It was designed to be:
- **Generic**: Works across different product categories (Skincare, Hair Care, etc.).
- **Robust**: Handles missing data, pagination, and network errors gracefully.
- **Enrichment-Ready**: Uses external APIs to find official manufacturer URLs and descriptions.

## Components

1.  **`scrape_products.py`**: A CLI tool to scrape product details (Name, Brand, Ingredients, Size, etc.).
2.  **`enrich_data.py`**: A CLI tool to enrich any CSV dataset with official source URLs.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/GeekKwame/veefyed-data-scraper.git
    cd veefyed-data-scraper
    ```

2.  Install dependencies:
    ```bash
    pip install requests beautifulsoup4 pandas
    ```

3.  Set up environment variables:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    GOOGLE_CX=your_search_engine_id_here
    ```

## Usage

### 1. Scraping Products

You can scrape any category by providing its URL.

```bash
# Scrape "Face Care" (Default)
python scrape_products.py --url "https://qudobeauty.com/cat/wholesale-face-care/"

# Scrape "Hair Care" (3 pages)
python scrape_products.py --url "https://qudobeauty.com/cat/wholesale-hair-products/" --pages 3 --output "hair_care.csv"
```

### 2. Enriching Data

Enrich your scraped data with official manufacturer links.

```bash
# Enrich the hair care data
python enrich_data.py --input "hair_care.csv" --output "hair_care_enriched.csv" --limit 20
```

## Data Output

The tools produce CSV files with the following structure:
- **Raw**: `Product Name`, `Brand`, `Category/Type`, `Ingredients`, `Size/Packaging`, `Image URL`, `Page URL`.
- **Enriched**: Adds `Manufacturer URL`, `Snippet`, `Enrichment Source`.

## License
[MIT](LICENSE)
