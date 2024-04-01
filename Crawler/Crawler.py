import pandas as pd
import requests
from bs4 import BeautifulSoup
import pyap
from urllib.parse import urljoin, urlparse
import spacy
from bs4 import BeautifulSoup
import csv
import pyarrow as pa
from pyarrow.parquet import ParquetFile

def write_addresses_to_csv(output_file, addresses):
    with open(output_file, mode='w', newline='\n') as file:
        writer = csv.DictWriter(file, fieldnames=["country", "region", "city", "postcode", "road", "road_numbers"])
        writer.writeheader()
        for address in addresses:
            writer.writerow(address)

# Read from Parquet file
df = ParquetFile('websites.parquet')
first_100_rows = next(df.iter_batches(batch_size = 100)) 
df = pa.Table.from_batches([first_100_rows]).to_pandas() 

# Function to fetch HTML content from a website
def fetch_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch HTML from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching HTML from {url}: {e}")
        return None

# Function to extract addresses from HTML content

def extract_addresses(html_content):
    addresses = []
    
    # Extract text from HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    # Extract potential addresses using pyap
    parsed_addresses = pyap.parse(text, country='US')
    for parsed_address in parsed_addresses:
        potential_address = parsed_address.full_address
        print('this is potential address foun  ' + potential_address)
        # Pass potential address through custom NER model
        doc = nlp(potential_address)
        ent1_list=[(ent1.text, ent1.label_) for ent1 in doc.ents]
        print("Address string -> "+potential_address)
        print("Parsed address -> "+str(ent1_list))

        address = {
        "country": None,
        "region": None,
        "city": None,
        "postcode": None,
        "road": None,
        "road_numbers": None
        }
        for ent_text, ent_label in ent1_list:
            #print(ent_text)
            #print(ent_label)
            if ent_label in ["ROAD", "ROAD_NUMBERS", "CITY", "REGION", "COUNTRY", "POSTCODE"]:

                if ent_label == "COUNTRY":
                    address["country"] = ent_text
                elif ent_label == "REGION":
                    address["region"] = ent_text
                elif ent_label == "CITY":
                    address["city"] = ent_text
                elif ent_label == "POSTCODE":
                    address["postcode"] = ent_text
                elif ent_label == "ROAD":
                    address["road"] = ent_text
                elif ent_label == "ROAD_NUMBERS":
                    address["road_numbers"] = ent_text

        addresses.append(address)
                #print(address)
                #print(address["road_numbers"])
                #print(address["road"])

    return addresses

# Load your custom NER model
custom_ner_model_path = "mymodel"  # Update with your model path
nlp = spacy.load(custom_ner_model_path)

# Function to extract URLs from a page
def extract_urls_from_page(html_content, base_url):
    urls = []
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)
        if parsed_url.netloc == parsed_home_url.netloc:
            if "about" in parsed_url.path or "contact" in parsed_url.path:
                urls.append(absolute_url)
    return urls

# Iterate over domain names, fetch HTML, and extract addresses
unique_addresses = set()
all_addresses = []
for domain in df["domain"]:
    base_url = f"https://{domain}"  # Add http:// or https:// as needed
    html_content = fetch_html(base_url)
    if html_content:
        # Flag to track if at least one address is found for this domain
        address_found = False
        
        # Extract addresses from the homepage
        addresses = extract_addresses(html_content)
        print(f"Addresses extracted from {base_url}:")
        for address in addresses:
            if tuple(address.items()) not in unique_addresses:
                all_addresses.append(address)
                unique_addresses.add(tuple(address.items()))
                address_found = True  # Set flag to True if an address is found

        # If at least one address is found for this domain, continue to the next domain
        if address_found:
            continue
        # Extract URLs from the homepage
        parsed_home_url = urlparse(base_url)
        linked_urls = extract_urls_from_page(html_content, base_url)    
        
        
        # Fetch HTML content from the linked URLs and extract addresses
        for linked_url in linked_urls:
            linked_html_content = fetch_html(linked_url)
            if linked_html_content:
                linked_addresses = extract_addresses(linked_html_content)
                print(f"Addresses extracted from {linked_url}:")
                for address in linked_addresses:
                    if tuple(address.items()) not in unique_addresses:
                        print(address)
                        all_addresses.append(address)
                        unique_addresses.add(tuple(address.items()))
                        address_found = True  # Set flag to True if an address is found
                        break  # Stop processing linked URLs if an address is found
            # If at least one address is found for this domain, continue to the next domain
            if address_found:
                break

        
df_addresses = pd.DataFrame(all_addresses)
df.drop_duplicates()
df_addresses.to_csv("extracted_addresses.csv", index=False)
print("Addresses written to extracted_addresses.csv")
