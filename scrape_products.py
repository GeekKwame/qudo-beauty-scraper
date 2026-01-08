import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import argparse
import sys
import re
from urllib.parse import urljoin

class QudoScraper:
    def __init__(self, base_url, max_pages=1, output_file="scraped_products.csv"):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_file = output_file
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    def get_soup(self, url):
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            print(f"Failed to load {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def get_product_details(self, product_url):
        soup = self.get_soup(product_url)
        if not soup:
            return None
        
        try:
            # Product Name
            name_tag = soup.select_one('h1.product_title')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            
            # Brand
            brand_tag = soup.select_one('.product_meta .posted_in a[href*="/brand/"]')
            brand = brand_tag.get_text(strip=True) if brand_tag else "N/A"
            
            # Category (Breadcrumbs)
            # Default to checking breadcrumbs for the specific category
            breadcrumb_nav = soup.select_one('nav.woocommerce-breadcrumb')
            category = "N/A"
            if breadcrumb_nav:
                categories = [a.get_text(strip=True) for a in breadcrumb_nav.find_all('a')]
                # Usually Home > Main Cat > Sub Cat > Product
                # We try to grab the most specific category before the product
                if len(categories) > 0:
                     category = categories[-1]
                     if category == "Home" and len(categories) > 1:
                         category = categories[-1]

            # Description & Ingredients extraction
            description_tab = soup.select_one('#tab-description')
            description_text = description_tab.get_text(separator="\n", strip=True) if description_tab else ""
            
            ingredients = "N/A"
            # Generic approach: Look for "Ingredients" or "Product contains:"
            if "Product contains:" in description_text:
                parts = description_text.split("Product contains:")
                if len(parts) > 1:
                    relevant_part = parts[-1].strip()
                    stop_markers = ["How to use", "Capacity", "Delivery", "Returns", "Volume", "Size"]
                    for marker in stop_markers:
                        if marker in relevant_part:
                            relevant_part = relevant_part.split(marker)[0]
                    ingredients = relevant_part.strip()
            # Fallback
            if (ingredients == "N/A" or len(ingredients) < 5) and "Ingredients" in description_text:
                 parts = description_text.split("Ingredients")
                 if len(parts) > 1:
                     # Try to grab a reasonable chunk
                     curr = parts[-1].strip()
                     # often followed by a simplified header or unwanted text
                     if ":" in curr and len(curr.split(":")[0]) < 20: 
                         # e.g. "Ingredients: Water, ..." -> split removes "Ingredients"
                         pass
                     ingredients = curr.split("\n\n")[0].strip()

            if len(ingredients) > 500:
                ingredients = ingredients[:500] + "..."

            # Size/Packaging
            size = "N/A"
            if "Capacity:" in description_text:
                cap_match = re.search(r'Capacity:\s*(.*?)(?:\n|$)', description_text)
                if cap_match:
                    size = cap_match.group(1).strip()
            
            if size == "N/A":
                 # Regex for Common sizes (ml, g, oz)
                 size_match = re.search(r'(\d+\s?(ml|oz|g|kg|L))', name, re.IGNORECASE)
                 if size_match:
                     size = size_match.group(1)
            
            # Image
            image_tag = soup.select_one('.woocommerce-product-gallery__image img')
            image_url = image_tag['src'] if image_tag else "N/A"
            
            return {
                "Product Name": name,
                "Brand": brand,
                "Category/Type": category,
                "Ingredients": ingredients,
                "Size/Packaging": size,
                "Product Image URL": image_url,
                "Product Page URL": product_url
            }

        except Exception as e:
            print(f"Error parsing {product_url}: {e}")
            return None

    def scrape(self):
        all_products = []
        
        # Ensure base_url ends with slash if not having query params
        if "?" not in self.base_url and not self.base_url.endswith("/"):
             self.base_url += "/"

        print(f"Starting scrape for {self.base_url}")
        
        for i in range(1, self.max_pages + 1):
            if i == 1:
                page_url = self.base_url
            else:
                # Handle pagination typically /page/N/
                if self.base_url.endswith("/"):
                    page_url = f"{self.base_url}page/{i}/"
                else:
                    page_url = f"{self.base_url}/page/{i}/"
            
            print(f"Scanning page {i}: {page_url}...")
            soup = self.get_soup(page_url)
            if not soup:
                continue

            links = soup.select('.woocommerce-loop-product__link')
            page_product_urls = []
            for link in links:
                href = link.get('href')
                if href:
                    page_product_urls.append(href)
            
            # Remove duplicates
            page_product_urls = list(set(page_product_urls))
            print(f"  Found {len(page_product_urls)} products on page {i}.")
            
            for p_url in page_product_urls:
                print(f"    Scraping {p_url}...")
                details = self.get_product_details(p_url)
                if details:
                    all_products.append(details)
                time.sleep(random.uniform(0.5, 1.5))

        # Save
        if all_products:
            df = pd.DataFrame(all_products)
            df.to_csv(self.output_file, index=False)
            print(f"Successfully scraped {len(all_products)} products. Saved to {self.output_file}")
        else:
            print("No products found.")

def main():
    parser = argparse.ArgumentParser(description="Generic Scraper for Qudo Beauty")
    parser.add_argument("--url", required=True, help="Category URL to scrape (e.g., https://qudobeauty.com/cat/wholesale-hair-products/)")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--output", default="scraped_products.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    scraper = QudoScraper(args.url, args.pages, args.output)
    scraper.scrape()

if __name__ == "__main__":
    main()
