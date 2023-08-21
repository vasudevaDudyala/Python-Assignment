import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape additional product information
def scrape_product_details(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract ASIN (if available)
    asin = soup.find("th", string="ASIN")
    asin_value = asin.find_next("td").get_text(strip=True) if asin else ""

    # Extract Product Description
    product_description = soup.find("div", id="productDescription")
    product_description_text = product_description.get_text(strip=True) if product_description else ""

    # Extract Manufacturer
    manufacturer = soup.find("a", id="bylineInfo")
    manufacturer_name = manufacturer.get_text(strip=True) if manufacturer else ""

    # Extract Description
    description = soup.find("meta", attrs={"name": "description"})
    description_content = description["content"] if description else ""

    return asin_value, product_description_text, manufacturer_name, description_content

# URL of the Amazon product listing page
base_url = "https://www.amazon.in/s"
query_params = {
    "k": "bags",
    "crid": "2M096C61O4MLT",
    "qid": "1653308124",
    "sprefix": "ba,aps,283",
    "ref": "sr_pg_1"
}

# Number of pages to scrape
num_pages = 20

# Initialize lists to store scraped data
product_urls = []
product_names = []
product_prices = []
ratings = []
review_counts = []

for page in range(1, num_pages + 1):
    query_params["page"] = page
    response = requests.get(base_url, params=query_params)
    soup = BeautifulSoup(response.content, "html.parser")

    product_cards = soup.find_all("div", class_="s-result-item")

    for card in product_cards:
        # Extract product URL
        product_link = card.find("a", class_="a-link-normal")
        if product_link:
            product_urls.append("https://www.amazon.in" + product_link["href"])

        # Extract product name
        product_name = card.find("span", class_="a-size-medium")
        if product_name:
            product_names.append(product_name.text.strip())

        # Extract product price
        product_price = card.find("span", class_="a-price")
        if product_price:
            product_prices.append(product_price.find("span", class_="a-offscreen").text.strip())

        # Extract rating
        rating = card.find("span", class_="a-icon-alt")
        if rating:
            ratings.append(rating.text.strip())

        # Extract review count
        review_count = card.find("span", class_="a-size-base")
        if review_count:
            review_counts.append(review_count.text.strip())

# Save the scraped data to a CSV file
output_file = "scraped_products_full.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", "ASIN", "Product Description",
         "Manufacturer", "Description"])

    for i in range(len(product_urls)):
        try:
            asin, product_description, manufacturer, description = scrape_product_details(product_urls[i])

            row_data = [
                product_urls[i],
                product_names[i],
                product_prices[i],
                ratings[i],
                review_counts[i],
                asin,
                product_description,
                manufacturer,
                description
            ]

            writer.writerow(row_data)
        except IndexError as e:
            print(f"Error processing index {i}: {e}")
            print("Data may be missing for this index.")
            continue

print(f"Scraped data saved to {output_file}")
