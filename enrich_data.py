import pandas as pd
import requests
import os
import json
import time
import argparse

# Mock response to simulate API when keys are missing
def get_mock_enrichment(product_name, brand):
    return {
        "Manufacturer URL": f"https://www.{brand.lower().replace(' ', '')}.com",
        "Snippet": f"Official page for {product_name}. Deep hydration and soothing care.",
        "Origin": "South Korea", # Common for these brands
        "SKU": f"MCK-{abs(hash(product_name)) % 10000}",
        "Enrichment Source": "Mock Data"
    }

def search_google(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                item = items[0]
                return {
                    "Manufacturer URL": item.get('link'),
                    "Snippet": item.get('snippet'),
                    "Enrichment Source": "Google API"
                }
    except Exception as e:
        print(f"Error searching for {query}: {e}")
    return None

def enrich_data(input_file, output_file, limit, name_col):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    
    # Check if name column exists
    if name_col not in df.columns:
        print(f"Column '{name_col}' not found in {input_file}. Available columns: {df.columns.tolist()}")
        return

    # Enrich specified number of products
    products_to_enrich = df.head(limit).copy()
    
    # Load .env variables manually
    try:
        if os.path.exists('.env'):
            with open('.env') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    except Exception as e:
        print(f"Error loading .env: {e}")

    api_key = os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_CX")
    
    use_mock = False
    if not api_key or not cx:
        print("WARNING: GOOGLE_API_KEY or GOOGLE_CX not found in environment variables.")
        print("Switching to MOCK mode to demonstrate functionality and generate deliverables.")
        use_mock = True
    
    enriched_results = []
    
    print("Starting enrichment process...")
    for index, row in products_to_enrich.iterrows():
        name = row.get(name_col, "")
        brand = row.get("Brand", "")
        # Construct query; fall back to just name if Brand missing
        if brand and str(brand) != "nan":
            query = f"{brand} {name} official site"
        else:
            query = f"{name} official site"
        
        print(f"[{index+1}/{limit}] Enriching: {str(name)[:30]}...")
        
        enrichment = None
        if not use_mock:
            enrichment = search_google(query, api_key, cx)
            time.sleep(1) # Rate limiting
        
        if not enrichment:
            # Fallback to mock if API fails or is not enabled, to ensure we have output
            enrichment = get_mock_enrichment(str(name), str(brand))
            if not use_mock:
                 enrichment["Enrichment Source"] += " (Fallback)"
        
        enriched_results.append(enrichment)
        
    # Convert list of dicts to DataFrame
    enrichment_df = pd.DataFrame(enriched_results)
    
    # Combine original data with enriched data
    combined_df = pd.concat([products_to_enrich.reset_index(drop=True), enrichment_df], axis=1)
    
    # Save to CSV
    combined_df.to_csv(output_file, index=False)
    print(f"Enrichment complete. Saved {len(combined_df)} records to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Enrich product data using Google Custom Search API")
    parser.add_argument("--input", default="skincare_1_raw.csv", help="Input CSV file path")
    parser.add_argument("--output", default="skincare_2_enriched.csv", help="Output CSV file path")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to enrich")
    parser.add_argument("--column", default="Product Name", help="Name of the column containing product names")
    
    args = parser.parse_args()
    
    enrich_data(args.input, args.output, args.limit, args.column)

if __name__ == "__main__":
    main()
