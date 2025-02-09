import json
import re

with open('sitemap_d8193f4ab33b7beff12431fba6499528.xml', 'r') as file:
    xml_data = file.read()

pattern = r'https:\/\/www\.zomato\.com\/bangalore\/([^\/]+)\/'
matches = re.findall(pattern, xml_data)

unique_urls = set(matches)
url_list = [{"id": index + 1, "url": f"https://www.zomato.com/bangalore/{url}"} for index, url in
            enumerate(unique_urls)]

json_output = json.dumps(url_list, indent=4)

with open('zomato_urls.json', 'w') as json_file:
    json_file.write(json_output)

print("JSON file created successfully.")
