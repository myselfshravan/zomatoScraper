from zomato_scraper import ZomatoScraper

url_list = ["https://www.zomato.com/bangalore/1947-jp-nagar-bangalore",
            "https://www.zomato.com/bangalore/1-bhk-bar-house-kitchen-1-koramangala-6th-block-bangalore"]

# Initialize the scraper
scraper = ZomatoScraper(output_file="ph_numbers.json")

# Initialize the driver
scraper.init_driver()

for url in url_list:
    scraper.load_page(url)

    # Extract the phone number
    phone_number = scraper.extract_phone_number()

    print(f"Phone number: {phone_number}")
